"""Phase 07: Dialogue Planning — plan dialogue intent, subtext, silence, rhythm."""

from __future__ import annotations

import json
from typing import Any

from ..models import ConfidenceLevel, KnowledgeObject, ValidationIssue
from ..phase_base import PhaseBase




class DialoguePlanningPhase(PhaseBase):
    phase_number = 7
    phase_name = "Dialogue Planning"
    _REQUIRED: list[str] = ["dialogues"]

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        prev = self.slice_context(pkg, ["phase_03", "phase_05", "phase_06"])
        phase_06 = prev.get("phase_06", {}) if isinstance(prev, dict) else {}
        scenes = phase_06.get("scenes", []) if isinstance(phase_06, dict) else []
        scene_map = [
            {
                "scene_number": s.get("scene_number"),
                "narrative_beat": s.get("narrative_beat", ""),
                "purpose": s.get("purpose", ""),
                "conflict": s.get("conflict", ""),
                "emotion": s.get("emotion", ""),
            }
            for s in scenes
            if isinstance(s, dict)
        ]
        return (
            f"# Phase 07: Dialogue Planning\n\n"
            f"Plan dialogue for every scene.\n\n"
            f"## Phase 06 scene anchors\n{json.dumps(scene_map, indent=2, default=str)}\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## For every scene generate\n"
            f"- scene_number (must exactly match a Phase 6 scene_number; do not invent decimals or sub-scenes)\n"
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
        self._anchor_scene_numbers = [int(s.get("scene_number")) for s in scenes if isinstance(s, dict) and isinstance(s.get("scene_number"), int)]
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
        return self.parse_draft(response, pkg)

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
