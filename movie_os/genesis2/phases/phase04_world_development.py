"""Phase 04: World Development — build setting, rules, atmosphere."""

from __future__ import annotations

import json
from typing import Any

from ..models import ConfidenceLevel, KnowledgeObject, ValidationIssue
from ..phase_base import PhaseBase


class WorldDevelopmentPhase(PhaseBase):
    phase_number = 4
    phase_name = "World Development"
    _REQUIRED: list[str] = ["environment", "rules"]
    # P0: Phase04 is a bounded structured call. The local model (qwen3:4b)
    # rambles into prose when given an unbounded budget, and the 4096-token
    # global ceiling under a 131072-token context window lets it generate
    # slowly past the 300s timeout. A phase-specific ceiling + structured
    # output keeps it schema-constrained and fast. Chosen from the successful
    # qualification range (mirrors Phase02/03/10's proven bounded budgets).
    _OUTPUT_BUDGET = 512

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        prev = self.slice_context(pkg, ["phase_01", "phase_02", "phase_03"])
        synopsis = pkg.get("synopsis", "")
        return (
            f"# Phase 04: World Development\n\n"
            f"Generate the world the story inhabits.\n\n"
            f"## Synopsis\n{synopsis}\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Generate\n"
            f"- history: world backstory\n"
            f"- culture: cultural norms and values\n"
            f"- technology: technology level\n"
            f"- environment: physical environment\n"
            f"- rules: list of world rules\n"
            f"- architecture: architectural style\n"
            f"- economy: economic system\n"
            f"- politics: political structure\n"
            f"- timeline: list of key historical events\n"
            f"- social_structure: social hierarchy\n\n"
            f"Respond with valid JSON only. Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> KnowledgeObject:
        from ..llm_client import _extract_json
        data = response if isinstance(response, dict) else _extract_json(response)
        return self._parse(data)

    @staticmethod
    def _parse(data: dict[str, Any]) -> KnowledgeObject:
        from ..models import WorldDevelopment
        return WorldDevelopment(**data)

    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        prompt = self.build_draft_prompt(pkg)
        from ..models import WorldDevelopment
        response_format = WorldDevelopment.model_json_schema()
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
        return self.parse_draft(response)

    def _review_specific(self, knowledge: KnowledgeObject) -> list[str]:
        issues: list[str] = []
        for field in self._REQUIRED:
            val = getattr(knowledge, field, None)
            if val == "" or val is None:
                issues.append(f"Missing {field} — core to world building")
        return issues

    def _validate_specific(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:  # noqa
        from ..models import ValidationIssue  # noqa
        issues: list[ValidationIssue] = []
        rules = getattr(knowledge, "rules", [])
        if isinstance(rules, list) and len(rules) > 0:
            for i, rule in enumerate(rules):
                if not (isinstance(rule, str) and rule.strip()):
                    issues.append(ValidationIssue(
                        category="schema_error", severity="warning",
                        location=f"{self.phase_name}.rules[{i}]",
                        description="World rule must be non-empty",
                    ))
        return issues
