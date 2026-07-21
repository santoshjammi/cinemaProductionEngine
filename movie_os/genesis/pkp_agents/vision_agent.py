"""VisionAgent — generates PKP-00 Vision Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class VisionAgent(PKPAgent):
    name = "vision_agent"
    spec_id = "PKP-00"
    spec_name = "Vision Specification"
    phase = "A"
    expected_keys: list[str] = ["vision_statement", "core_purpose", "intended_impact", "audience_transformation", "creative_philosophy", "success_definition", "non_negotiable_principles"]
    dependencies: list[str] = []

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Vision Specification. Define: vision statement, core purpose, "
                "intended impact, audience transformation, creative philosophy, success definition, "
                "and non-negotiable principles. Distill the creative soul of the project from the synopsis. "
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
        required = ["vision_statement", "core_purpose", "intended_impact",
                    "audience_transformation", "creative_philosophy",
                    "success_definition", "non_negotiable_principles"]
        for field in required:
            if field not in content:
                errors.append(f"Missing required field: {field}")
        return errors