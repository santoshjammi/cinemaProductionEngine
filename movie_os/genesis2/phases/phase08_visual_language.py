"""Phase 08: Visual Language — generate color, lighting, composition, camera intent."""

from __future__ import annotations

import json
from typing import Any

from ..models import VisualLanguage, KnowledgeObject
from ..phase_base import PhaseBase


class VisualLanguagePhase(PhaseBase):
    phase_number = 8
    phase_name = "Visual Language"

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        prev = {k: pkg.get(k, {}) for k in ["phase_01", "phase_04", "phase_05", "phase_06"]}
        return (
            f"# Phase 08: Visual Language\n\n"
            f"Generate the visual language for the story.\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Generate\n"
            f"- color: color palette and philosophy\n"
            f"- lighting: lighting approach\n"
            f"- composition: composition principles\n"
            f"- textures: texture palette\n"
            f"- atmosphere: overall visual atmosphere\n"
            f"- camera_intent: camera movement philosophy\n"
            f"- lens_suggestions: lens recommendations\n"
            f"- movement_philosophy: camera movement philosophy\n"
            f"- environmental_storytelling: how environment tells the story\n\n"
            f"Respond with valid JSON only. Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> VisualLanguage:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        return VisualLanguage(**data)

    def draft(self, pkg: dict[str, Any]) -> VisualLanguage:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)
