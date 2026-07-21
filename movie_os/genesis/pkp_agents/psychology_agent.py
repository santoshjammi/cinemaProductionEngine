"""PsychologyAgent — generates PKP-08 Psychology Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class PsychologyAgent(PKPAgent):
    name = "psychology_agent"
    spec_id = "PKP-08"
    spec_name = "Psychology Specification"
    phase = "C"
    expected_keys: list[str] = ["psychology_profiles"]
    dependencies = ["PKP-06", "PKP-07"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Psychology Specification. For each character define: internal "
                "conflicts, fears, desires, wounds, defense mechanisms, growth edges, "
                "emotional triggers, and psychological arc. Show how relationships pressure "
                "and reveal each character's interior. Respond with JSON containing a "
                "'psychology_profiles' array plus a confidence field."
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
        if "psychology_profiles" not in content:
            errors.append("Missing required field: psychology_profiles")
        elif not isinstance(content["psychology_profiles"], list):
            errors.append("psychology_profiles must be an array")
        return errors