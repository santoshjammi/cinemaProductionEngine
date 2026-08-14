"""Phase 08: Visual Language — define visual motifs, color palette, shot language."""

from __future__ import annotations

import json
from typing import Any

from ..models import ConfidenceLevel, KnowledgeObject, ValidationIssue
from ..phase_base import PhaseBase


class VisualLanguagePhase(PhaseBase):
    phase_number = 8
    phase_name = "Visual Language"
    _REQUIRED: list[str] = ["color", "lighting", "composition"]

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        prev = self.slice_context(pkg, ["phase_01"])
        synopsis = pkg.get("synopsis", "")
        return (
            f"# Phase 08: Visual Language\n\n"
            f"Define the visual language of the story.\n\n"
            f"## Synopsis\n{synopsis}\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Define\n"
            f"- color: overall color palette\n"
            f"- lighting: lighting philosophy\n"
            f"- composition: framing and visual balance\n"
            f"- textures: surface quality and material feel\n"
            f"- atmosphere: mood conveyed visually\n"
            f"- camera_intent: how camera supports narrative\n"
            f"- lens_suggestions: recommended lenses\n"
            f"- movement_philosophy: approach to camera movement\n"
            f"- environmental_storytelling: visual storytelling cues\n\n"
            f"Respond with valid JSON only. Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> KnowledgeObject:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        return self._parse(data)

    @staticmethod
    def _parse(data: dict[str, Any]) -> KnowledgeObject:
        from ..models import VisualLanguage
        return VisualLanguage(**data)

    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)

    def _review_specific(self, knowledge: KnowledgeObject) -> list[str]:
        issues: list[str] = []
        for field in self._REQUIRED:
            val = getattr(knowledge, field, None)
            if not (isinstance(val, str) and val.strip()):
                issues.append(f"Missing {field} — core to visual direction")
        return issues

    def _validate_specific(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:  # noqa
        from ..models import ValidationIssue  # noqa
        issues: list[ValidationIssue] = []
        color = getattr(knowledge, "color", None)
        if isinstance(color, str) and len(color.strip()) < 3:
            issues.append(ValidationIssue(
                category="quality", severity="warning",
                location=f"{self.phase_name}.color",
                description="Color palette description is too brief",
            ))
        return issues
