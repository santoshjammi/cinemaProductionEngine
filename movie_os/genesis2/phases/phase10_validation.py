"""Phase 10: Validation — run automatic validation on all previous phases."""

from __future__ import annotations

import json
from typing import Any

from ..models import Validation, ValidationIssue, KnowledgeObject
from ..phase_base import PhaseBase


class ValidationPhase(PhaseBase):
    phase_number = 10
    phase_name = "Validation"

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        all_phases = {k: v for k, v in pkg.items() if k.startswith("phase_")}
        return (
            f"# Phase 10: Validation\n\n"
            f"Run automatic validation on all previous phases.\n\n"
            f"## All Phase Outputs\n{json.dumps(all_phases, indent=2, default=str)}\n\n"
            f"## Check for\n"
            f"- missing_info: required fields that are empty\n"
            f"- contradictions: conflicting information between phases\n"
            f"- timeline_errors: events that don't follow logically\n"
            f"- character_consistency: character traits that change without reason\n"
            f"- theme_consistency: thematic elements that contradict\n"
            f"- world_consistency: world rules that are violated\n"
            f"- narrative_logic: plot holes or logical gaps\n"
            f"- specification_completeness: missing production specs\n\n"
            f"Respond with JSON: {{ issues: [{{category, severity, location, description, suggestion}}], passed: bool, score: float }}\n"
            f"Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> Validation:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        issues = [ValidationIssue(**i) for i in data.get("issues", [])]
        return Validation(issues=issues, passed=data.get("passed", False), score=data.get("score", 0.0))

    def draft(self, pkg: dict[str, Any]) -> Validation:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)

    def validate(self, knowledge: Validation) -> list[ValidationIssue]:
        """Validation phase validates its own output."""
        issues = super().validate(knowledge)
        if knowledge.issues:
            errors = [i for i in knowledge.issues if i.severity == "error"]
            if errors:
                issues.extend(errors)
        return issues
