"""Phase 11: Creative Critique — a separate model critiques everything."""

from __future__ import annotations

import json
from typing import Any

from ..models import CreativeCritique, CritiqueFinding, KnowledgeObject
from ..phase_base import PhaseBase


class CreativeCritiquePhase(PhaseBase):
    phase_number = 11
    phase_name = "Creative Critique"

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        all_phases = {k: v for k, v in pkg.items() if k.startswith("phase_")}
        return (
            f"# Phase 11: Creative Critique\n\n"
            f"A separate model critiques everything produced so far.\n\n"
            f"## All Phase Outputs\n{json.dumps(all_phases, indent=2, default=str)}\n\n"
            f"## Questions\n"
            f"- Is this emotionally believable?\n"
            f"- Are motivations realistic?\n"
            f"- Are scenes repetitive?\n"
            f"- Does every scene matter?\n"
            f"- Does every character matter?\n"
            f"- Does tension increase?\n"
            f"- Does the ending feel earned?\n"
            f"- Could this movie exist without Scene X?\n"
            f"- Could Character Y be removed?\n"
            f"- Is there enough emotional contrast?\n\n"
            f"Respond with JSON: {{ findings: [{{question, answer, severity, recommendation}}], overall_assessment: str, recommended_actions: [str] }}\n"
            f"Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> CreativeCritique:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        findings = [CritiqueFinding(**f) for f in data.get("findings", [])]
        return CreativeCritique(
            findings=findings,
            overall_assessment=data.get("overall_assessment", ""),
            recommended_actions=data.get("recommended_actions", []),
        )

    def draft(self, pkg: dict[str, Any]) -> CreativeCritique:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)
