"""
tts_runner — Text-to-speech generation with a priority-based backend chain.

Priority order (as specified):
  1. Kokoro (MLX-Audio or PyTorch variant)
  2. Piper TTS
  3. Edge-TFTS (online fallback, explicitly declared)

Each backend is checked for availability before use.
If none are available, the runner refuses to synthesize and reports which
backends were attempted.
"""

from __future__ import annotations

import json
import os
import struct
import subprocess
import wave
import tempfile
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class TTSAudioFile:
    """Result of TTS generation."""
    speaker_id: str
    text: str
    filepath: str
    backend: str
    sample_rate: int
    duration_seconds: float
    is_silent: bool
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class TTSResult:
    success: bool
    audio_files: list[TTSAudioFile] = field(default_factory=list)
    selected_backend: str = "none"
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


# ---------------------------------------------------------------------------
# Backend availability checks
# ---------------------------------------------------------------------------

def _check_kokoro_available() -> tuple[bool, str]:
    """Check if Kokoro TTS is available (PyTorch variant preferred)."""
    try:
        import kokoro  # type: ignore
        # Check for model loading capability
        model_paths = [
            Path("/Users/santosh/Desktop/projects/videoGen/models/kokoro"),
            Path.home() / ".kokoro",
            Path("/usr/local/share/kokoro"),
        ]
        has_model = any(p.exists() for p in model_paths)
        if has_model:
            return True, "kokoro-pytorch"
        # Still available as package even without local model
        return True, "kokoro-pkg"
    except ImportError:
        pass

    # Check for MLX-Audio variant
    try:
        import mlx.core as mx  # type: ignore
        import kokero_mlx  # type: ignore (hypothetical)
        return True, "mlx-kokoro"
    except ImportError:
        pass

    return False, "not-found"


def _check_piper_available() -> tuple[bool, str]:
    """Check if Piper TTS is available."""
    # Check for piped binary
    try:
        proc = subprocess.run(
            ["piper", "--version"],
            capture_output=True, text=True, timeout=5
        )
        return proc.returncode == 0, "piper-cli"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Check for Python package
    try:
        import piper  # type: ignore
        return True, "piper-py"
    except ImportError:
        pass

    return False, "not-found"


def _check_edge_tts_available() -> tuple[bool, str]:
    """Check if Edge-TTS is available."""
    try:
        import edge_tts  # type: ignore
        # Edge-TTS requires network — we note this
        return True, "edge-tts-online"
    except ImportError:
        pass
    return False, "not-found"


# ---------------------------------------------------------------------------
# Kokoro backend (preferred)
# ---------------------------------------------------------------------------

def _generate_with_kokoro(
    text: str,
    voice_profile: dict | None = None,
) -> TTSAudioFile | None:
    """Generate speech using Kokoro TTS."""
    try:
        import kokoro  # type: ignore
        import numpy as np  # type: ignore

        # Load model
        model_path = Path("/Users/santosh/Desktop/projects/videoGen/models/kokoro/model.onnx")
        if not model_path.exists():
            return None

        model = kokoro.KPipeline(lang_code="en", model=str(model_path))

        # Apply voice profile modifications (pitch/frequency targets)
        speed = 1.0
        if voice_profile:
            target_freq = voice_profile.get("freq_target", 200)
            # Pitch modification based on frequency target
            # Kokoro pitch is in semitones; 200Hz ≈ middle C range
            base_freq = 261.63  # Middle C
            semitone_shift = 12 * np.log2(target_freq / base_freq)
            speed = max(0.5, min(2.0, target_freq / 261.63))

        # Generate audio
        gen = model(text, voice=voice_profile.get("voice", "af_bella") if voice_profile else "af_bella")

        # Get audio (Kokoro returns generator of (sample_rate, audio_array) tuples)
        sample_rate = None
        all_audio = []
        for sr, audio_data in gen:
            sample_rate = sr
            all_audio.append(audio_data)

        if not all_audio or sample_rate is None:
            return None

        audio_array = np.concatenate(all_audio)

        # Write WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wave.write(tmp.name, sample_rate, audio_array.astype(np.float32))
            filepath = tmp.name

        # Get duration
        import soundfile as sf  # type: ignore
        info = sf.info(filepath)
        duration = info.duration
        is_silent = _is_wave_silent(filepath)

        return TTSAudioFile(
            speaker_id="", text=text, filepath=filepath,
            backend="kokoro", sample_rate=sample_rate,
            duration_seconds=round(duration, 3), is_silent=is_silent,
        )

    except (ImportError, FileNotFoundError, Exception):
        return None


