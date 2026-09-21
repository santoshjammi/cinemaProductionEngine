"""Phase 07: Dialogue Planning — plan dialogue intent, subtext, silence, rhythm."""

from __future__ import annotations

import json
import logging
from typing import Any

from ..models import ConfidenceLevel, KnowledgeObject, ValidationIssue
from ..phase_base import PhaseBase

logger = logging.getLogger("movie_os.genesis2.phase07")




class DialoguePlanningPhase(PhaseBase):
    phase_number = 7
    phase_name = "Dialogue Planning"
    _REQUIRED: list[str] = ["dialogues"]

    def _scene_intent_map(self, pkg: dict[str, Any]) -> dict[int, dict[str, str]]:
        """Build a scene_number -> {objective, conflict, outcome} map from the
        Narrative-Expansion (Phase05) scenes, which carry the DISTINCT per-scene
        intent.  Phase06 scene anchors often have empty purpose/conflict/emotion,
        so binding dialogue prompts to Phase06 alone yields near-identical prompts
        and duplicated dialogue across distinct scenes.  Phase05 is the richer
        structural source (P0-03 preservation).

        The FLAT ``phase_05.scenes`` list carries the correct GLOBAL scene
        numbering (1..N).  The nested ``acts[].sequences[].scenes`` restart
        numbering per act (each act's scene 1 collides), so flat scenes take
        precedence and nested acts only fill scene numbers not already present.
        """
        intent: dict[int, dict[str, str]] = {}
        phase_05 = pkg.get("phase_05", {}) or {}
        for ne_scene in (phase_05.get("scenes", []) or []):
            if isinstance(ne_scene, dict) and isinstance(ne_scene.get("scene_number"), int):
                sn = int(ne_scene.get("scene_number"))
                intent[sn] = {
                    "objective": str(ne_scene.get("objective", "") or ""),
                    "conflict": str(ne_scene.get("conflict", "") or ""),
                    "outcome": str(ne_scene.get("outcome", "") or ""),
                }
        for act in (phase_05.get("acts", []) or []):
            if not isinstance(act, dict):
                continue
            for seq in (act.get("sequences", []) or []):
                if not isinstance(seq, dict):
                    continue
                for ne_scene in (seq.get("scenes", []) or []):
                    if isinstance(ne_scene, dict) and isinstance(ne_scene.get("scene_number"), int):
                        sn = int(ne_scene.get("scene_number"))
                        if sn not in intent:
                            intent[sn] = {
                                "objective": str(ne_scene.get("objective", "") or ""),
                                "conflict": str(ne_scene.get("conflict", "") or ""),
                                "outcome": str(ne_scene.get("outcome", "") or ""),
                            }
        return intent

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        prev = self.slice_context(pkg, ["phase_03", "phase_05", "phase_06"])
        phase_06 = prev.get("phase_06", {}) if isinstance(prev, dict) else {}
        scenes = phase_06.get("scenes", []) if isinstance(phase_06, dict) else []
        # Bind each scene anchor to its DISTINCT Phase05 intent so the model
        # receives differentiated scene objectives/conflicts/outcomes.  Phase06
        # anchors alone are often empty and produce duplicated dialogue.
        intent_map = self._scene_intent_map(pkg)
        dialogue_policy = (pkg.get("constraints", {}) or {}).get("dialogue_policy") or (pkg.get("constraints", {}) or {}).get("dialogue_policy_rules") or {}
        scene_map = [
            {
                "scene_number": s.get("scene_number"),
                "title": s.get("title", ""),
                "narrative_beat": s.get("narrative_beat", ""),
                "purpose": s.get("purpose", ""),
                "conflict": s.get("conflict", ""),
                "emotion": s.get("emotion", ""),
                "objective": intent_map.get(int(s.get("scene_number")), {}).get("objective", ""),
                "scene_conflict": intent_map.get(int(s.get("scene_number")), {}).get("conflict", ""),
                "outcome": intent_map.get(int(s.get("scene_number")), {}).get("outcome", ""),
            }
            for s in scenes
            if isinstance(s, dict)
        ]
        canon = (pkg.get("constraints", {}) or {}).get("canonical_requirements") or []
        canon_block = ""
        if canon:
            lines = "\n".join(f"- {c['id']} ({c['category']}): {c['statement']}" for c in canon)
            canon_block = (
                f"## Canonical Episode Requirements (MUST realize ALL across the dialogue)\n"
                f"Your dialogue across all scenes must collectively realize every canonical "
                f"MUST requirement. The CONFRONTATION requirement (REQ-006) must include a "
                f"moment where Sarah directly names the avoidance and forces the central "
                f"truth into the interaction (quiet, not shouting). The RESOLUTION (REQ-008) "
                f"must show movement toward reconnection. None may be dropped.\n{lines}\n"
            )
        return (
            f"# Phase 07: Dialogue Planning\n\n"
            f"Plan dialogue for every scene.\n\n"
            f"{canon_block}"
            f"## Phase 06 scene anchors\n{json.dumps(scene_map, indent=2, default=str)}\n\n"
            f"## Dialogue policy\n{json.dumps(dialogue_policy, indent=2, default=str)}\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## For every scene generate\n"
            f"- scene_number (must exactly match a Phase 6 scene_number; do not invent decimals or sub-scenes)\n"
            f"- scene title and scene objective must remain consistent with Phase 6\n"
            f"- conversation_intent, subtext\n"
            f"- emotional_state, silence_opportunities (list)\n"
            f"- dialogue_rhythm, speech_patterns, voice_direction\n"
            f"- **lines**: THE PRIMARY SPOKEN DIALOGUE. MUST contain AT LEAST 6\n"
            f"  entries, each {{speaker, text, delivery_intent, emotion}}. Alternate\n"
            f"  speakers so both characters are heard. Use real character names\n"
            f"  (e.g. MARK, SARAH), not A/B. Write a NATURAL, flowing conversation\n"
            f"  — not a summary. Each line should be a real spoken beat: a question,\n"
            f"  a reaction, a small acknowledgement, a hesitation, a reassurance.\n"
            f"  Vary the emotional tone across the exchange (tension, softening,\n"
            f"  warmth). Keep each line crisp and short — one clear thought per line,\n"
            f"  but make the EXCHANGE feel like two people really talking.\n"
            f"- **inner_voice**: OPTIONAL, 1-2 lines ONLY for the suffering/withdrawn\n"
            f"  character's whispering inner voice (speaker = '<NAME>_INNER',\n"
            f"  emotion = 'whisper'). This is SEPARATE from lines — do NOT put the\n"
            f"  main conversation here. Put the spoken conversation in lines.\n\n"
            f"Required JSON shape:\n"
            f"{{\n"
            f'  "dialogues": [\n'
            f'    {{"scene_number": 1, "conversation_intent": "...", "subtext": "...", "emotional_state": "...", "silence_opportunities": ["..."], "dialogue_rhythm": "...", "speech_patterns": "...", "voice_direction": "...", "lines": [{{"speaker": "MARK", "text": "...", "delivery_intent": "...", "emotion": "..."}}], "inner_voice": []}}\n'
            f"  ]\n"
            f"}}\n\n"
            f"Respond with JSON only. The scene_number field must exactly match a Phase 6 anchor integer."
        )

    def parse_draft(self, response: str, pkg: dict[str, Any] | None = None) -> KnowledgeObject:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        dial_data = data.get("dialogues", [])
        dialogues = []
        from ..models import DialogueLine, DialoguePlan
        for d in dial_data:
            if hasattr(d, 'model_dump'):
                d = d.model_dump()
            else:
                d = dict(d)
            if not isinstance(d, dict):
                continue
            raw_scene_number = d.get("scene_number")
            scene_number = int(raw_scene_number) if isinstance(raw_scene_number, int) else raw_scene_number
            if scene_number is None:
                scene_number = 0
            d["scene_number"] = scene_number
            for field in ("lines", "inner_voice"):
                if field in d and isinstance(d[field], list):
                    normalized = []
                    for item in d[field]:
                        if not isinstance(item, dict):
                            continue
                        line = DialogueLine(
                            speaker=str(item.get("speaker", "")),
                            text=str(item.get("text", "")),
                            delivery_intent=str(item.get("delivery_intent", item.get("emotion", ""))),
                            emotion=str(item.get("emotion", "neutral")),
                        )
                        normalized.append(line)
                    d[field] = normalized
            if not d.get("lines") and d.get("inner_voice"):
                d["lines"] = d["inner_voice"]
                d["inner_voice"] = []
            # Deterministic identity assignment: stable within episode for unchanged order.
            for idx, line in enumerate(d.get("lines", []), start=1):
                if hasattr(line, "model_dump"):
                    ld = line.model_dump()
                else:
                    ld = dict(line)
                ld["line_id"] = f"{scene_number}:D{idx:03d}"
                d["lines"][idx - 1] = DialogueLine(**ld)
            for idx, line in enumerate(d.get("inner_voice", []), start=1):
                if hasattr(line, "model_dump"):
                    ld = line.model_dump()
                else:
                    ld = dict(line)
                ld["line_id"] = f"{scene_number}:I{idx:03d}"
                d["inner_voice"][idx - 1] = DialogueLine(**ld)
            dialogues.append(DialoguePlan(**d))
        from ..models import DialoguePlanning
        if len(dialogues) == 1 and pkg is not None:
            scene_numbers = [s.get("scene_number") for s in (pkg.get("phase_06", {}) or {}).get("scenes", []) if isinstance(s, dict) and isinstance(s.get("scene_number"), int)]
            if len(scene_numbers) > 1:
                base = dialogues[0].model_dump() if hasattr(dialogues[0], "model_dump") else dict(dialogues[0])
                base_scene = base.get("scene_number")
                if base_scene in scene_numbers:
                    ordered_scene_numbers = [base_scene] + [sn for sn in scene_numbers if sn != base_scene]
                    replicated = []
                    for sn in ordered_scene_numbers:
                        clone = json.loads(json.dumps(base))
                        clone["scene_number"] = sn
                        for idx, line in enumerate(clone.get("lines", []), start=1):
                            line["line_id"] = f"{sn}:D{idx:03d}"
                        for idx, line in enumerate(clone.get("inner_voice", []), start=1):
                            line["line_id"] = f"{sn}:I{idx:03d}"
                        replicated.append(DialoguePlan(**clone))
                    dialogues = replicated
        return DialoguePlanning(dialogues=dialogues, purpose=data.get("purpose", ""), creative_intent=data.get("creative_intent", ""), reasoning=data.get("reasoning", ""), confidence=data.get("confidence", "inferred"))

    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        phase_06 = pkg.get("phase_06", {}) or {}
        scenes = phase_06.get("scenes", []) if isinstance(phase_06, dict) else []
        # Anchor to the union of Scene-Planning scenes AND Narrative-Expansion
        # scenes. The bridge emits scenes from BOTH (P0-03 preservation); if
        # dialogue only covers phase_06, narrative-expansion scenes would be
        # left without dialogue and the freeze gate would reject. Every scene
        # the brief will carry must have a dialogue anchor.
        anchor_nums = {int(s.get("scene_number")) for s in scenes if isinstance(s, dict) and isinstance(s.get("scene_number"), int)}
        # Narrative-Expansion scenes may be nested inside acts[].sequences[].scenes
        # (not a flat phase_05.scenes list). Traverse the full structure so every
        # scene the bridge will emit has a dialogue anchor (P0-03 preservation).
        phase_05 = pkg.get("phase_05", {}) or {}
        for ne_scene in (phase_05.get("scenes", []) or []):
            if isinstance(ne_scene, dict) and isinstance(ne_scene.get("scene_number"), int):
                anchor_nums.add(int(ne_scene.get("scene_number")))
        for act in (phase_05.get("acts", []) or []):
            if not isinstance(act, dict):
                continue
            for seq in (act.get("sequences", []) or []):
                if not isinstance(seq, dict):
                    continue
                for ne_scene in (seq.get("scenes", []) or []):
                    if isinstance(ne_scene, dict) and isinstance(ne_scene.get("scene_number"), int):
                        anchor_nums.add(int(ne_scene.get("scene_number")))
        self._anchor_scene_numbers = sorted(anchor_nums)
        prompt = self.build_draft_prompt(pkg)
        cfg = getattr(self.llm, "_config", None)
        from ..models import DialoguePlanning
        response_format = DialoguePlanning.model_json_schema()
        if cfg is not None and hasattr(self.llm, "_get_provider"):
            try:
                from ..llm_providers import LLMConfig
                phase_cfg = LLMConfig(**cfg.model_dump()) if hasattr(cfg, "model_dump") else cfg
                # Dialogue Planning is a bounded structured call. Keep the budget
                # phase-specific so we do not inherit the broad global ceiling.
                phase_cfg.max_tokens = min(int(getattr(phase_cfg, "max_tokens", 0) or 0), 1536) or 1536
                try:
                    response_obj = getattr(self.llm, "generate_json")(prompt, "planner", self.phase_name, self.phase_name, response_format=response_format)
                except TypeError:
                    response_obj = getattr(self.llm, "generate_json")(prompt, cfg, "planner")
                response = json.dumps(response_obj)
            except Exception:
                response = self.llm.generate(prompt)
        else:
            response = self.llm.generate(prompt)
        knowledge = self.parse_draft(response, pkg)

        # ── P0: orphan-scene FAIL-CLOSED gate. ──
        # Do NOT silently drop dialogues whose scene_number is not an
        # authoritative anchor. The Guardian's contract is fail-closed: an
        # orphan reference must surface as a validation ERROR (see
        # _validate_specific), not be silently discarded. Keeping the orphan
        # lets validation run and the phase fail closed.
        # (Removed the prior filter that stripped orphans before validation —
        # that hid the reference_error and allowed silent success.)

        # ── P0-01/20: repair current phase, don't regenerate the story. ──
        # The local model reliably omits some scenes when asked for many at once.
        # Detect any planned scene missing from the produced dialogue and request
        # a focused, per-scene dialogue repair so every scene is covered.
        if self._anchor_scene_numbers:
            produced = {d.scene_number for d in getattr(knowledge, "dialogues", [])}
            missing = [n for n in self._anchor_scene_numbers if n not in produced]
            if missing:
                repaired = self._repair_missing_scenes(pkg, missing)
                if repaired:
                    existing = getattr(knowledge, "dialogues", [])
                    knowledge.dialogues = list(existing) + repaired
            underfilled = []
            for dlg in getattr(knowledge, "dialogues", []):
                lines = getattr(dlg, "lines", []) or []
                if len(lines) < 6:
                    scene_num = getattr(dlg, "scene_number", None)
                    if isinstance(scene_num, int):
                        underfilled.append(scene_num)
            if underfilled:
                repaired = self._repair_missing_scenes(pkg, underfilled)
                if repaired:
                    merged = []
                    repaired_map = {d.scene_number: d for d in repaired}
                    for dlg in getattr(knowledge, "dialogues", []):
                        sn = getattr(dlg, "scene_number", None)
                        merged.append(repaired_map.get(sn, dlg))
                    knowledge.dialogues = merged
        # ── P0: duplicate-dialogue integrity gate. ──
        # Distinct authoritative scenes must not receive identical dialogue
        # payloads.  If two scenes with materially distinct intent end up with
        # the same normalized full-scene dialogue, perform ONE bounded
        # scene-specific repair for the later duplicate; if it is still a
        # duplicate, fail closed (never accept duplicated scene substance).
        if self._anchor_scene_numbers:
            knowledge = self._deduplicate_dialogues(pkg, knowledge)
        return knowledge

    @staticmethod
    def _normalize_dialogue_payload(dlg: Any) -> tuple:
        """Normalize a dialogue plan's lines to a comparable tuple (whitespace
        and speaker-label formatting normalized, semantic content preserved)."""
        lines = getattr(dlg, "lines", None) or []
        out = []
        for ln in lines:
            if hasattr(ln, "model_dump"):
                ld = ln.model_dump()
            elif isinstance(ln, dict):
                ld = ln
            else:
                ld = {}
            speaker = " ".join(str(ld.get("speaker", "")).strip().split()).upper()
            text = " ".join(str(ld.get("text", "")).strip().split())
            out.append((speaker, text))
        return tuple(out)

    def _deduplicate_dialogues(self, pkg: dict[str, Any], knowledge: KnowledgeObject) -> KnowledgeObject:
        """Reject exact full-scene dialogue duplicates across distinct scenes.

        Returns the knowledge with duplicates repaired (one bounded attempt per
        offending scene).  If a scene remains an exact duplicate after repair,
        it is dropped and the phase will fail closed via validation (no dialogue
        for that scene)."""
        dialogues = list(getattr(knowledge, "dialogues", []) or [])
        if len(dialogues) < 2:
            return knowledge
        intent_map = self._scene_intent_map(pkg)
        seen: dict[tuple, int] = {}  # normalized payload -> first scene_number
        repaired_scenes: set[int] = set()
        for dlg in dialogues:
            sn = getattr(dlg, "scene_number", None)
            if not isinstance(sn, int):
                continue
            payload = self._normalize_dialogue_payload(dlg)
            if not payload:
                continue
            if payload in seen:
                first_sn = seen[payload]
                # Only treat as a defect if the two scenes have materially
                # distinct intent (different objective/conflict/outcome).
                a = intent_map.get(first_sn, {})
                b = intent_map.get(sn, {})
                if a == b and a.get("objective"):
                    # Same intent referenced twice — not a cross-scene defect.
                    continue
                if sn not in repaired_scenes:
                    repaired = self._repair_duplicate_scene(pkg, sn, first_sn, payload)
                    if repaired is not None:
                        # Replace the duplicate in place.
                        for i, d in enumerate(dialogues):
                            if getattr(d, "scene_number", None) == sn:
                                dialogues[i] = repaired
                                break
                        repaired_scenes.add(sn)
                        # Re-check the repaired payload against the map.  If it
                        # is STILL an exact duplicate of any already-seen scene
                        # (including the original it was meant to replace), fail
                        # closed and drop it.
                        new_payload = self._normalize_dialogue_payload(repaired)
                        if new_payload in seen:
                            dialogues = [d for d in dialogues if getattr(d, "scene_number", None) != sn]
                    else:
                        # Repair failed -> fail closed (drop the duplicate).
                        dialogues = [d for d in dialogues if getattr(d, "scene_number", None) != sn]
            else:
                seen[payload] = sn
        knowledge.dialogues = dialogues
        return knowledge

    def _repair_duplicate_scene(self, pkg: dict[str, Any], scene_num: int, first_sn: int, existing_payload: tuple):
        """One bounded scene-specific repair for a duplicated dialogue scene."""
        intent_map = self._scene_intent_map(pkg)
        anchor = intent_map.get(scene_num, {})
        objective = anchor.get("objective", "")
        conflict = anchor.get("conflict", "")
        outcome = anchor.get("outcome", "")
        prompt = (
            f"Write a NEW, distinct natural conversation for scene {scene_num}. "
            f"This scene's unique objective: {objective or '(none)'}. "
            f"Unique conflict: {conflict or '(none)'}. "
            f"Unique outcome: {outcome or '(none)'}. "
            f"Two characters MARK and SARAH. "
            f"Your dialogue MUST be semantically different from scene {first_sn}'s dialogue "
            f"and must advance THIS scene's specific objective. "
            "Return ONLY valid JSON dialogue for THIS one scene:\n"
            '{"scene_number": ' + str(scene_num) + ', "conversation_intent": "...", '
            '"subtext": "...", "emotional_state": "...", "lines": ['
            '{"speaker": "MARK", "text": "...", "delivery_intent": "...", "emotion": "..."}, '
            '{"speaker": "SARAH", "text": "...", "delivery_intent": "...", "emotion": "..."}, '
            '{"speaker": "MARK", "text": "...", "delivery_intent": "...", "emotion": "..."}, '
            '{"speaker": "SARAH", "text": "...", "delivery_intent": "...", "emotion": "..."}, '
            '{"speaker": "MARK", "text": "...", "delivery_intent": "...", "emotion": "..."}, '
            '{"speaker": "SARAH", "text": "...", "delivery_intent": "...", "emotion": "..."}]}'
        )
        try:
            response = self.llm.generate(prompt, phase_name=self.phase_name, task_key=f"{self.phase_name}:dedup")
            parsed = self.parse_draft(response, pkg)
            if getattr(parsed, "dialogues", None):
                for dlg in getattr(parsed, "dialogues", []):
                    if dlg.scene_number == scene_num and dlg.lines:
                        return dlg
            parsed_scene = self._parse_single_scene(response, scene_num)
            if parsed_scene is not None:
                return parsed_scene
        except Exception as e:
            logger.warning(f"[Dialogue Planning] dedup repair scene {scene_num} failed: {e}")
        return None

    def _repair_missing_scenes(self, pkg: dict[str, Any], missing_scene_numbers: list[int]) -> list:
        """Generate dialogue for scenes the model skipped. Focused per-scene
        prompts are far more reliable for the local model than one giant batch.
        Only repairs *missing* scenes — never rewrites existing dialogue."""
        phase_06 = pkg.get("phase_06", {}) or {}
        scenes = phase_06.get("scenes", []) if isinstance(phase_06, dict) else []
        scene_anchors = {
            int(s.get("scene_number")): s for s in scenes
            if isinstance(s, dict) and isinstance(s.get("scene_number"), int)
        }
        # Prefer the distinct Phase05 scene intent (objective/conflict/outcome)
        # for the repair prompt.  Phase06 anchors often carry empty
        # narrative_beat/purpose, which produced malformed prompts like
        # "beat: " and made the model ramble into prose instead of JSON.
        intent_map = self._scene_intent_map(pkg)
        cfg = getattr(self.llm, "_config", None)
        repaired = []
        for scene_num in missing_scene_numbers:
            anchor = scene_anchors.get(scene_num, {})
            intent = intent_map.get(scene_num, {})
            purpose = intent.get("objective", "") or anchor.get("purpose", "")
            beat = intent.get("narrative_beat", "") or anchor.get("narrative_beat", "")
            conflict = intent.get("conflict", "")
            outcome = intent.get("outcome", "")
            prompt = (
                f"Write a short natural conversation for scene {scene_num} "
                f"({beat} beat: {purpose}). "
                f"Scene conflict: {conflict or '(none)'}. "
                f"Scene outcome: {outcome or '(none)'}. "
                f"Two characters MARK and SARAH. "
                "Return ONLY valid JSON dialogue for THIS one scene:\n"
                '{"scene_number": ' + str(scene_num) + ', "conversation_intent": "...", '
                '"subtext": "...", "emotional_state": "...", "lines": ['
                '{"speaker": "MARK", "text": "...", "delivery_intent": "...", "emotion": "..."}, '
                '{"speaker": "SARAH", "text": "...", "delivery_intent": "...", "emotion": "..."}, '
                '{"speaker": "MARK", "text": "...", "delivery_intent": "...", "emotion": "..."}, '
                '{"speaker": "SARAH", "text": "...", "delivery_intent": "...", "emotion": "..."}, '
                '{"speaker": "MARK", "text": "...", "delivery_intent": "...", "emotion": "..."}, '
                '{"speaker": "SARAH", "text": "...", "delivery_intent": "...", "emotion": "..."}]}'
            )
            # Bounded retry on the repair call: a transient Ollama timeout must
            # not strand a scene with no dialogue.  Re-asks the same repair for
            # the same scene — it never rewrites existing dialogue.
            for attempt in range(2):
                try:
                    response = self.llm.generate(prompt, phase_name=self.phase_name, task_key=f"{self.phase_name}:repair")
                    parsed = self.parse_draft(response, pkg)
                    # The repair prompt returns a bare scene dict (no "dialogues"
                    # wrapper); parse_draft then yields nothing. Detect that and
                    # parse the scene directly.
                    if not getattr(parsed, "dialogues", None):
                        parsed_scene = self._parse_single_scene(response, scene_num)
                        if parsed_scene is not None:
                            repaired.append(parsed_scene)
                            break
                    else:
                        for dlg in getattr(parsed, "dialogues", []):
                            if dlg.scene_number == scene_num and dlg.lines:
                                repaired.append(dlg)
                                break
                        else:
                            continue  # found wrapper but not this scene; retry
                        break
                except Exception as e:
                    logger.warning(f"[Dialogue Planning] repair scene {scene_num} attempt {attempt + 1} failed: {e}")
        return repaired

    def _parse_single_scene(self, response: str, scene_num: int):
        """Parse a bare scene dialogue object (no 'dialogues' wrapper)."""
        from ..llm_client import _extract_json
        from ..models import DialogueLine, DialoguePlan
        data = _extract_json(response)
        if not isinstance(data, dict):
            return None
        if not isinstance(data.get("scene_number"), int):
            data["scene_number"] = scene_num
        lines = []
        for item in data.get("lines", []) or []:
            if not isinstance(item, dict):
                continue
            lines.append(DialogueLine(
                speaker=str(item.get("speaker", "")),
                text=str(item.get("text", "")),
                delivery_intent=str(item.get("delivery_intent", item.get("emotion", ""))),
                emotion=str(item.get("emotion", "neutral")),
            ))
        if not lines:
            return None
        plan = DialoguePlan(
            scene_number=scene_num,
            conversation_intent=str(data.get("conversation_intent", "")),
            subtext=str(data.get("subtext", "")),
            emotional_state=str(data.get("emotional_state", "")),
            lines=lines,
            inner_voice=[],
        )
        for idx, line in enumerate(lines, start=1):
            line.line_id = f"{scene_num}:D{idx:03d}"
        return plan

    def _review_specific(self, knowledge: KnowledgeObject) -> list[str]:
        issues: list[str] = []
        dialogues = getattr(knowledge, "dialogues", [])
        if not dialogues or (isinstance(dialogues, list) and len(dialogues) == 0):
            issues.append("No dialogue planned — at least one key exchange expected")
        return issues

    def persist_checkpoint(self, result: Any, output_dir: str | Path) -> Path:
        from pathlib import Path
        from ..engine import Genesis2Engine
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        return Genesis2Engine.write_phase_checkpoint(out, result, result)

    def _validate_specific(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:  # noqa
        from ..models import ValidationIssue  # noqa
        issues: list[ValidationIssue] = []
        dialogues = getattr(knowledge, "dialogues", [])
        if isinstance(dialogues, list):
            for i, dia in enumerate(dialogues):
                ddata = dia.model_dump() if hasattr(dia, 'model_dump') else {}
                if not isinstance(ddata, dict):
                    continue
                intent = ddata.get("conversation_intent")
                if not (isinstance(intent, str) and intent.strip()):
                    issues.append(ValidationIssue(
                        category="schema_error", severity="warning",
                        location=f"{self.phase_name}.dialogues[{i}].intent",
                        description="Dialogue conversation_intent is required",
                    ))
                scene_number = ddata.get("scene_number")
                if self._anchor_scene_numbers and scene_number not in self._anchor_scene_numbers:
                    issues.append(ValidationIssue(
                        category="reference_error", severity="error",
                        location=f"{self.phase_name}.dialogues[{i}].scene_number",
                        description=f"Dialogue scene_number {scene_number} is not present in Phase 6 anchors {self._anchor_scene_numbers}",
                    ))
                if isinstance(scene_number, float) and not scene_number.is_integer():
                    issues.append(ValidationIssue(
                        category="reference_error", severity="error",
                        location=f"{self.phase_name}.dialogues[{i}].scene_number",
                        description=f"Dialogue scene_number {scene_number} must be an integer anchor from Phase 6",
                    ))
                # ── Minimum dialogue density: at least 6 spoken lines per scene ──
                lines = ddata.get("lines", []) or []
                if len(lines) < 6:
                    issues.append(ValidationIssue(
                        category="structure", severity="error",
                        location=f"{self.phase_name}.dialogues[{i}].lines",
                        description=f"Scene {ddata.get('scene_number', i+1)} has only {len(lines)} spoken lines — "
                                    f"at least 6 are required for a real conversation",
                    ))
                for j, line in enumerate(lines):
                    if not getattr(line, 'delivery_intent', '') and not (isinstance(line, dict) and line.get('delivery_intent')):
                        issues.append(ValidationIssue(
                            category="schema_error", severity="error",
                            location=f"{self.phase_name}.dialogues[{i}].lines[{j}].delivery_intent",
                            description="Dialogue delivery_intent is required",
                        ))
                    if not getattr(line, 'line_id', '') and not (isinstance(line, dict) and line.get('line_id')):
                        issues.append(ValidationIssue(
                            category="schema_error", severity="warning",
                            location=f"{self.phase_name}.dialogues[{i}].lines[{j}].line_id",
                            description="Dialogue line_id is assigned at persistence time",
                        ))
        return issues
