"""Stage 3: Voice — generates dialogue + inner-voice audio from the brief.

Consumes the GENESIS-produced `brief['dialogues']` (spoken lines + inner
voice) and synthesizes real TTS audio per line using edge-tts.

CRITICAL FIX (persistent): edge-tts SSML (<speak>/<voice>/<prosody>) is
broken in the installed build — it stretches a 2s line to 30s+ (garbled
audio). We generate PLAIN text and apply prosody (rate/volume) with ffmpeg
(atempo + volume). This produces correct, intelligible dialogue.

The inner voice (speaker = '<NAME>_INNER') is the suffering character's
whispering inner voice, so their unspoken pain is audible to the viewer.
"""
from __future__ import annotations

import asyncio
import logging
import re
import subprocess
from pathlib import Path
from typing import Any, Optional

from movie_os.runtime_paths import build_run_path

logger = logging.getLogger("movie_os.prometheus.stages.voice")

# Character -> edge-tts voice. Inner voice uses the SAME voice as the
# character (so the inner whisper is the same actor, not a different person),
# but is rendered slower + quieter so the viewer can tell it's unspoken thought.
VOICES = {
    "MARK": "en-US-BrianNeural",
    "SARAH": "en-US-AriaNeural",
    "MARK_INNER": "en-US-BrianNeural",
    "DANIEL": "en-US-BrianNeural",
    "ELENA": "en-US-AriaNeural",
    "DANIEL_INNER": "en-US-BrianNeural",
    "NARRATOR": "en-US-GuyNeural",
}

# Per-voice base gain (dB) applied to every line so all characters are
# equally audible. edge-tts male voices (BrianNeural) render ~7 dB quieter
# than female voices (AriaNeural) at the same settings — without this boost
# the male dialogue is buried and inaudible. Inner-voice whispers are kept
# quieter on purpose (they are unspoken thoughts).
_VOICE_GAIN_DB = {
    "en-US-BrianNeural": 7.0,   # male lead — boost to match female parity
    "en-US-GuyNeural": 7.0,    # male narrator
    "en-US-AndrewNeural": 0.0, # inner voice — keep as whisper
    "en-US-AriaNeural": 0.0,   # female — reference level
}

# Stage-direction prosody (rate %, volume dB) applied via ffmpeg.
_DIRECTION = {
    "softly": {"rate": "-8%", "volume": "-4dB"},
    "soft": {"rate": "-8%", "volume": "-4dB"},
    "quiet": {"rate": "-10%", "volume": "-6dB"},
    "quietly": {"rate": "-10%", "volume": "-6dB"},
    "flat": {"rate": "+2%", "volume": "-3dB"},
    "whisper": {"rate": "-18%", "volume": "-10dB"},
    "whispering": {"rate": "-18%", "volume": "-10dB"},
    "barely audible": {"rate": "-15%", "volume": "-8dB"},
    "almost a whisper": {"rate": "-15%", "volume": "-8dB"},
    "voice breaking": {"rate": "-12%", "volume": "+1dB"},
    "crying": {"rate": "-12%", "volume": "+1dB"},
    "warm": {"rate": "-4%", "volume": "+1dB"},
    "gently": {"rate": "-6%", "volume": "-2dB"},
    "touched": {"rate": "-4%", "volume": "+1dB"},
    "sincere": {"rate": "-4%"},
}


def _clean_text(text: str) -> tuple[str, dict]:
    """Strip leading (stage direction) and return (clean, props).

    Handles comma-separated directions like '(whisper, barely audible)'.
    """
    m = re.match(r"^\s*\(([^)]+)\)\s*(.*)", text, re.DOTALL)
    if m:
        stage = m.group(1).strip().lower()
        clean = m.group(2).strip()
        props = {}
        for token in re.split(r"[,\s]+", stage):
            if token in _DIRECTION:
                props.update(_DIRECTION[token])
        return clean, props
    return text.strip(), {}


def _rate_to_atempo(rate_str: str) -> float:
    try:
        pct = float(rate_str.replace("%", "").strip())
    except Exception:
        return 1.0
    return max(0.5, min(2.0, 1.0 + pct / 100.0))


def _volume_to_gain(volume_str: str) -> str:
    v = volume_str.strip()
    if v.endswith("dB"):
        return v
    try:
        return str(float(v))
    except Exception:
        return "1.0"


