"""Movie OS v1 — Audio Mixer for multi-layer mixing.

Mixes voiceover + music + SFX per scene using FFmpeg's audio filters.
Supports:
- Per-layer volume control
- Fade in/out per layer
- Ducking (music lowers when voice speaks)
- Scene-level audio composition
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


logger = logging.getLogger("movie_os.infra.audio_mixer")


@dataclass
class AudioMixConfig:
    """Configuration for audio mixing."""
    # Layer volumes (0.0 to 1.0)
    voice_volume: float = 1.0
    music_volume: float = 0.3
    sfx_volume: float = 0.5

    # Ducking: how much music lowers when voice is present
    duck_amount: float = 0.7  # Music reduces to 30% of its volume during voice
    duck_threshold_db: float = -20.0  # dB threshold for detecting voice presence

    # Fade settings
    fade_in_duration: float = 2.0  # seconds
    fade_out_duration: float = 3.0  # seconds

    # Output settings
    sample_rate: int = 48000
    channels: int = 2  # stereo
    output_format: str = "wav"  # wav, mp3, flac


@dataclass
class AudioLayer:
    """Represents a single audio layer."""
    file_path: str
    layer_type: str  # "voice", "music", "sfx"
    volume: float = 1.0
    fade_in: float = 0.0
    fade_out: float = 0.0
    start_offset: float = 0.0
    duration: Optional[float] = None


class AudioMixer:
    """Multi-layer audio mixer using FFmpeg.

    Mixes voice, music, and SFX layers with:
    - Per-layer volume control
    - Fade in/out
    - Ducking (music lowers during voice)
    - Scene-level composition
    """

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg = ffmpeg_path

    async def mix_scene_audio(
        self,
        layers: list[AudioLayer],
        config: AudioMixConfig,
        output_path: str,
        scene_duration: float
    ) -> bool:
        """Mix all audio layers for a single scene.

        Args:
            layers: List of audio layers (voice, music, SFX)
            config: Mixing configuration
            output_path: Output mixed audio file path
            scene_duration: Total duration of the scene in seconds

        Returns:
            True if mixing succeeded
        """
        if not layers:
            # Create silence for the scene duration
            cmd = [
                self.ffmpeg, "-y",
                "-f", "lavfi",
                "-i", f"anullsrc=r={config.sample_rate}:cl=stereo:d={scene_duration}",
                "-c:a", f"pcm_s16le",
                output_path
            ]
            return await self._run_ffmpeg(cmd)

        # Build FFmpeg audio filter chain
        audio_filters = []

        # Process each layer
        for idx, layer in enumerate(layers):
            input_arg = f"-i {layer.file_path}" if idx == 0 else f"-ss {layer.start_offset} -i {layer.file_path}"

            layer_filters = []

            # Apply volume
            vol = layer.volume * (config.voice_volume if layer.layer_type == "voice"
                                  else config.music_volume if layer.layer_type == "music"
                                  else config.sfx_volume)
            layer_filters.append(f"volume={vol}")

            # Apply fade in
            if layer.fade_in > 0:
                layer_filters.append(f"afade=t=in:st=0:d={layer.fade_in}")

            # Apply fade out
            if layer.fade_out > 0:
                fade_start = max(0, scene_duration - layer.fade_out)
                layer_filters.append(f"afade=t=out:st={fade_start}:d={layer.fade_out}")

            audio_filters.append(f"[{idx}:a]{','.join(layer_filters)}[a{idx}]")

        # Mix all layers
        if len(layers) > 1:
            inputs = "".join(f"[a{i}]" for i in range(len(layers)))
            audio_filters.append(f"{inputs}amix=inputs={len(layers)}:duration=longest:dropout=0[aout]")

        # Build full command
        cmd = [self.ffmpeg, "-y"]
        for idx, layer in enumerate(layers):
            if idx == 0:
                cmd.extend(["-i", layer.file_path])
            else:
                cmd.extend(["-ss", str(layer.start_offset), "-i", layer.file_path])

        cmd.extend([
            "-filter_complex", ";".join(audio_filters),
            "-map", "[aout]",
            "-c:a", "pcm_s16le",
            "-ar", str(config.sample_rate),
            "-ac", str(config.channels),
            output_path
        ])

        return await self._run_ffmpeg(cmd)

    async def apply_ducking(
        self,
        voice_layer: AudioLayer,
        music_layer: AudioLayer,
        config: AudioMixConfig,
        output_path: str,
        scene_duration: float
    ) -> bool:
        """Apply audio ducking: lower music volume when voice is present.

        Uses FFmpeg's sidechain compression to automatically reduce music
        volume during voice segments.

        Args:
            voice_layer: Voice audio layer
            music_layer: Music audio layer
            config: Ducking configuration
            output_path: Output path with ducked audio
            scene_duration: Scene duration in seconds

        Returns:
            True if successful
        """
        # Create sidechain input (voice)
        cmd = [
            self.ffmpeg, "-y",
            "-i", voice_layer.file_path,
            "-i", music_layer.file_path,
            "-filter_complex",
            f"[1:a]volume={config.music_volume * (1 - config.duck_amount)}[ducked];"
            f"[0:a][ducked]sidechaincompress=threshold={config.duck_threshold_db}:ratio=4:attack=200:release=1000[music];"
            f"[0:a][music]amix=inputs=2:duration=longest[aout]",
            "-map", "[aout]",
            "-c:a", "pcm_s16le",
            "-ar", str(config.sample_rate),
            "-ac", str(config.channels),
            output_path
        ]

        return await self._run_ffmpeg(cmd)

    async def _run_ffmpeg(self, cmd: list[str]) -> bool:
        """Run FFmpeg command and return success status."""
        try:
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()

            if result.returncode != 0:
                logger.error(f"FFmpeg failed (rc={result.returncode}): {stderr.decode()[:200]}")
                return False

            return True

        except Exception as e:
            logger.error(f"FFmpeg exception: {e}")
            return False


__all__ = ["AudioMixer", "AudioMixConfig", "AudioLayer"]
