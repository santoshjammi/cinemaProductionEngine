"""VoiceCapability — synthesizes voice from text (TTS).

This is where TTS models live (Edge TTS, Voicebox, Kokoro, future).
For Phase 0, this is a stub. The implementation comes in later phases.
"""

from __future__ import annotations

import logging

from .base import (
    Capability,
    VoiceCapabilityError,
    VoiceIntent,
    VoiceResult,
)


logger = logging.getLogger("movie_os.capabilities.voice")


class VoiceCapability(Capability[VoiceIntent, VoiceResult]):
    """Synthesize a voice clip from text."""

    name = "voice"
    description = "Synthesize a voice clip from text using a TTS model."
    version = "0.1.0"

    def __init__(self, provider=None):
        self._provider = provider

    def can_handle(self, intent: VoiceIntent) -> bool:
        return bool(intent.text)

    async def execute(self, intent: VoiceIntent) -> VoiceResult:
        if not intent.text:
            raise VoiceCapabilityError("VoiceIntent.text is required")
        if self._provider is not None and hasattr(self._provider, "render"):
            asset = await self._provider.render(intent)
            if isinstance(asset, VoiceResult):
                return asset
            from movie_os.domain.asset import Asset
            if isinstance(asset, Asset):
                return VoiceResult(asset=asset, duration_seconds=asset.duration_seconds or 0.0)
            return asset
        raise NotImplementedError(
            "VoiceCapability is a stub in Phase 0. "
            "Implementation lands in Phase 4 (wrap edge-tts)."
        )
