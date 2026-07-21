"""Phase 05: Narrative Expansion — convert story into acts, sequences, scenes."""

from __future__ import annotations

import json
from typing import Any

from ..models import NarrativeExpansion, Scene, KnowledgeObject
from ..phase_base import PhaseBase


class NarrativeExpansionPhase(PhaseBase):
    phase_number = 5
    phase_name = "Narrative Expansion"

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        prev = {k: pkg.get(k, {}) for k in ["phase_01", "phase_02", "phase_03", "phase_04"]}
        synopsis = pkg.get("synopsis", "")
        return (
            f"# Phase 05: Narrative Expansion\n\n"
            f"Convert the story into acts, sequences, and scenes.\n\n"
            f"## Synopsis\n{synopsis}\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Generate\n"
            f"- acts: list of {{name, description, sequences}}\n"
            f"- sequences: list of {{name, act, scenes}}\n"
            f"- scenes: list of {{scene_number, act, sequence, objective, conflict, outcome, emotional_objective}}\n\n"
            f"Respond with valid JSON only. Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> NarrativeExpansion:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        scenes = [Scene(**s) for s in data.pop("scenes", [])]
        return NarrativeExpansion(**data, scenes=scenes)

    def draft(self, pkg: dict[str, Any]) -> NarrativeExpansion:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)
