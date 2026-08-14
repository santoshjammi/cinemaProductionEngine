"""Stage 5: Editing — composes scenes into a rough cut.

Takes images + audio artifacts as input and creates the assembly timeline,
ordering, timing, and transitions for the film.
"""

from __future__ import annotations

import json
import logging
import shutil
from typing import Any, Optional
from pathlib import Path

from movie_os.runtime_paths import build_run_path

logger = logging.getLogger("movie_os.prometheus.stages.editing")


class EditingStage:
    """Editing stage: assembles scenes into a rough-cut timeline."""

    def __init__(
        self,
        certificate: Any | None = None,
        brief: dict[str, Any] | None = None,
    ):
        self.certificate = certificate
        self.brief = brief or {}
        self._video_provider: Any | None = None

    @property
    def video_provider(self) -> Any:
        if self._video_provider is not None:
            return self._video_provider
        try:
            from movie_os.providers.video.base import VideoProvider  # type: ignore
            return VideoProvider()
        except Exception:
            return None

    def set_video_provider(self, provider: Any) -> None:
        """Inject a video provider (useful for testing with a mock)."""
        self._video_provider = provider

    def run(self) -> dict[str, Any]:
        """Execute the editing stage."""
        image_artifacts = self.brief.get('image_artifacts', [])
        voice_artifacts = self.brief.get('voice_artifacts', [])
        scene_count = max(1, len(image_artifacts), len(voice_artifacts))

        timeline_entries = []
        for i in range(scene_count):
            scene_id = i + 1
            entry = {
                "scene_id": scene_id,
                "start_time": i * 5.0,
                "end_time": (i + 1) * 5.0,
                "image_artifact": self._pick_image(image_artifacts, scene_id),
                "voice_artifact": self._pick_audio(voice_artifacts, scene_id),
            }
            timeline_entries.append(entry)

        timeline_path = str(build_run_path(self.brief, "render", "timeline.json"))
        result_data = {
            "project_name": getattr(self.certificate, 'project_name', 'Untitled') if self.certificate else 'Untitled',
            "timeline": timeline_entries,
            "total_scenes": scene_count,
            "duration_seconds": scene_count * 5.0,
        }

        return {
            "artifacts": [{
                "type": "video",
                "path": timeline_path,
                "url": None,
                "metadata": {"timeline_entries": len(timeline_entries), "raw_data": result_data},
            }],
            "stage_name": "Editing",
            "scenes_assembled": scene_count,
        }

    def _pick_image(self, artifacts: list[dict[str, Any]], scene_id: int) -> dict[str, Any] | None:
        """Pick the image artifact for this scene."""
        for art in artifacts:
            if art.get('metadata', {}).get('scene_id') == scene_id:
                return art
        # Fallback to first.
        return artifacts[0] if artifacts else None

    def _pick_audio(self, artifacts: list[dict[str, Any]], scene_id: int) -> dict[str, Any] | None:
        """Pick the audio artifact for this scene."""
        for art in artifacts:
            if art.get('metadata', {}).get('scene_id') == scene_id:
                return art
        return artifacts[0] if artifacts else None

    def create_initial_state(self, name: str = "Editing") -> dict[str, Any]:
        return {
            "name": name,
            "class_name": "EditingStage",
            "stage": {
                "name": name,
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "artifacts": [],
                "error": None,
            },
        }
