"""Stage 1: Storyboard — converts scene descriptions to visual storyboard frames."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

from movie_os.runtime_paths import build_run_path

logger = logging.getLogger("movie_os.prometheus.stages.storyboard")


class StoryboardStage:
    """Storyboard stage: converts GENESIS blueprint scenes into visual storyboards.

    Takes scene descriptions from the ProductionCertificate.blueprint and
    produces storyboard frames with scene layout, camera angle, and visual prompts.
    """

    def __init__(self, certificate: Any | None = None, brief: dict[str, Any] | None = None):
        self.certificate = certificate
        self.brief = brief or {}

    def run(self) -> dict[str, Any]:
        """Run the storyboard stage and return a result dict with artifacts."""
        blueprint = self.certificate.blueprint if hasattr(self.certificate, 'blueprint') else {}
        scenes = blueprint.get("scenes", [])

        if not scenes:
            logger.warning("[StoryboardStage] No scenes in blueprint — generating default storyboard")
            scenes = [{"id": 1, "description": "Establishing shot of the setting"}]

        artifacts = []

        for scene in scenes:
            scene_id = scene.get("id") or scene.get("scene_number") or scene.get("number") or 1
            description = scene.get("description", "") or scene.get("scene_description", "")
            
            # Generate a storyboard entry with composition notes
            artifact_path = str(build_run_path(self.brief, "motion", f"scene_{scene_id:03d}_storyboard.png"))

            scene_shot = self._scene_shot(scene_id)
            scene_dialogue = self._scene_dialogue(scene_id)

            # Create compositional metadata for the storyboard frame
            composition = self._compose_frame(scene_id, description, scene_shot, scene_dialogue)

            artifacts.append({
                "type": "storyboard",
                "path": artifact_path,
                "url": None,
                "metadata": {
                    "scene_id": scene_id,
                    "composition": composition,
                    "prompt": description,
                    "camera_angle": composition.get("camera_angle", "wide"),
                    "lighting": composition.get("lighting", "natural"),
                    "description": description,
                    "speaker_coverage": composition.get("speaker_coverage"),
                    "listener_coverage": composition.get("listener_coverage"),
                    "lip_sync_visible": composition.get("lip_sync_visible", False),
                    "performance_intent": scene_shot.get("performance_intent"),
                },
            })

        result = {
            "artifacts": artifacts,
            "stage_name": "Storyboard",
            "scenes_processed": len(artifacts),
        }
        logger.info(f"[StoryboardStage] Generated {len(artifacts)} storyboard frames")
        return result

    def _scene_shot(self, scene_id: int) -> dict[str, Any]:
        for shot in self.brief.get("shots", []) or []:
            if shot.get("scene_id") == scene_id:
                return shot
        for scene in self.brief.get("scenes", []) or []:
            sid = scene.get("number") or scene.get("scene_number") or scene.get("id")
            if sid == scene_id and isinstance(scene.get("shot"), dict):
                return scene["shot"]
        return {}

    def _scene_dialogue(self, scene_id: int) -> dict[str, Any]:
        for dialogue in self.brief.get("dialogues", []) or []:
            if dialogue.get("scene_number") == scene_id:
                return dialogue
        return {}

    def _compose_frame(self, scene_id: int, description: str, scene_shot: dict[str, Any] | None = None, scene_dialogue: dict[str, Any] | None = None) -> dict[str, Any]:
        """Generate composition parameters for a storyboard frame."""
        scene_shot = scene_shot or {}
        scene_dialogue = scene_dialogue or {}
        words = " ".join([
            description or "",
            str(scene_shot.get("framing", "")),
            str(scene_shot.get("function", "")),
            str(scene_shot.get("performance_intent", "")),
            str(scene_shot.get("visual_intent", "")),
        ]).lower()
        
        if any(w in words for w in ["morning", "dawn", "sunrise", "bright"]):
            lighting = "golden_hour"
        elif any(w in words for w in ["night", "dark", "evening", "twilight"]):
            lighting = "low_key"
        elif any(w in words for w in ["rain", "storm", "overcast"]):
            lighting = "diffuse_overcast"
        else:
            lighting = "natural"

        if any(w in words for w in ["over_shoulder", "over-the-shoulder", "ots"]):
            camera_angle = "over_the_shoulder"
        elif any(w in words for w in ["two-shot", "two shot", "two_shot"]):
            camera_angle = "two_shot"
        elif any(w in words for w in ["insert", "detail", "reaction"]):
            camera_angle = "insert_close_up"
        elif any(w in words for w in ["wide", "panorama", "landscape", "exterior"]):
            camera_angle = "wide"
        elif any(w in words for w in ["close_up", "close-up", "portrait"]):
            camera_angle = "close_up"
        elif any(w in words for w in ["aerial", "birdseye", "overhead"]):
            camera_angle = "aerial"
        else:
            camera_angle = "medium"

        spoken_lines = scene_dialogue.get("lines", []) or []
        listener = None
        if len(spoken_lines) >= 2:
            listener = spoken_lines[1].get("speaker")
        elif spoken_lines:
            speaker = spoken_lines[0].get("speaker")
            listener = "SARAH" if speaker == "MARK" else "MARK"
        lip_sync_visible = bool(scene_shot.get("lip_sync_required", False)) and camera_angle in {"close_up", "insert_close_up", "over_the_shoulder", "two_shot"}

        return {
            "camera_angle": camera_angle,
            "lighting": lighting,
            "aspect_ratio": self.brief.get("aspect_ratio", "16:9"),
            "resolution": self.brief.get("resolution", 1080),
            "speaker_coverage": scene_shot.get("speaker", spoken_lines[0].get("speaker") if spoken_lines else None),
            "listener_coverage": listener,
            "lip_sync_visible": lip_sync_visible,
            "performance_intent": scene_shot.get("performance_intent") or (spoken_lines[0].get("emotion") if spoken_lines else None),
        }

    def create_initial_state(self, name: str = "Storyboard") -> dict[str, Any]:
        """Create initial stage state for pipeline bookkeeping."""
        return {
            "name": name,
            "class_name": "StoryboardStage",
            "stage": {
                "name": name,
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "artifacts": [],
                "error": None,
            },
        }
