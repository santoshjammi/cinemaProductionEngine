"""Phase 03: Character Psychology — generate all characters with full psychology."""

from __future__ import annotations

import json
from typing import Any

from ..models import CharacterPsychology, Character, KnowledgeObject
from ..phase_base import PhaseBase


class CharacterPsychologyPhase(PhaseBase):
    phase_number = 3
    phase_name = "Character Psychology"

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        prev = {k: pkg.get(k, {}) for k in ["phase_01", "phase_02"]}
        synopsis = pkg.get("synopsis", "")
        return (
            f"# Phase 03: Character Psychology\n\n"
            f"Generate complete character profiles.\n\n"
            f"## Synopsis\n{synopsis}\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Generate for EVERY character\n"
            f"- name, role (protagonist/antagonist/supporting)\n"
            f"- identity, history, goals, fear, need, want\n"
            f"- weakness, strength, internal_conflict, external_conflict\n"
            f"- speech_style, personality, transformation\n\n"
            f"Respond with JSON: {{ protagonist: {{...}}, antagonist: {{...}} or null, supporting_characters: [...] }}\n"
            f"Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> CharacterPsychology:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        proto = Character(**data.get("protagonist", {}))
        antag_data = data.get("antagonist")
        antag = Character(**antag_data) if antag_data else None
        supporting = [Character(**c) for c in data.get("supporting_characters", [])]
        return CharacterPsychology(protagonist=proto, antagonist=antag, supporting_characters=supporting)

    def draft(self, pkg: dict[str, Any]) -> CharacterPsychology:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)
