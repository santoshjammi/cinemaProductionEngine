"""Phase 04: World Development — generate the story's world."""

from __future__ import annotations

import json
from typing import Any

from ..models import WorldDevelopment, KnowledgeObject
from ..phase_base import PhaseBase


class WorldDevelopmentPhase(PhaseBase):
    phase_number = 4
    phase_name = "World Development"

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        prev = {k: pkg.get(k, {}) for k in ["phase_01", "phase_02", "phase_03"]}
        synopsis = pkg.get("synopsis", "")
        return (
            f"# Phase 04: World Development\n\n"
            f"Generate the world the story inhabits.\n\n"
            f"## Synopsis\n{synopsis}\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Generate\n"
            f"- history: world backstory\n"
            f"- culture: cultural norms and values\n"
            f"- technology: technology level\n"
            f"- environment: physical environment\n"
            f"- rules: list of world rules\n"
            f"- architecture: architectural style\n"
            f"- economy: economic system\n"
            f"- politics: political structure\n"
            f"- timeline: list of key historical events\n"
            f"- social_structure: social hierarchy\n\n"
            f"Respond with valid JSON only. Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> WorldDevelopment:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        return WorldDevelopment(**data)

    def draft(self, pkg: dict[str, Any]) -> WorldDevelopment:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)
