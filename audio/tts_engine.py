"""
XTTS-v2 TTS Engine — local emotional text-to-speech.

Uses Coqui TTS with XTTS-v2 model for:
- Voice cloning (GuyNeural/JennyNeural style voices)
- Emotional range via prosody control
- Multi-turn dialogue with natural delivery

Fallbacks to edge-tts if XTTS model hasn't been downloaded yet.
"""

import asyncio
import json
import logging
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger("tts_engine")

# XTTS-v2 config
XTTS_MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
XVA_VOICES_DIR = Path.home() / ".local" / "share" / "tts" / "voices"

# ─── Voice profiles ───────────────────────────────────────────────────────
# Each profile maps to a reference audio for XTTS voice cloning.
# We generate a short reference clip using edge-tts so XTTS has
# a base voice to clone with its own prosody.

VOICE_PROFILES = {
    "mark": {
        "label": "Male US (Mark)",
        "edge_voice": "en-US-GuyNeural",
        "ref_text": (
            "This is Mark. I used to think silence was peaceful, "
            "but now I realize it's just empty."
        ),
        "speed": 1.0,
        "emotion_default": "neutral",
    },
    "sarah": {
        "label": "Female US (Sarah)",
        "edge_voice": "en-US-JennyNeural",
        "ref_text": (
            "This is Sarah. Sometimes the hardest conversations "
            "are the ones we never have."
        ),
        "speed": 1.0,
        "emotion_default": "neutral",
    },
    "narrator": {
        "label": "Narrator (US Male)",
        "edge_voice": "en-US-GuyNeural",
        "ref_text": (
            "The space between two people can be measured in inches "
            "or in years of silence."
        ),
        "speed": 0.95,
        "emotion_default": "calm",
    },
}

# ─── Emotion → prosody parameters ──────────────────────────────────────
# These get passed to XTTS when available, or approximated via edge-tts SSML

EMOTION_PROXIES = {
    "sad": {"speed": 0.85, "pitch": "-2st", "volume": "0.8"},
    "angry": {"speed": 1.1, "pitch": "+3st", "volume": "1.2"},
    "happy": {"speed": 1.05, "pitch": "+2st", "volume": "1.0"},
    "calm": {"speed": 0.9, "pitch": "-1st", "volume": "0.7"},
    "tense": {"speed": 1.0, "pitch": "+1st", "volume": "0.9"},
    "fearful": {"speed": 0.95, "pitch": "+1st", "volume": "0.6"},
    "surprised": {"speed": 1.1, "pitch": "+3st", "volume": "1.1"},
    "neutral": {"speed": 1.0, "pitch": "0st", "volume": "0.9"},
    "hopeful": {"speed": 0.95, "pitch": "+1st", "volume": "0.8"},
}


def _check_xtts_available() -> bool:
    """Check if XTTS-v2 model is downloaded and available.
    XTTS caches under Hugging Face hub or TTS cache dir."""
    # Check Hugging Face cache
    hf_home = Path.home() / ".cache" / "huggingface" / "hub"
    if hf_home.exists():
        for p in hf_home.rglob("**/model.safetensors*"):
            if "xtts" in str(p).lower():
                logger.info(f"XTTS-v2 found in HF cache")
                return True

    # Check TTS local cache
    tts_cache = Path.home() / ".local" / "share" / "tts"
    for p in tts_cache.rglob("**/config.json"):
        if "xtts" in str(p).lower():
            logger.info(f"XTTS-v2 found in TTS cache")
            return True

    # Check the model's known download path
    xtts_path = Path.home() / ".local" / "share" / "tts" / XTTS_MODEL_NAME
    if xtts_path.exists():
        logger.info(f"XTTS-v2 found at {xtts_path}")
        return True

    logger.info("XTTS-v2 model not yet downloaded")
    return False


def _generate_ref_audio(edge_voice: str, text: str, output_path: Path) -> bool:
    """Generate a reference audio clip from edge-tts for XTTS voice cloning."""
    if output_path.exists():
        return True
    cmd = [
        "edge-tts", "--voice", edge_voice,
        "--rate", "+0%",
        "--text", text,
        "--write-media", str(output_path),
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=30)
        return output_path.exists()
    except Exception as e:
        logger.warning(f"Ref audio gen failed: {e}")
        return False


async def generate_tts_xtts(
    text: str,
    voice_profile: str,
    emotion: str = "neutral",
    output_path: Optional[Path] = None,
) -> Optional[Path]:
    """
    Generate TTS using XTTS-v2 with emotional prosody.

    Falls back to edge-tts with SSML if XTTS model isn't available.
    """
    profile = VOICE_PROFILES.get(voice_profile)
    if not profile:
        logger.error(f"Unknown voice profile: {voice_profile}")
        return None

    if output_path is None:
        output_path = Path(tempfile.mktemp(suffix=".wav"))

    # ── Try XTTS-v2 ──
    xtts_ok = _check_xtts_available()
    if xtts_ok:
        try:
            return await _xtts_generate(text, voice_profile, emotion, output_path)
        except Exception as e:
            logger.warning(f"XTTS failed ({e}), falling back to edge-tts")

    # ── Fallback: edge-tts with SSML for emotional proxy ──
    return await _edge_generate(text, voice_profile, emotion, output_path)