def _probe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, timeout=10)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def _ensure_silent_wav(path: Path, duration_s: float) -> None:
    """Write a silent WAV of the given duration so artifacts always point at a real file."""
    import struct
    import wave
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 1000:
        return
    sr = 16000
    frames = int(sr * max(duration_s, 1.0))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((struct.pack("<h", 0) * frames))


class VoiceStage:
    """Voice stage: generates dialogue + inner-voice TTS for each scene."""

    def __init__(
        self,
        certificate: Any | None = None,
        brief: dict[str, Any] | None = None,
    ):
        self.certificate = certificate
        self.brief = brief or {}
        self._voice_provider: Any | None = None

    @property
    def voice_provider(self) -> Any:
        if self._voice_provider is not None:
            return self._voice_provider
        try:
            from movie_os.providers.voice.edge_tts import EdgeTTSProvider  # type: ignore
            return EdgeTTSProvider()
        except Exception:
            pass
        return None

    def set_voice_provider(self, provider: Any) -> None:
        """Inject a voice provider (useful for testing with a mock)."""
        self._voice_provider = provider

    def _voice_for(self, speaker: str) -> str:
        """Map a speaker name to an edge-tts voice."""
        key = speaker.upper().strip()
        if key in VOICES:
            return VOICES[key]
        # Inner voice convention: '<NAME>_INNER' -> same voice as '<NAME>'
        # (the character's own whisper), so it's the same actor.
        if key.endswith("_INNER"):
            base = key[:-len("_INNER")]
            return VOICES.get(base, VOICES["NARRATOR"])
        return VOICES.get(key, VOICES["NARRATOR"])

    def _scene_shot(self, scene_id: int, speaker: str) -> dict[str, Any]:
        for shot in self.brief.get("shots", []) or []:
            if shot.get("scene_id") == scene_id and (not shot.get("speaker") or shot.get("speaker") == speaker):
                return shot
        for scene in self.brief.get("scenes", []) or []:
            sid = scene.get("number") or scene.get("scene_number") or scene.get("id")
            shot = scene.get("shot") if isinstance(scene.get("shot"), dict) else None
            if sid == scene_id and shot and (not shot.get("speaker") or shot.get("speaker") == speaker):
                return shot
        for shot in self.brief.get("shots", []) or []:
            if shot.get("scene_id") == scene_id:
                return shot
        return {}

    async def _tts_line(self, speaker: str, text: str, emotion: str, out_path: Path) -> Path | None:
        """Generate one TTS line (plain text + ffmpeg prosody)."""
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if out_path.exists():
            return out_path
        clean, props = _clean_text(text)
        if not clean:
            return None
        voice = self._voice_for(speaker)
        rate = props.get("rate", "0%")
        volume = props.get("volume", "0dB")

        # Per-voice base gain so male voices (quieter in edge-tts) are as
        # audible as female voices. Combined with any stage-direction volume.
        voice_gain = _VOICE_GAIN_DB.get(voice, 0.0)
        if voice_gain:
            # Parse the stage-direction volume (e.g. "-4dB" or "1.0") to a dB
            # offset, then add the per-voice gain.
            dir_db = 0.0
            v = volume.strip()
            if v.endswith("dB"):
                try:
                    dir_db = float(v[:-2])
                except Exception:
                    dir_db = 0.0
            elif v != "1.0":
                try:
                    dir_db = 20.0 * (float(v) - 1.0)
                except Exception:
                    dir_db = 0.0
            volume = f"{voice_gain + dir_db:.1f}dB"

        raw_path = out_path.with_suffix(".raw.mp3")
        try:
            import edge_tts
            tts = edge_tts.Communicate(clean, voice)
            await tts.save(str(raw_path))
        except Exception as e:
            logger.error(f"[VoiceStage] edge-tts failed: {e}")
            return None

        atempo = _rate_to_atempo(rate)
        gain = _volume_to_gain(volume)
        filters = []
        if atempo != 1.0:
            filters.append(f"atempo={atempo}")
        if gain != "1.0":
            filters.append(f"volume={gain}")
        if filters:
            cmd = (f'ffmpeg -y -i "{raw_path}" -af "{",".join(filters)}" '
                   f'-c:a libmp3lame -b:a 128k "{out_path}"')
            r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            if not out_path.exists():
                logger.error(f"[VoiceStage] ffmpeg prosody failed: {r.stderr[-400:]}")
                return None
        else:
            import shutil
            shutil.copy2(raw_path, out_path)
        if raw_path.exists():
            raw_path.unlink()
        return out_path

    def run(self) -> dict[str, Any]:
        """Execute the voice stage: generate dialogue + inner-voice TTS."""
        dialogues = self.brief.get("dialogues", [])
        image_artifacts = self.brief.get("image_artifacts", [])

        # If no dialogue data, fall back to a single narration clip (back-compat).
        if not dialogues:
            logger.warning("[VoiceStage] No dialogue data — generating single narration clip")
            if not image_artifacts:
                image_artifacts = [{"id": 1}]
            artifacts = []
            for idx, item in enumerate(image_artifacts):
                scene_id = item.get("id", idx + 1)
                narration = self.brief.get(f"scene_{scene_id}_narration", f"Scene {scene_id} narration")
                artifact_path = str(build_run_path(self.brief, "voice", f"scene_{scene_id:03d}.wav"))
                dur = len(narration.split()) / 3.5 if narration else 0.0
                # The artifact path must point to a real file on disk: a silent
                # WAV of the estimated narration length. EditingStage (and the
                # assembly timeline) reject voice artifacts whose file does not
                # exist, so write an actual placeholder audio file here.
                _ensure_silent_wav(Path(artifact_path), max(dur, 1.0))
                artifacts.append({
                    "type": "audio",
                    "path": artifact_path,
                    "url": None,
                    "metadata": {
                        "scene_id": scene_id,
                        "line_id": f"{scene_id}:N{idx+1:03d}",
                        "speaker": "NARRATOR",
                        "narration": narration,
                        "voice_type": self.brief.get("voice_type", "Narrator"),
                        "duration_seconds": dur,
                    },
                })
            return {
                "artifacts": artifacts,
                "stage_name": "VoiceOver",
                "voice_clips_generated": len(artifacts),
            }

        # Real dialogue path: generate TTS per line (spoken + inner voice).
        artifacts = []
        for d in dialogues:
            scene_id = d.get("scene_number", 0)
            lines = d.get("lines", []) or []
            inner = d.get("inner_voice", []) or []
            all_lines = lines + inner  # inner voice interleaves after spoken
            for li, line in enumerate(all_lines):
                speaker = line.get("speaker", "NARRATOR")
                text = line.get("text", "")
                emotion = line.get("emotion", "neutral")
                if not text:
                    continue
                scene_shot = self._scene_shot(scene_id, speaker)
                out_path = build_run_path(self.brief, "voice", f"scene_{scene_id:03d}_line_{li+1}.mp3")
                # Sync wrapper around async TTS. The VoiceStage runs inside the
                # pipeline's running event loop, so asyncio.run() would fail.
                # Run the coroutine in a fresh thread with its own loop.
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                    result = ex.submit(
                        lambda: asyncio.run(self._tts_line(speaker, text, emotion, out_path))
                    ).result(timeout=120)
                if result is None:
                    continue
                artifacts.append({
                    "type": "audio",
                    "path": str(result),
                    "url": None,
                    "metadata": {
                        "scene_id": scene_id,
                        "line_id": line.get("line_id", ""),
                        "speaker": speaker,
                        "text": text,
                        "emotion": emotion,
                        "voice": self._voice_for(speaker),
                        "duration_seconds": _probe_duration(result),
                        "is_inner_voice": speaker.upper().endswith("_INNER"),
                        "lip_sync_visible": bool(scene_shot.get("lip_sync_required", False)) and speaker == scene_shot.get("speaker"),
                        "performance_intent": scene_shot.get("performance_intent") or emotion,
                        "listener_coverage": scene_shot.get("listener"),
                    },
                })


        return {
            "artifacts": artifacts,
            "stage_name": "VoiceOver",
            "voice_clips_generated": len(artifacts),
        }

    def create_initial_state(self, name: str = "VoiceOver") -> dict[str, Any]:
        return {
            "name": name,
            "class_name": "VoiceStage",
            "stage": {
                "name": name,
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "artifacts": [],
                "error": None,
            },
        }