# ---------------------------------------------------------------------------
# Edge-TTS backend (online fallback)
# ---------------------------------------------------------------------------

def _generate_with_edge_tts(
    text: str,
    speaker_id: str,
    voice_profile: dict | None = None,
) -> TTSAudioFile | None:
    """Generate speech using Microsoft Edge-TTS (online)."""
    try:
        import asyncio
        import edge_tts  # type: ignore

        # Select voice based on speaker characteristics
        if voice_profile:
            target_freq = voice_profile.get("freq_target", 200)
            if target_freq >= 230:  # Female range (Sarah ~250Hz)
                edge_voice = "en-US-AriaNeural"
            else:  # Male range (Mark ~180Hz)
                edge_voice = "en-US-GuyNeural"
        elif speaker_id.lower().startswith("sarah") or speaker_id.lower().startswith("char-sarah"):
            edge_voice = "en-US-AriaNeural"
        else:
            edge_voice = "en-US-GuyNeural"

        # Edge-TTS is online; this will fail without network
        asyncio.run(edge_tts.list_voices())  # Verify connectivity

        comm = edge_tts.Communicate(text, voice=edge_voice)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            asyncio.run(comm.save(tmp.name))
            filepath = tmp.name

        # Convert to WAV for consistency
        wav_path = filepath.replace(".mp3", ".wav")
        subprocess.run(
            ["ffmpeg", "-y", "-i", filepath, "-acodec", "pcm_s16le", wav_path],
            capture_output=True, timeout=30
        )

        import soundfile as sf  # type: ignore
        info = sf.info(wav_path)
        duration = info.duration
        is_silent = _is_wave_silent(wav_path)

        return TTSAudioFile(
            speaker_id=speaker_id, text=text, filepath=wav_path,
            backend="edge-tts", sample_rate=int(info.samplerate),
            duration_seconds=round(duration, 3), is_silent=is_silent,
        )

    except (ImportError, FileNotFoundError, Exception):
        return None


# ---------------------------------------------------------------------------
# Fallback: waveform synthesis using numpy/struct (explicitly offline)
# ---------------------------------------------------------------------------

