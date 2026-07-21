"""
scene_file_writer.py — writes cinematic scene pages to a structured JSON file
that downstream agents (ComfyUI dispatcher, TTS/SFX routers) can consume directly.

Output layout per run:
    pipeline/output/{prod_id}/gen_{timestamp}/
        scenes.json          ← canonical screenplay + all bundles
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("pipeline.scenes")


# ── helpers ───────────────────────────────────────────────────────────────────

def _safe(value: Any, default: str = "") -> str:
    """Coerce None → empty string; everything else → str."""
    if value is None:
        return default
    return str(value)


_SCENE_ID_KEYS = ("id", "sceneNumber", "scene_number", "number")
_ITEM_SCENE_KEY = "sceneNumber"


def _scene_id(scene: Dict[str, Any]) -> int:
    for key in _SCENE_ID_KEYS:
        val = scene.get(key)
        if val is not None:
            return int(val)
    raise ValueError(f"Cannot determine scene ID from: {scene}")


def _item_scene_id(item: Dict[str, Any]) -> int:
    val = item.get(_ITEM_SCENE_KEY)
    if val is not None:
        return int(val)
    raise ValueError(f"Cannot determine target scene ID from: {item}")


# ── SceneFileWriter ───────────────────────────────────────────────────────────

class SceneFileWriter:
    """Writes the canonical scenes.json alongside manifest.json."""

    def __init__(self, run_dir: Path):
        self.run_dir = run_dir
        self.scenes_path = run_dir / "scenes.json"

    # ------------------------------------------------------------------ public
    def write(
        self,
        story: Dict[str, Any],
        scenes: List[Dict[str, Any]],
        dialogues: List[Dict[str, Any]],
        prompts: List[Dict[str, Any]],
        audio: Optional[List[Dict[str, Any]]] = None,
    ) -> Path:
        """Enrich every scene with dialogue / visual / audio data and write scenes.json.

        Returns the path written so downstream code can open it immediately.
        """
        payload: Dict[str, Any] = {
            "manifest": self._build_manifest(story, len(scenes)),
            "scenes": [],
        }

        dia_idx = self._by_scene_id(dialogues)
        prm_idx = self._by_scene_id(prompts)
        aud_idx = self._by_scene_id(audio or [])

        for idx, raw in enumerate(scenes):
            sid = _scene_id(raw)
            page: Dict[str, Any] = {
                "id": sid,
                "title": _safe(raw.get("title")),
                "description": _safe(raw.get("description", raw.get("visual_direction"))),
                "location": _safe(raw.get("location")),
                "time": _safe(raw.get("time")),
                "duration_estimate": _safe(raw.get("duration_estimate", "")),
                "characters": raw.get("characters", []),
                "emotionalBeat": _safe(
                    raw.get("emotionalBeat", raw.get("emotional_beat"))
                ),

                # ── screenplay surface ───────────────────────────────
                "voiceover": self._pull_voiceover(sid, dialogues),
                "dialogue": [
                    {
                        "speaker": _safe(d.get("speaker", d.get("character"))),
                        "emotion": _safe(d.get("emotion")),
                        "delivery": _safe(d.get("delivery")),
                        "text": _safe(
                            d.get("text", d.get("dialogue", d.get("line")))
                        ),
                    }
                    for d in dia_idx.get(sid, [])
                ],

                # ── visual bundle (for ComfyUI / Flux dispatch) ───────
                "visualBundle": [
                    {
                        "cinematicPrompt": _safe(
                            p.get("cinematicPrompt", p.get("cinematic_prompt"))
                        ),
                        "cameraAngle": _safe(p.get("cameraAngle", p.get("camera_angle"))),
                        "lighting": _safe(p.get("lighting")),
                        "colorPalette": p.get("colorPalette", p.get("color_palette", [])),
                        "visualStyle": _safe(p.get("visualStyle", p.get("visual_style"))),
                    }
                    for p in prm_idx.get(sid, [])
                ],

                # ── audio cues (for TTS / SFX routers) ───────────────
                "audioCues": [
                    {
                        "sfx": _safe(a.get("sfx")),
                        "musicCue": _safe(
                            a.get("musicCue", a.get("music_cue"))
                        ),
                        "voiceoverScript": _safe(
                            a.get("voiceoverScript", a.get("voiceover_script"))
                        ),
                    }
                    for a in aud_idx.get(sid, [])
                ],

                # legacy alias for backward compat with older downstream consumers
                "visual_direction": _safe(raw.get("visual_direction")),
                "audio_cues_raw": raw.get("audio_cues", []),
            }

            payload["scenes"].append(page)

        self.scenes_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        logger.info(
            "Wrote %d cinematic scene pages → %s",
            len(payload["scenes"]),
            self.scenes_path,
        )
        return self.scenes_path

    # ------------------------------------------------------------------ private
    @staticmethod
    def _build_manifest(story: Dict[str, Any], num_scenes: int) -> Dict[str, Any]:
        return {
            "storyTitle": _safe(story.get("title"), "Untitled"),
            "logline": _safe(story.get("logline", "")),
            "numScenes": num_scenes,
            "generatedAt": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }

    @staticmethod
    def _by_scene_id(items: List[Dict[str, Any]]) -> Dict[int, List[Dict[str, Any]]]:
        """Group items (dialogue / prompt / audio) by their sceneNumber field."""
        result: Dict[int, List[Dict[str, Any]]] = {}
        for item in items:
            sid = _item_scene_id(item)
            result.setdefault(sid, []).append(item)
        return result

    @staticmethod
    def _pull_voiceover(sid: int, dialogues: List[Dict[str, Any]]) -> str:
        """Find a VO line for this scene (heuristic on emotion label)."""
        for d in dialogues:
            try:
                if _item_scene_id(d) != sid:
                    continue
            except ValueError:
                continue
            emo = _safe(d.get("emotion"), "")
            if "narration" in emo.lower() or "voiceover" in emo.lower():
                return _safe(d.get("text", d.get("dialogue", d.get("line"))))
        for d in dialogues:
            try:
                if _item_scene_id(d) == sid:
                    vo = d.get("voice_over") or d.get("voiceover")
                    if vo:
                        return _safe(vo)
            except ValueError:
                continue
        return ""


# ── convenience ───────────────────────────────────────────────────────────────

def write_scenes(
    run_dir: Path,
    story: Dict[str, Any],
    scenes: List[Dict[str, Any]],
    dialogues: List[Dict[str, Any]],
    prompts: List[Dict[str, Any]],
    audio: Optional[List[Dict[str, Any]]] = None,
) -> Path:
    """Module-level convenience function."""
    return SceneFileWriter(run_dir).write(story, scenes, dialogues, prompts, audio)
