"""
audio_mixer — Dialogue + music mixing with silence preservation.

Operations:
  - Load dialogue WAV files and music tracks
  - Resample to common sample rate (44100 Hz)
  - Apply level adjustments (dialogue boosted above music)
  - Preserve required silence periods from the timing plan
  - Export mixed audio as WAV
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import wave
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class MixResult:
    success: bool
    mixed_file: str | None = None
    duration_seconds: float = 0.0
    sample_rate: int = 44100
    channels: int = 1
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class SilenceSpec:
    """Silence interval in seconds."""
    start: float
    duration: float

    def to_dict(self):
        return {"start": self.start, "duration": self.duration}


# ---------------------------------------------------------------------------
# Audio loading (via ffmpeg decode for compatibility)
# ---------------------------------------------------------------------------

def _load_audio_as_float(filepath: str | Path, sample_rate: int = 44100) -> tuple[Any, float] | None:
    """Load audio file as numpy float32 array using ffmpeg decode.

    Returns (array, duration) or None on failure.
    Uses ffmpeg's -f f32le output to get raw float samples.
    """
    import numpy as np  # type: ignore

    try:
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=sample_rate,channels,duration",
            "-of", "json",
            str(filepath),
        ]
        proc = subprocess.run(probe_cmd, capture_output=True, text=False, timeout=15)
        if proc.returncode != 0:
            return None

        data = json.loads(proc.stdout)
        stream = data.get("streams", [{}])[0]
        channels = stream.get("channels", 1) or 1
        sr = int(stream.get("sample_rate", sample_rate))
        dur_str = stream.get("duration", "0")

        # Resample to target sample rate if needed using ffmpeg
        resample_needed = sr != sample_rate

        if resample_needed:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                subprocess.run(
                    ["ffmpeg", "-y", "-i", str(filepath),
                     "-ar", str(sample_rate),
                     "-ac", "1",  # Mono for simplicity
                     "-f", "f32le", tmp.name],
                    capture_output=True, timeout=30
                )
                load_path = tmp.name
        else:
            load_path = filepath

        # Decode to float32
        decode_cmd = [
            "ffmpeg", "-y", "-i", str(load_path),
            "-f", "f32le", "-acodec", "pcm_f32le",
            "-ar", str(sample_rate), "-",
        ]
        proc2 = subprocess.run(decode_cmd, capture_output=True, timeout=30)
        if proc2.returncode != 0:
            return None

        samples = np.frombuffer(proc2.stdout, dtype=np.float32)

        # If stereo was detected, mix to mono by averaging channels
        if channels > 1 and not resample_needed:
            n_frames = len(samples) // channels
            if n_frames > 0:
                samples = samples[:n_frames * channels].reshape(n_frames, channels).mean(axis=1)

        duration = float(dur_str) if dur_str else len(samples) / sample_rate
        return samples, duration

    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception):
        return None


def _save_audio_numpy(filepath: str | Path, samples: Any, sample_rate: int = 44100) -> str:
    """Save numpy float32 array as WAV file."""
    import numpy as np  # type: ignore

    p = Path(filepath)
    p.parent.mkdir(parents=True, exist_ok=True)

    # Clamp to safe range
    samples = np.clip(samples, -1.0, 1.0)

    # Convert to int16 for WAV
    samples_int16 = (samples * 32767).astype(np.int16)

    with wave.open(str(p), 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(samples_int16.tobytes())

    return str(p)


# ---------------------------------------------------------------------------
# Mixing logic
# ---------------------------------------------------------------------------

def _apply_silence_periods(audio: Any, silence_specs: list[SilenceSpec], sr: int) -> Any:
    """Apply silence (zero out) at specified intervals."""
    import numpy as np  # type: ignore

    for spec in silence_specs:
        start_sample = int(spec.start * sr)
        end_sample = start_sample + int(spec.duration * sr)
        if start_sample < len(audio):
            audio[start_sample:end_sample] = 0.0

    return audio


def _compute_silence_from_dialogue(dialogue_data: dict, duration: float) -> list[SilenceSpec]:
    """Derive silence intervals from dialogue structure.

    Rules:
      - 0.5s pause between speaker turns
      - 1.0s silence before first line if scene starts with tension (from audio_tone)
      - Duration of each line ≈ text length / 150 characters-per-second speaking rate
    """
    lines = dialogue_data.get("lines", [])
    silence_specs: list[SilenceSpec] = []

    total_text_length = sum(len(line.get("text", "")) for line in lines)
    speak_rate_chars_per_sec = 150.0

    current_time = 0.0

    # Check if scene starts with tension (from audio tone)
    audio_tone = dialogue_data.get("audio_tone", "")
    starts_with_tension = any(kw in str(audio_tone).lower() for kw in ["tension", "quiet", "melancholic", "restrained"])

    if starts_with_tension and lines:
        silence_specs.append(SilenceSpec(start=0.0, duration=1.0))
        current_time = 1.0

    for i, line in enumerate(lines):
        text = line.get("text", "")
        # Estimate speech duration (conversational rate with emotional modifiers)
        base_duration = max(1.0, len(text) / speak_rate_chars_per_sec)

        # Emotional modifier — "cautious_hope" or "fear" slows delivery
        emotion = ""
        speaker_data = dialogue_data.get("emotional_state", {})
        speaker_id = line.get("speaker_id", "")
        for spk in ["sarah", "mark"]:
            spk_data = speaker_data.get(spk, {})
            if spk_id.lower().endswith(spk):
                emotion = spk_data.get("emotion", "")
                break

        if "fear" in emotion or "cautious" in emotion:
            base_duration *= 1.3  # Slower delivery

        # Add pause after line (unless it's the last line)
        silence_specs.append(SilenceSpec(start=current_time, duration=base_duration))
        current_time += base_duration + 0.5  # Default 0.5s gap between speakers

    return silence_specs


# ---------------------------------------------------------------------------
# Main Mixer
# ---------------------------------------------------------------------------

class AudioMixer:
    """Mix dialogue tracks above music with silence preservation."""

    def mix(
        self,
        dialogue_files: list[str | Path],
        ambience_track: str | Path | None = None,
        score_track: str | Path | None = None,
        dialogue_data: dict | None = None,
        target_duration: float = 5.0,
        output_dir: Path | str | None = None,
    ) -> MixResult:
        """Mix all audio components into a single WAV file."""
        import numpy as np  # type: ignore

        try:
            # Load dialogue files
            dialogue_tracks = []
            for df in dialogue_files:
                loaded = _load_audio_as_float(df)
                if loaded is None:
                    return MixResult(success=False, error=f"Failed to load dialogue file: {df}")
                dialogue_tracks.append((loaded[0], loaded[1]))

            # Load music tracks (ambience + score)
            music_tracks = []
            for mt in [ambience_track, score_track]:
                if mt:
                    loaded = _load_audio_as_float(mt)
                    if loaded is not None and loaded[0].size > 0:
                        music_tracks.append((loaded[0], loaded[1]))

            # Determine common sample rate (use dialogue's SR)
            target_sr = 44100
            if dialogue_tracks:
                target_sr = 44100  # Force 44100 for output compatibility

            # Resample all tracks to common length
            total_samples = int(target_sr * max(target_duration, dialogue_tracks[0][0].size if dialogue_tracks else target_duration))

            # Pad/truncate each track to common length
            resampled_dialogues = []
            for dialog_audio, _ in dialogue_tracks:
                if len(dialog_audio) < total_samples:
                    padded = np.pad(dialog_audio, (0, total_samples - len(dialog_audio)), mode='constant')
                else:
                    padded = dialog_audio[:total_samples]
                resampled_dialogues.append(padded)

            # Combine dialogue (sum all speakers)
            combined_dialogue = np.zeros(total_samples)
            for d in resampled_dialogues:
                combined_dialogue += d / len(resampled_dialogues)  # Average to prevent clipping

            # Create music mix
            if music_tracks:
                # Normalize and combine music tracks
                combined_music = np.zeros(total_samples)
                for music_audio, _ in music_tracks:
                    if len(music_audio) < total_samples:
                        music_audio = np.pad(music_audio, (0, total_samples - len(music_audio)), mode='constant')
                    else:
                        music_audio = music_audio[:total_samples]
                    combined_music += music_audio / max(len(music_tracks), 1)

                # Normalize music to safe level
                if len(combined_music) > 0 and np.max(np.abs(combined_music)) > 0:
                    combined_music = combined_music / np.max(np.abs(combined_music)) * 0.25  # Keep music quiet

                # Mix: dialogue boosted above music (dialogue at 0.8, music at 0.25)
                final = combined_dialogue * 0.7 + combined_music * 1.0
            else:
                final = combined_dialogue * 0.9

            # Apply silence preservation from timing plan or dialogue structure
            if dialogue_data:
                silence_specs = _compute_silence_from_dialogue(dialogue_data, target_duration)
                final = _apply_silence_periods(final, silence_specs, target_sr)
                self.details["silence_specs"] = [s.to_dict() for s in silence_specs]

            # Final normalization (prevent clipping while preserving dynamics)
            peak = np.max(np.abs(final)) if len(final) > 0 else 1
            if peak > 0:
                final = np.clip(final / peak * 0.95, -1.0, 1.0)

            # Save output
            output_path = Path(output_dir) / "mixed_audio.wav" if output_dir else Path("/tmp/scene_mixed.wav")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            _save_audio_numpy(output_path, final, target_sr)

            return MixResult(
                success=True,
                mixed_file=str(output_path),
                duration_seconds=target_duration,
                sample_rate=target_sr,
                channels=1,
                details={
                    "dialogue_tracks_count": len(dialogue_tracks),
                    "music_tracks_count": len(music_tracks),
                    "silence_specs_count": len(silence_specs) if dialogue_data else 0,
                },
            )

        except Exception as e:
            return MixResult(success=False, error=f"Mixer failed: {e}")


def validate_mixed_audio(filepath: str | Path) -> MixResult:
    """Validate the mixed audio file."""
    from builder.media_validators import AudioValidator

    val = AudioValidator(filepath)
    result = val.validate()

    return MixResult(
        success=result.valid,
        mixed_file=str(filepath),
        duration_seconds=result.details.get("duration_seconds", 0),
        sample_rate=result.details.get("sample_rate", 44100),
        details=result.to_dict(),
    )
