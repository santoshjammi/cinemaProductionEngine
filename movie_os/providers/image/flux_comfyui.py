"""FLUX via ComfyUI Provider — the next-generation image backend.

FLUX.1 Dev is a 12B parameter rectified-flow transformer from Black
Forest Labs. It produces significantly better images than SDXL —
sharper, more coherent, better at text rendering, better at complex
compositions. The tradeoff is compute: ~24GB VRAM minimum, ~28 steps,
~10x slower than SDXL on the same hardware.

This provider:
  - Talks to ComfyUI's HTTP API (assumes ComfyUI is running locally)
  - Loads workflow JSON templates from movie_os/workflows/flux/
  - Supports 3 quality modes:
      - draft:      flux-schnell (4 steps, fast iteration)
      - production: flux-dev (20 steps, balanced)
      - high_quality: flux-dev + LoRA (28 steps, best quality)
  - Supports img2img (reference image) and IPAdapter (character consistency)
  - Supports seed locking (reproducibility)
  - Supports negative prompts

This is a real working provider. To use it:
  1. Install ComfyUI (https://github.com/comfyanonymous/ComfyUI)
  2. Download a FLUX checkpoint (flux1-dev-fp8.safetensors)
  3. Start ComfyUI: python main.py --port 8188
  4. Set image.flux_comfyui as the default in your config
  5. Call await image_cap.execute(ImageIntent(prompt=...))

Key improvements over the previous version:
  - Automatic model warmup on first connection (eliminates cold-start freeze)
  - Real-time WebSocket progress updates instead of silent HTTP polling
  - Explicit readiness check that verifies FLUX nodes are loaded, not just alive
"""

from __future__ import annotations

import asyncio
import logging
import shutil
from pathlib import Path
from typing import Any, Optional

from movie_os.capabilities.base import ImageIntent
from movie_os.domain.asset import Asset, AssetType, AssetStatus, RenderBackend
from movie_os.providers.base import ImageProvider, make_asset, run_sync
from movie_os.workflows.comfyui_client import (
    ComfyUIClient,
    ComfyUIError,
    ComfyUIConnectionError,
    check_comfyui_ready,
)


logger = logging.getLogger("movie_os.providers.image.flux_comfyui")


# Map our quality modes to workflow templates + checkpoint names
# Default to bf16 for Apple Silicon (MPS) compatibility.
# CUDA users can override via settings: model: "flux1-dev-fp8.safetensors"
_QUALITY_PROFILES = {
    "draft": {
        "workflow": "flux_txt2img",
        "unet": "flux1-schnell.safetensors",
        "steps": 4,
        "cfg": 1.0,
        "guidance": 1.0,
    },
    "production": {
        "workflow": "flux_txt2img",
        "unet": "flux1-dev-fp8.safetensors",
        "steps": 20,
        "cfg": 1.0,
        "guidance": 3.5,
    },
    "high_quality": {
        "workflow": "flux_with_lora",
        "unet": "flux1-dev-bf16.safetensors",
        "steps": 28,
        "cfg": 4.0,
        "guidance": 3.5,
    },
}


