"""CreativeStrategyAgent — generates PKP-01 Creative Strategy Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class CreativeStrategyAgent(PKPAgent):
    name = "creative_strategy_agent"
    spec_id = "PKP-01"
    spec_name = "Creative Strategy Specification"
    phase = "A"
    expected_keys: list[str] = ["strategic_positioning", "genre_tone_strategy", "thematic_priorities", "audience_targeting", "differentiation", "emotional_journey", "creative_pillars"]
    dependencies = ["PKP-00"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Creative Strategy Specification. Define: strategic positioning, "
                "genre and tone strategy, thematic priorities, audience targeting strategy, "
                "differentiation approach, emotional journey map, and creative pillars. "
                "Translate the vision into actionable creative strategy. "
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
        required = ["strategic_positioning", "genre_tone_strategy", "thematic_priorities",
                    "audience_targeting", "differentiation", "emotional_journey",
                    "creative_pillars"]
        for field in required:
            if field not in content:
                errors.append(f"Missing required field: {field}")
        return errors