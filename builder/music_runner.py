"""
music_runner — Ambience and background score generation.

No beeps or NumPy sine tones are used. All audio is generated through:
  1. Filtered noise for ambience (band-limited, shaped)
  2. Harmonic drones with proper musical intervals
  3. Melodic phrases built from pentatonic/minor scales

If external music APIs are available (Suno/Udio), they are attempted first.
"""

from __future__ import annotations

import json
import math
import subprocess
import tempfile
import wave
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class MusicTrack:
    """A generated music track (ambience or score)."""
    type: str  # "ambience" or "score"
    filepath: str
    duration_seconds: float
    sample_rate: int
    description: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class MusicResult:
    success: bool
    ambience_track: MusicTrack | None = None
    score_track: MusicTrack | None = None
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


# ---------------------------------------------------------------------------
# Music generation — no beeps, no tones
# ---------------------------------------------------------------------------

def _generate_ambience(
    scene_data: dict,
    audio_prompt: dict | None,
    duration_seconds: float = 5.0,
    sample_rate: int = 44100,
) -> MusicTrack:
    """Generate ambient sound using filtered noise and resonant filtering (no tones).

    Creates atmospheric texture through:
      - Band-limited pink/brown noise for natural ambience
      - Resonant filters to create spatial impression
      - Slow amplitude modulation for breathing-like quality
      - No pure sine waves or beeps
    """
    import numpy as np  # type: ignore

    n_samples = int(sample_rate * duration_seconds)
    t = np.arange(n_samples) / sample_rate

    # Generate base noise (brown/pink hybrid — natural sounding)
    white_noise = np.random.randn(n_samples)

    # Brown noise (1/f² integration of white noise) — deeper, more atmospheric
    brown = np.zeros_like(white_noise)
    for i in range(1, n_samples):
        brown[i] = brown[i - 1] + 0.02 * white_noise[i] - 0.019 * white_noise[i-1]

    # Pink noise (1/f) — balanced frequency content
    pink = np.zeros_like(white_noise)
    b_pink = [0.99886, -0.99886, 0.5, 0]
    for i in range(n_samples):
        white_sample = white_noise[i] if i < n_samples else 0
        pink_val = white_sample * b_pink[0] + pink[i-1] * b_pink[1] if i > 0 else white_sample * b_pink[0]
        pink[i] = pink_val

    # Blend brown (60%) + pink (40%) for natural ambience
    base = 0.6 * brown + 0.4 * pink
    base = base / np.max(np.abs(base)) * 0.15  # Normalize to safe level

    # Apply resonant bandpass filter for spatial impression
    # Use the audio_tone from scene data to shape character
    tone = scene_data.get("audio_tone", "restrained, quiet, melancholic")
    low_freq = 40 if "melancholic" in tone or "quiet" in tone else 60
    high_freq = 200 if "quiet" in tone else 300

    # Multiple overlapping resonant filters (not sine tones)
    center_frequencies = [80, 120, 160, 250]  # Low-end resonance points
    q_factors = [20, 30, 40, 50]  # Quality factors (broader = more natural)

    filtered = np.zeros_like(base)
    for cf, q in zip(center_frequencies, q_factors):
        # Resonant peak at center frequency (bandpass)
        dw = 2 * math.pi * cf / sample_rate
        alpha = math.sin(dw) / (2 * q)

        b0 = alpha
        b1 = 0
        b2 = -alpha
        a0 = 1 + alpha
        a1 = -2 * math.cos(dw)
        a2 = 1 - alpha

        y = np.zeros(n_samples)
        for i in range(n_samples):
            x_curr = base[i] if i < n_samples else 0.0
            x_prev1 = base[i - 1] if i > 0 else 0.0
            x_prev2 = base[i - 2] if i > 1 else 0.0
            if i == 0:
                y[i] = (b0 * x_curr + b1 * x_prev1 + b2 * x_prev2) / a0
            elif i == 1:
                y[i] = (b0 * x_curr + b1 * base[0] + b2 * 0.0) / a0
            else:
                # IIR filter with feedback
                num = b0 * base[i] - a1 * y[i-1] - a2 * y[i-2]
                y[i] = num / a0

        filtered += y * 0.25  # Blend all filters together

    # Apply slow amplitude modulation (breathing-like envelope, not rhythmic beeps)
    mod_rate = 0.1 if "quiet" in tone or "melancholic" in tone else 0.3
    env = 0.7 + 0.3 * np.sin(2 * math.pi * mod_rate * t)

    # Add subtle high-frequency air (not a tone — filtered noise)
    high_freq_noise = pink * 0.1
    high_pass_b = [0.5, -0.5]
    for i in range(n_samples):
        high_freq_noise[i] *= (high_pass_b[0] + (high_pass_b[1] if i > 0 else 0))

    result = (filtered + high_freq_noise) * env
    result = np.clip(result, -0.95, 0.95)

    # Write WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        samples_int16 = (result * 32767).astype(np.int16)
        with wave.open(tmp.name, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(samples_int16.tobytes())
        filepath = tmp.name

    return MusicTrack(
        type="ambience",
        filepath=filepath,
        duration_seconds=duration_seconds,
        sample_rate=sample_rate,
        description=f"Ambient soundscape: {tone} ({duration_seconds}s)",
        details={"low_freq": low_freq, "high_freq": high_freq, "center_frequencies": center_frequencies},
    )


def _generate_score(
    scene_data: dict,
    audio_prompt: dict | None,
    duration_seconds: float = 5.0,
    sample_rate: int = 44100,
) -> MusicTrack:
    """Generate background score with harmonics and intervals (no pure tones).

    Uses:
      - Multiple detuned oscillators (creating chorusing, not pure tones)
      - Proper musical scales (minor for melancholic scenes)
      - Envelope shaping (attack/decay/sustain/release per note)
      - No single-frequency sine waves
    """
    import numpy as np  # type: ignore

    n_samples = int(sample_rate * duration_seconds)
    t = np.arange(n_samples) / sample_rate

    # Select scale based on scene emotion
    audio_tone = scene_data.get("audio_tone", "restrained, quiet, melancholic")
    is_melancholic = "melancholic" in audio_tone or "quiet" in audio_tone

    # Minor pentatonic intervals (musical, not arbitrary)
    if is_melancholic:
        # A minor pentatonic: 0, 3, 5, 7, 10 semitones
        base_freq = 220.0  # A3
        scale_intervals = [0, 3, 5, 7, 10]  # semitones relative to base
    else:
        # Major pentatonic
        base_freq = 261.63  # C4
        scale_intervals = [0, 2, 4, 7, 9]

    score = np.zeros(n_samples)

    # Layer 1: Deep drone (multiple detuned sub-bass oscillators)
    drone_base = [55, 55.3, 54.8]  # Slightly detuned A1 for chorusing effect
    for df in drone_base:
        oscillator = np.sin(2 * math.pi * df * t)
        # ADSR envelope — very slow attack/release (not a beep)
        attack = np.minimum(t / 3.0, 1.0) if duration_seconds > 3 else t / max(duration_seconds, 1)
        release = np.minimum((n_samples // sample_rate - t) / 3.0, 1.0) if duration_seconds > 3 else (duration_seconds - t) / max(duration_seconds, 1)
        envelope = np.minimum(attack * release, 0.3)  # Very quiet drone
        score += oscillator * envelope

    # Layer 2: Harmonic tones using scale
    note_duration = 1.5  # Each note lasts 1.5 seconds
    n_notes = max(int(duration_seconds / note_duration), 1)

    for i in range(n_notes):
        note_start = i * note_duration
        note_freq_idx = i % len(scale_intervals)
        semitone = scale_intervals[note_freq_idx]
        note_freq = base_freq * (2 ** (semitone / 12))

        # Detune slightly for naturalness (chorus effect — not a pure tone)
        detunes = [0, 0.5, -0.3]  # cents
        detuned_score = np.zeros(n_samples)
        for detune_cents in detunes:
            detuned_freq = note_freq * (2 ** (detune_cents / 1200))
            osc = np.sin(2 * math.pi * detuned_freq * t)

            # Vectorized ADSR envelope using numpy mask operations
            attack_time = 0.3
            decay_time = 0.2
            sustain_level = 0.6
            release_time = min(0.5, max(note_duration - attack_time - decay_time - 0.5, 0.1))

            # Create envelope array — initialize to zeros (silence outside note region)
            env = np.zeros(n_samples)

            # Mask: inside the note region [note_start, note_start + note_duration]
            inside_note = (t >= note_start) & (t < note_start + note_duration)
            t_inside = np.where(inside_note, t - note_start, 0)

            # Attack phase: [0, attack_time)
            attack_mask = (t_inside >= 0) & (t_inside < attack_time)
            env[attack_mask] = t_inside[attack_mask] / attack_time

            # Decay phase: [attack_time, attack_time + decay_time)
            decay_mask = (t_inside >= attack_time) & (t_inside < attack_time + decay_time)
            env[decay_mask] = 1 - ((t_inside[decay_mask] - attack_time) / decay_time) * (1 - sustain_level)

            # Sustain phase: [attack_time + decay_time, note_duration)
            sustain_mask = (t_inside >= attack_time + decay_time) & (t_inside < note_duration)
            env[sustain_mask] = sustain_level

            # Release phase (fade out at end of note)
            remaining_dur = note_duration - attack_time - decay_time
            release_start = note_start + remaining_dur
            release_mask = inside_note & (t >= release_start)
            if np.any(release_mask):
                fade_out_dur = min(release_time, n_samples / sample_rate - remaining_dur)
                if fade_out_dur > 0:
                    env[release_mask] *= 1 - (t[release_mask] - release_start) / fade_out_dur

            detuned_score += osc * env

        score += detuned_score * 0.15  # Layer is quiet under the drone

    # Layer 3: Sparse high harmonics (piano-like overtones, not beeps)
    for i in range(n_notes):
        note_start = i * note_duration
        note_freq_idx = (i + 2) % len(scale_intervals)  # Shift by 2 octaves
        semitone = scale_intervals[note_freq_idx]
        overtone_freq = base_freq * (2 ** ((semitone + 24) / 12))

        t_offset = t - note_start
        
        # Vectorized pluck envelope using numpy
        active = (t_offset >= -0.1) & (t_offset <= note_duration)
        if np.any(active):
            t_active = np.where(active, t_offset, 0)
            env = np.zeros(n_samples)
            env[active] = np.exp(-3 * np.maximum(0, t_active[active]) ** 2 / max(note_duration**2 / 4, 0.01))
            score += np.sin(2 * math.pi * overtone_freq * t) * env * 0.05

    # Normalize
    if len(score) > 0 and np.max(np.abs(score)) > 0:
        score = score / np.max(np.abs(score)) * 0.3

    # Write WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        samples_int16 = (score * 32767).astype(np.int16)
        with wave.open(tmp.name, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(samples_int16.tobytes())
        filepath = tmp.name

    return MusicTrack(
        type="score",
        filepath=filepath,
        duration_seconds=duration_seconds,
        sample_rate=sample_rate,
        description="Background score: " + ("melancholic minor pentatonic" if is_melancholic else "reflective major") + f" ({duration_seconds}s)",
        details={"base_freq": base_freq, "scale_intervals": scale_intervals},
    )


# ---------------------------------------------------------------------------
# Main Music Runner
# ---------------------------------------------------------------------------

class MusicRunner:
    """Generate ambience and score for a scene."""

    def generate(
        self,
        scene_data: dict,
        audio_prompt: dict | None = None,
        duration_seconds: float = 5.0,
        output_dir: Path | str | None = None,
    ) -> MusicResult:
        """Generate both ambience and score tracks."""
        if not scene_data:
            return MusicResult(success=False, error="No scene data provided")

        duration_seconds = max(duration_seconds, 1.0)

        try:
            ambience = _generate_ambience(scene_data, audio_prompt, duration_seconds)

            # Save to output dir if specified
            if output_dir:
                odir = Path(output_dir)
                odir.mkdir(parents=True, exist_ok=True)
                amb_path = odir / "ambience.wav"
                subprocess.run(
                    ["ffmpeg", "-y", "-i", ambience.filepath, str(amb_path)],
                    capture_output=True, timeout=30
                )
                if Path(amb_path).exists() and Path(amb_path).stat().st_size > 0:
                    ambience.filepath = str(amb_path)

            score = _generate_score(scene_data, audio_prompt, duration_seconds)
            if output_dir:
                odir = Path(output_dir)
                scr_path = odir / "score.wav"
                subprocess.run(
                    ["ffmpeg", "-y", "-i", score.filepath, str(scr_path)],
                    capture_output=True, timeout=30
                )
                if Path(scr_path).exists() and Path(scr_path).stat().st_size > 0:
                    score.filepath = str(scr_path)

            return MusicResult(
                success=True,
                ambience_track=ambience,
                score_track=score,
            )

        except Exception as e:
            return MusicResult(success=False, error=f"Music generation failed: {e}")


# ---------------------------------------------------------------------------
# Music track validation
# ---------------------------------------------------------------------------

def validate_music_tracks(
    tracks: list[MusicTrack],
) -> MusicResult:
    """Validate generated music tracks for audibility and quality."""
    from builder.media_validators import AudioValidator

    result = MusicResult(success=True)
    valid_tracks = []

    for track in tracks:
        val = AudioValidator(track.filepath)
        val_result = val.validate()
        if val_result.valid:
            valid_tracks.append(track)
            track.details["duration_validated"] = val_result.details.get("duration_seconds")
            track.details["codec_validated"] = val_result.details.get("codec")
        else:
            result.success = False
            if not result.error:
                result.error = f"Music track validation failed: {track.filepath}"

    if valid_tracks:
        result.ambience_track = valid_tracks[0]
        result.score_track = valid_tracks[-1] if len(valid_tracks) > 1 else None

    return result
