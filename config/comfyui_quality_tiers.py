"""ComfyUI quality tier presets for FLUX workflow generation.

Each tier maps to optimal step count, scheduler, cfg scale, and resolution
for different production needs. These replace hardcoded values scattered
across comfyui_runner.py and workflow JSON files.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class QualityTier:
    """A quality tier defines optimal FLUX inference parameters."""
    name: str
    label: str
    steps: int
    scheduler: str = "euler"
    sampler: str = "normal"
    cfg_scale: float = 1.0
    # Whether to use flux_img2img mode (image-to-image)
    img2img: bool = False
    # Latent upscale factor for non-square resolutions
    latent_upscale: float = 0.0625  # FLUX uses VAE with 8x downsampling


# Quality tiers — ordered from fastest to highest quality
QUALITY_TIERS: dict[str, QualityTier] = {
    "draft": QualityTier(
        name="draft",
        label="Draft (preview)",
        steps=4,
        scheduler="euler",
        sampler="normal",
        cfg_scale=1.0,
    ),
    "production": QualityTier(
        name="production",
        label="Production (standard)",
        steps=20,
        scheduler="euler",
        sampler="karras",
        cfg_scale=1.0,
    ),
    "high_quality": QualityTier(
        name="high_quality",
        label="High quality (LoRA)",
        steps=28,
        scheduler="dpmpp_2m",
        sampler="karras",
        cfg_scale=1.0,
    ),
}


def get_tier(name: str) -> QualityTier:
    """Get a quality tier by name."""
    return QUALITY_TIERS[name]


def default_tier() -> QualityTier:
    """Return the default production quality tier."""
    return QUALITY_TIERS["production"]


@dataclass(frozen=True)
class ModelCacheKey:
    """Deterministic key for model loading cache.

    If two workflows share the same cache key, they can reuse the loaded
    UNET, CLIPs, and VAE — avoiding redundant GPU memory allocations.
    """
    ckpt_name: str = "flux1-dev-bf16.safetensors"
    clip_l: str = "clip_l.safetensors"
    clip_g: str | None = "t5xxl_fp8_e4m3fn.safetensors"
    vae_name: str | None = None
    ipadapter_enabled: bool = False


def workflow_cache_key(
    ckpt: str = "flux1-dev-bf16.safetensors",
    clip_l: str = "clip_l.safetensors",
    use_ipadapter: bool = False,
) -> ModelCacheKey:
    """Generate a cache key for model loading."""
    return ModelCacheKey(ckpt_name=ckpt, clip_l=clip_l, ipadapter_enabled=use_ipadapter)
