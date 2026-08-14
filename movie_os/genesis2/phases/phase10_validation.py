"""Phase 10: Validation — validate all previous phases for consistency."""

from __future__ import annotations

import json
from typing import Any

from ..models import ConfidenceLevel, KnowledgeObject, ValidationIssue, Validation as ValidationKO
from ..phase_base import PhaseBase


class ValidationPhase(PhaseBase):
    phase_number = 10
    phase_name = "Validation"
    _REQUIRED: list[str] = ["issues", "passed"]

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        previous_keys = [f"phase_{i:02d}" for i in range(1, 10)]
        prev = self.slice_context(pkg, previous_keys)
        return (
            f"# Phase 10: Validation\n\n"
            f"Validate all previous phases for consistency.\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Check for\n"
            f"- Missing required fields in any phase output\n"
            f"- Contradictions between phases\n"
            f"- Inconsistencies in character names / plot threads\n"
            f"- Pacing and structural issues\n\n"
            f"Respond with JSON: {{ \"issues\": [], \"passed\": true, \"score\": 1.0 }}\n"
            f"Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> KnowledgeObject:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        return self._parse(data)

    @staticmethod
    def _parse(data: dict[str, Any]) -> KnowledgeObject:
        issues_list = data.get("issues", [])
        if isinstance(issues_list, list):
            parsed_issues = [ValidationIssue(**i) for i in issues_list if isinstance(i, dict)]
        else:
            parsed_issues = []
        return ValidationKO(
            issues=parsed_issues,
            passed=bool(data.get("passed", False)),
            score=float(data.get("score", 0.0)),
            purpose=data.get("purpose", ""), creative_intent=data.get("creative_intent", ""),
            reasoning=data.get("reasoning", ""), confidence=data.get("confidence", "inferred"),
        )

    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)

    def _review_specific(self, knowledge: KnowledgeObject) -> list[str]:
        issues: list[str] = []
        passed = getattr(knowledge, "passed", None)
        score = getattr(knowledge, "score", None)
        if not isinstance(passed, bool):
            issues.append("validation.passed must be a boolean")
        elif not passed and isinstance(score, (int, float)) and score > 0.7:
            issues.append("Validation failed but score contradicts — possible inconsistency")
        return issues

    def _validate_specific(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:  # noqa
        from ..models import ValidationIssue  # noqa
        issues: list[ValidationIssue] = []
        passed = getattr(knowledge, "passed", None)
        if not isinstance(passed, bool):
            issues.append(ValidationIssue(
                category="schema_error", severity="error",
                location=f"{self.phase_name}.passed",
                description="passed field must be boolean",
            ))
        score = getattr(knowledge, "score", None)
        if isinstance(score, (int, float)):
            if score < 0 or score > 1:
                issues.append(ValidationIssue(
                    category="schema_error", severity="error",
                    location=f"{self.phase_name}.score",
                    description="score must be between 0 and 1",
                ))
        return issues
