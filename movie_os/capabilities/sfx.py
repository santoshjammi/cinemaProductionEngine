"""SFXCapability — generates sound effects (thunder, rain, doors, etc.).

This is where SFX generation lives (procedural synthesis, future
models). Phase 8 adds the capability so the multi-agent pipeline
can route to it; concrete providers can plug in via the registry.
"""

from __future__ import annotations

import logging

from .base import (
    Capability,
    SFXCapabilityError,
    SFXIntent,
    SFXResult,
)


logger = logging.getLogger("movie_os.capabilities.sfx")


class SFXCapability(Capability[SFXIntent, SFXResult]):
    """Generate a single SFX clip for a given effect type."""

    name = "sfx"
    description = "Generate a sound effect (thunder, rain, ambient, etc.)."
    version = "0.1.0"

    def __init__(self, provider=None):
        self._provider = provider

    def can_handle(self, intent: SFXIntent) -> bool:
        return bool(intent.effect_type)

    async def execute(self, intent: SFXIntent) -> SFXResult:
        if not intent.effect_type:
            raise SFXCapabilityError("SFXIntent.effect_type is required")
        if self._provider is not None and hasattr(self._provider, "render"):
            asset = await self._provider.render(intent)
            if isinstance(asset, SFXResult):
                return asset
            from movie_os.domain.asset import Asset
            if isinstance(asset, Asset):
                return SFXResult(asset=asset, data={"duration": asset.duration_seconds or 0.0})
            return asset
        # Fallback: return empty result so the pipeline doesn't fail
        logger.debug(f"SFXCapability: no provider for {intent.effect_type}")
        return SFXResult(data={"skipped": True, "effect_type": intent.effect_type})
