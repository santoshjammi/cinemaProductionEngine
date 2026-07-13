"""Edge TTS Provider — wraps Microsoft Edge TTS (text-to-speech).

This is the default TTS provider. It uses edge-tts (free, local-friendly
since it just calls Microsoft's public endpoint) and supports SSML prosody
tags for rate, volume, and pitch.

The actual edge-tts call happens in `TTSService` from
`backend/app/services/tts_service.py`. This provider wraps it with
the new async Provider interface.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from movie_os.capabilities.base import VoiceIntent
from movie_os.domain.asset import Asset, AssetType, AssetStatus, RenderBackend
from movie_os.providers.base import VoiceProvider, make_asset, run_sync


logger = logging.getLogger("movie_os.providers.voice.edge_tts")


class EdgeTTSProvider(VoiceProvider):
    """Microsoft Edge TTS — free, cloud-based, no API key needed.

    Wraps the TTSService from backend/app/services/tts_service.py.
    """

    name = "edge_tts"
    backend = RenderBackend.EDGE_TTS

    def __init__(
        self,
        default_voice: str = "en-US-GuyNeural",
        default_language: str = "en-US",
        default_rate: str = "+0%",
    ):
        self.default_voice = default_voice
        self.default_language = default_language
        self.default_rate = default_rate
        self._tts_service = None

    def _ensure_service(self, output_dir: str):
        """Lazy-load the TTS service."""
        if self._tts_service is not None:
            return
        import sys
        backend_path = Path(__file__).parent.parent.parent.parent / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        from app.services.tts_service import TTSService
        self._tts_service = TTSService(output_dir)

    async def render(self, intent: VoiceIntent) -> Asset:
        """Synthesize speech from text."""
        if not intent.text:
            raise ValueError("VoiceIntent.text is required")

        output_dir = intent.metadata.get("output_dir", "output/videos") if intent.metadata else "output/videos"
        pipeline_id = intent.metadata.get("pipeline_id", "edge_tts_render") if intent.metadata else "edge_tts_render"
        scene_num = intent.metadata.get("scene_number", 1) if intent.metadata else 1

        voice = intent.voice or self.default_voice
        rate = intent.rate
        volume = intent.volume
        pitch = intent.pitch
        if intent.prosody_override:
            rate = intent.prosody_override.get("rate", rate)
            volume = intent.prosody_override.get("volume", volume)
            pitch = intent.prosody_override.get("pitch", pitch)

        # The actual call is sync — wrap in to_thread
        asset = await run_sync(
            self._synthesize_sync,
            text=intent.text,
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
            output_dir=output_dir,
            pipeline_id=pipeline_id,
            scene_num=scene_num,
        )
        return asset

    def _synthesize_sync(
        self,
        text: str,
        voice: str,
        rate: str,
        volume: str,
        pitch: str,
        output_dir: str,
        pipeline_id: str,
        scene_num: int,
    ) -> Asset:
        """The actual sync synthesis call."""
        self._ensure_service(output_dir)
        # The TTSService has a generate_speech method that's async
        # but the underlying edge-tts is sync. We call the inner sync logic.
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(
            self._tts_service.generate_speech(
                pipeline_id, scene_num, text,
                prosody_override={"rate": rate, "volume": volume, "pitch": pitch} if any([rate, volume, pitch]) else None,
                vocal_fracture=False,
            )
        )
        audio_path = self._tts_service.get_audio_path(pipeline_id, scene_num)
        # Get duration
        duration = 0.0
        if audio_path and audio_path.exists():
            try:
                import subprocess
                r = subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
                    capture_output=True, text=True, timeout=5,
                )
                duration = float(r.stdout.strip())
            except Exception:
                pass

        return make_asset(
            path=audio_path,
            asset_type=AssetType.AUDIO,
            backend=self.backend,
            metadata={
                "voice": voice,
                "text": text,
                "rate": rate,
                "volume": volume,
                "pitch": pitch,
            },
            duration_seconds=duration,
        )

    def can_handle(self, intent: VoiceIntent) -> bool:
        return bool(intent.text)


def make(settings: dict, cost_per_call_usd: float = 0.0) -> EdgeTTSProvider:
    """Build an EdgeTTSProvider from config settings."""
    return EdgeTTSProvider(
        default_voice=settings.get("default_voice", "en-US-GuyNeural"),
        default_language=settings.get("default_language", "en-US"),
        default_rate=settings.get("default_rate", "+0%"),
    )
