"""ProductionDesignAgent — generates PKP-11 Production Design Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class ProductionDesignAgent(PKPAgent):
    name = "production_design_agent"
    spec_id = "PKP-11"
    spec_name = "Production Design Specification"
    phase = "E"
    expected_keys: list[str] = ["design_concept", "color_palette", "set_design", "location_design", "props_philosophy", "costume_design"]
    dependencies = ["PKP-05"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Production Design Specification. Define: overall design concept, "
                "color palette, texture language, set design principles, location design, "
                "props philosophy, costume design, makeup design, and visual mood references. "
                "Materialize the world into physical/visual design language. "
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
        required = ["design_concept", "color_palette", "set_design", "location_design",
                    "props_philosophy", "costume_design"]
        for field in required:
            if field not in content:
                errors.append(f"Missing required field: {field}")
        return errors