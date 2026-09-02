"""SVDLocalProvider — generate video clips using Stable Video Diffusion (local).

Uses the StabilityAI `stable-video-diffusion-img2vid-xt` model via the
diffusers library.  On first call the checkpoint is downloaded from HuggingFace
and cached on disk (~5-6 GB).  This provider works both as a ComfyUI-less
standalone (for testing) and as a real SVD engine for production use.

Required: `pip install diffusers torch accelerate` in the virtualenv.
"""

from __future__ import annotations

import asyncio
import logging
import tempfile
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from movie_os.providers.video.base import VideoIntent  # noqa: F401

logger = logging.getLogger("movie_os.providers.video.svd_local")


class SVDLocalProvider:
    """Stable Video Diffusion local provider (diffusers pipeline)."""

    name = "svd_local"
    backend = "stable_video_diffusion"

    MODEL_ID = "stabilityai/stable-video-diffusion-img2vid-xt"

    def __init__(
        self,
        model_id: str | None = None,
        device: str | None = None,
        dtype: str | None = None,
        cache_dir: str | Path | None = None,
    ):
        self.model_id = model_id or self.MODEL_ID
        from movie_os.domain.asset import RenderBackend as RB

        self.backend = RB.SVD_LOCAL  # type: ignore[attr-defined]
        self.device = device or self._detect_device()
        import torch
        self.dtype_dtype = dtype or (
            "float16" if torch_available(self.device) else "float32"
        )
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self._pipeline = None

    # ------------------------------------------------------------------
    # Pipeline helpers
    # ------------------------------------------------------------------

    @property
    def pipeline(self):
        """Lazy-load the SVD pipeline (thread-safe once loaded)."""
        if self._pipeline is not None:
            return self._pipeline
        import torch  # noqa: F811

        dtype = getattr(torch, self.dtype_dtype) or torch.float32
        from diffusers import StableVideoDiffusionPipeline  # noqa: F401

        cache_dir = self.cache_dir or Path(tempfile.gettempdir()) / "svd_models"
        cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Loading SVD pipeline [%s] → %s", self.model_id, self.device)
        self._pipeline = StableVideoDiffusionPipeline.from_pretrained(
            self.model_id,
            torch_dtype=dtype,
            cache_dir=str(cache_dir),
        )
        if torch_available(self.device):
            self._pipeline.to(self.device)
            if hasattr(self._pipeline, "enable_sequential_cpu_offload"):
                # Most memory-efficient: keeps weights on CPU, moves each module
                # to the accelerator only when needed. Avoids the MPS peak-memory
                # blowup from the temporal VAE on Apple Silicon.
                self._pipeline.enable_sequential_cpu_offload()
            elif hasattr(self._pipeline, "enable_model_cpu_offload"):
                self._pipeline.enable_model_cpu_offload()
            if hasattr(self._pipeline, "enable_vae_slicing"):
                self._pipeline.enable_vae_slicing()

        logger.info("SVD pipeline loaded on %s (%s)", self.device, dtype)
        return self._pipeline

    def _detect_device(self) -> str:
        try:
            import torch  # noqa: F401

            if torch.cuda.is_available():
                return "cuda"
            if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass
        return "cpu"


# ------------------------------------------------------------------
# Sync wrapper (SVDLocalProvider is *mostly* synchronous; async layer
# just wraps in a thread so the Capability dispatch path stays uniform).
# ------------------------------------------------------------------

def torch_available(device: str) -> bool:
    """Return True if torch can initialise on the given device."""
    try:
        import torch  # noqa: F401

        if device.startswith("cuda") and not torch.cuda.is_available():
            return False
        return True
    except ImportError:
        return False


async def render_with_svd(
    image_path: str | Path,
    output_dir: Path | str | None = None,
    width: int = 576,
    height: int = 1024,
    motion_bucket_id: int = 127,
    noise_aug_strength: float = 0.02,
    decode_chunk_size: int = 8,
    fps: int = 7,
) -> Path:
    """Run SVD image→video and return the output MP4 path."""

    import base64
    import io
    import subprocess

    from PIL import Image  # noqa: F401

    img_path = Path(image_path)
    if not img_path.exists():
        raise FileNotFoundError(f"Input image not found: {img_path}")
    pil_image = Image.open(img_path).convert("RGB").resize((width, height))

    provider = SVDLocalProvider()
    pipe = provider.pipeline  # triggers lazy load

    t0 = time.time()
    logger.info("SVD inference start (image=%s, %dx%d)", img_path, width, height)
    frames = pipe(
        pil_image,
        decode_chunk_size=decode_chunk_size,
        motion_bucket_id=motion_bucket_id,
        noise_aug_strength=noise_aug_strength,
    ).frames[0]

    elapsed_s = time.time() - t0
    logger.info("SVD inference done in %.1fs (%d frames)", elapsed_s, len(frames))

    # --- Write frames to disk and assemble MP4 ----------------------------

    out_dir = Path(output_dir) if output_dir else Path("/tmp") / "svd_output"
    out_dir.mkdir(parents=True, exist_ok=True)

    frames_dir = tempfile.mkdtemp(prefix="svd_frames_")
    for i, fr in enumerate(frames):
        fp = Path(frames_dir) / f"frame_{i:04d}.png"
        fr.save(str(fp))

    # Use ffmpeg to assemble
    mp4_path = out_dir / "clip_svd.mp4"
    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-framerate", str(fps),
                "-pattern_type", "glob",
                "-i", f"{frames_dir}/frame_*.png",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-preset", "medium",
                "-crf", "18",
                str(mp4_path),
            ],
            check=True, capture_output=False,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.warning("ffmpeg assemble failed; saving frames dir for debug: %s", e)
        mp4_path = out_dir / "frames_only"

    if not mp4_path.exists() or mp4_path.stat().st_size == 0:
        # Fallback: create a tiny MP4 from the first frame looped
        mp4_path = _fallback_video(mp4_path.parent, frames_dir)

    return mp4_path


def _fallback_video(out_dir: Path, frames_dir: str) -> Path:
    """Make a tiny 1s video from the last frame, repeated."""
    mp4_path = out_dir / "clip_fallback.mp4"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-loop", "1", "-i", f"{frames_dir}/frame_*.png",
             "-t", "1", "-c:v", "libx264", str(mp4_path)],
            check=True, capture_output=False,
        )
    except Exception:
        pass
    return mp4_path


class SVDLocalProviderImpl:
    """SVD provider instance used by the Capability dispatch."""

    name = "svd_local"
    backend = "stable_video_diffusion"

    def __init__(self, **kwargs):
        self._impl_data = kwargs  # stored but not used; real impl is in render_with_svd()


__all__ = [
    "SVDLocalProvider",
    "torch_available",
    "render_with_svd",
]
