"""Phase 12: Knowledge Integration — integrate all knowledge into final PKP."""

from __future__ import annotations

import json
from typing import Any

from ..models import ConfidenceLevel, KnowledgeObject, ValidationIssue, KnowledgeIntegration as IntegrationKO
from ..phase_base import PhaseBase


class KnowledgeIntegrationPhase(PhaseBase):
    phase_number = 12
    phase_name = "Knowledge Integration"
    _REQUIRED: list[str] = ["package", "knowledge_graph"]
    # P0: Phase12 is a bounded structured call. The local model (qwen3:4b)
    # rambles into prose when given an unbounded budget, and the 4096-token
    # global ceiling under a 131072-token context window lets it generate
    # slowly past the 300s timeout. A phase-specific ceiling + structured
    # output keeps it schema-constrained and fast (mirrors Phase02/03/04/10).
    _OUTPUT_BUDGET = 512

    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        previous_keys = [f"phase_{i:02d}" for i in range(1, 12)]
        prev = self.slice_context(pkg, previous_keys)
        prev_str = json.dumps(prev, indent=2, default=str)
        return (
            f"# Phase 12: Knowledge Integration\n\n"
            f"Integrate all knowledge into a unified package.\n\n"
            f"## All Previous Phases (summary)\n{prev_str}\n\n"
            f"## Integrate\n"
            f"- package: full knowledge package summary with metadata\n"
            f"- knowledge_graph: graph of interconnected knowledge nodes and edges\n"
            f"- asset_registry: list of all generated assets catalogued\n"
            f"- dependencies: phase-to-phase dependency mapping\n"
            f"- cross_references: cross-references between related elements\n"
            f"- version_history: tracked versions and changes\n\n"
            f"Respond with valid JSON only. Include purpose, creative_intent, reasoning, confidence."
        )

    def parse_draft(self, response: str) -> KnowledgeObject:
        from ..llm_client import _extract_json
        data = response if isinstance(response, dict) else _extract_json(response)
        from ..models import (
            KnowledgeGraphNode, KnowledgeGraphEdge, KnowledgeIntegration,
        )
        graph_data = data.get("knowledge_graph", {}) or {}
        if not isinstance(graph_data, dict):
            graph_data = {}
        nodes_raw = graph_data.get("nodes", [])
        edges_raw = graph_data.get("edges", [])
        nodes = []
        for n in nodes_raw:
            if hasattr(n, 'model_dump'):
                nodes.append(n)
            elif isinstance(n, dict):
                nodes.append(KnowledgeGraphNode(**n))
            else:
                nodes.append(n)
        edges = []
        for e in edges_raw:
            if hasattr(e, 'model_dump'):
                edges.append(e)
            elif isinstance(e, dict):
                edges.append(KnowledgeGraphEdge(**e))
            else:
                edges.append(e)
        dependencies = data.get("dependencies", [])
        if isinstance(dependencies, list):
            normalized_dependencies = []
            for dep in dependencies:
                if isinstance(dep, dict):
                    normalized_dependencies.append(dep)
                else:
                    normalized_dependencies.append({"value": str(dep)})
        else:
            normalized_dependencies = []
        package = data.get("package", {})
        if not isinstance(package, dict) or not package:
            package = {
                "integrated": True,
                "summary": data.get("reasoning", ""),
                "purpose": data.get("purpose", ""),
            }
        return KnowledgeIntegration(
            package=package,
            knowledge_graph={"nodes": nodes, "edges": edges},
            asset_registry=data.get("asset_registry", []),
            dependencies=normalized_dependencies,
            cross_references=data.get("cross_references", []),
            version_history=data.get("version_history", []),
            purpose=data.get("purpose", ""), creative_intent=data.get("creative_intent", ""),
            reasoning=data.get("reasoning", ""), confidence=data.get("confidence", "inferred"),
        )

    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        prompt = self.build_draft_prompt(pkg)
        from ..models import KnowledgeIntegration
        response_format = KnowledgeIntegration.model_json_schema()
        generator = getattr(self.llm, "generate_json")
        config = getattr(self.llm, "_config", None)
        if config is not None:
            original_max_tokens = config.max_tokens
            config.max_tokens = self._OUTPUT_BUDGET
            try:
                try:
                    response = generator(prompt, "planner", self.phase_name, self.phase_name, response_format=response_format)
                except TypeError:
                    response = generator(prompt, config, "planner")
            finally:
                config.max_tokens = original_max_tokens
        else:
            try:
                response = generator(prompt, "planner", self.phase_name, self.phase_name, response_format=response_format)
            except TypeError:
                response = generator(prompt)
        return self.parse_draft(response)

    def _review_specific(self, knowledge: KnowledgeObject) -> list[str]:
        issues: list[str] = []
        package = getattr(knowledge, "package", None)
        kg = getattr(knowledge, "knowledge_graph", None)
        if not (isinstance(package, dict) and len(package) > 0):
            issues.append("Empty package — must contain integrated knowledge summary")
        if not (isinstance(kg, dict)):
            issues.append("Invalid knowledge_graph structure")
        return issues

    def _validate_specific(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:  # noqa
        from ..models import ValidationIssue  # noqa
        issues: list[ValidationIssue] = []
        package = getattr(knowledge, "package", None)
        kg = getattr(knowledge, "knowledge_graph", None)

        if not (isinstance(package, dict) and len(package) > 0):
            issues.append(ValidationIssue(
                category="schema_error", severity="error",
                location=f"{self.phase_name}.package",
                description="Package must be a non-empty dict with integrated knowledge",
            ))
        if kg is None or not isinstance(kg, dict):
            issues.append(ValidationIssue(
                category="schema_error", severity="error",
                location=f"{self.phase_name}.knowledge_graph",
                description="knowledge_graph must be a dict with nodes and edges",
            ))
        return issues
