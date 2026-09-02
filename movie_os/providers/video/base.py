"""VideoCapability — generates short video clips from images via Stable Video Diffusion.

This capability dispatches to a registered VideoProvider (e.g., SVDComfyUIProvider,
SVDLocalProvider). The provider handles model loading and inference.

Usage:
    result = await video_cap.execute(VideoIntent(image_path="scene.png", prompt="camera push-in"))
"""

from __future__ import annotations

import logging
from typing import Any

from movie_os.domain.asset import Asset, AssetType

logger = logging.getLogger("movie_os.capabilities.video")


class VideoIntent:
    """Intent for video generation."""
    def __init__(
        self,
        image_path=None,
        prompt="",
        motion="default",
        width=576,
        height=1024,
        num_frames=25,
        fps=7,
        motion_bucket_id=127,
        noise_aug_strength=0.02,
        decode_chunk_size=8,
        frames_per_second=7,
        output_path=None,
    ):
        self.image_path = image_path
        self.prompt = prompt
        self.motion = motion
        self.width = width
        self.height = height
        self.num_frames = num_frames
        self.fps = fps
        self.motion_bucket_id = motion_bucket_id
        self.noise_aug_strength = noise_aug_strength
        self.decode_chunk_size = decode_chunk_size
        self.frames_per_second = frames_per_second
        self.output_path = output_path


class VideoResult:
    """Result from video generation."""
    def __init__(self, asset: Asset = None, motion_score=None, backend=None):
        self.asset = asset
        self.motion_score = motion_score
        self.backend = backend


class VideoProvider:
    """Abstract base for a video capability provider (VideoIntent -> VideoResult)."""

    name: str = "video_provider"
    description: str = "Video generation via Stable Video Diffusion."
    version: str = "1.0"

    def can_handle(self, intent: VideoIntent) -> int | str | bool:  # noqa: SIM103
        return True

    async def render(self, intent: VideoIntent) -> Asset:
        raise NotImplementedError


class VideoCapability:
    """Generate a video clip from an image using SVD."""

    name = "video"
    description = "Generate a short video clip from a single image."
    version = "1.0.0"

    def __init__(self, provider=None):
        self._provider = provider

    @property
    def provider(self) -> Any:
        if self._provider is None:
            # Lazy fallback — try importing SVDLocalProvider
            from movie_os.providers.video.svd_local import SVDLocalProvider
            self._provider = SVDLocalProvider()
        return self._provider

    def can_handle(self, intent: VideoIntent) -> bool:
        return bool(intent.image_path) or (intent.prompt and intent.motion)

    async def execute(self, intent: VideoIntent) -> VideoResult:
        if not intent.image_path and not (intent.prompt and intent.motion):
            raise ValueError(
                "VideoIntent requires either image_path OR (prompt + motion)"
            )

        provider = self.provider

        logger.info("VideoCapability executing via %s", provider.__class__.__name__)

        if hasattr(provider, "render"):
            asset = await provider.render(intent)
        elif hasattr(provider, "generate"):
            asset = await provider.generate(intent)
        else:
            raise ValueError(
                f"Provider {provider.__class__.__name__} needs render() or generate()"
            )

        return VideoResult(asset=asset, backend=getattr(provider, "backend", None))
