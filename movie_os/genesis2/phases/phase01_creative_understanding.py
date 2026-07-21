"""Phase 01: Creative Understanding — understand what the story actually means."""

from __future__ import annotations

import json
from typing import Any

from ..models import CreativeUnderstanding, KnowledgeObject
from ..phase_base import PhaseBase


class CreativeUnderstandingPhase(PhaseBase):
    phase_number = 1
    phase_name = "Creative Understanding"

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        synopsis = pkg.get("synopsis", "")
        constraints = pkg.get("constraints", {})
        return (
            f"# Phase 01: Creative Understanding\n\n"
            f"Understand what the story actually means.\n\n"
            f"## Synopsis\n{synopsis}\n\n"
            f"## Constraints\n{json.dumps(constraints, indent=2)}\n\n"
            f"## Extract\n"
            f"- theme: the central thematic idea\n"
            f"- genre: primary genre\n"
            f"- subgenre: specific subgenre\n"
            f"- audience: target audience\n"
            f"- mood: overall emotional mood\n"
            f"- core_question: the question the story asks\n"
            f"- message: what the story says\n"
            f"- conflict: central conflict\n"
            f"- transformation: how the audience should transform\n"
            f"- success_criteria: list of criteria for success\n\n"
            f"Respond with valid JSON only. Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> CreativeUnderstanding:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        return CreativeUnderstanding(**data)

    def draft(self, pkg: dict[str, Any]) -> CreativeUnderstanding:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)
