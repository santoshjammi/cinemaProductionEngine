"""Phase 02: Story Foundation — expand synopsis into structured story elements."""

from __future__ import annotations

import json
from typing import Any

from ..models import ConfidenceLevel, KnowledgeObject, ValidationIssue
from ..phase_base import PhaseBase


class StoryFoundationPhase(PhaseBase):
    phase_number = 2
    phase_name = "Story Foundation"
    _REQUIRED: list[str] = ["premise", "acts", "story_beats"]

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        prev = pkg.get("phase_01", {})
        synopsis = pkg.get("synopsis", "")
        return (
            f"# Phase 02: Story Foundation\n\n"
            f"Expand the synopsis into a structured story foundation.\n\n"
            f"## Synopsis\n{synopsis}\n\n"
            f"## Creative Understanding\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Generate\n"
            f"- characters: must explicitly include MARK and SARAH whenever the synopsis involves them\n"
            f"- premise: one-sentence premise\n"
            f"- dramatic_question: the CENTRAL question the story poses. The HOOK\n"
            f"  opens it (creates curiosity), the PLOT deepens it (raises stakes),\n"
            f"  and the CLIMAX answers it (the payoff). Phrase it as a question the\n"
            f"  viewer is waiting to have answered, e.g. 'Will Mark tell Sarah the\n"
            f"  truth before his fear destroys their trust?'\n"
            f"- acts: list of acts with name, description, events\n"
            f"- major_events: list of key plot events\n"
            f"- emotional_journey: list of emotional states across the story\n"
            f"- story_beats: list of {{name, description, position, emotional_intent}}\n"
            f"- narrative_rhythm: description of pacing\n"
            f"- foreshadowing: list of foreshadowing elements\n"
            f"- symbolism: list of symbolic elements\n"
            f"- motifs: list of recurring motifs\n\n"
            f"Respond with valid JSON only. Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> KnowledgeObject:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        return self._parse(data)

    @staticmethod
    def _parse(data: dict[str, Any]) -> KnowledgeObject:
        from ..models import StoryFoundation
        return StoryFoundation._from_llm(data)

    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)

    def _review_specific(self, knowledge: KnowledgeObject) -> list[str]:
        issues: list[str] = []
        for field in self._REQUIRED:
            val = getattr(knowledge, field, None)
            # Accept empty lists/strings — validation will catch structural issues
            if val is None:
                issues.append(f"Missing {field} — core to story structure")
            elif isinstance(val, str) and not val.strip():
                issues.append(f"Missing {field} — core to story structure")
        return issues

    def _validate_specific(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:
        from ..models import ValidationIssue  # noqa
        issues: list[ValidationIssue] = []
        premise = getattr(knowledge, "premise", None)
        if premise and len(str(premise).strip()) < 10:
            issues.append(ValidationIssue(
                category="quality", severity="warning",
                location=f"{self.phase_name}.premise",
                description="Premise is too short for a story foundation",
            ))
        acts = getattr(knowledge, "acts", [])
        if isinstance(acts, list) and len(acts) > 0:
            for i, act in enumerate(acts):
                if isinstance(act, dict) and not act.get("name") and not act.get("description"):
                    issues.append(ValidationIssue(
                        category="schema_error", severity="error",
                        location=f"{self.phase_name}.acts[{i}]",
                        description="Act must have name or description",
                    ))
        beats = getattr(knowledge, "story_beats", [])
        if isinstance(beats, list) and len(beats) > 0:
            for i, beat in enumerate(beats):
                if hasattr(beat, 'model_dump'):
                    bdata = beat.model_dump()
                elif isinstance(beat, dict):
                    bdata = beat
                else:
                    continue
                if not bdata.get("name"):
                    issues.append(ValidationIssue(
                        category="schema_error", severity="warning",
                        location=f"{self.phase_name}.story_beats[{i}]",
                        description="Story beat must have a name",
                    ))
        return issues
