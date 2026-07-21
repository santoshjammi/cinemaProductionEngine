"""Phase 02: Story Foundation — expand synopsis into structured story elements."""

from __future__ import annotations

import json
from typing import Any

from ..models import StoryFoundation, StoryBeat, KnowledgeObject
from ..phase_base import PhaseBase


class StoryFoundationPhase(PhaseBase):
    phase_number = 2
    phase_name = "Story Foundation"

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        prev = pkg.get("phase_01", {})
        synopsis = pkg.get("synopsis", "")
        return (
            f"# Phase 02: Story Foundation\n\n"
            f"Expand the synopsis into a structured story foundation.\n\n"
            f"## Synopsis\n{synopsis}\n\n"
            f"## Creative Understanding\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Generate\n"
            f"- premise: one-sentence premise\n"
            f"- acts: list of acts with name, description, events\n"
            f"- major_events: list of key plot events\n"
            f"- emotional_journey: list of emotional states across the story\n"
            f"- story_beats: list of {{name, description, position, emotional_intent}}\n"
            f"- narrative_rhythm: description of pacing\n"
            f"- foreshadowing: list of foreshadowing elements\n"
            f"- symbolism: list of symbolic elements\n"
            f"- motifs: list of recurring motifs\n\n"
            f"Respond with valid JSON only. Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> StoryFoundation:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        return StoryFoundation._from_llm(data)

    def draft(self, pkg: dict[str, Any]) -> StoryFoundation:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)
