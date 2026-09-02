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
        constraints = pkg.get("constraints", {}) or {}
        canon = constraints.get("canonical_requirements") or []
        canon_block = ""
        resolution_block = ""
        if canon:
            lines = "\n".join(
                f"- {c['id']} ({c['category']}): {c['statement']}" for c in canon
            )
            canon_block = (
                f"## Canonical Episode Requirements (MUST realize ALL)\n"
                f"Your acts/sequences/scenes must collectively realize every canonical "
                f"MUST requirement. One scene may realize several; none may be dropped.\n{lines}\n"
            )
            # Generic terminal-resolution contract: when the frozen manifest
            # mandates a RESOLUTION requirement (category or semantic_role
            # RESOLUTION, obligation MUST), the arc must NOT terminate on
            # revelation/confrontation/climax alone. The final scene (or final
            # arc segment) must show an observable movement toward resolution.
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
                    f"## Terminal Resolution Contract\n"
                    f"The manifest mandates a RESOLUTION requirement ({ids}). "
                    f"Your arc MUST NOT end only on revelation, confrontation, or climax. "
                    f"The FINAL scene (or final arc segment) must show an observable "
                    f"relational change — movement toward reconnection — via behavior "
                    f"or dialogue that supports resolution. Do not prescribe exact "
                    f"dialogue; require semantic realization. The final scene's "
                    f"narrative_beat should be 'resolution' (or a beat that clearly "
                    f"realizes the resolution requirement).\n"
                )
        return (
            f"# Phase 05: Narrative Expansion\n\n"
            f"Convert the story into acts, sequences, and scenes.\n\n"
            f"## Synopsis\n{synopsis}\n\n"
            f"{canon_block}"
            f"{resolution_block}"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Generate — the acts/sequences/scenes structure is the PRIMARY output\n"
            f"Your response MUST contain the full narrative structure. The metadata fields "
            f"(purpose, creative_intent, reasoning, confidence) are SECONDARY and must be "
            f"short — one sentence each at most. Do NOT spend the response on reasoning; "
            f"spend it on the structure.\n"
            f"- acts: list of {{name, description, sequences}}\n"
            f"- sequences: list of {{name, act, scenes}}\n"
            f"- scenes: list of {{scene_number, act, sequence, objective, conflict, outcome, emotional_objective, narrative_beat}}\n"
            f"  where narrative_beat is one of: hook | plot | turning_point | climax | resolution\n"
            f"  - hook: the opening scene that POSES the dramatic question and creates curiosity\n"
            f"  - plot: scenes that DEEPEN the question and raise stakes\n"
            f"  - turning_point: the 'all is lost' moment right before the climax where the answer seems impossible\n"
            f"  - climax: the scene that ANSWERS the dramatic question\n"
            f"  - resolution: the final scene that shows the relational change / movement toward reconnection\n"
            f"  Ensure the arc is complete: at least one hook, several plot, one turning_point, one climax, "
            f"and (when a resolution requirement is mandated) a final resolution scene.\n"
            f"  Explicitly realize REQ-005 with a clear escalation beat where Mark withdraws further and the relational distance worsens.\n\n"
            f"Respond with valid JSON only. The acts/sequences/scenes arrays MUST be populated — "
            f"never empty. Keep purpose, creative_intent, reasoning, confidence to one short sentence each."
        )

    def parse_draft(self, response: str | dict[str, Any]) -> KnowledgeObject:
        if isinstance(response, dict):
            data = dict(response)
        else:
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
        knowledge = NarrativeExpansion(**data, scenes=scenes)
        # Canonicalize: project nested acts[].sequences[].scenes into the flat
        # authoritative scenes[] before validation.  The model may emit scenes
        # only inside the nested structure; the flat list is the authoritative
        # runtime collection the validator and downstream phases consume.
        return self.canonicalize_narrative_scenes(knowledge)

    @staticmethod
    def _scene_from_dict(s: dict[str, Any]):
        from ..models import Scene
        return Scene(**s)

    def canonicalize_narrative_scenes(self, knowledge: KnowledgeObject) -> KnowledgeObject:
        """Deterministically project nested acts[].sequences[].scenes into the
        flat authoritative scenes[] list.

        Cases:
          A) flat empty, nested nonempty  -> populate flat from nested (act, seq, scene order)
          B) flat nonempty, nested empty  -> preserve flat
          C) flat nonempty, nested nonempty -> reconcile by stable scene identity;
             merge additional nested scenes; FAIL on conflicting same scene_id
          D) both empty -> leave empty (Phase05 validation will fail closed)

        No LLM, no creative mutation.  Provenance (source act/sequence) is
        preserved on each projected scene.
        """
        from ..models import Scene
        flat = list(getattr(knowledge, "scenes", []) or [])
        acts = getattr(knowledge, "acts", []) or []

        # Collect nested scenes in deterministic order: act order, then
        # sequence order, then scene order.
        nested: list[dict[str, Any]] = []
        for act in acts:
            if not isinstance(act, dict):
                continue
            act_name = str(act.get("name", "") or "")
            for seq in (act.get("sequences", []) or []):
                if not isinstance(seq, dict):
                    continue
                seq_name = str(seq.get("name", "") or "")
                for sc in (seq.get("scenes", []) or []):
                    if not isinstance(sc, dict):
                        continue
                    sc = dict(sc)
                    sc.setdefault("_source_act", act_name)
                    sc.setdefault("_source_sequence", seq_name)
                    nested.append(sc)

        # Case D: both empty -> leave as-is (validation fails closed).
        if not flat and not nested:
            return knowledge

        # Case B: flat nonempty, nested empty -> preserve flat.
        if flat and not nested:
            return knowledge

        # Case A: flat empty, nested nonempty -> populate flat from nested.
        # Nested scenes may collide on scene_number across acts (each act
        # restarts numbering at 1).  Renumber deterministically with a global
        # counter so every projected scene has a unique stable id, matching the
        # bridge's act-flattening behavior.
        if not flat and nested:
            seen_ids: set[int] = set()
            next_global = 1
            projected = []
            for s in nested:
                sn = s.get("scene_number")
                if isinstance(sn, int) and sn in seen_ids:
                    # Collision: assign a fresh global id.
                    while next_global in seen_ids:
                        next_global += 1
                    s = dict(s)
                    s["scene_number"] = next_global
                    sn = next_global
                if isinstance(sn, int):
                    seen_ids.add(sn)
                projected.append(self._scene_from_dict(s))
            knowledge.scenes = projected
            return knowledge

        # Case C: both nonempty -> reconcile by stable scene identity.
        # The FLAT scenes[] is the authoritative runtime collection
        # (CANONICAL_SCENE_LAW).  When flat and nested conflict for the same
        # scene_id, the flat (authoritative) representation WINS and the
        # conflicting nested scene is dropped — the model may emit an
        # inconsistent duplicate, but the authoritative flat list is what
        # downstream phases and the bridge consume.  Only merge non-empty
        # values from nested when flat is missing a field.
        _SEMANTIC_FIELDS = ("objective", "conflict", "outcome", "emotional_objective", "narrative_beat")
        flat_map: dict[int, Scene] = {}
        for sc in flat:
            sn = getattr(sc, "scene_number", None)
            if isinstance(sn, int):
                flat_map[sn] = sc
        merged: dict[int, Scene] = dict(flat_map)
        for s in nested:
            sn = s.get("scene_number")
            if not isinstance(sn, int):
                continue
            if sn in merged:
                existing = merged[sn]
                existing_dump = existing.model_dump() if hasattr(existing, "model_dump") else {}
                # Merge non-empty nested values into flat where flat is missing
                # a field.  On a genuine conflict (both non-empty and different),
                # the flat (authoritative) value wins; the nested duplicate is
                # dropped.
                for k in _SEMANTIC_FIELDS:
                    fv = existing_dump.get(k)
                    nv = s.get(k)
                    fv_empty = fv is None or (isinstance(fv, str) and not fv.strip())
                    nv_empty = nv is None or (isinstance(nv, str) and not str(nv).strip())
                    if fv_empty and not nv_empty:
                        setattr(existing, k, nv)
                merged[sn] = existing
            else:
                merged[sn] = self._scene_from_dict(s)
        # Preserve deterministic order: flat order first, then any additional
        # nested scenes in nested order.
        ordered = list(flat_map.values())
        for s in nested:
            sn = s.get("scene_number")
            if isinstance(sn, int) and sn not in flat_map:
                ordered.append(merged[sn])
        knowledge.scenes = ordered
        return knowledge

    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        prompt = self.build_draft_prompt(pkg)
        cfg = getattr(self.llm, "_config", None)
        from ..models import NarrativeExpansion
        response_format = NarrativeExpansion.model_json_schema()
        # The base schema marks acts/sequences/scenes optional (default_factory),
        # so the model legally omits them and emits only metadata. Require the
        # structure fields so the structured-output path forces them to be present.
        response_format["required"] = [
            "purpose", "creative_intent", "reasoning", "confidence",
            "acts", "sequences", "scenes",
        ]
        bounded_tokens = 1536
        if cfg is not None and hasattr(self.llm, "_get_provider"):
            try:
                from ..llm_providers import LLMConfig
                phase_cfg = LLMConfig(**cfg.model_dump()) if hasattr(cfg, "model_dump") else cfg
                # Phase 05 is the first large structural expansion pass. Keep it
                # bounded so it does not inherit the broad global ceiling and run
                # away, but leave enough room for the full acts/sequences/scenes
                # structure (the required schema forces the model to emit it).
                bounded_tokens = min(int(getattr(phase_cfg, "max_tokens", 0) or 0), 2560) or 2560
                original_tokens = getattr(cfg, "max_tokens", bounded_tokens)
                cfg.max_tokens = bounded_tokens
                try:
                    response_obj = getattr(self.llm, "generate_json")(prompt, "planner", self.phase_name, self.phase_name, response_format=response_format)
                except TypeError:
                    response_obj = getattr(self.llm, "generate_json")(prompt, cfg, "planner")
                finally:
                    cfg.max_tokens = original_tokens
                response = response_obj
            except Exception:
                response = self.llm.generate(prompt, phase_name=self.phase_name, task_key=self.phase_name)
        else:
            response = self.llm.generate(prompt, phase_name=self.phase_name, task_key=self.phase_name)
        knowledge = self.parse_draft(response)
        # P0: bounded targeted repair. The local model sometimes returns only
        # metadata (purpose/creative_intent/reasoning) with no acts/scenes, or
        # scenes only in the nested structure. If the canonical flat scenes[]
        # is still empty after canonicalization, re-prompt ONCE with a focused
        # instruction to emit the acts/sequences/scenes structure. Deterministic,
        # repairs the current phase only, no retry-until-pass.
        if not getattr(knowledge, "scenes", []):
            repair_prompt = (
                f"# Phase 05: Narrative Expansion — REPAIR\n\n"
                f"Your previous response contained no narrative scenes. You MUST emit the "
                f"complete acts/sequences/scenes structure now.\n\n"
                f"## Synopsis\n{pkg.get('synopsis', '')}\n\n"
                f"## Generate\n"
                f"- acts: list of {{name, description, sequences}}\n"
                f"- sequences: list of {{name, act, scenes}}\n"
                f"- scenes: list of {{scene_number, act, sequence, objective, conflict, outcome, emotional_objective, narrative_beat}}\n"
                f"  where narrative_beat is one of: hook | plot | turning_point | climax\n"
                f"  Ensure the arc is complete: at least one hook, several plot, one turning_point, one climax.\n"
                f"  Explicitly realize REQ-005 (escalation), REQ-006 (confrontation), REQ-008 (resolution).\n\n"
                f"Respond with valid JSON only. Include purpose, creative_intent, reasoning, confidence."
            )
            if cfg is not None and hasattr(self.llm, "_get_provider"):
                try:
                    original_tokens = getattr(cfg, "max_tokens", bounded_tokens)
                    cfg.max_tokens = bounded_tokens
                    try:
                        response_obj = getattr(self.llm, "generate_json")(repair_prompt, "planner", self.phase_name, self.phase_name, response_format=response_format)
                    except TypeError:
                        response_obj = getattr(self.llm, "generate_json")(repair_prompt, cfg, "planner")
                    finally:
                        cfg.max_tokens = original_tokens
                    response = response_obj
                except Exception:
                    response = self.llm.generate(repair_prompt, phase_name=self.phase_name, task_key=self.phase_name)
            else:
                response = self.llm.generate(repair_prompt, phase_name=self.phase_name, task_key=self.phase_name)
            knowledge = self.parse_draft(response)
        return knowledge

    def _review_specific(self, knowledge: KnowledgeObject) -> list[str]:
        issues: list[str] = []
        for field in self._REQUIRED:
            val = getattr(knowledge, field, None)
            if val == "" or val is None:
                issues.append(f"Missing {field} — essential narrative structure")
        scenes = getattr(knowledge, "scenes", [])
        if not scenes:
            issues.append("No scenes expanded — Phase 05 must produce at least one narrative scene")
        return issues

    def _validate_specific(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:  # noqa
        from ..models import ValidationIssue  # noqa
        from ..models import Scene as ModelScene
        issues: list[ValidationIssue] = []
        scenes = getattr(knowledge, "scenes", [])
        if not scenes:
            issues.append(ValidationIssue(
                category="structure", severity="error",
                location=f"{self.phase_name}.scenes",
                description="No scenes expanded — Phase 05 must produce at least one narrative scene",
            ))
            return issues
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
