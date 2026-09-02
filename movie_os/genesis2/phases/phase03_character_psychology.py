"""Phase 03: Character Psychology — generate all characters with full psychology."""

from __future__ import annotations

import json
from typing import Any

from ..models import ConfidenceLevel, KnowledgeObject, ValidationIssue
from ..phase_base import PhaseBase


class CharacterPsychologyPhase(PhaseBase):
    phase_number = 3
    phase_name = "Character Psychology"
    _REQUIRED: list[str] = ["protagonist"]
    # P0: Phase03 is a bounded structured call. The local model (qwen3:4b)
    # rambles into prose when given an unbounded budget, and the 4096-token
    # global ceiling under a 131072-token context window lets it generate
    # slowly past the 300s timeout. A phase-specific ceiling + structured
    # output keeps it schema-constrained and fast. Chosen from the successful
    # qualification range (mirrors Phase02's proven 1024 budget).
    _OUTPUT_BUDGET = 1024

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        prev = self.slice_context(pkg, ["phase_01", "phase_02"])
        synopsis = pkg.get("synopsis", "")
        return (
            f"# Phase 03: Character Psychology\n\n"
            f"Generate complete character profiles.\n\n"
            f"## Synopsis\n{synopsis}\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Generate for EVERY character\n"
            f"- name, role (protagonist/antagonist/supporting)\n"
            f"- identity, history, goals, fear, need, want\n"
            f"- weakness, strength, internal_conflict, external_conflict\n"
            f"- speech_style, personality, transformation\n\n"
            f"## Required characters\n"
            f"- If the story involves MARK and SARAH, you must produce both.\n"
            f"- Do not omit SARAH just because the synopsis foregrounds MARK.\n"
            f"- Keep SARAH as a distinct supporting character with her own goals, fear, need, and voice.\n\n"
            f"Respond with JSON: {{ protagonist: {{...}}, antagonist: {{...}} or null, supporting_characters: [...] }}\n"
            f"Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> KnowledgeObject:
        from ..llm_client import _extract_json
        data = response if isinstance(response, dict) else _extract_json(response)
        return self._parse(data)

    @staticmethod
    def _parse(data: dict[str, Any]) -> KnowledgeObject:
        from ..models import Character, CharacterPsychology

        def _normalize_char(c: dict) -> dict:
            c = dict(c)
            if isinstance(c.get("goals"), str):
                c["goals"] = [c["goals"]]
            # Coerce None to empty string for all string fields
            for k, v in list(c.items()):
                if v is None:
                    c[k] = ""
            # Ensure all required string fields exist
            for field in ("name", "role", "identity", "history", "fear", "need", "want",
                          "weakness", "strength", "internal_conflict", "external_conflict",
                          "speech_style", "personality", "transformation"):
                if field not in c:
                    c[field] = ""
            return c

        proto_data = _normalize_char(data.get("protagonist", {}))
        proto = Character(**proto_data)
        antag_d = data.get("antagonist")
        antag = Character(**_normalize_char(antag_d)) if antag_d else None
        supporting = [Character(**_normalize_char(c)) for c in data.get("supporting_characters", [])]
        return CharacterPsychology(
            protagonist=proto, antagonist=antag, supporting_characters=supporting,
            purpose=data.get("purpose", ""), creative_intent=data.get("creative_intent", ""),
            reasoning=data.get("reasoning", ""), confidence=data.get("confidence", "inferred"),
        )

    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        prompt = self.build_draft_prompt(pkg)
        from ..models import CharacterPsychology
        response_format = CharacterPsychology.model_json_schema()
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
        # Must have a protagonist with identity
        protog = getattr(knowledge, "protagonist", None)
        if not protog or not hasattr(protog, 'name') or not protog.name:
            issues.append("Missing protagonist — central character required")
        elif not hasattr(protog, 'identity') or not protog.identity:
            issues.append("Protagonist missing identity — who are they?")
        elif not hasattr(protog, 'goals') or not getattr(protog, "goals", None):
            issues.append("Protagonist missing goals — what do they want?")

        # Antagonist is optional but encouraged
        antag = getattr(knowledge, "antagonist", None)
        if protog and not antag:
            issues.append("No antagonist defined — consider adding an opposing force")

        supported = getattr(knowledge, "supporting_characters", [])
        if isinstance(supported, list) and len(supported) > 0:
            for i, sc in enumerate(supported):
                sname = getattr(sc, 'name', None)
                if not (isinstance(sname, str) and sname.strip()):
                    issues.append(f"Supporting character[{i}] missing name")
        return issues

    def _validate_specific(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:
        from ..models import ValidationIssue  # noqa
        issues: list[ValidationIssue] = []
        protog = getattr(knowledge, "protagonist", None)
        if isinstance(protog, dict):
            pname = protog.get("name")
        elif hasattr(protog, 'name'):
            pname = getattr(protog, 'name', '')
        else:
            pname = None

        if not (isinstance(pname, str) and pname.strip()):
            issues.append(ValidationIssue(
                category="schema_error", severity="warning",
                location=f"{self.phase_name}.protagonist.name",
                description="Protagonist name is required",
            ))
        return issues
