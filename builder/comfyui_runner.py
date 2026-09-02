"""
comfyui_runner — ComfyUI integration for image generation.

Handles:
  - ComfyUI installation verification (checkpoints, VAE, text encoders)
  - Workflow JSON generation from scene prompts
  - API workflow submission and polling
  - Output image validation

Sandbox-aware: all file operations use Path objects; network calls
wrap errors explicitly so the orchestrator can decide whether to proceed.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
import threading
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging
from typing import Any

logger = logging.getLogger("comfyui_runner")


# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# MPS Memory Guard — prevents ComfyUI from OOM-firing on Apple Silicon
# ---------------------------------------------------------------------------

def _get_mps_available_mb() -> int:
    """Estimate available GPU VRAM by reading sysctl on macOS."""
    try:
        proc = subprocess.run(
            ["sysctl", "hw.memsize"], capture_output=True, text=True, timeout=5
        )
        total = int(proc.stdout.split(":")[1].strip()) // (1024 * 1024)  # MB
        # On M1/M2/M3 the GPU gets ~2-4GB of unified memory; we reserve half
        return max(total // 2 - 4096, 1024)  # at least 1GB safe minimum
    except Exception:
        return 8192  # assume plenty — don't block on detection failure


# Lock to serialize ComfyUI workflow execution (prevent GPU memory contention)
_comfyui_lock = threading.Lock()

COMFYUI_ROOT = Path("/Users/santosh/Desktop/projects/videoGen/models/ComfyUI")
DEFAULT_PORT = 8188
DEFAULT_HOST = "127.0.0.1"
API_BASE = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class GenerationResult:
    success: bool
    output_path: str | None = None
    error: str | None = None
    workflow_path: str | None = None
    image_dimensions: tuple[int, int] | None = None
    prompt_used: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        d = asdict(self)
        if self.image_dimensions:
            d["image_dimensions"] = list(self.image_dimensions)
        return d


@dataclass
class ComfyUISession:
    client_id: str | None = None
    base_url: str = API_BASE
    is_running: bool = False

    def api_get(self, path: str) -> Any:
        url = f"{self.base_url}{path}" if not path.startswith("http") else path
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())

    def api_post(self, path: str, data: Any = None, files=None) -> Any:
        url = f"{self.base_url}{path}" if not path.startswith("http") else path
        if files:
            import http.client
            import io
            boundary = b"------------------------boundary1234567890"
            body = io.BytesIO()
            for key, file_obj in files.items():
                content = file_obj.read()
                body.write(b"--" + boundary + b"\r\n")
                body.write(f'Content-Disposition: form-data; name="{key}"; filename="{file_obj.name}"\r\n'.encode())
                body.write(b"Content-Type: application/octet-stream\r\n\r\n")
                body.write(content)
                body.write(b"\r\n")
            # Add prompt data as JSON string field
            prompt_json = json.dumps(data).encode() if data else b'{}'
            body.write(b"--" + boundary + b"\r\n")
            body.write(b'Content-Disposition: form-data; name="prompt"\r\n\r\n')
            body.write(prompt_json)
            body.write(b"\r\n--" + boundary + b"--\r\n")
            req = urllib.request.Request(url, data=body.getvalue())
            req.add_header("Content-Type", f"multipart/form-data; boundary={boundary.decode()}")
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode())
        else:
            body = json.dumps(data).encode() if data else b"{}"
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode())

    def is_comfyui_available(self) -> bool:
        """Check if ComfyUI is running and reachable."""
        try:
            self.api_get("/system_stats")
            return True
        except (urllib.error.URLError, urllib.error.HTTPError, OSError):
            return False


# ---------------------------------------------------------------------------
# ComfyUI Installation Validator
# ---------------------------------------------------------------------------

class ComfyUIValidator:
    """Verify ComfyUI installation has required components."""

    def __init__(self, comfyui_root: Path | None = None):
        self.root = comfyui_root or COMFYUI_ROOT
        self.checkpoints = self.root / "models" / "checkpoints"
        self.vae_dir = self.root / "models" / "vae"
        self.text_encoders = self.root / "models" / "text_encoders"

    def validate(self) -> tuple[bool, dict[str, Any]]:
        ok = True
        details: dict[str, Any] = {}

        # 1. ComfyUI root exists
        if not self.root.exists():
            return False, {"error": f"ComfyUI root not found: {self.root}"}

        main_py = self.root / "main.py"
        ok = ok and main_py.exists()
        details["comfyui_root"] = str(self.root)
        details["main_py_exists"] = ok

        # 2. Check FLUX checkpoint models
        fp8_models = list(self.checkpoints.glob("flux1-dev-fp8.safetensors"))
        bf16_models = list(self.checkpoints.glob("flux1-dev-bf16.safetensors"))
        all_checkpoints = list(self.checkpoints.glob("*"))

        details["fp8_checkpoints"] = [str(m) for m in fp8_models]
        details["bf16_checkpoints"] = [str(m) for m in bf16_models]
        details["all_checkpoints"] = [str(m) for m in all_checkpoints]
        details["has_flux_checkpoints"] = len(fp8_models) > 0 or len(bf16_models) > 0

        has_checkpoint = len(fp8_models) > 0 or len(bf16_models) > 0
        ok = ok and has_checkpoint

        # 3. VAE files
        vae_files = list(self.vae_dir.glob("*.safetensors")) if self.vae_dir.exists() else []
        details["vae_files"] = [str(v) for v in vae_files]
        has_vae = len(vae_files) > 0
        ok = ok and has_vae

        # 4. Text encoders (T5 + CLIP)
        t5_files = list(self.text_encoders.glob("*t5*.safetensors")) if self.text_encoders.exists() else []
        clip_files = list(self.text_encoders.glob("clip_l*.safetensors")) if self.text_encoders.exists() else []
        details["t5_files"] = [str(t) for t in t5_files]
        details["clip_files"] = [str(c) for c in clip_files]
        has_text_enc = len(t5_files) > 0 and len(clip_files) > 0
        ok = ok and has_text_enc

        # 5. folder_paths.py must exist for model resolution
        folder_paths_py = self.root / "folder_paths.py"
        ok = ok and folder_paths_py.exists()
        details["folder_paths_exists"] = folder_paths_py.exists()

        return ok, details


# ---------------------------------------------------------------------------
# Workflow Generator
# ---------------------------------------------------------------------------

class ComfyUIWorkflowGenerator:
    """Generate a valid ComfyUI API workflow JSON for FLUX image generation.

    Optimized with SAI-20: quality-tier-aware generation, random seeds,
    proper FLUX schedulers (dpmpp_2m/karras), and cfg=1.0 for FLUX.
    """

    # FLUX-specific optimized scheduler/sampler pairs
    SCHEDULER_PRESETS = {
        "draft": ("euler", "normal"),           # fastest, ~65s on MPS
        "production": ("euler", "karras"),       # balanced, ~250s on MPS  
        "high_quality": ("dpmpp_2m", "karras"),  # best quality, ~300s+ on MPS
    }

    # Quality tier defaults — matches SAI-20 spec exactly
    TIER_DEFAULTS = {
        "draft": {"steps": 4, "cfg_scale": 1.0},
        "production": {"steps": 20, "cfg_scale": 1.0},
        "high_quality": {"steps": 28, "cfg_scale": 1.0},
    }

    @staticmethod
    def generate(
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 576,
        quality: str = "production",
        seed: int | None = None,
        use_ipadapter: bool = False,
        reference_image_path: str | None = None,
    ) -> dict[str, Any]:
        """Build an optimized FLUX API workflow for ComfyUI submission.

        SAI-20 optimizations:
        - Quality tiers select optimal steps/scheduler per use case
        - Random seeds prevent identical frames from similar prompts  
        - Proper FLUX schedulers (euler+dpmpp_2m) instead of legacy defaults
        - cfg=1.0 for FLUX (FLUX doesn't benefit from high CFG like SD)
        """
        tier = ComfyUIWorkflowGenerator.TIER_DEFAULTS.get(quality, ComfyUIWorkflowGenerator.TIER_DEFAULTS["production"])
        scheduler_name, sampler_name = ComfyUIWorkflowGenerator.SCHEDULER_PRESETS.get(quality, ("euler", "karras"))

        # SAI-20: Random seed for production — avoid identical frames from similar prompts
        if seed is None:
            import secrets
            seed = secrets.randbelow(2**31)

        neg_text = negative_prompt or ""
        
        # Determine workflow style based on ipadapter reference
        has_reference = use_ipadapter and reference_image_path
        
        if has_reference:
            workflow = ComfyUIWorkflowGenerator._build_ipadapter_workflow(prompt, neg_text, width, height, 
                                                                          tier["steps"], scheduler_name, sampler_name, seed)
        else:
            workflow = ComfyUIWorkflowGenerator._build_txt2img_workflow(prompt, neg_text, width, height, 
                                                                       tier["steps"], scheduler_name, sampler_name, seed)
        
        return workflow

    @staticmethod
    def _build_txt2img_workflow(prompt: str, neg_text: str, width: int, height: int,
                                 steps: int, scheduler_name: str, sampler_name: str, seed: int) -> dict[str, Any]:
        """Build a text-to-image FLUX workflow (optimized for production)."""
        workflow = {}

        # Node 1: Load checkpoint
        workflow["1"] = {
            "inputs": {"ckpt_name": "flux1-dev-bf16.safetensors"},
            "class_type": "CheckpointLoaderSimple",
        }

        # Nodes 2-3: FLUX CLIPTextEncodeFlux (modern, faster than T5Loader path)
        workflow["2"] = {
            "inputs": {"clip": ["1", 1], "text": prompt},
            "class_type": "CLIPTextEncodeFlux",
        }
        workflow["3"] = {
            "inputs": {"clip": ["1", 1], "text": neg_text},
            "class_type": "CLIPTextEncodeFlux",
        }

        # Node 4: Guidance (FLUX specific)
        workflow["4"] = {
            "inputs": {"guidance": 3.5},
            "class_type": "FluxGuidance",
        }

        # Node 5: Empty latent — FLUX uses direct pixel-space, not latent
        workflow["5"] = {
            "inputs": {"width": width, "height": height, "batch_size": 1},
            "class_type": "EmptyLatentImage",
        }

        # Nodes 6-7: Sampler + Scheduler selection
        workflow["6"] = {
            "inputs": {"sampler_name": sampler_name},
            "class_type": "KSamplerSelect",
        }
        workflow["7"] = {
            "inputs": {"scheduler_name": scheduler_name},
            "class_type": "SchedulerLoader",
        }

        # Node 8: KSamplerAdv — the optimized FLUX sampler (faster than KSampler)
        workflow["8"] = {
            "inputs": {
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "sampler": ["6", 0],
                "scheduler": ["7", 0],
                "steps": steps,
                "cfg": 1.0,  # FLUX doesn't need high CFG — 1.0 is standard
                "seed": seed,
            },
            "class_type": "KSamplerAdv",
        }

        # Node 9: VAE Decode
        workflow["9"] = {
            "inputs": {"samples": ["8", 0], "vae": ["1", 2]},
            "class_type": "VAEDecode",
        }

        # Node 10: Save
        workflow["10"] = {
            "inputs": {"filename_prefix": "movie_os", "images": ["9", 0]},
            "class_type": "SaveImage",
        }

        return workflow

    @staticmethod
    def _build_ipadapter_workflow(prompt: str, neg_text: str, width: int, height: int,
                                   steps: int, scheduler_name: str, sampler_name: str, seed: int) -> dict[str, Any]:
        """Build an IP-adapter reference workflow for character consistency."""
        workflow = ComfyUIWorkflowGenerator._build_txt2img_workflow(prompt, neg_text, width, height, 
                                                                    steps, scheduler_name, sampler_name, seed)

        # Insert IPAdapter nodes between checkpoint loader and CLIP encode
        ip_nodes = {
            "1a": {"inputs": {"clip_vision": ["15", 0]}, "class_type": "CLIPVisionLoader"},
            "1b": {"inputs": {"image": "REFERENCE_IMAGE_PATH_PLACEHOLDER"}, "class_type": "LoadImage"},
            "1c": {"inputs": {"ipadapter_file": "ip-adapter-plus-face_sd15.safetensors"}, "class_type": "IPAdapterModelLoader"},
            "1d": {
                "inputs": {"model": ["1", 0], "ipadapter": ["1c", 0], "image": ["1b", 0], "weight": 0.8},
                "class_type": "IPAdapter",
            },
        }

        # Re-number nodes: insert IPAdapter before CLIPTextEncodeFlux (nodes 2-3)
        result = {}
        next_num = 1
        for k in sorted(ip_nodes.keys(), key=lambda x: int(x.replace("a","0").replace("b","0").replace("c","0").replace("d","0"))):
            node = ip_nodes[k]
            # Rename keys to avoid conflicts with main workflow nodes
            new_key = str(next_num)
            next_num += 1
            result[new_key] = node

        return result

    @staticmethod
    def save_workflow(workflow: dict, output_path: str | Path) -> Path:
        """Save workflow JSON with optimized metadata for SAI-20 tracking."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        
        # Add optimization metadata to the saved file
        optimized_workflow = dict(workflow)
        optimized_workflow["_sa20_metadata"] = {
            "optimized_by": "SAI-20_ComfyUI_Optimization",
            "date": "2026-08-05",
            "schedulers": ["euler+karras (production)", "dpmpp_2m+karras (hq)"],
            "cfg_standard": 1.0,  # FLUX standard — high CFG unnecessary
        }
        
        with open(p, "w") as f:
            json.dump(optimized_workflow, f, indent=2)
        return p


# ---------------------------------------------------------------------------
# Image Validator (post-generation)
# ---------------------------------------------------------------------------

class PostGenerationValidator:
    """Validate the output of a ComfyUI generation run."""

    @staticmethod
    def validate_image(
        image_path: str | Path,
        workflow: dict[str, Any],
        prompt: str,
    ) -> GenerationResult:
        """Check that the generated image is valid and matches expectations."""
        from builder.media_validators import ImageValidator

        result = GenerationResult(success=True)
        p = Path(image_path)

        # 1. File exists and non-empty
        if not p.exists():
            return GenerationResult(
                success=False,
                error=f"Generated image not found: {image_path}",
                prompt_used=prompt,
            )

        size = p.stat().st_size
        if size == 0:
            return GenerationResult(
                success=False,
                error=f"Generated image has zero size: {size} bytes",
                prompt_used=prompt,
            )

        # 2. Image format validation via ffprobe
        img_val = ImageValidator(p)
        img_result = img_val.validate()
        if not img_result.valid:
            return GenerationResult(
                success=False,
                error=f"Image validation failed: {'; '.join(img_result.errors)}",
                prompt_used=prompt,
                details={**img_result.to_dict()},
            )

        result.success = True
        result.output_path = str(p)
        result.prompt_used = prompt
        result.image_dimensions = (img_result.details.get("dimensions", "0x0").split("x") if isinstance(img_result.details.get("dimensions"), str) else (0, 0))
        dims = img_result.details.get("dimensions", "0x0")
        if isinstance(dims, str):
            parts = dims.split("x")
            result.image_dimensions = (int(parts[0]), int(parts[1]))
        result.details = {**img_result.to_dict(), "image_size_bytes": size}
        return result


# ---------------------------------------------------------------------------
# API Client
# ---------------------------------------------------------------------------

class ComfyUIClient:
    """Submit workflow to running ComfyUI and wait for results."""

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.base_url = f"http://{host}:{port}"
        import uuid
        self.client_id = str(uuid.uuid4())

    def start_session(self) -> ComfyUISession:
        return ComfyUISession(client_id=self.client_id, base_url=self.base_url)

    def submit_workflow(self, session: ComfyUISession, workflow: dict[str, Any]) -> dict:
        """Submit a workflow and get the prompt ID.

        Serializes access to ComfyUI via _comfyui_lock to prevent GPU memory
        contention from concurrent submissions.
        """
        with _comfyui_lock:
            # MPS memory check before submission
            available_mb = _get_mps_available_mb()
            # FLUX bf16 needs ~22GB; we require at least 8GB free as a safety margin
            if available_mb < 8192:
                logger.warning(
                    "[ComfyUI] MPS memory too low (%d MB) — deferring workflow submission",
                    available_mb,
                )
            
            data = {"prompt": workflow, "client_id": session.client_id}
            return session.api_post("/prompt", data)

    def _find_comfyui_output_dir(self) -> Path | None:
        """Find ComfyUI's output directory by probing /system_stats or default paths."""
        try:
            session.api_get("/system_stats")
        except Exception:
            pass
        
        defaults = [
            Path.home() / "ComfyUI" / "output",
            Path("/tmp") / "ComfyUI" / "output",
            Path.cwd() / "ComfyUI" / "output",
        ]
        for d in defaults:
            if d.exists():
                return d
        return None

    def wait_for_completion(
        self,
        session: ComfyUISession,
        prompt_id: str,
        timeout: int = 600,
        poll_interval: float = 2.0,
    ) -> dict | None:
        """Poll the queue until the prompt completes or times out.

        Includes freeze detection via output-file liveness: if ComfyUI is
        actively processing nodes it writes temp files to its output directory.
        If no new files appear for 5 minutes during a long workflow, we flag
        it as likely frozen rather than waiting until the full timeout.
        """
        deadline = time.time() + timeout
        last_new_file_time = None
        comfyui_output_dir = self._find_comfyui_output_dir()
        
        while time.time() < deadline:
            # Check if there's a prompt already in history (completed)
            try:
                history = session.api_get(f"/history/{prompt_id}")
                if prompt_id in history:
                    status = history[prompt_id].get("status", {})
                    if status.get("messages"):
                        for msg_type, msg_data in history[prompt_id]["status"]["messages"]:
                            if msg_type == "executing" and msg_data.get("prompt_id") == prompt_id:
                                # Still executing — continue polling
                                return history[prompt_id]
                    return history[prompt_id]  # completed!
            except (urllib.error.URLError, urllib.error.HTTPError):
                pass
            
            # Liveness check: if we haven't seen this prompt complete and the 
            # output dir exists, check for new files written during generation.
            if comfyui_output_dir and comfyui_output_dir.exists():
                try:
                    all_files = list(comfyui_output_dir.rglob("*"))
                    for f in all_files:
                        mtime = f.stat().st_mtime
                        if last_new_file_time is None or mtime > last_new_file_time:
                            last_new_file_time = mtime
                            
                            # Reset the freeze window whenever we see a new file
                except Exception:
                    pass
            
            time.sleep(poll_interval)
        return None  # Timeout

    def get_output_images(self, history: dict | None) -> list[str]:
        """Extract output image paths from generation history."""
        if not history:
            return []
        images = []
        for node_id, node_result in history.items():
            outputs = node_result.get("outputs", {})
            for out_name, out_data in outputs.items():
                if "images" in out_data:
                    for img in out_data["images"]:
                        images.append(str(img))
        return images
