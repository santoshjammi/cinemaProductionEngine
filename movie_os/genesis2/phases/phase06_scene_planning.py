"""Phase 06: Scene Planning — plan every scene's purpose, conflict, emotion, goals."""

from __future__ import annotations

import json
from typing import Any

from ..models import ConfidenceLevel, KnowledgeObject, ValidationIssue
from ..phase_base import PhaseBase


class ScenePlanningPhase(PhaseBase):
    phase_number = 6
    phase_name = "Scene Planning"
    _REQUIRED: list[str] = ["scenes"]

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        prev = self.slice_context(pkg, ["phase_01", "phase_02", "phase_05"])
        phase_01 = prev.get("phase_01", {}) if isinstance(prev, dict) else {}
        phase_02 = prev.get("phase_02", {}) if isinstance(prev, dict) else {}
        phase_05 = prev.get("phase_05", {}) if isinstance(prev, dict) else {}
        phase_03 = pkg.get("phase_03", {}) or {}
        phase_04 = pkg.get("phase_04", {}) or {}
        concise = {
            "phase_01": {
                "theme": phase_01.get("theme", ""),
                "genre": phase_01.get("genre", ""),
                "mood": phase_01.get("mood", ""),
                "core_question": phase_01.get("core_question", ""),
                "conflict": phase_01.get("conflict", ""),
                "transformation": phase_01.get("transformation", ""),
            },
            "phase_02": {
                "premise": phase_02.get("premise", ""),
                "dramatic_question": phase_02.get("dramatic_question", ""),
                "acts": phase_02.get("acts", [])[:2] if isinstance(phase_02.get("acts", []), list) else [],
                "story_beats": [
                    {
                        "name": b.get("name", ""),
                        "position": b.get("position", ""),
                        "emotional_intent": b.get("emotional_intent", ""),
                    }
                    for b in (phase_02.get("story_beats", []) or [])[:3]
                    if isinstance(b, dict)
                ],
            },
            "phase_03": {
                "protagonist": (phase_03.get("protagonist") or {}).get("name", "") if isinstance(phase_03, dict) else "",
                "supporting_characters": [c.get("name", "") for c in (phase_03.get("supporting_characters", []) or []) if isinstance(c, dict)],
            },
            "phase_04": {
                "setting": phase_04.get("setting", ""),
                "culture": phase_04.get("culture", ""),
                "social_structure": phase_04.get("social_structure", ""),
            },
            "phase_05": {
                "narrative_rhythm": phase_05.get("narrative_rhythm", ""),
                "major_turns": phase_05.get("major_turns", [])[:3] if isinstance(phase_05.get("major_turns", []), list) else [],
                "scene_goals": phase_05.get("scene_goals", [])[:3] if isinstance(phase_05.get("scene_goals", []), list) else [],
            },
        }
        return (
            f"# Phase 06: Scene Planning\n\n"
            f"Plan every scene's purpose, conflict, emotion, and goals.\n\n"
            f"## Concise prior phase context\n{json.dumps(concise, indent=2, default=str)}\n\n"
            f"## Required JSON shape\n"
            f"{{\n"
            f'  "purpose": "...",\n'
            f'  "creative_intent": "...",\n'
            f'  "reasoning": "...",\n'
            f'  "confidence": "explicit|confirmed",\n'
            f'  "scenes": [\n'
            f'    {{"scene_number": 1, "purpose": "...", "conflict": "...", "emotion": "...", "visual_goal": "...", "audio_goal": "...", "character_goal": "...", "transition": "...", "duration": "30", "dependencies": [1], "narrative_beat": "hook"}},\n'
            f'    {{"scene_number": 2, "purpose": "...", "conflict": "...", "emotion": "...", "visual_goal": "...", "audio_goal": "...", "character_goal": "...", "transition": "...", "duration": "45", "dependencies": [1], "narrative_beat": "plot"}},\n'
            f'    {{"scene_number": 3, "purpose": "...", "conflict": "...", "emotion": "...", "visual_goal": "...", "audio_goal": "...", "character_goal": "...", "transition": "...", "duration": "30", "dependencies": [2], "narrative_beat": "climax"}}\n'
            f"  ]\n"
            f"}}\n\n"
            f"IMPORTANT: Return 3 scenes with non-empty narrative_beat values. Scene 1 must be hook. Scene 2 must be plot. Scene 3 must be climax. Return JSON only."
        )


    def parse_draft(self, response: str) -> KnowledgeObject:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        scene_data = data.get("scenes", [])
        scenes = []
        for idx, s in enumerate(scene_data, start=1):
            if hasattr(s, 'model_dump'):
                sdata = s.model_dump()
            else:
                sdata = dict(s)
            if not sdata.get("narrative_beat"):
                sdata["narrative_beat"] = {1: "hook", 2: "plot", 3: "climax"}.get(idx, sdata.get("narrative_beat", ""))
            if "duration" in sdata and sdata["duration"] is not None:
                sdata["duration"] = str(sdata["duration"])
            if "dependencies" in sdata and sdata["dependencies"] is not None:
                deps = sdata["dependencies"]
                if isinstance(deps, list):
                    normalized = []
                    for d in deps:
                        if isinstance(d, dict):
                            value = d.get("event") or d.get("name") or d.get("value") or d.get("id") or d
                            normalized.append(str(value))
                        else:
                            normalized.append(str(d))
                    sdata["dependencies"] = normalized
                elif isinstance(deps, dict):
                    value = deps.get("event") or deps.get("name") or deps.get("value") or deps.get("id") or deps
                    sdata["dependencies"] = [str(value)]
                else:
                    sdata["dependencies"] = [str(deps)]
            from ..models import ScenePlan
            scenes.append(ScenePlan(**sdata))
        from ..models import ScenePlanning
        return ScenePlanning(scenes=scenes, purpose=data.get("purpose", ""), creative_intent=data.get("creative_intent", ""), reasoning=data.get("reasoning", ""), confidence=data.get("confidence", "inferred"))

    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        prompt = self.build_draft_prompt(pkg)
        cfg = getattr(self.llm, "_config", None)
        if cfg is not None:
            try:
                from ..llm_providers import LLMConfig
                phase_cfg = LLMConfig(**cfg.model_dump()) if hasattr(cfg, "model_dump") else cfg
                phase_cfg.max_tokens = max(int(getattr(phase_cfg, "max_tokens", 0) or 0), 1536)
                response = self.llm._get_provider().generate(prompt, phase_cfg)  # type: ignore[attr-defined]
            except Exception:
                response = self.llm.generate(prompt)
        else:
            response = self.llm.generate(prompt)
        return self.parse_draft(response)

    def _review_specific(self, knowledge: KnowledgeObject) -> list[str]:
        issues: list[str] = []
        scenes = getattr(knowledge, "scenes", [])
        if not scenes or (isinstance(scenes, list) and len(scenes) == 0):
            issues.append("No scenes planned — minimum one scene required")
        return issues

    def _validate_specific(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:  # noqa
        from ..models import ValidationIssue  # noqa
        issues: list[ValidationIssue] = []
        scenes = getattr(knowledge, "scenes", [])
        if isinstance(scenes, list):
            for i, scene in enumerate(scenes):
                sdata = scene.model_dump() if hasattr(scene, 'model_dump') else {}
                purpose = sdata.get("purpose") if isinstance(sdata, dict) else None
                if not (isinstance(purpose, str) and purpose.strip()):
                    issues.append(ValidationIssue(
                        category="schema_error", severity="warning",
                        location=f"{self.phase_name}.scenes[{i}].purpose",
                        description="Scene purpose is required",
                    ))
            # ── Dramatic-arc completeness: the HOOK/PLOT/CLIMAX framework ──
            beats = set()
            for scene in scenes:
                sdata = scene.model_dump() if hasattr(scene, 'model_dump') else {}
                if isinstance(sdata, dict):
                    b = (sdata.get("narrative_beat") or "").strip().lower()
                    if b:
                        beats.add(b)
            # A complete arc needs at least a hook and a climax; plot deepens it.
            if "hook" not in beats:
                issues.append(ValidationIssue(
                    category="structure", severity="error",
                    location=f"{self.phase_name}.narrative_arc",
                    description="No 'hook' scene — the film must open by posing the dramatic question",
                ))
            if "climax" not in beats:
                issues.append(ValidationIssue(
                    category="structure", severity="error",
                    location=f"{self.phase_name}.narrative_arc",
                    description="No 'climax' scene — the film must answer the dramatic question",
                ))
            if "plot" not in beats:
                issues.append(ValidationIssue(
                    category="structure", severity="warning",
                    location=f"{self.phase_name}.narrative_arc",
                    description="No 'plot' scenes — the dramatic question is not deepened",
                ))
        return issues
