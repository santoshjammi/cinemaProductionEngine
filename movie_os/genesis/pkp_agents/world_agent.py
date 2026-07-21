"""WorldAgent — generates PKP-05 World Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class WorldAgent(PKPAgent):
    name = "world_agent"
    spec_id = "PKP-05"
    spec_name = "World Specification"
    phase = "B"
    expected_keys: list[str] = ["world_premise", "geography", "time_period", "social_structures", "technology_level", "rules_of_the_world", "key_locations"]
    dependencies = ["PKP-04"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the World Specification. Define: world premise, geography, "
                "time period, social structures, cultural norms, technology level, "
                "economic systems, political systems, rules of the world, key locations, "
                "and world consistency rules. Build the diegetic container in which the "
                "story unfolds. Respond with JSON containing these fields plus a confidence field."
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
        required = ["world_premise", "geography", "time_period", "social_structures",
                    "technology_level", "rules_of_the_world", "key_locations"]
        for field in required:
            if field not in content:
                errors.append(f"Missing required field: {field}")
        return errors