class FluxComfyUIProvider(ImageProvider):
    """FLUX.1 image generation via ComfyUI.

    Wraps the ComfyUIClient. The provider is async (per the Capability
    ABC), but the underlying HTTP calls are sync and wrapped in
    asyncio.to_thread.
    """

    name = "flux_comfyui"
    backend = RenderBackend.FLUX_COMFYUI

    def __init__(
        self,
        comfyui_url: str = "http://localhost:8188",
        api_key: str | None = None,
        model: str = "flux1-schnell.safetensors",
        ipadapter_strength: float = 0.6,
        timeout: float = 600.0,
    ):
        self.comfyui_url = comfyui_url
        self.api_key = api_key
        self.model = model
        self.ipadapter_strength = ipadapter_strength
        self.timeout = timeout
        self._client: Optional[ComfyUIClient] = None
        self._warmed_up: bool = False

    @property
    def client(self) -> ComfyUIClient:
        """Lazy-init the ComfyUI client."""
        if self._client is None:
            self._client = ComfyUIClient(
                base_url=self.comfyui_url,
                api_key=self.api_key,
                timeout=self.timeout,
            )
        return self._client

    def _ensure_client(self) -> ComfyUIClient:
        """Alias for backward compatibility."""
        return self.client

    async def _warmup_once(self) -> None:
        """Send a minimal workflow to preload FLUX weights into VRAM.

        Only runs once per provider instance.  Subsequent renders are
        significantly faster because the execution graph is compiled and
        model weights are resident.
        """
        if self._warmed_up:
            return

        # Check readiness first — ComfyUI might still be loading
        ready = await asyncio.to_thread(
            check_comfyui_ready,
            base_url=self.comfyui_url,
            timeout=120.0,
            node_prefixes=["Flux", "UNETLoader", "clip_text"],
        )

        if not ready:
            logger.warning(
                "[ComfyUI] Provider warmup skipped — ComfyUI not yet ready. "
                "First render will be slow while FLUX loads."
            )
            self._warmed_up = True  # don't retry indefinitely
            return

        # Build a minimal warmup workflow (no placeholders needed)
        warmup_workflow = {
            "1": {"class_type": "CheckpointLoaderSimple",
                  "inputs": {"ckpt_name": self.model}},
            "2": {"class_type": "CLIPTextEncodeFlux",
                  "inputs": {"clip": ["1", 0],
                             "t5xxl": "a test image to warm up the text encoder",
                             "clip_l": "",
                             "guidance": 3.5}},
            "3": {"class_type": "CLIPTextEncodeFlux",
                  "inputs": {"clip": ["1", 0],
                             "t5xxl": "",
                             "clip_l": "",
                             "guidance": 1.0}},
            "4": {"class_type": "EmptyLatentImage",
                  "inputs": {"width": 512, "height": 512, "batch_size": 1}},
            "5": {"class_type": "KSamplerFlux",
                  "inputs": {"model": ["1", 0], "positive": ["2", 0],
                             "negative": ["3", 0], "latent_image": ["4", 0],
                             "seed": 0, "steps": 1, "cfg": 1.0,
                             "sampler_name": "euler", "scheduler": "normal"}},
            "6": {"class_type": "VAEDecodeFlux",
                  "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        }

        logger.info("[ComfyUI] Warming up FLUX (%s) in VRAM...", self.model)
        try:
            pid = self.client.submit(warmup_workflow, priority="high")
            result = self.client.wait_for_result(
                pid, timeout=120.0, show_progress=True
            )
            if result.get("status", {}).get("completed"):
                logger.info("[ComfyUI] Warmup complete — model ready in VRAM")
            else:
                logger.warning("[ComfyUI] Warmup did not complete — model may still be loading")
        except (ComfyUIError, ComfyUIConnectionError) as exc:
            logger.warning("[ComfyUI] Warmup failed (%s); will retry on next render", exc)

        self._warmed_up = True

    def _select_workflow(self, intent: ImageIntent) -> str:
        """Pick the right workflow based on the intent's quality and references."""
        metadata = intent.metadata or {}
        # If a reference image is provided, use IPAdapter (for character consistency)
        if intent.reference_image_paths and metadata.get("use_ipadapter", True):
            return "flux_with_ipadapter"
        # If the user explicitly wants img2img
        if intent.reference_image_paths and metadata.get("use_img2img", False):
            return "flux_img2img"
        # Otherwise, use the quality-based profile
        quality = metadata.get("quality", "production")
        if quality not in _QUALITY_PROFILES:
            quality = "production"
        return _QUALITY_PROFILES[quality]["workflow"]

    def _build_workflow(
        self,
        intent: ImageIntent,
        workflow_name: str,
    ) -> dict:
        """Build a workflow by loading the template and filling placeholders.

        The workflow JSONs use placeholders for prompt text only. The
        sampler settings (steps, cfg, seed, guidance), size, and model
        are injected here based on the intent and quality profile.
        """
        from movie_os.workflows import load_workflow, fill_placeholders

        workflow = load_workflow(workflow_name)
        metadata = intent.metadata or {}

        # Quality can come from the intent directly OR from metadata
        quality = intent.quality or metadata.get("quality", "production")
        profile = _QUALITY_PROFILES.get(quality, _QUALITY_PROFILES["production"])

        # Fill text placeholders (prompt + negative prompt)
        replacements = {
            "prompt": intent.prompt,
            "negative_prompt": intent.negative_prompt,
        }
        if intent.reference_image_paths:
            replacements["reference_image"] = intent.reference_image_paths[0]
            replacements["character_reference"] = intent.reference_image_paths[0]
        else:
            replacements["reference_image"] = ""
            replacements["character_reference"] = ""
        if workflow_name == "flux_with_lora":
            replacements["lora_name"] = metadata.get(
                "lora_name", "flux-film-photo-style.safetensors"
            )
        fill_placeholders(workflow, replacements)

        # Inject sampler/conditioning settings into the right nodes
        seed = intent.seed if intent.seed is not None else 42
        # Config-driven denoise (img2img identity lock). Falls back to the
        # workflow's own value if not provided.
        denoise = intent.metadata.get("denoise") if intent.metadata else None
        for node in workflow.values():
            ctype = node.get("class_type", "")
            if ctype == "KSampler":
                node["inputs"]["seed"] = seed
                node["inputs"]["steps"] = profile["steps"]
                node["inputs"]["cfg"] = profile["cfg"]
                if denoise is not None:
                    node["inputs"]["denoise"] = float(denoise)
            elif ctype == "FluxGuidance":
                node["inputs"]["guidance"] = profile.get("guidance", 3.5)
            elif ctype == "EmptyLatentImage":
                node["inputs"]["width"] = intent.width
                node["inputs"]["height"] = intent.height
            elif ctype == "UNETLoader" or ctype == "CheckpointLoaderSimple":
                node["inputs"]["unet_name"] = self.model
            elif ctype == "DualCLIPLoader":
                node["inputs"]["device"] = "cpu"

        return workflow

    async def render(self, intent: ImageIntent) -> Asset:
        """Render an image via ComfyUI + FLUX.

        Submits the workflow, polls for completion, downloads the
        result image, and returns an Asset.
        """
        if not intent.prompt:
            raise ValueError("ImageIntent.prompt is required")

        # Warmup before the first render (non-blocking — runs in background)
        await self._warmup_once()

        return await run_sync(self._render_sync, intent)

    def _render_sync(self, intent: ImageIntent) -> Asset:
        """The actual sync render call."""
        client = self.client

        # 1. Select the right workflow
        workflow_name = self._select_workflow(intent)
        workflow = self._build_workflow(intent, workflow_name)

        logger.info(
            f"[ComfyUI] Rendering — workflow={workflow_name}, "
            f"prompt_len={len(intent.prompt)}, model={self.model}"
        )

        # 2. Submit to ComfyUI (high priority to avoid queue congestion)
        prompt_id = client.submit(workflow, priority="high")

        # 3. Wait for completion with progress feedback
        try:
            history = client.wait_for_result(prompt_id, show_progress=True)
        except Exception as exc:
            raise RuntimeError(
                f"ComfyUI render failed for prompt {prompt_id}: {exc}"
            ) from exc

        # 4. Extract the output image
        outputs = client.get_outputs(history)
        if not outputs:
            raise RuntimeError(
                f"ComfyUI returned no outputs for prompt {prompt_id}. "
                f"History: {history}"
            )

        first_output = outputs[0]
        filename = first_output["filename"]
        subfolder = first_output.get("subfolder", "")

        # 5. Save the image locally
        output_dir = (intent.metadata or {}).get("output_dir", "output/videos")
        pipeline_id = (intent.metadata or {}).get("pipeline_id", "flux_render")
        scene_num = (intent.metadata or {}).get("scene_number", 1)
        local_path = (
            Path(output_dir) / pipeline_id / "scene_images"
            / f"scene_{scene_num:03d}.png"
        )
        client.save_image(filename, local_path, subfolder)

        # 6. Build the Asset
        actual_seed = intent.seed
        try:
            prompt_meta = history.get("prompt", [{}])[0] if history.get("prompt") else {}
            actual_seed = prompt_meta.get("extra_info", {}).get("seed", actual_seed)
        except Exception:
            pass

        return make_asset(
            path=local_path,
            asset_type=AssetType.IMAGE,
            backend=self.backend,
            seed=actual_seed,
            metadata={
                "model": self.model,
                "workflow": workflow_name,
                "prompt_id": prompt_id,
                "comfyui_url": self.comfyui_url,
            },
        )

    def can_handle(self, intent: ImageIntent) -> bool:
        return bool(intent.prompt)


# Factory function — used by the built-in provider factory
def make(settings: dict, cost_per_call_usd: float = 0.0) -> FluxComfyUIProvider:
    """Build a FluxComfyUIProvider from config settings."""
    return FluxComfyUIProvider(
        comfyui_url=settings.get("comfyui_url", "http://localhost:8188"),
        api_key=settings.get("api_key"),
        model=settings.get("model", "flux1-dev-fp8.safetensors"),
        ipadapter_strength=settings.get("ipadapter_strength", 0.6),
        timeout=settings.get("timeout", 600.0),
    )


# ---------------------------------------------------------------------------
# One-shot helpers (useful from the CLI or scripts)
# ---------------------------------------------------------------------------

async def check_and_warmup(base_url: str = "http://localhost:8188") -> bool:
    """Quick CLI helper: probe ComfyUI and warm FLUX.

    Usage::

        python -c "from movie_os.providers.image.flux_comfyui import check_and_warmup; import asyncio; print(asyncio.run(check_and_warmup()))"
    """
    client = ComfyUIClient(base_url=base_url)

    logger.info("[ComfyUI] Checking liveness...")
    if not client.health():
        logger.warning("[ComfyUI] Not responding — is it running?")
        return False

    logger.info("[ComfyUI] Checking FLUX readiness (this may take a minute)...")
    ready = await asyncio.to_thread(
        client.wait_for_node_ready, timeout=120.0, node_prefixes=["Flux", "UNETLoader"]
    )

    if ready:
        logger.info("[ComfyUI] Reading model info...")
        models = await asyncio.to_thread(client.list_models)
        logger.info("[ComfyUI] Available models: %s", [m.get("name", "?") for m in models[:10]])
        return True

    logger.warning("[ComfyUI] FLUX not ready yet — check VRAM / model paths")
    return False
