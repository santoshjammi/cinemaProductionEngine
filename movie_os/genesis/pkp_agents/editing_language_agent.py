"""EditingLanguageAgent — generates PKP-13 Editing Language Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class EditingLanguageAgent(PKPAgent):
    name = "editing_language_agent"
    spec_id = "PKP-13"
    spec_name = "Editing Language Specification"
    phase = "E"
    expected_keys: list[str] = ["cutting_philosophy", "rhythm_principles", "transition_vocabulary", "montage_rules", "continuity_conventions", "emotional_pacing"]
    dependencies = ["PKP-09"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Editing Language Specification. Define: cutting philosophy, "
                "rhythm principles, transition vocabulary, montage rules, continuity "
                "conventions, temporal manipulation, and emotional pacing through edit. "
                "Translate narrative pacing into editorial intent. "
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
        required = ["cutting_philosophy", "rhythm_principles", "transition_vocabulary",
                    "montage_rules", "continuity_conventions", "emotional_pacing"]
        for field in required:
            if field not in content:
                errors.append(f"Missing required field: {field}")
        return errors