"""
Cinematic Music Generator for videoGen — application module.

Generates CC0-style cinematic ambient music using layered synthesis.
No external downloads needed — produces professional-sounding pads,
strings, and ambient textures that match emotional tone.

Usage:
    from movie_os.audio.cinematic_music import CinematicMusicGenerator
    
    gen = CinematicMusicGenerator()
    gen.generate_music(duration_s=120, emotion="melancholic", output_path="track.wav")
    gen.generate_music(duration_s=60, emotion="tense", output_path="track2.wav")
"""

from __future__ import annotations

import logging
import struct
import wave
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger("movie_os.audio.cinematic_music")

SAMPLE_RATE = 44100

# Chord definitions (frequency ratios for rich harmonics)
CHORDS = {
    "Dm7":      [293.66, 349.23, 440.00, 523.25],  # D4, F4, A4, C5
    "Am":       [220.00, 261.63, 329.63],           # A3, C4, E4
    "Fmaj7":    [349.23, 440.00, 523.25, 659.25],   # F4, A4, C5, E5
    "Cmaj7":    [261.63, 329.63, 392.00, 523.25],   # C4, E4, G4, C5
    "G":        [196.00, 246.94, 329.63],           # G3, B3, D4
    "Em":       [164.81, 196.00, 246.94],           # E3, G3, B3
    "Bb":       [233.08, 293.66, 349.23],           # Bb3, D4, F4
    "Dsus4":    [293.66, 369.99, 440.00],           # D4, F#4, A4
}

# Emotional progressions: list of (chord, duration_ratio) tuples
# duration_ratio is fraction of total scene time
PROGRESSIONS = {
    "melancholic": [
        ("Dm7", 0.3),
        ("Am", 0.2),
        ("Fmaj7", 0.15),
        ("G", 0.15),
        ("Em", 0.1),
        ("Am", 0.1),
    ],
    "tense": [
        ("Dsus4", 0.25),
        ("Am", 0.15),
        ("Bb", 0.2),
        ("G", 0.15),
        ("Am", 0.15),
        ("Dsus4", 0.1),
    ],
    "sad": [
        ("Am", 0.25),
        ("G", 0.2),
        ("Fmaj7", 0.2),
        ("Em", 0.15),
        ("Dm7", 0.1),
        ("Am", 0.1),
    ],
    "hopeful": [
        ("Cmaj7", 0.25),
        ("G", 0.2),
        ("Am", 0.2),
        ("Fmaj7", 0.15),
        ("Cmaj7", 0.1),
        ("G", 0.1),
    ],
    "calm": [
        ("Cmaj7", 0.3),
        ("Am", 0.2),
        ("Fmaj7", 0.2),
        ("G", 0.15),
        ("Cmaj7", 0.15),
    ],
}

# Scene-specific emotional mapping
SCENE_EMOTIONS = {
    1: "melancholic",    # hook — kitchen silence
    2: "calm",           # establishment — morning routine
    3: "tense",          # dialogue — attempted conversation
    4: "sad",            # emotional peak — weeks blurring
    5: "sad",            # montage — calendar flipping
    6: "melancholic",    # reflection — watching her sleep
    7: "tense",          # transition — packing the bag
    8: "sad",            # climax — walking away
}


