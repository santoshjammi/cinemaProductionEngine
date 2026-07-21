"""ResearchAgent — generates PKP-03 Research Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class ResearchAgent(PKPAgent):
    name = "research_agent"
    spec_id = "PKP-03"
    spec_name = "Research Specification"
    phase = "B"
    expected_keys: list[str] = ["research_domains", "key_findings", "factual_anchors", "cultural_context", "technical_references"]
    dependencies = ["PKP-02"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Research Specification. Define: research domains, key findings, "
                "factual anchors, real-world references, cultural context, historical context, "
                "technical references, and open research questions. Ground the production in "
                "verifiable domain knowledge. Respond with JSON containing these fields plus a "
                "confidence field."
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
        required = ["research_domains", "key_findings", "factual_anchors",
                    "cultural_context", "technical_references"]
        for field in required:
            if field not in content:
                errors.append(f"Missing required field: {field}")
        return errors