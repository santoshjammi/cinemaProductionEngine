"""MusicCapability — generates music tracks (per zone / mood).

This is where music generation models live (procedural synthesis, MusicGen,
future models). For Phase 0, this is a stub. The implementation comes
in later phases.
"""

from __future__ import annotations

import logging

from .base import (
    Capability,
    MusicCapabilityError,
    MusicIntent,
    MusicResult,
)


logger = logging.getLogger("movie_os.capabilities.music")


class MusicCapability(Capability[MusicIntent, MusicResult]):
    """Generate a music track for a given zone and duration."""

    name = "music"
    description = "Generate a music track for a zone (act_1, act_2, act_3, sting)."
    version = "0.1.0"

    def __init__(self, provider=None):
        self._provider = provider

    def can_handle(self, intent: MusicIntent) -> bool:
        return bool(intent.zone)

    async def execute(self, intent: MusicIntent) -> MusicResult:
        if not intent.zone:
            raise MusicCapabilityError("MusicIntent.zone is required")
        if self._provider is not None and hasattr(self._provider, "render"):
            asset = await self._provider.render(intent)
            # Wrap in MusicResult if not already
            if isinstance(asset, MusicResult):
                return asset
            from movie_os.domain.asset import Asset
            if isinstance(asset, Asset):
                return MusicResult(asset=asset, duration_seconds=asset.duration_seconds or 0.0)
            return asset
        raise NotImplementedError(
            "MusicCapability is a stub in Phase 0. "
            "Implementation lands in Phase 4 (wrap MusicGenerator)."
        )
