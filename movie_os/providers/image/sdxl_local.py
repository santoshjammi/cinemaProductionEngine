"""SDXL Local Provider — wraps the existing SDXL image generator.

This provider generates images using Stable Diffusion XL running
locally on the M1 Max (MPS) or CPU.

It wraps the SDXLGenerator from `scripts/generate_from_yaml.py` —
the existing code that's been producing all our test videos. The
provider class is async, but the underlying SDXL generation is sync;
we use `asyncio.to_thread` to avoid blocking the event loop.

Note: this is a real, working provider. It produces images. Use
`ImageIntent(prompt=...)` and call `await provider.render(intent)`.
"""

from __future__ import annotations

import asyncio
import importlib.util
import logging
from pathlib import Path
from typing import Any

from movie_os.capabilities.base import ImageIntent
from movie_os.domain.asset import Asset, AssetType, AssetStatus, RenderBackend
from movie_os.providers.base import ImageProvider, make_asset, run_sync


logger = logging.getLogger("movie_os.providers.image.sdxl_local")


class SDXLLocalProvider(ImageProvider):
    """SDXL image generation running locally (MPS / CUDA / CPU)."""

    name = "sdxl_local"
    backend = RenderBackend.SDXL_LOCAL

    def __init__(
        self,
        model: str = "stabilityai/stable-diffusion-xl-base-1.0",
        device: str = "mps",
        dtype: str = "float16",
        resolution_width: int = 1024,
        resolution_height: int = 576,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
        num_candidates: int = 4,
        min_clip_score: float = 0.30,
    ):
        self.model = model
        self.device = device
        self.dtype = dtype
        self.resolution_width = resolution_width
        self.resolution_height = resolution_height
        self.num_inference_steps = num_inference_steps
        self.guidance_scale = guidance_scale
        self.num_candidates = num_candidates
        self.min_clip_score = min_clip_score
        self._generator = None
        self._manifest = None

    def _ensure_generator(self, manifest: dict):
        """Lazy-load the SDXL generator."""
        if self._generator is not None and self._manifest is manifest:
            return
        # Import the legacy SDXLGenerator from scripts/generate_from_yaml.py
        gen_script = Path(__file__).parent.parent.parent.parent / "scripts" / "generate_from_yaml.py"
        if not gen_script.exists():
            raise FileNotFoundError(
                f"SDXL generator not found at {gen_script}. "
                "The legacy generator script is required for the SDXL provider."
            )
        spec = importlib.util.spec_from_file_location("generate_from_yaml", gen_script)
        gen_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gen_module)
        manifest["__manifest_path__"] = str(gen_script)
        self._generator = gen_module.SDXLGenerator(manifest, output_dir=self._output_dir or "output/videos")
        self._manifest = manifest

    def _build_minimal_manifest(self, intent: ImageIntent) -> dict:
        """Build a minimal manifest for the SDXL generator from an ImageIntent."""
        return {
            "model": {
                "name": self.model,
                "type": "sdxl",
                "dtype": self.dtype,
                "device": self.device,
                "resolution": {"width": self.resolution_width, "height": self.resolution_height},
            },
            "generation": {
                "num_inference_steps": self.num_inference_steps,
                "guidance_scale": self.guidance_scale,
                "num_candidates": self.num_candidates,
                "min_clip_score": self.min_clip_score,
            },
            "characters": {},
            "visual_system": {
                "negative_prompt": intent.negative_prompt,
            },
        }

    async def render(self, intent: ImageIntent) -> Asset:
        """Render an image synchronously (wrapped in to_thread)."""
        # Phase 4 — wrap, not rewrite.
        # The actual generation happens in the legacy SDXLGenerator.
        # We build a minimal scene dict and call it.

        if not intent.prompt:
            raise ValueError("ImageIntent.prompt is required")

        # Build a minimal scene dict (the legacy generator expects scenes)
        scene = {
            "scene_number": 1,
            "title": "Untitled",
            "phase": "default",
            "beat": "default",
            "act": "act_1_observation",
            "mood": "neutral",
            "energy": 5,
            "voiceover": "",
            "scene_description": intent.prompt,
            "visual_cause_of_emotion": "",
            "shot_language": {
                "shot_size": "medium",
                "lighting_key": "natural_shadows",
                "lens_mm": 50,
                "depth_of_field": "shallow",
            },
            "characters_present": [],
            "ken_burns_effect": "ken-burns",
            "duration_hint": "20-30s",
        }
        manifest = self._build_minimal_manifest(intent)
        output_dir = intent.metadata.get("output_dir", "output/videos") if intent.metadata else "output/videos"
        pipeline_id = intent.metadata.get("pipeline_id", "sdxl_render") if intent.metadata else "sdxl_render"
        # The legacy generator is sync — run it in a thread
        result = await run_sync(
            self._generate_sync, scene, manifest, output_dir, pipeline_id
        )
        return result

    def _generate_sync(self, scene: dict, manifest: dict, output_dir: str, pipeline_id: str) -> Asset:
        """The actual sync generation call."""
        self._output_dir = output_dir
        self._ensure_generator(manifest)
        result = self._generator.generate_scene_image(pipeline_id, scene)
        # The legacy generator returns {"scene_number", "status", "clip_score", ...}
        # and writes the file to output_dir/pipeline_id/scene_images/scene_001.png
        image_path = Path(output_dir) / pipeline_id / "scene_images" / f"scene_{scene['scene_number']:03d}.png"
        clip_score = result.get("clip_score")
        return make_asset(
            path=image_path,
            asset_type=AssetType.IMAGE,
            backend=self.backend,
            clip_score=clip_score,
            metadata={
                "model": self.model,
                "prompt": scene["scene_description"],
                "result": result,
            },
        )

    def can_handle(self, intent: ImageIntent) -> bool:
        return bool(intent.prompt)


# Factory function — used by the built-in provider factory
def make(settings: dict, cost_per_call_usd: float = 0.0) -> SDXLLocalProvider:
    """Build an SDXLLocalProvider from config settings."""
    return SDXLLocalProvider(
        model=settings.get("model", "stabilityai/stable-diffusion-xl-base-1.0"),
        device=settings.get("device", "mps"),
        dtype=settings.get("dtype", "float16"),
        resolution_width=settings.get("resolution_width", 1024),
        resolution_height=settings.get("resolution_height", 576),
        num_inference_steps=settings.get("num_inference_steps", 30),
        guidance_scale=settings.get("guidance_scale", 7.5),
        num_candidates=settings.get("num_candidates", 4),
        min_clip_score=settings.get("min_clip_score", 0.30),
    )
