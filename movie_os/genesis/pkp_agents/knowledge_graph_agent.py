"""KnowledgeGraphAgent — generates PKP-18 Knowledge Graph Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class KnowledgeGraphAgent(PKPAgent):
    name = "knowledge_graph_agent"
    spec_id = "PKP-18"
    spec_name = "Knowledge Graph Specification"
    phase = "G"
    expected_keys: list[str] = ["node_taxonomy", "edge_taxonomy", "provenance_policy", "confidence_policy", "query_patterns", "graph_invariants"]
    dependencies: list[str] = []

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Knowledge Graph Specification. Define: node taxonomy, edge "
                "taxonomy, provenance policy, confidence policy, query patterns, graph "
                "invariants, and integration points with downstream systems. Specify how "
                "the Production Knowledge Graph itself is structured and maintained. "
                "Respond with JSON containing these fields plus a confidence field."
            ),
            synopsis=pkg.synopsis,
            context=self.get_dependency_content(pkg),
            constraints=pkg.constraints,
        )

    def parse_response(self, response: str, pkg: "ProductionKnowledgeGraph") -> dict[str, Any]:
        from movie_os.genesis.llm_client import LLMClient
        return LLMClient._extract_json(response)

    def validate(self, content: dict[str, Any], pkg: "ProductionKnowledgeGraph") -> list[str]:
        errors = super().validate(content, pkg)
        required = ["node_taxonomy", "edge_taxonomy", "provenance_policy",
                    "confidence_policy", "query_patterns", "graph_invariants"]
        for field in required:
            if field not in content:
                errors.append(f"Missing required field: {field}")
        return errors