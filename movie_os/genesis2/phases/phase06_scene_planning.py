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
        canon = (pkg.get("constraints", {}) or {}).get("canonical_requirements") or []
        canon_block = ""
        resolution_block = ""
        if canon:
            lines = "\n".join(f"- {c['id']} ({c['category']}): {c['statement']}" for c in canon)
            canon_block = (
                f"## Canonical Episode Requirements (MUST realize ALL)\n"
                f"Your scenes must collectively realize every canonical MUST requirement. "
                f"One scene may realize several; none may be dropped.\n{lines}\n"
            )
            # Generic terminal-resolution contract (mirrors Phase05): when the
            # manifest mandates a RESOLUTION requirement, the scene plan must
            # include a final resolution scene with non-empty semantic fields.
            resolution_reqs = [
                c for c in canon
                if str(c.get("obligation", "")).upper() == "MUST"
                and (
                    str(c.get("category", "")).upper() == "RESOLUTION"
                    or str(c.get("semantic_role", "")).upper() == "RESOLUTION"
                )
            ]
            if resolution_reqs:
                ids = ", ".join(str(c.get("id", "")) for c in resolution_reqs)
                resolution_block = (
                    f"## Terminal Resolution Contract (MANDATORY)\n"
                    f"The manifest mandates a RESOLUTION requirement ({ids}). "
                    f"Your scene plan MUST include a FINAL resolution scene (narrative_beat "
                    f"'resolution') that shows observable movement toward reconnection "
                    f"(behavior or dialogue). This resolution scene is REQUIRED — do not "
                    f"omit it. It MUST have non-empty purpose, conflict/tension, and at "
                    f"least one evidence field (emotion/visual_goal/audio_goal/character_goal/"
                    f"transition). Do not prescribe exact dialogue; require semantic "
                    f"realization. The scene list MUST be: hook, plot, climax, resolution "
                    f"(4 scenes minimum).\n"
                )
        return (
            f"# Phase 06: Scene Planning\n\n"
            f"Plan every scene's purpose, conflict, emotion, and goals.\n\n"
            f"{canon_block}"
            f"{resolution_block}"
            f"## Concise prior phase context\n{json.dumps(concise, indent=2, default=str)}\n\n"
            f"## Required JSON shape\n"
            f"{{\n"
            f'  "purpose": "...",\n'
            f'  "creative_intent": "...",\n'
            f'  "reasoning": "...",\n'
            f'  "confidence": "explicit|confirmed",\n'
            f'  "scenes": [\n'
            f'    {{"scene_number": 1, "title": "...", "purpose": "...", "conflict": "...", "emotion": "...", "visual_goal": "...", "audio_goal": "...", "character_goal": "...", "transition": "...", "duration": "30", "dependencies": [1], "narrative_beat": "hook"}},\n'
            f'    {{"scene_number": 2, "title": "...", "purpose": "...", "conflict": "...", "emotion": "...", "visual_goal": "...", "audio_goal": "...", "character_goal": "...", "transition": "...", "duration": "45", "dependencies": [1], "narrative_beat": "plot"}},\n'
            f'    {{"scene_number": 3, "title": "...", "purpose": "...", "conflict": "...", "emotion": "...", "visual_goal": "...", "audio_goal": "...", "character_goal": "...", "transition": "...", "duration": "30", "dependencies": [2], "narrative_beat": "climax"}}\n'
            f"  ]\n"
            f"}}\n\n"
            f"IMPORTANT: Return scenes with non-empty title and narrative_beat values. Scene 1 must be hook. Scene 2 must be plot. Scene 3 must be climax. "
            f"When a resolution requirement is mandated, you MUST add a FINAL resolution scene (narrative_beat 'resolution') with non-empty purpose, conflict, and at least one evidence field — the scene list must be hook, plot, climax, resolution. Return JSON only."
        )


    def parse_draft(self, response: str) -> KnowledgeObject:
        from ..llm_client import _extract_json
        data = response if isinstance(response, dict) else _extract_json(response)
        scene_data = data.get("scenes", [])
        # Canonicalize: the model may emit scenes nested inside
        # acts[].sequences[].scenes while the flat scenes[] list stays empty.
        # Project nested scenes into the flat authoritative list (act order,
        # then sequence order, then scene order), renumbering collisions with a
        # global counter — mirroring Phase05's canonicalization.
        if not scene_data:
            nested = []
            for act in (data.get("acts", []) or []):
                if not isinstance(act, dict):
                    continue
                for seq in (act.get("sequences", []) or []):
                    if not isinstance(seq, dict):
                        continue
                    for sc in (seq.get("scenes", []) or []):
                        if isinstance(sc, dict):
                            nested.append(dict(sc))
            if nested:
                seen: set[int] = set()
                next_global = 1
                for s in nested:
                    sn = s.get("scene_number")
                    if isinstance(sn, int) and sn in seen:
                        while next_global in seen:
                            next_global += 1
                        s["scene_number"] = next_global
                        sn = next_global
                    if isinstance(sn, int):
                        seen.add(sn)
                scene_data = nested
        scenes = []
        for idx, s in enumerate(scene_data, start=1):
            if hasattr(s, 'model_dump'):
                sdata = s.model_dump()
            else:
                sdata = dict(s)
            if not sdata.get("narrative_beat"):
                sdata["narrative_beat"] = {1: "hook", 2: "plot", 3: "climax"}.get(idx, sdata.get("narrative_beat", ""))
            if not sdata.get("title"):
                sdata["title"] = sdata.get("purpose", "").strip() or f"Scene {sdata.get('scene_number', idx)}"
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
        # Detect whether the frozen manifest mandates a RESOLUTION requirement.
        # Stored on the instance so _validate_specific (which lacks pkg) can
        # fail closed when the resolution scene is missing or too sparse.
        canon = (pkg.get("constraints", {}) or {}).get("canonical_requirements") or []
        self._resolution_required = any(
            str(c.get("obligation", "")).upper() == "MUST"
            and (
                str(c.get("category", "")).upper() == "RESOLUTION"
                or str(c.get("semantic_role", "")).upper() == "RESOLUTION"
            )
            for c in canon
        )
        prompt = self.build_draft_prompt(pkg)
        cfg = getattr(self.llm, "_config", None)
        from ..models import ScenePlanning
        response_format = ScenePlanning.model_json_schema()
        # P0: bounded structured-output fix (same class as Phase05). The local
        # model legally omits optional schema fields, so a title-and-beat-only
        # scene plan passes parse but fails the freeze gate (REQ008 resolution
        # contract). Force the semantic fields to be REQUIRED so the model must
        # emit them. This does not weaken validation — it makes the schema
        # match what the freeze gate already enforces.
        response_format["required"] = ["purpose", "creative_intent", "reasoning", "confidence", "scenes"]
        _defs = response_format.get("$defs", {})
        _sp = _defs.get("ScenePlan")
        if isinstance(_sp, dict):
            _sp["required"] = [
                "scene_number", "title", "purpose", "conflict", "emotion",
                "visual_goal", "audio_goal", "character_goal", "transition",
                "duration", "dependencies", "narrative_beat",
            ]
        if cfg is not None and hasattr(self.llm, "_get_provider"):
            try:
                from ..llm_providers import LLMConfig
                phase_cfg = LLMConfig(**cfg.model_dump()) if hasattr(cfg, "model_dump") else cfg
                # Phase 06 is a bounded structured scene-planning call. It must
                # not inherit a broader global 4096-token ceiling because that
                # materially increases the likelihood of generation runaway.
                # The value below is a phase-specific ceiling chosen from the
                # successful qualification range, not a universal default.
                phase_cfg.max_tokens = min(int(getattr(phase_cfg, "max_tokens", 1536) or 1536), 1536)
                try:
                    response_obj = getattr(self.llm, "generate_json")(prompt, "planner", self.phase_name, self.phase_name, response_format=response_format)
                except TypeError:
                    response_obj = getattr(self.llm, "generate_json")(prompt, cfg, "planner")
                response = json.dumps(response_obj)
            except Exception:
                response = self.llm.generate(prompt, phase_name=self.phase_name, task_key=self.phase_name)
        else:
            response = self.llm.generate(prompt, phase_name=self.phase_name, task_key=self.phase_name)
        knowledge = self.parse_draft(response)
        # P0: bounded beat-coverage repair. The local model sometimes omits a
        # required beat (hook/climax). Re-prompt ONCE with a focused instruction
        # naming the missing beat. Deterministic, bounded (1 repair), does not
        # weaken validation.
        scenes = getattr(knowledge, "scenes", []) or []
        beats = set()
        for sc in scenes:
            b = (getattr(sc, "narrative_beat", "") or "").strip().lower()
            if b:
                beats.add(b)
        # P0: when the frozen manifest mandates a RESOLUTION requirement, the
        # scene plan MUST include a final 'resolution' beat.  The prior code
        # only retried hook/climax, so GENESIS could complete without ever
        # realizing REQ-008 and the freeze gate would (correctly) block on
        # REQUIRED_STORY_BEAT_COVERAGE.  Include 'resolution' in the required
        # set so the bounded retry actually produces the mandated beat.
        required_beats = ["hook", "climax"]
        if getattr(self, "_resolution_required", False):
            required_beats.append("resolution")
        missing = [b for b in required_beats if b not in beats]
        if missing and cfg is not None and hasattr(self.llm, "_get_provider"):
            focused = (
                "# Phase 06: Scene Planning (retry — missing required beat)\n"
                "Your previous plan was missing these required beats: "
                + ", ".join(missing) + ".\n"
                "Return a complete scene plan with a scene for EVERY beat: hook, plot, climax"
                + (", resolution" if "resolution" in missing else "")
                + ". "
                "Scene 1 must be hook, the final scene must be "
                + ("resolution" if "resolution" in missing else "climax")
                + ". "
                "Use the synopsis: " + str(pkg.get("synopsis", ""))[:300] + "\n"
                'Respond with valid JSON only: {"scenes": [{"scene_number": 1, "title": "...", "purpose": "...", "conflict": "...", "emotion": "...", "visual_goal": "...", "audio_goal": "...", "character_goal": "...", "transition": "...", "duration": "30", "dependencies": [1], "narrative_beat": "hook"}, ...]}'
            )
            try:
                phase_cfg.max_tokens = min(int(getattr(phase_cfg, "max_tokens", 1536) or 1536), 1536)
                try:
                    response_obj = getattr(self.llm, "generate_json")(focused, "planner", self.phase_name, f"{self.phase_name}:retry", response_format=response_format)
                except TypeError:
                    response_obj = getattr(self.llm, "generate_json")(focused, cfg, "planner")
                knowledge = self.parse_draft(json.dumps(response_obj))
            except Exception:
                pass
        return knowledge

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
            # ── Terminal-resolution semantic contract (fail closed) ──
            # When the manifest mandates a RESOLUTION requirement, the final
            # resolution scene must carry non-empty semantic fields (purpose,
            # conflict/tension, outcome). A title-and-beat-only resolution scene
            # is too weak to realize the requirement — flag it as an error.
            # The resolution requirement is detected during draft() (which has
            # pkg) and stored on the instance.
            if getattr(self, "_resolution_required", False):
                res_scenes = [
                    s for s in scenes
                    if (s.model_dump() if hasattr(s, 'model_dump') else {}).get("narrative_beat", "").strip().lower() == "resolution"
                ]
                if not res_scenes:
                    issues.append(ValidationIssue(
                        category="structure", severity="error",
                        location=f"{self.phase_name}.narrative_arc",
                        description="Manifest mandates a RESOLUTION requirement but no scene has narrative_beat 'resolution'",
                    ))
                else:
                    for s in res_scenes:
                        sdata = s.model_dump() if hasattr(s, 'model_dump') else {}
                        purpose = sdata.get("purpose")
                        conflict = sdata.get("conflict") or sdata.get("tension")
                        # ScenePlan has no `outcome` field; the evidence fields
                        # are the descriptive fields beyond purpose/conflict.
                        evidence_fields = ("emotion", "visual_goal", "audio_goal", "character_goal", "transition")
                        evidence = [sdata.get(f) for f in evidence_fields]
                        empty = lambda v: v is None or (isinstance(v, str) and not v.strip())
                        if empty(purpose) or empty(conflict) or all(empty(v) for v in evidence):
                            issues.append(ValidationIssue(
                                category="schema_error", severity="error",
                                location=f"{self.phase_name}.scenes[resolution]",
                                description="Resolution scene must have non-empty purpose, conflict/tension, and at least one evidence field (title-and-beat-only is too weak)",
                            ))
        return issues
