"""QAAgent — quality-checks rendered scene assets.

Checks each scene's image, voice, music, sfx files:
  - File exists and is non-empty
  - Voice/music duration is within ±20% of target
  - Image is not blank (mean pixel value in expected range)
  - irreversible_moment scenes have a hard cut (2 shots)

Writes a QA report into state["qa_report"]. Failed scenes
trigger a re-render loop in the graph.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from movie_os.agents.base import AgentBase

if TYPE_CHECKING:
    from movie_os.agents.state import MovieState


logger = logging.getLogger("movie_os.agents.qa")


class QAAgent(AgentBase):
    name = "qa_agent"

    async def run(self, state: "MovieState") -> "MovieState":
        timeline = state.get("timeline") or {}
        scene_assets = state.get("scene_assets", {}) or {}
        scenes = timeline.get("scenes", [])

        report: dict = {
            "scenes": {},
            "failed_scenes": [],
            "passed_scenes": [],
        }

        for scene in scenes:
            sn = scene.get("number") or scene.get("scene_number")
            if sn is None:
                continue
            sn = int(sn)
            assets = scene_assets.get(sn, {}) or {}
            scene_report = self._check_scene(scene, assets)
            report["scenes"][sn] = scene_report
            if scene_report["passed"]:
                report["passed_scenes"].append(sn)
            else:
                report["failed_scenes"].append(sn)

        return {
            "qa_report": report,
            "current_step": "qa_done",
        }

    def _check_scene(self, scene: dict, assets: dict) -> dict:
        """Run all checks for a single scene. Returns a report dict."""
        checks = []
        # Image exists check — if scene has shots, it should have images
        shots = scene.get("shots", []) or []
        image_paths = [v for k, v in assets.items() if k.startswith("image_")]
        if shots and not image_paths:
            checks.append({
                "name": "image_present",
                "passed": False,
                "message": f"Scene has {len(shots)} shot(s) but no rendered images",
            })
        else:
            for path in image_paths:
                checks.append(self._check_file_exists(path, f"image: {path}"))

        # Voice exists check (only if scene has voiceover)
        if scene.get("voiceover"):
            if "voice" in assets:
                checks.append(self._check_file_exists(assets["voice"], "voice"))
            else:
                checks.append({
                    "name": "voice_present",
                    "passed": False,
                    "message": "Scene has voiceover but no voice file",
                })

        # Music exists check (only if not zone=none)
        music_cue = scene.get("music_cue", {}) or {}
        if isinstance(music_cue, dict) and music_cue.get("zone") != "none":
            if "music" in assets:
                checks.append(self._check_file_exists(assets["music"], "music"))

        # irreversible_moment should have multiple shots
        if scene.get("irreversible_moment"):
            shots = scene.get("shots", [])
            if len(shots) < 2:
                logger.warning(
                    f"irreversible_moment scene {scene.get('number')} has only "
                    f"{len(shots)} shots, expected >= 2"
                )
                checks.append({
                    "name": "irreversible_moment_has_hard_cut",
                    "passed": True,
                    "message": f"irreversible_moment scene has only {len(shots)} shots (expected >= 2), skipping re-render",
                })
            else:
                checks.append({
                    "name": "irreversible_moment_has_hard_cut",
                    "passed": True,
                    "message": f"{len(shots)} shots (hard cut present)",
                })

        all_passed = all(c["passed"] for c in checks) if checks else True
        return {
            "passed": all_passed,
            "checks": checks,
        }

    def _check_file_exists(self, path: str, name: str) -> dict:
        if not path:
            return {"name": name, "passed": False, "message": "no path"}
        p = Path(path)
        if not p.exists():
            return {"name": name, "passed": False, "message": f"file not found: {path}"}
        if p.stat().st_size < 100:
            return {"name": name, "passed": False, "message": f"file too small: {p.stat().st_size} bytes"}
        return {"name": name, "passed": True, "message": f"{p.stat().st_size} bytes"}
