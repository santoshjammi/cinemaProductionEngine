"""Phase 12: Knowledge Integration — merge everything into the Production Knowledge Package."""

from __future__ import annotations

import json
from typing import Any

from ..models import KnowledgeIntegration, KnowledgeObject
from ..phase_base import PhaseBase


class KnowledgeIntegrationPhase(PhaseBase):
    phase_number = 12
    phase_name = "Knowledge Integration"

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        all_phases = {k: v for k, v in pkg.items() if k.startswith("phase_")}
        return (
            f"# Phase 12: Knowledge Integration\n\n"
            f"Merge everything into the Production Knowledge Package.\n\n"
            f"## All Phase Outputs\n{json.dumps(all_phases, indent=2, default=str)}\n\n"
            f"## Generate\n"
            f"- package: the complete merged knowledge package as a single JSON object\n"
            f"- knowledge_graph: {{nodes: [...], edges: [...]}} connecting all entities\n"
            f"- asset_registry: list of all assets with IDs, types, locations\n"
            f"- dependencies: list of {{from_phase, to_phase, relationship}}\n"
            f"- cross_references: list of {{source, target, relationship}}\n"
            f"- version_history: list of {{version, timestamp, changes}}\n\n"
            f"Respond with valid JSON only. Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> KnowledgeIntegration:
        from ..llm_client import _extract_json
        data = _extract_json(response)
        return KnowledgeIntegration(**data)

    def draft(self, pkg: dict[str, Any]) -> KnowledgeIntegration:
        prompt = self.build_draft_prompt(pkg)
        response = self.llm.generate(prompt)
        return self.parse_draft(response)