async def _xtts_generate(
    text: str,
    voice_profile: str,
    emotion: str,
    output_path: Path,
) -> Optional[Path]:
    """Generate speech via XTTS-v2 Python API."""
    logger.info(f"  [XTTS] Generating speech ({voice_profile}, {emotion})...")

    profile = VOICE_PROFILES[voice_profile]

    # Lazily import TTS to avoid slow startup
    from TTS.api import TTS

    # Initialize TTS with XTTS-v2
    tts = TTS(XTTS_MODEL_NAME)

    # Set up reference audio
    ref_dir = XVA_VOICES_DIR / voice_profile
    ref_dir.mkdir(parents=True, exist_ok=True)
    ref_wav = ref_dir / "reference.wav"

    if not ref_wav.exists():
        if not _generate_ref_audio(profile["edge_voice"], profile["ref_text"], ref_wav):
            logger.warning("Failed to generate reference audio, continuing anyway")

    # Apply emotional prosody
    emo = EMOTION_PROXIES.get(emotion, EMOTION_PROXIES["neutral"])
    speed = emo["speed"] * profile.get("speed", 1.0)

    # XTTS with voice cloning via reference audio
    kwargs = dict(
        text=text,
        file_path=str(output_path),
        language="en",
        speed=speed,
    )

    if ref_wav.exists():
        kwargs["speaker_wav"] = str(ref_wav)

    tts.tts_to_file(**kwargs)

    if output_path.exists():
        size_kb = output_path.stat().st_size / 1024
        logger.info(f"  [XTTS] Done → {output_path.name} ({size_kb:.0f} KB)")
        return output_path

    logger.warning("XTTS output file not created")
    return None


async def _edge_generate(
    text: str,
    voice_profile: str,
    emotion: str,
    output_path: Path,
) -> Optional[Path]:
    """
    Fallback: edge-tts with SSML markup for emotional approximation.

    Wraps text in <prosody> tags adjusted by emotion.
    """
    profile = VOICE_PROFILES[voice_profile]
    emo = EMOTION_PROXIES.get(emotion, EMOTION_PROXIES["neutral"])

    edge_voice = profile["edge_voice"]
    speed = emo["speed"] * profile.get("speed", 1.0)
    rate_str = f"{'+' if speed > 1.0 else ''}{int((speed - 1.0) * 100)}%"
    pitch = emo.get("pitch", "0st")

    # Build SSML wrapped text
    ssml_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    ssml = (
        f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">'
        f'<voice name="{edge_voice}">'
        f'<prosody rate="{rate_str}" pitch="{pitch}">'
        f'{ssml_text}'
        f'</prosody>'
        f'</voice>'
        f'</speak>'
    )

    # Write SSML to temp file
    ssml_path = output_path.with_suffix(".ssml.xml")
    ssml_path.write_text(ssml)

    logger.info(f"  [edge-tts] Generating ({voice_profile}, {emotion}, rate={rate_str})...")

    # edge-tts can use SSML via --text but we need to use the SSML directly
    # edge-tts doesn't support SSML files, so let's use the simpler approach
    # with rate modification only
    escaped_text = text.replace('"', "'")
    cmd = (
        f'edge-tts --voice "{edge_voice}" '
        f'--rate "{rate_str}" '
        f'--pitch "{pitch}" '
        f'--text "{escaped_text}" '
        f'--write-media "{output_path}"'
    )

    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await proc.communicate()

    if output_path.exists():
        size_kb = output_path.stat().st_size / 1024
        logger.info(f"  [edge-tts] Done → {output_path.name} ({size_kb:.0f} KB)")
        return output_path

    logger.error(f"  [edge-tts] Failed: {stderr.decode()[:200]}")
    return None


async def generate_scene_dialogue(
    scene_id: int,
    lines: list,
    output_dir: Path,
) -> list:
    """
    Generate TTS for all lines in a scene.
    Returns list of (speaker, text, emotion, path) tuples.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    for i, line in enumerate(lines):
        speaker = line.get("speaker", "NARRATOR").lower()
        text = line.get("dialogue_text", "")
        emotion = line.get("emotion", "neutral")

        # Map speaker to voice profile
        if speaker in ("mark", "marker", "male"):
            profile = "mark"
        elif speaker in ("sarah", "female"):
            profile = "sarah"
        else:
            profile = "narrator"

        path = output_dir / f"scene_{scene_id:03d}_line_{i+1}_tts.wav"
        result = await generate_tts_xtts(text, profile, emotion, path)
        results.append((speaker, text, emotion, result))

    return results


# ─── Status ───────────────────────────────────────────────────────────────


def status_report() -> str:
    """Report on TTS capabilities."""
    lines = ["🗣️ TTS Engine Status"]
    lines.append("=" * 50)
    xtts = _check_xtts_available()
    lines.append(f"  XTTS-v2 model: {'✅ Available' if xtts else '⬜ Not downloaded'}")
    lines.append(f"  Fallback: edge-tts (always available)")
    lines.append(f"  Voices: {', '.join(VOICE_PROFILES.keys())}")
    lines.append(f"  Emotion proxies: {', '.join(EMOTION_PROXIES.keys())}")
    lines.append("")
    if not xtts:
        lines.append("  To download XTTS-v2 model, first run:")
        lines.append("    python3 -c \"from TTS.api import TTS; TTS('tts_models/multilingual/multi-dataset/xtts_v2')\"")
        lines.append("  (This downloads ~2GB once, then stays cached)")
    return "\n".join(lines)


if __name__ == "__main__":
    import tempfile
    logging.basicConfig(level=logging.INFO)
    print(status_report())

    # Quick test
    print("\n--- Test generation ---")
    asyncio.run(
        generate_tts_xtts(
            "I keep thinking about what you said last night.",
            voice_profile="mark",
            emotion="sad",
            output_path=Path(tempfile.mktemp(suffix=".wav")),
        )
    )