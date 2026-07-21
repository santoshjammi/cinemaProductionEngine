"""CharacterAgent — generates PKP-06 Character Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class CharacterAgent(PKPAgent):
    name = "character_agent"
    spec_id = "PKP-06"
    spec_name = "Character Specification"
    phase = "C"
    expected_keys: list[str] = ["characters"]
    dependencies = ["PKP-04", "PKP-05"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Character Specification. Define a cast of characters, each with: "
                "name, role (protagonist/antagonist/supporting), archetype, backstory, "
                "physical description, personality traits, motivations, flaws, arc, and "
                "world integration. Each character must serve the story spine. "
                "Respond with JSON containing a 'characters' array plus a confidence field."
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
        if "characters" not in content:
            errors.append("Missing required field: characters")
        elif not isinstance(content["characters"], list) or len(content["characters"]) == 0:
            errors.append("characters must be a non-empty array")
        return errors