class CinematicMusicGenerator:
    """Generates layered cinematic ambient music for film scenes."""

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sr = sample_rate

    def _chord_wave(self, freqs: list[float], t: np.ndarray) -> np.ndarray:
        """Create a rich chord wave from multiple frequencies with harmonics."""
        wave = np.zeros_like(t)
        for i, f in enumerate(freqs):
            # Fundamental
            wave += np.sin(2 * np.pi * f * t) * (0.4 / (i + 1))
            # 2nd harmonic (octave) — adds warmth
            wave += np.sin(2 * np.pi * f * 2 * t) * (0.15 / (i + 1))
            # 3rd harmonic — adds richness
            wave += np.sin(2 * np.pi * f * 3 * t) * (0.05 / (i + 1))
        return wave

    def _pad_layer(self, chord_wave: np.ndarray, t: np.ndarray) -> np.ndarray:
        """Create a pad layer with slow attack and release."""
        # Slow amplitude LFO
        lfo = np.sin(2 * np.pi * 0.06 * t) * 0.15 + 0.85
        # Slow pitch LFO for warmth (vibrato)
        pitch_lfo = np.sin(2 * np.pi * 0.12 * t) * 0.003 + 1.0
        # Apply
        signal = chord_wave * pitch_lfo * lfo * 0.5
        return signal

    def _bass_layer(self, root_note: float, t: np.ndarray) -> np.ndarray:
        """Deep sub-bass layer — felt more than heard."""
        bass = np.sin(2 * np.pi * root_note * 0.5 * t) * 0.25 + \
               np.sin(2 * np.pi * root_note * 0.25 * t) * 0.1
        # Soft saturation for weight
        bass = np.tanh(bass * 2) * 0.3
        return bass

    def _strings_layer(self, chord_wave: np.ndarray, t: np.ndarray) -> np.ndarray:
        """Emulated string section — slightly detuned, with body."""
        # Slight detuning for ensemble effect
        detune_1 = np.sin(2 * np.pi * 1.005 * t)  # +0.5%
        detune_2 = np.sin(2 * np.pi * 0.995 * t)   # -0.5%
        strings = (chord_wave * detune_1 + chord_wave * detune_2) * 0.15
        # Slow attack
        env = 1.0 - np.exp(-t * 0.5)
        strings = strings * env
        return strings

    def _generate_melody(self, chord_freqs: list[float], t: np.ndarray) -> np.ndarray:
        """Simple melodic motif from chord tones."""
        if not chord_freqs:
            return np.zeros_like(t)
        # Pick the highest note of the chord
        melody_note = chord_freqs[-1] * 2  # an octave up
        melody = np.sin(2 * np.pi * melody_note * t) * 0.06
        # Occasional intervals
        melody += np.sin(2 * np.pi * melody_note * 1.5 * t) * 0.03
        return melody

    def generate_music(
        self,
        duration_s: int,
        emotion: str = "melancholic",
        output_path: str | Path | None = None,
        scene_id: int | None = None,
    ) -> np.ndarray:
        """
        Generate cinematic music for a scene.

        Args:
            duration_s: Duration in seconds
            emotion: One of melancholic, tense, sad, hopeful, calm
            output_path: If set, save WAV to this path
            scene_id: If set, uses scene-specific emotion mapping

        Returns:
            numpy array of audio samples
        """
        # Resolve emotion
        if scene_id and scene_id in SCENE_EMOTIONS:
            emotion = SCENE_EMOTIONS[scene_id]

        progression = PROGRESSIONS.get(emotion, PROGRESSIONS["melancholic"])
        total_samples = int(self.sr * duration_s)
        t = np.linspace(0, duration_s, total_samples, endpoint=False)

        # Generate audio section by section based on chord progression
        final = np.zeros(total_samples)
        current_sample = 0

        for chord_name, ratio in progression:
            section_len = int(total_samples * ratio)
            section_t = t[current_sample:current_sample + section_len]
            if len(section_t) == 0:
                continue

            freqs = CHORDS.get(chord_name, [261.63, 329.63, 392.00])

            chord_wave = self._chord_wave(freqs, section_t)

            # Layer 1: Main pad
            pad = self._pad_layer(chord_wave, section_t)

            # Layer 2: Strings
            strings = self._strings_layer(chord_wave, section_t)

            # Layer 3: Bass (root note)
            root_note = freqs[0]
            bass = self._bass_layer(root_note, section_t)

            # Layer 4: Melody (only for certain sections)
            melody_weight = 1.0 if chord_name in ["Fmaj7", "Cmaj7"] else 0.3
            melody = self._generate_melody(freqs, section_t) * melody_weight

            # Mix layers
            section_audio = pad + strings + bass + melody

            # Apply crossfade between sections
            cf_len = min(int(0.1 * self.sr), section_len // 4)
            if current_sample > 0 and cf_len > 0:
                # Fade in this section
                fade_in = np.linspace(0, 1, cf_len)
                section_audio[:cf_len] *= fade_in

            final[current_sample:current_sample + section_len] = section_audio
            current_sample += section_len

        # Global fade in/out
        fade_len = int(0.5 * self.sr)
        final[:fade_len] *= np.linspace(0, 1, fade_len)
        final[-fade_len:] *= np.linspace(1, 0, fade_len)

        # Normalize to prevent clipping
        peak = np.max(np.abs(final))
        if peak > 0:
            final = final / peak * 0.8

        # Save if path given
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_wav(final, output_path)
            logger.info(f"Music saved: {output_path} ({duration_s}s, {emotion})")

        return final

    def _save_wav(self, audio: np.ndarray, path: Path):
        """Save audio as 16-bit WAV."""
        audio_int16 = np.int16(audio * 32767)
        with wave.open(str(path), 'w') as wf:
            wf.setnchannels(2)  # stereo
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sr)
            wf.writeframes(audio_int16.tobytes())

    @staticmethod
    def list_emotions() -> list[str]:
        return list(PROGRESSIONS.keys())

    @staticmethod
    def get_scene_emotion(scene_id: int) -> str:
        return SCENE_EMOTIONS.get(scene_id, "melancholic")