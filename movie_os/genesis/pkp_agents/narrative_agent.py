"""NarrativeAgent — generates PKP-09 Narrative Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class NarrativeAgent(PKPAgent):
    name = "narrative_agent"
    spec_id = "PKP-09"
    spec_name = "Narrative Specification"
    phase = "D"
    expected_keys: list[str] = ["narrative_structure", "scene_sequence", "pov_strategy", "pacing_curve", "dramatic_beats", "climax", "resolution"]
    dependencies = ["PKP-04", "PKP-08"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Narrative Specification. Define: narrative structure (e.g. "
                "three-act, five-act, non-linear), sequence of scenes/sequences, POV strategy, "
                "pacing curve, dramatic beats, turning points, climax, resolution, and "
                "thematic expression through plot. Reconcile story spine with character "
                "psychology. Respond with JSON containing these fields plus a confidence field."
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
        required = ["narrative_structure", "scene_sequence", "pov_strategy",
                    "pacing_curve", "dramatic_beats", "climax", "resolution"]
        for field in required:
            if field not in content:
                errors.append(f"Missing required field: {field}")
        return errors