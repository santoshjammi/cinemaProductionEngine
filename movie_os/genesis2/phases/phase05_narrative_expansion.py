"""Phase 05: Narrative Expansion — convert story into acts, sequences, scenes."""

from __future__ import annotations

import json
from typing import Any

from ..models import ConfidenceLevel, KnowledgeObject, ValidationIssue
from ..phase_base import PhaseBase


class NarrativeExpansionPhase(PhaseBase):
    phase_number = 5
    phase_name = "Narrative Expansion"
    _REQUIRED: list[str] = ["acts", "scenes"]

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        prev = self.slice_context(pkg, ["phase_01", "phase_02", "phase_03", "phase_04"])
        synopsis = pkg.get("synopsis", "")
        return (
            f"# Phase 05: Narrative Expansion\n\n"
            f"Convert the story into acts, sequences, and scenes.\n\n"
            f"## Synopsis\n{synopsis}\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Generate\n"
            f"- acts: list of {{name, description, sequences}}\n"
            f"- sequences: list of {{name, act, scenes}}\n"
            f"- scenes: list of {{scene_number, act, sequence, objective, conflict, outcome, emotional_objective, narrative_beat}}\n"
            f"  where narrative_beat is one of: hook | plot | turning_point | climax\n"
            f"  - hook: the opening scene that POSES the dramatic question and creates curiosity\n"
            f"  - plot: scenes that DEEPEN the question and raise stakes\n"
            f"  - turning_point: the 'all is lost' moment right before the climax where the answer seems impossible\n"
            f"  - climax: the final scene that ANSWERS the dramatic question\n"
            f"  Ensure the arc is complete: at least one hook, several plot, one turning_point, one climax.\n\n"
            f"Respond with valid JSON only. Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> KnowledgeObject:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        scene_data = data.pop("scenes", [])
        scenes = []
        for s in scene_data:
            if hasattr(s, 'model_dump'):
                scenes.append(s)
            else:
                from ..models import Scene
                scenes.append(Scene(**s))
        from ..models import NarrativeExpansion
        return NarrativeExpansion(**data, scenes=scenes)

    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)

    def _review_specific(self, knowledge: KnowledgeObject) -> list[str]:
        issues: list[str] = []
        for field in self._REQUIRED:
            val = getattr(knowledge, field, None)
            if val == "" or val is None:
                issues.append(f"Missing {field} — essential narrative structure")
        return issues

    def _validate_specific(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:  # noqa
        from ..models import ValidationIssue  # noqa
        from ..models import Scene as ModelScene
        issues: list[ValidationIssue] = []
        scenes = getattr(knowledge, "scenes", [])
        if isinstance(scenes, list) and len(scenes) > 0:
            for i, scene in enumerate(scenes):
                sdata = scene.model_dump() if hasattr(scene, 'model_dump') else scene
                sobj = getattr(scene, '__dict__', None)
                if isinstance(sdata, dict):
                    s_num = sdata.get("scene_number")
                elif isinstance(scene, ModelScene):
                    s_num = scene.scene_number
                else:
                    s_num = sdata.get("scene_number") if isinstance(sdata, dict) else None

                if s_num is None or (isinstance(s_num, int) and s_num < 1):
                    issues.append(ValidationIssue(
                        category="schema_error", severity="warning",
                        location=f"{self.phase_name}.scenes[{i}]",
                        description="Scene must have a valid scene_number >= 1",
                    ))
        return issues
