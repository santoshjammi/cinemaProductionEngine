"""Phase 09: Production Specs — define runtime, format, technical requirements."""

from __future__ import annotations

import json
from typing import Any

from ..models import ConfidenceLevel, KnowledgeObject, ValidationIssue
from ..phase_base import PhaseBase


class ProductionSpecificationsPhase(PhaseBase):
    phase_number = 9
    phase_name = "Production Specifications"
    _REQUIRED: list[str] = ["character_specs", "location_specs"]

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        previous_keys = [f"phase_{i:02d}" for i in range(1, 9)]
        prev = self.slice_context(pkg, previous_keys)
        return (
            f"# Phase 09: Production Specifications\n\n"
            f"Define technical requirements for production.\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Define for each category\n"
            f"- character_specs: character visual specs\n"
            f"- location_specs: location specs\n"
            f"- camera_specs: camera equipment\n"
            f"- lighting_specs: lighting setup\n"
            f"- animation_specs: animation requirements\n"
            f"- audio_specs: audio requirements\n"
            f"- music_specs: music direction\n"
            f"- editing_specs: post-production\n"
            f"- rendering_specs: final output specs\n\n"
            f"Respond with valid JSON only. Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> KnowledgeObject:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        return self._parse(data)

    @staticmethod
    def _parse(data: dict[str, Any]) -> KnowledgeObject:
        from ..models import ProductionSpecifications
        return ProductionSpecifications(**data)

    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)

    def _review_specific(self, knowledge: KnowledgeObject) -> list[str]:
        issues: list[str] = []
        for field in self._REQUIRED:
            val = getattr(knowledge, field, None)
            if not (isinstance(val, list) and len(val) > 0):
                issues.append(f"Empty {field} — at least one entry required")
        return issues

    def _validate_specific(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:  # noqa
        from ..models import ValidationIssue  # noqa
        issues: list[ValidationIssue] = []
        for field in self._REQUIRED:
            val = getattr(knowledge, field, None)
            if isinstance(val, list) and len(val) > 0:
                pass  # valid
            elif not (isinstance(val, list)):
                issues.append(ValidationIssue(
                    category="schema_error", severity="error",
                    location=f"{self.phase_name}.{field}",
                    description=f"{field} must be a list (may be empty)",
                ))
        return issues
