"""Stage 5: Editing — composes scenes into a rough cut.

Takes images + audio artifacts as input and creates the assembly timeline,
ordering, timing, and transitions for the film.
"""

from __future__ import annotations

import logging
from typing import Any, Optional
from pathlib import Path

from movie_os.runtime_paths import build_run_path

logger = logging.getLogger("movie_os.prometheus.stages.editing")

# Defaults
DEFAULT_PAUSE = 0.7    # seconds between lines (scene tail)
MIN_SCENE_DURATION = 8.0


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
        voice_artifacts: list[dict[str, Any]] = self.brief.get('voice_artifacts', [])

        # --- Validate every voice artifact has the required metadata & path ---
        for art in voice_artifacts:
            meta = art.get("metadata", {})
            if not meta:
                raise ValueError(
                    "Voice artifact is missing metadata. "
                    "Required fields: scene_id, line_id, speaker, duration_seconds"
                )
            for key in ("scene_id", "line_id", "speaker", "duration_seconds"):
                if key not in meta:
                    raise ValueError(
                        f"Voice artifact {art.get('line_id', art)} metadata missing '{key}'. "
                        "Required: scene_id, line_id, speaker, duration_seconds"
                    )
            p = Path(art.get("path", ""))
            if not p or not p.exists():
                raise ValueError(
                    f"Voice artifact audio path does not exist: {art.get('path', '<missing>')}. "
                    "All voice artifacts must have a valid file path."
                )

        # --- Build the deterministic per-line timeline ---
        # One timeline entry PER LINE (i.e. per voice_artifact), grouped by
        # scene order so that entries appear in natural narrative order.  We do
        # NOT fabricate scene_ids or repeat artifacts from the first entry.
        pause = DEFAULT_PAUSE

        cumulative_start = 0.0
        timeline_entries: list[dict[str, Any]] = []

        for idx, art in enumerate(voice_artifacts):
            meta = art["metadata"]
            dur = float(meta["duration_seconds"])

            is_last = (idx == len(voice_artifacts) - 1)
            entry_pause = 0.0 if is_last else pause

            start_time = cumulative_start
            end_time = round(start_time + dur, 6)

            timeline_entries.append({
                "line_id": meta["line_id"],
                "scene_id": int(meta["scene_id"]),
                "speaker": meta["speaker"],
                "audio_path": art["path"],
                "start_time": start_time,
                "end_time": end_time,
                "duration_seconds": dur,
                "pause_after_seconds": entry_pause,
            })

            if not is_last:
                cumulative_start = end_time + entry_pause

        total_dur = round(sum(
            e["duration_seconds"] + e["pause_after_seconds"]
            for e in timeline_entries
        ), 6) if timeline_entries else 0.0

        timeline_path = str(build_run_path(self.brief, "render", "timeline.json"))
        result_data = {
            "project_name": getattr(self.certificate, 'project_name', 'Untitled') if self.certificate else 'Untitled',
            "timeline": timeline_entries,
            "total_scenes": len(set(e["scene_id"] for e in timeline_entries)),
            "duration_seconds": total_dur,
        }

        return {
            "artifacts": [{
                "type": "video",
                "path": timeline_path,
                "url": None,
                "metadata": {"timeline_entries": len(timeline_entries), "raw_data": result_data},
            }],
            "stage_name": "Editing",
            "scenes_assembled": result_data["total_scenes"],
        }

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
