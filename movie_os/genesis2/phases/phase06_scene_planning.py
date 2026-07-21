"""Phase 06: Scene Planning — plan every scene's purpose, conflict, emotion, goals."""

from __future__ import annotations

import json
from typing import Any

from ..models import ScenePlanning, ScenePlan, KnowledgeObject
from ..phase_base import PhaseBase


class ScenePlanningPhase(PhaseBase):
    phase_number = 6
    phase_name = "Scene Planning"

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        prev = {k: pkg.get(k, {}) for k in ["phase_01", "phase_02", "phase_05"]}
        return (
            f"# Phase 06: Scene Planning\n\n"
            f"Plan every scene's purpose, conflict, emotion, and goals.\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## For every scene generate\n"
            f"- scene_number, purpose, conflict, emotion\n"
            f"- visual_goal, audio_goal, character_goal\n"
            f"- transition, duration, dependencies\n\n"
            f"Respond with JSON: {{ scenes: [...] }}\n"
            f"Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> ScenePlanning:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        scenes = [ScenePlan(**s) for s in data.get("scenes", [])]
        return ScenePlanning(scenes=scenes)

    def draft(self, pkg: dict[str, Any]) -> ScenePlanning:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)
