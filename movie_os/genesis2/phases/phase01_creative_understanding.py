"""Phase 01: Creative Understanding — understand what the story actually means."""

from __future__ import annotations

import json
from typing import Any

from ..models import ConfidenceLevel, KnowledgeObject, ValidationIssue
from ..phase_base import PhaseBase


class CreativeUnderstandingPhase(PhaseBase):
    phase_number = 1
    phase_name = "Creative Understanding"
    _REQUIRED: list[str] = [
        "theme", "genre", "mood", "core_question", "audience"
    ]

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        synopsis = pkg.get("synopsis", "")
        constraints = pkg.get("constraints", {})
        return (
            f"# Phase 01: Creative Understanding\n\n"
            f"Understand what the story actually means.\n\n"
            f"## Synopsis\n{synopsis}\n\n"
            f"## Constraints\n{json.dumps(constraints, indent=2)}\n\n"
            f"## Required JSON shape\n"
            f"{{\n"
            f'  "purpose": "...",\n'
            f'  "creative_intent": "...",\n'
            f'  "reasoning": "...",\n'
            f'  "confidence": "explicit|confirmed",\n'
            f'  "theme": "...",\n'
            f'  "genre": "...",\n'
            f'  "subgenre": "...",\n'
            f'  "audience": "...",\n'
            f'  "mood": "...",\n'
            f'  "core_question": "...",\n'
            f'  "message": "...",\n'
            f'  "conflict": "...",\n'
            f'  "transformation": "...",\n'
            f'  "success_criteria": ["..."]\n'
            f"}}\n\n"
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
            f"IMPORTANT: Do not leave any required field blank. Return valid JSON only."
        )


    def parse_draft(self, response: str) -> KnowledgeObject:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        return self._parse(data)

    @staticmethod
    def _parse(data: dict[str, Any]) -> KnowledgeObject:
        """Parse dict into the correct subtype depending on shape."""
        # If it has a 'protagonist' key, dispatch to character phase (for multi-phase mocks)
        if data.get("protagonist"):
            from ..models import Character, CharacterPsychology
            proto_data = data["protagonist"]
            # Normalize goals to list if it's a string
            if isinstance(proto_data.get("goals"), str):
                proto_data["goals"] = [proto_data["goals"]]
            proto = Character(**proto_data)
            antag_d = data.get("antagonist")
            antag = Character(**antag_d) if antag_d else None
            supporting = [Character(**c) for c in data.get("supporting_characters", [])]
            return CharacterPsychology(protagonist=proto, antagonist=antag, supporting_characters=supporting)
        from ..models import CreativeUnderstanding
        # Normalize fields that might come as lists from real LLM
        cleaned = dict(data)
        if isinstance(cleaned.get("conflict"), list):
            cleaned["conflict"] = str(cleaned["conflict"])
        if isinstance(cleaned.get("success_criteria"), list):
            cleaned["success_criteria"] = [
                str(c) if isinstance(c, dict) else c
                for c in cleaned["success_criteria"]
            ]
        return CreativeUnderstanding(**cleaned)

    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)

    # ── Phase-specific review ───────────────────────────────

    def _review_specific(self, knowledge: KnowledgeObject) -> list[str]:
        issues: list[str] = []
        for field in self._REQUIRED:
            val = getattr(knowledge, field, None)
            if not val:
                issues.append(f"Missing {field} — essential for creative meaning")
        conf = getattr(knowledge, "confidence", None)
        if conf and conf not in (ConfidenceLevel.EXPLICIT, ConfidenceLevel.CONFIRMED):
            issues.append(
                f"Confidence '{conf}' is too low for Creative Understanding"
            )
        sc = getattr(knowledge, "success_criteria", [])
        if sc:
            if isinstance(sc, str):
                pass  # single value is valid
            elif hasattr(sc, "__iter__") and not isinstance(sc, str):
                if len(list(sc)) < 1:
                    issues.append("success_criteria must list at least one item")
        return issues

    # ── Phase-specific validate ─────────────────────────────

    def _validate_specific(self, knowledge: KnowledgeObject) -> list["ValidationIssue"]:
        from ..models import ValidationIssue
        issues: list[ValidationIssue] = []
        theme = getattr(knowledge, "theme", None)
        if topic_is_empty(theme):
            issues.append(ValidationIssue(
                category="schema_error", severity="error",
                location=f"{self.phase_name}.theme",
                description="theme is required for Creative Understanding",
            ))
        elif len(str(theme).strip()) < 3:
            issues.append(ValidationIssue(
                category="schema_error", severity="warning",
                location=f"{self.phase_name}.theme",
                description="theme is too short (min 3 chars)",
            ))
        genre = getattr(knowledge, "genre", None)
        if genre and not str(genre).strip():
            issues.append(ValidationIssue(
                category="schema_error", severity="error",
                location=f"{self.phase_name}.genre",
                description="genre must be non-empty",
            ))
        return issues

    # ── Help / imports ──────────────────────────────────────

    def confidence_ok(self, confidence):  # noqa: ANN201
        """Return True if confidence meets the threshold."""
        allowed = {ConfidenceLevel.EXPLICIT, ConfidenceLevel.CONFIRMED}
        return confidence in allowed


def topic_is_empty(val):  # noqa: ANN201
    """Quick check for empty/missing text fields."""
    if isinstance(val, str):
        return not val.strip()
    return val is None
