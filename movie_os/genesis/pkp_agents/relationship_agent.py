"""RelationshipAgent — generates PKP-07 Relationship Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class RelationshipAgent(PKPAgent):
    name = "relationship_agent"
    spec_id = "PKP-07"
    spec_name = "Relationship Specification"
    phase = "C"
    expected_keys: list[str] = ["relationships"]
    dependencies = ["PKP-06"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Relationship Specification. Define the relational network among "
                "characters: each relationship has source, target, type (familial/romantic/rival/"
                "mentor/etc.), dynamics, history, power balance, conflict potential, and "
                "arc trajectory. Map alliances, tensions, and emotional load. "
                "Respond with JSON containing a 'relationships' array plus a confidence field."
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
        if "relationships" not in content:
            errors.append("Missing required field: relationships")
        elif not isinstance(content["relationships"], list) or len(content["relationships"]) == 0:
            errors.append("relationships must be a non-empty array")
        return errors