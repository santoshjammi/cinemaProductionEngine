"""VideoCapability — animates an image into a video clip.

This is where image-to-video models live (Stable Video Diffusion,
AnimateDiff, future models). For Phase 0, this is a stub. The
implementation comes in later phases.
"""

from __future__ import annotations

import logging

from .base import (
    Capability,
    VideoCapabilityError,
    VideoIntent,
    VideoResult,
)


logger = logging.getLogger("movie_os.capabilities.video")


class VideoCapability(Capability[VideoIntent, VideoResult]):
    """Animate a still image into a short video clip."""

    name = "video"
    description = "Animate a still image into a short video clip."
    version = "0.1.0"

    def __init__(self, provider=None):
        self._provider = provider

    def can_handle(self, intent: VideoIntent) -> bool:
        return bool(intent.image_path)

    async def execute(self, intent: VideoIntent) -> VideoResult:
        if not intent.image_path:
            raise VideoCapabilityError("VideoIntent.image_path is required")
        if self._provider is not None and hasattr(self._provider, "render"):
            return await self._provider.render(intent)
        raise NotImplementedError(
            "VideoCapability is a stub in Phase 0. "
            "Implementation lands in Phase 4 (wrap SVD) and beyond."
        )
