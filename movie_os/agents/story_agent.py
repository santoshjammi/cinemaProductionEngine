"""StoryAgent — generates the Master Timeline from a brief.

Reads the brief (a YAML file path or a dict), invokes the story
capability to generate a Master Timeline, and runs the ShotPlanner
to fill in shots/frames. The resulting timeline goes into
state["timeline"].
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, TYPE_CHECKING

import yaml

from movie_os.agents.base import AgentBase

if TYPE_CHECKING:
    from movie_os.agents.state import MovieState


logger = logging.getLogger("movie_os.agents.story")


class StoryAgent(AgentBase):
    """Read a brief, generate a Master Timeline, plan shots/frames."""

    name = "story_agent"

    async def run(self, state: "MovieState") -> "MovieState":
        brief = state.get("brief", {})
        timeline = await self._build_timeline(brief)
        out = {"timeline": timeline, "current_step": "story_done"}
        if isinstance(timeline, dict) and "dna" in timeline:
            out["dna"] = timeline["dna"]
        return out

    async def _build_timeline(self, brief: dict[str, Any]) -> dict[str, Any]:
        """Build a timeline from the brief.

        Priority:
          1. If the brief has a `scenes` list (a pre-built timeline),
             use it directly. Common path for tests and pre-baked stories.
          2. If the brief has a `timeline` key, use that.
          3. Otherwise, try the story capability (LMStudio).
          4. If that fails, build a single-scene timeline from the brief.
        """
        if "scenes" in brief and brief["scenes"]:
            return self._ensure_shots_and_frames({
                "version": "1.0",
                "dna": brief.get("dna", {}),
                "scenes": brief["scenes"],
            })
        if "timeline" in brief and brief["timeline"]:
            timeline = brief["timeline"]
            return self._ensure_shots_and_frames(timeline)

        # Otherwise, try the story capability (LMStudio or stub)
        cap = self.try_get_capability("story")
        if cap is None:
            logger.warning("No 'story' capability registered; using brief-as-timeline")
            return self._brief_as_timeline(brief)

        try:
            from movie_os.capabilities.base import StoryIntent
            intent = StoryIntent(
                task="scenes",
                synopsis=brief.get("synopsis", ""),
                dna=brief.get("dna", {}),
                context=brief.get("context", ""),
                story=brief.get("story", ""),
                parameters=brief.get("parameters", {}),
                metadata={"brief_path": brief.get("source_path", "")},
            )
            result = await cap.execute(intent)
            # StoryResult has `content`, not `data` — fall back gracefully
            timeline = (
                getattr(result, "content", None)
                or getattr(result, "data", None)
                or result
            )
        except Exception as e:
            logger.warning(f"Story capability failed ({e}); using brief-as-timeline")
            return self._brief_as_timeline(brief)

        return self._ensure_shots_and_frames(timeline)

    def _ensure_shots_and_frames(self, timeline: Any) -> dict:
        """Run ShotPlanner to fill shots/frames if not present.

        Uses the new Pydantic Scene (movie_os.domain.Scene) which
        has a `shots` attribute. The old master_timeline.Scene is
        skipped because it doesn't have that field.
        """
        from story_factory.master_timeline import MasterTimeline
        if isinstance(timeline, MasterTimeline):
            timeline = timeline.to_dict().get("master_timeline", {})
        elif not isinstance(timeline, dict):
            timeline = {}

        scenes = timeline.get("scenes", [])
        if not scenes:
            return timeline
        # All scenes need non-empty shots arrays
        if all(s.get("shots") for s in scenes):
            return timeline

        try:
            from movie_os.data_layer import get_character_registry
            from movie_os.domain import Scene as PydanticScene
            from movie_os.domain.shot_planner import ShotPlanner
            planner = ShotPlanner(character_registry=get_character_registry())
            new_scenes = []
            for s in scenes:
                if "number" not in s and "scene_number" in s:
                    s["number"] = s["scene_number"]
                if "target_duration_seconds" not in s or float(s.get("target_duration_seconds") or 0) <= 0:
                    if "duration_seconds" in s:
                        s["target_duration_seconds"] = s["duration_seconds"]
                # Build a Pydantic Scene from the dict
                scene = PydanticScene(**{
                    k: v for k, v in s.items()
                    if k in (
                        "number", "title", "phase", "beat",
                        "emotional_state", "energy",
                        "voiceover", "dialogues",
                        "scene_description", "scene_description_alt",
                        "visual_cause_of_emotion",
                        "shot_language", "characters_present", "environment_id",
                        "music_cue", "ambient_cue", "silence_engine",
                        "vocal_fracture", "irreversible_moment",
                        "pre_moment", "post_moment", "shows_duality",
                        "target_duration_seconds", "duration_seconds",
                        "ken_burns_effect", "export_profiles", "sfx_layers",
                        "shots", "frames",
                    )
                })
                shots = planner.plan_shots(scene)
                for shot in shots:
                    shot.frames = planner.plan_frames(shot, scene)
                scene.shots = list(shots)
                # Convert back to dict
                new_scenes.append(scene.model_dump(mode="json"))
            return {**timeline, "scenes": new_scenes}
        except Exception as e:
            logger.debug(f"ShotPlanner fill skipped: {e}")
            return timeline

    def _brief_as_timeline(self, brief: dict) -> dict:
        """Build a single-scene timeline from a brief dict (for tests/CLI)."""
        scene = {
            "scene_number": 1,
            "number": 1,
            "title": brief.get("title", "Opening"),
            "act": brief.get("act", "act_1_observation"),
            "phase": brief.get("phase", "hook"),
            "beat": brief.get("beat", "opening_hook"),
            "scene_description": brief.get("synopsis", "A cinematic moment."),
            "scene_description_alt": "",
            "energy": brief.get("energy", 3),
            "target_duration_seconds": brief.get("duration", 10.0),
            "duration_seconds": brief.get("duration", 10.0),
            "shot_language": brief.get("shot_language", {"shot_size": "medium"}),
            "irreversible_moment": brief.get("irreversible_moment", False),
            "voiceover": brief.get("voiceover", ""),
            "music_cue": brief.get("music_cue", {"zone": "act_1", "volume": 0.3}),
            "silence_engine": brief.get("silence_engine", {}),
            "shots": [],
        }
        return {
            "version": "1.0",
            "dna": brief.get("dna", {}),
            "scenes": [scene],
        }


def load_brief(path: str | Path) -> dict:
    """Load a brief from a YAML file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Brief not found: {p}")
    with open(p) as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Brief must be a YAML mapping, got {type(data).__name__}")
    data["source_path"] = str(p.resolve())
    return data
