"""DirectorialAgent — generates PKP-10 Directorial Language Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class DirectorialAgent(PKPAgent):
    name = "directorial_agent"
    spec_id = "PKP-10"
    spec_name = "Directorial Language Specification"
    phase = "E"
    expected_keys: list[str] = ["directorial_vision", "visual_grammar", "shot_vocabulary", "camera_movement", "blocking_principles", "performance_direction"]
    dependencies = ["PKP-09"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Directorial Language Specification. Define: directorial vision, "
                "visual grammar, shot vocabulary, camera movement philosophy, blocking "
                "principles, performance direction, pacing direction, symbolic/motif system, "
                "and reference filmography. Translate narrative into directorial intent. "
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
        required = ["directorial_vision", "visual_grammar", "shot_vocabulary",
                    "camera_movement", "blocking_principles", "performance_direction"]
        for field in required:
            if field not in content:
                errors.append(f"Missing required field: {field}")
        return errors