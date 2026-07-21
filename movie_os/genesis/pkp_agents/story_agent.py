"""StoryAgent — generates PKP-04 Story Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class StoryAgent(PKPAgent):
    name = "story_agent"
    spec_id = "PKP-04"
    spec_name = "Story Specification"
    phase = "B"
    expected_keys: list[str] = ["premise", "central_conflict", "story_goal", "story_spine", "plot_beats", "thematic_spine", "stakes"]
    dependencies = ["PKP-03"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Story Specification. Define: premise, central conflict, "
                "story goal, story spine (beginning/middle/end), key plot beats, thematic "
                "spine, stakes, and story arc structure. Crystallize the narrative skeleton "
                "from the synopsis and research. Respond with JSON containing these fields "
                "plus a confidence field."
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
        required = ["premise", "central_conflict", "story_goal", "story_spine",
                    "plot_beats", "thematic_spine", "stakes"]
        for field in required:
            if field not in content:
                errors.append(f"Missing required field: {field}")
        return errors