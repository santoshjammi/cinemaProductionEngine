"""Phase 07: Dialogue Planning — plan dialogue intent, subtext, silence, rhythm."""

from __future__ import annotations

import json
from typing import Any

from ..models import DialoguePlanning, DialoguePlan, KnowledgeObject
from ..phase_base import PhaseBase


class DialoguePlanningPhase(PhaseBase):
    phase_number = 7
    phase_name = "Dialogue Planning"

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        prev = {k: pkg.get(k, {}) for k in ["phase_03", "phase_05", "phase_06"]}
        return (
            f"# Phase 07: Dialogue Planning\n\n"
            f"Plan dialogue for every scene.\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## For every scene generate\n"
            f"- scene_number, conversation_intent, subtext\n"
            f"- emotional_state, silence_opportunities (list)\n"
            f"- dialogue_rhythm, speech_patterns, voice_direction\n\n"
            f"Respond with JSON: {{ dialogues: [...] }}\n"
            f"Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> DialoguePlanning:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        dialogues = [DialoguePlan(**d) for d in data.get("dialogues", [])]
        return DialoguePlanning(dialogues=dialogues)

    def draft(self, pkg: dict[str, Any]) -> DialoguePlanning:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)
