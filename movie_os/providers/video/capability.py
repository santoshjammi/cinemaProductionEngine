"""VideoCapability — generates short video clips from images via Stable Video Diffusion.

This capability dispatches to a registered VideoProvider (e.g., SVDComfyUIProvider,
SVDLocalProvider). The provider handles model loading and inference.

Usage:
    result = await video_cap.execute(VideoIntent(image_path="scene.png", prompt="camera push-in"))
"""

from __future__ import annotations

import logging
from typing import Any

from .base import (
    Capability,
    VideoCapabilityError,
    VideoIntent,
    VideoResult,
)


logger = logging.getLogger("movie_os.capabilities.video")


class VideoCapability(Capability[VideoIntent, VideoResult]):
    """Generate a video clip from an image using SVD."""

    name = "video"
    description = "Generate a short video clip from a single image."
    version = "1.0.0"

    def __init__(self, provider: Any = None):
        self._provider = provider

    @property
    def provider(self) -> Any:
        if self._provider is None:
            from movie_os.providers.video.registry import get_default_registry
            registry = get_default_registry()
            if registry.has("video"):
                self._provider = registry.get("video")
        return self._provider

    def can_handle(self, intent: VideoIntent) -> bool:
        return bool(intent.image_path) or (intent.prompt and intent.motion)

    async def execute(self, intent: VideoIntent) -> VideoResult:
        if not intent.image_path and not (intent.prompt and intent.motion):
            raise VideoCapabilityError(
                "VideoIntent requires either image_path OR (prompt + motion)"
            )

        provider = self.provider
        if provider is None:
            # Lazy fallback — try importing SVDLocalProvider
            from movie_os.providers.video.svd_local import SVDLocalProvider
            provider = SVDLocalProvider()
            result = await provider.render(intent)
            return VideoResult(
                asset=result,
                motion_score=None,
                backend=getattr(provider, 'backend', None),
            )

        logger.info("VideoCapability via %s", provider.__class__.__name__)

        if hasattr(provider, "render"):
            asset = await provider.render(intent)
        elif hasattr(provider, "generate"):
            asset = await provider.generate(intent)
        else:
            raise VideoCapabilityError(
                f"Provider {provider.__class__.__name__} needs render() or generate()"
            )

        return VideoResult(
            asset=asset,
            motion_score=None,
            backend=getattr(provider, "backend", None),
        )
