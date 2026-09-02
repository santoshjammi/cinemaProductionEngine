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
    # P0: Phase08 is a bounded structured call. The local model (qwen3:4b)
    # rambles into prose when given an unbounded budget, and the 4096-token
    # global ceiling under a 131072-token context window lets it generate
    # slowly past the 300s timeout. A phase-specific ceiling + structured
    # output keeps it schema-constrained and fast. Chosen from the successful
    # qualification range (mirrors Phase02/03/04/10's proven bounded budgets).
    _OUTPUT_BUDGET = 512

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
        data = response if isinstance(response, dict) else _extract_json(response)
        return self._parse(data)

    @staticmethod
    def _parse(data: dict[str, Any]) -> KnowledgeObject:
        from ..models import VisualLanguage
        return VisualLanguage(**data)

    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        prompt = self.build_draft_prompt(pkg)
        from ..models import VisualLanguage
        response_format = VisualLanguage.model_json_schema()
        generator = getattr(self.llm, "generate_json")
        config = getattr(self.llm, "_config", None)
        if config is not None:
            original_max_tokens = config.max_tokens
            config.max_tokens = self._OUTPUT_BUDGET
            try:
                try:
                    response = generator(prompt, "planner", self.phase_name, self.phase_name, response_format=response_format)
                except TypeError:
                    response = generator(prompt, config, "planner")
            finally:
                config.max_tokens = original_max_tokens
        else:
            try:
                response = generator(prompt, "planner", self.phase_name, self.phase_name, response_format=response_format)
            except TypeError:
                response = generator(prompt)
        knowledge = self.parse_draft(response)
        # P0-01/20 repair: the local model sometimes returns an empty or partial
        # VisualLanguage. Retry once with a focused prompt when a required field
        # (visual OR base purpose/creative_intent/reasoning) is missing.
        # Deterministic, repairs the current phase only.
        if any(not str(getattr(knowledge, f, "") or "").strip() for f in self._REQUIRED) or \
           any(not str(getattr(knowledge, f, "") or "").strip() for f in ("purpose", "creative_intent", "reasoning")):
            focused = (
                "# Phase 08: Visual Language (retry — required fields missing)\n"
                "Provide complete, concrete values for these EXACT keys. Use the "
                "synopsis: " + str(pkg.get("synopsis", ""))[:300] + "\n"
                'Respond with valid JSON only: {"purpose": "...", "creative_intent": "...", '
                '"reasoning": "...", "color": "...", "lighting": "...", '
                '"composition": "...", "textures": "...", "atmosphere": "...", '
                '"camera_intent": "...", "lens_suggestions": "...", '
                '"movement_philosophy": "...", "environmental_storytelling": "..."}'
            )
            try:
                if config is not None:
                    config.max_tokens = self._OUTPUT_BUDGET
                    try:
                        knowledge = self.parse_draft(generator(focused, "planner", self.phase_name, f"{self.phase_name}:retry", response_format=response_format))
                    except TypeError:
                        knowledge = self.parse_draft(generator(focused, config, "planner"))
                    finally:
                        config.max_tokens = original_max_tokens
                else:
                    knowledge = self.parse_draft(generator(focused, "planner", self.phase_name, f"{self.phase_name}:retry", response_format=response_format))
            except Exception:
                pass
        return knowledge

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
