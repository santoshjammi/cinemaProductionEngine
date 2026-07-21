"""DistributionAgent — generates PKP-16 Distribution Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class DistributionAgent(PKPAgent):
    name = "distribution_agent"
    spec_id = "PKP-16"
    spec_name = "Distribution Specification"
    phase = "G"
    expected_keys: list[str] = ["target_platforms", "delivery_formats", "accessibility", "rating_expectations", "release_strategy"]
    dependencies = ["PKP-02"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Distribution Specification. Define: target platforms, "
                "delivery formats, encoding specs, regional considerations, accessibility "
                "requirements, rating expectations, marketing positioning, and release "
                "strategy. Match distribution plan to project scope and audience. "
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
        required = ["target_platforms", "delivery_formats", "accessibility",
                    "rating_expectations", "release_strategy"]
        for field in required:
            if field not in content:
                errors.append(f"Missing required field: {field}")
        return errors