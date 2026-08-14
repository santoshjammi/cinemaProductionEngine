"""Stage 4: Music — generates background score for the film.

Takes video + audio artifacts as input and generates a musical score
that matches the mood/tone of each scene.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Optional

from movie_os.runtime_paths import build_run_path

logger = logging.getLogger("movie_os.prometheus.stages.music")


class MusicStage:
    """Background music composition stage."""

    def __init__(self, certificate: Any | None = None, brief: dict[str, Any] | None = None):
        self.certificate = certificate
        self.brief = brief or {}
        self._music_provider: Any | None = None

    @property
    def music_provider(self) -> Any:
        if self._music_provider is not None:
            return self._music_provider
        try:
            from movie_os.providers.music.procedural import ProceduralMusicProvider  # type: ignore
            return ProceduralMusicProvider()
        except Exception:
            return None

    def set_music_provider(self, provider: Any) -> None:
        """Inject a music provider (useful for testing with a mock)."""
        self._music_provider = provider

    def run(self) -> dict[str, Any]:
        """Execute the music composition stage."""
        voice_artifacts = self.brief.get('voice_artifacts', [])
        image_artifacts = self.brief.get('image_artifacts', [])
        brief_scenes = {s.get('scene_number') or s.get('number'): s for s in self.brief.get('scenes', [])}

        scene_count = max(1, len(image_artifacts) or 0)

        # Map scene -> CC0 music track (emotional arc). Falls back to a
        # generic ambient track if the scene's music_cue is unknown.
        music_dir = Path("assets/music")
        track_map = {
            "guarded": "cinematic_ambient_piano",
            "withdrawn": "isolation_ambient",
            "frustrated": "dark_rain_piano_strings",
            "emotional_peak": "circle_of_life_sad",
            "resolved": "lucas_king_hurt",
        }

        artifacts = []
        for i in range(scene_count):
            scene_id = i + 1
            scene = brief_scenes.get(scene_id, {})
            emotion = scene.get('emotional_state', 'neutral')
            # Pick a track by emotion keyword
            track_key = None
            for kw, tk in track_map.items():
                if kw in str(emotion).lower():
                    track_key = tk
                    break
            if track_key is None:
                track_key = "cinematic_ambient_piano"
            src = music_dir / f"{track_key}.mp3"
            artifact_path = str(build_run_path(self.brief, "music", f"scene_{scene_id:03d}.mp3"))
            # Copy the real CC0 track into the artifact path (idempotent)
            if src.exists():
                try:
                    import shutil
                    Path(artifact_path).parent.mkdir(parents=True, exist_ok=True)
                    if not Path(artifact_path).exists() or Path(artifact_path).stat().st_size == 0:
                        shutil.copy2(src, artifact_path)
                except Exception as e:
                    logger.warning(f"[MusicStage] copy failed for scene {scene_id}: {e}")
            artifacts.append({
                "type": "music",
                "path": artifact_path,
                "url": None,
                "metadata": {
                    "scene_id": scene_id,
                    "mood": emotion,
                    "track": track_key,
                    "duration_seconds": 60.0,
                    "bpm": self.brief.get('bpm', 120),
                },
            })

        if not artifacts:
            artifacts = [{
                "type": "music",
                "path": str(build_run_path(self.brief, "music", "track_001.mp3")),
                "url": None,
                "metadata": {"composition": "default_score", "duration_seconds": 60.0},
            }]

        return {
            "artifacts": artifacts,
            "stage_name": "MusicComposition",
            "music_tracks_generated": len(artifacts),
        }

    def create_initial_state(self, name: str = "MusicComposition") -> dict[str, Any]:
        return {
            "name": name,
            "class_name": "MusicStage",
            "stage": {
                "name": name,
                "status": "pending",
                "started_at": None,
                "completed_at": None,
                "artifacts": [],
                "error": None,
            },
        }
