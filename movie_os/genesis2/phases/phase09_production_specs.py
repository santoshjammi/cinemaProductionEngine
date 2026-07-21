"""Phase 09: Production Specifications — generate all production specs."""

from __future__ import annotations

import json
from typing import Any

from ..models import ProductionSpecifications, KnowledgeObject
from ..phase_base import PhaseBase


class ProductionSpecificationsPhase(PhaseBase):
    phase_number = 9
    phase_name = "Production Specifications"

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        prev = {k: pkg.get(k, {}) for k in ["phase_03", "phase_04", "phase_06", "phase_07", "phase_08"]}
        return (
            f"# Phase 09: Production Specifications\n\n"
            f"Generate detailed production specifications.\n\n"
            f"## Previous Phases\n{json.dumps(prev, indent=2, default=str)}\n\n"
            f"## Generate for each category\n"
            f"- character_specs: list of character specs with appearance, wardrobe, props\n"
            f"- location_specs: list of location specs with set design, lighting, atmosphere\n"
            f"- camera_specs: list of camera specs with body, lens, rig\n"
            f"- lighting_specs: list of lighting specs with fixtures, gels, intensity\n"
            f"- animation_specs: list of animation specs (if applicable)\n"
            f"- audio_specs: list of audio specs with mics, recording, processing\n"
            f"- music_specs: list of music specs with instruments, tempo, mood\n"
            f"- editing_specs: list of editing specs with software, workflow, transitions\n"
            f"- rendering_specs: list of rendering specs with resolution, format, codec\n\n"
            f"Respond with valid JSON only. Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> ProductionSpecifications:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        return ProductionSpecifications(**data)

    def draft(self, pkg: dict[str, Any]) -> ProductionSpecifications:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)
