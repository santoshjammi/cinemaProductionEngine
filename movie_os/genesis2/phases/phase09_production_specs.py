"""Phase 09: Production Specifications — define runtime, format, technical requirements."""

from __future__ import annotations

import json
from typing import Any

from ..models import KnowledgeObject, ValidationIssue
from ..phase_base import PhaseBase


class ProductionSpecificationsPhase(PhaseBase):
    phase_number = 9
    phase_name = "Production Specifications"
    _REQUIRED: list[str] = ["character_specs", "location_specs"]

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        previous_keys = [f"phase_{i:02d}" for i in range(1, 9)]
        prev = self.slice_context(pkg, previous_keys)
        synopsis = pkg.get("synopsis", "")
        return (
            f"# Phase 09: Production Specifications\n\n"
            f"Define technical requirements for production.\n\n"
            f"## Synopsis\n{synopsis}\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Define for each category\n"
            f"- character_specs: character visual specs\n"
            f"- location_specs: location specs\n"
            f"- camera_specs: camera equipment\n"
            f"- lighting_specs: lighting setup\n"
            f"- animation_specs: animation requirements\n"
            f"- audio_specs: audio requirements\n"
            f"- music_specs: music direction\n"
            f"- editing_specs: post-production\n"
            f"- rendering_specs: final output specs\n\n"
            f"Required JSON shape:\n"
            f"{{\n"
            f'  "purpose": "...",\n'
            f'  "creative_intent": "...",\n'
            f'  "reasoning": "...",\n'
            f'  "confidence": "confirmed",\n'
            f'  "character_specs": [{{"character": "...", "wardrobe": "...", "props": ["..."]}}],\n'
            f'  "location_specs": [{{"location": "...", "set_design": "..."}}],\n'
            f'  "camera_specs": [{{"body": "...", "lens": "..."}}],\n'
            f'  "lighting_specs": [{{"fixtures": "...", "gels": "..."}}],\n'
            f'  "animation_specs": [],\n'
            f'  "audio_specs": [{{"mics": "...", "recording": "..."}}],\n'
            f'  "music_specs": [{{"instruments": "...", "tempo": "..."}}],\n'
            f'  "editing_specs": [{{"software": "...", "workflow": "..."}}],\n'
            f'  "rendering_specs": [{{"resolution": "...", "format": "..."}}]\n'
            f"}}\n\n"
            f"Return JSON only. Keep the production blueprint complete and bounded."
        )

    def parse_draft(self, response: str | dict[str, Any]) -> KnowledgeObject:
        if isinstance(response, dict):
            data = dict(response)
        else:
            from ..llm_client import _extract_json
            data = _extract_json(response)
        from ..models import ProductionSpecifications
        return ProductionSpecifications(**data)

    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        prompt = self.build_draft_prompt(pkg)
        cfg = getattr(self.llm, "_config", None)
        from ..models import ProductionSpecifications
        response_format = ProductionSpecifications.model_json_schema()
        if cfg is not None and hasattr(self.llm, "_get_provider"):
            try:
                from ..llm_providers import LLMConfig
                phase_cfg = LLMConfig(**cfg.model_dump()) if hasattr(cfg, "model_dump") else cfg
                # Keep Phase 09 bounded so it does not inherit a runaway global ceiling.
                phase_cfg.max_tokens = min(int(getattr(phase_cfg, "max_tokens", 0) or 0), 1024) or 1024
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
        # P0-04: the local model sometimes returns empty base fields
        # (purpose/creative_intent/reasoning) or empty required specs. Retry once
        # with a focused prompt. Deterministic, repairs the current phase only.
        if any(not str(getattr(knowledge, f, "") or "").strip() for f in ("purpose", "creative_intent", "reasoning")):
            focused = (
                "# Phase 09: Production Specifications (retry — required fields missing)\n"
                "Provide complete, concrete values for these EXACT keys. Use the "
                "synopsis: " + str(pkg.get("synopsis", ""))[:300] + "\n"
                'Respond with valid JSON only: {"purpose": "...", "creative_intent": "...", '
                '"reasoning": "...", "character_specs": [...], "location_specs": [...], '
                '"camera_specs": [...], "lighting_specs": [...], "audio_specs": [...], '
                '"music_specs": [...], "editing_specs": [...], "rendering_specs": [...]}'
            )
            try:
                knowledge = self.parse_draft(self.llm.generate(focused, phase_name=self.phase_name, task_key=f"{self.phase_name}:retry"))
            except Exception:
                pass
        return knowledge

    def _review_specific(self, knowledge: KnowledgeObject) -> list[str]:
        issues: list[str] = []
        for field in self._REQUIRED:
            val = getattr(knowledge, field, None)
            if not (isinstance(val, list) and len(val) > 0):
                issues.append(f"Empty {field} — at least one entry required")
        return issues

    def _validate_specific(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:  # noqa
        issues: list[ValidationIssue] = []
        for field in self._REQUIRED:
            val = getattr(knowledge, field, None)
            if isinstance(val, list) and len(val) > 0:
                pass  # valid
            elif not isinstance(val, list):
                issues.append(ValidationIssue(
                    category="schema_error", severity="error",
                    location=f"{self.phase_name}.{field}",
                    description=f"{field} must be a list (may be empty)",
                ))
        return issues