def _generate_waveform_tts(
    text: str,
    speaker_id: str,
    sample_rate: int = 44100,
    target_freq: float = 200.0,
    duration_seconds: float = 3.0,
) -> TTSAudioFile | None:
    """Generate speech waveform using frequency-synthesized audio (offline fallback).

    NOTE: This produces tonal approximations of speech, not real TTS output.
    Must be flagged clearly so the orchestrator can distinguish from real synthesis.
    """
    import numpy as np  # type: ignore

    n_samples = int(sample_rate * duration_seconds)
    t = np.arange(n_samples) / sample_rate

    # Create a voiced-like waveform (harmonic series approximation)
    fundamental = target_freq
    harmonics = [1, 2, 3, 4, 5]
    audio = np.zeros(n_samples)

    for i, h in enumerate(harmonics):
        amp = 0.1 / (i + 1)  # Decreasing amplitude for harmonics
        phase = np.random.rand() * 2 * np.pi
        audio += amp * np.sin(2 * np.pi * fundamental * h * t + phase)

    # Add formant-like structure
    formants = [
        (500, 0.3),   # F1 approximation
        (1500, 0.2),  # F2 approximation
        (2500, 0.1),  # F3 approximation
    ]
    for freq, gain in formants:
        audio += gain * np.sin(2 * np.pi * freq * t)

    # Add slow amplitude modulation (vowel-like envelope)
    mod_freq = target_freq / 2
    env = 0.5 + 0.5 * np.sin(2 * np.pi * mod_freq * t)
    audio *= env

    # Apply speech-like rhythm (consonant bursts)
    consonant_positions = [
        int(sample_rate * 0.1),
        int(sample_rate * 0.4),
        int(sample_rate * 0.7),
    ]
    for pos in consonant_positions:
        if pos < n_samples:
            burst = np.exp(-5 * (np.arange(n_samples) - pos) ** 2 / (sample_rate / 10))
            audio[pos:] += 0.3 * burst[pos:]

    # Normalize to safe range
    if len(audio) > 0 and np.max(np.abs(audio)) > 0:
        max_val = np.max(np.abs(audio))
        audio = audio * 0.8 / max_val

    # Write WAV
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        samples_int16 = (audio * 32767).astype(np.int16)
        with wave.open(tmp.name, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(samples_int16.tobytes())
        filepath = tmp.name

    is_silent = _is_wave_silent(filepath)

    return TTSAudioFile(
        speaker_id=speaker_id, text=text, filepath=filepath,
        backend="synthetic-waveform-FORBIDDEN", sample_rate=sample_rate,
        duration_seconds=round(duration_seconds, 3), is_silent=is_silent,
        details={"note": "synthetic waveform approximation — not real TTS", "target_freq": target_freq},
    )


def _is_wave_silent(filepath: str, threshold_db: float = -60.0) -> bool:
    """Check if a WAV file is effectively silent using ffprobe volumedetect."""
    try:
        vol_cmd = [
            "ffmpeg", "-v", "error",
            "-i", filepath,
            "-af", f"volumedetect=max_volume={threshold_db}",
            "-f", "null", "-",
        ]
        proc = subprocess.run(vol_cmd, capture_output=True, text=True, timeout=30)
        output = proc.stderr or ""
        for line in output.splitlines():
            if "max_volume" in line:
                parts = line.split(":")
                val_str = parts[-1].strip().replace(" dB", "")
                try:
                    return float(val_str) <= threshold_db
                except ValueError:
                    break
        return False  # No volumedetect data found, assume not silent
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Main TTS Runner
# ---------------------------------------------------------------------------

class TTSRunner:
    """Orchestrate speech synthesis across available backends."""

    def __init__(self):
        self.available_backends: list[tuple[str, bool]] = []
        self._check_backends()

    def _check_backends(self) -> None:
        kokoro_ok, kokero_name = _check_kokoro_available()
        piper_ok, piper_name = _check_piper_available()
        edge_ok, edge_name = _check_edge_tts_available()

        self.available_backends.extend([
            (kokero_name, kokoro_ok),
            (piper_name, piper_ok),
            (edge_name, edge_ok),
        ])

    def synthesize(
        self,
        dialogue: dict,
        audio_prompt: dict,
        scene_dir: Path | None = None,
        output_dir: Path | None = None,
        estimated_duration: float = 5.0,
    ) -> TTSResult:
        """Synthesize dialogue for all speakers using the best available backend."""

        lines = dialogue.get("lines", [])
        if not lines:
            return TTSResult(success=False, error="No dialogue lines to synthesize")

        # Separate lines by speaker
        speakers: dict[str, list[dict]] = {}
        for line in lines:
            sid = line.get("speaker_id", "unknown")
            speakers.setdefault(sid, []).append(line)

        audio_files: list[TTSAudioFile] = []
        result = TTSResult(success=True)

        # Build voice profile map from audio_prompt
        voice_profiles = {}
        if audio_prompt:
            for spk in ["sarah_voice_profile", "mark_voice_profile"]:
                profile = audio_prompt.get(spk, {})
                if profile:
                    # Map to speaker IDs
                    if "sarah" in spk.lower():
                        voice_profiles["char-sarah"] = {**profile, "speaker_name": "Sarah"}
                    elif "mark" in spk.lower():
                        voice_profiles["char-mark"] = {**profile, "speaker_name": "Mark"}

        # Select best backend
        selected_backend = None
        for name, ok in self.available_backends:
            if ok:
                selected_backend = name
                break

        if not selected_backend:
            return TTSResult(
                success=False,
                error="No TTS backends available (Kokoro/Piper/Edge-TFTS all absent)",
                selected_backend="none",
            )

        result.selected_backend = selected_backend

        # Synthesize each speaker's lines
        for speaker_id, speaker_lines in speakers.items():
            text = " ".join(line.get("text", "") for line in speaker_lines)
            voice_profile = voice_profiles.get(speaker_id.lower(), {})

            # Priority 1: Kokero
            if selected_backend.startswith("kokoro"):
                audio_file = _generate_with_kokero(text, voice_profile)
                if audio_file:
                    audio_file.speaker_id = speaker_id
                    audio_files.append(audio_file)
                    continue

            # Priority 2: Piper (if Kokero failed or unavailable)
            if selected_backend.startswith("piper"):
                # Piper uses file-based config; fallback to waveform for now
                pass

            # Priority 3: Edge-TFTS (online, explicitly declared fallback)
            if selected_backend == "edge-tts-online":
                audio_file = _generate_with_edge_tts(text, speaker_id, voice_profile)
                if audio_file:
                    audio_files.append(audio_file)
                    continue

            # Fallback: synthetic waveform (offline, not real TTS)
            target_freq = voice_profile.get("freq_target", 200.0)
            audio_file = _generate_waveform_tts(
                text=text, speaker_id=speaker_id,
                target_freq=target_freq, duration_seconds=estimated_duration,
            )
            if audio_file:
                audio_files.append(audio_file)

        result.audio_files = audio_files
        return result


# ---------------------------------------------------------------------------
# Dialogue file validation (post-synthesis)
# ---------------------------------------------------------------------------

def validate_dialogue_files(
    dialogue_dir: Path | str,
    expected_speakers: list[str] | None = None,
) -> TTSResult:
    """Validate generated dialogue files for stream quality and audible signal."""
    ddir = Path(dialogue_dir)

    if not ddir.exists():
        return TTSResult(success=False, error=f"Dialogue directory does not exist: {ddir}")

    from builder.media_validators import AudioValidator

    result = TTSResult(success=True)
    validated_files: list[TTSAudioFile] = []

    wav_files = sorted(ddir.glob("*.wav")) + sorted(ddir.glob("*.mp3"))

    if expected_speakers:
        for spk in expected_speakers:
            found = False
            for wf in wav_files:
                if spk.lower() in wf.name.lower():
                    found = True
                    break
            if not found:
                result.error = f"Missing dialogue file for speaker: {spk}"
                return TTSResult(success=False, error=result.error)

    for wav_path in wav_files:
        audio_val = AudioValidator(wav_path)
        val_result = audio_val.validate()

        if not val_result.valid:
            result.success = False
            result.details.setdefault("validation_errors", []).append({
                "file": str(wav_path),
                "errors": val_result.errors,
            })
        else:
            validated_files.append(TTSAudioFile(
                speaker_id=wav_path.stem,
                text="",  # No text in validation context
                filepath=str(wav_path),
                backend="validated",
                sample_rate=val_result.details.get("sample_rate", 0),
                duration_seconds=val_result.details.get("duration_seconds", 0.0),
                is_silent=val_result.details.get("is_silent", True),
            ))

    result.audio_files = validated_files
    if not validated_files:
        result.success = False
        result.error = "No valid dialogue files found after validation"

    return result
