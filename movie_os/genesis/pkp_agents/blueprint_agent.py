"""BlueprintAgent — generates PKP-15 Production Blueprint Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class BlueprintAgent(PKPAgent):
    name = "blueprint_agent"
    spec_id = "PKP-15"
    spec_name = "Production Blueprint Specification"
    phase = "F"
    expected_keys: list[str] = ["scene_blueprint", "sequence_ordering", "asset_manifest", "production_phases", "delivery_milestones"]
    dependencies = ["PKP-09", "PKP-10", "PKP-11", "PKP-12", "PKP-13", "PKP-14"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Production Blueprint Specification. Integrate narrative, "
                "directorial, design, audio, editing, and animation intents into a unified "
                "production blueprint. Define: scene-by-scene blueprint, sequence ordering, "
                "cross-departmental dependencies, asset manifest, production phases, and "
                "delivery milestones. Reconcile all upstream specs into one executable plan. "
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
        required = ["scene_blueprint", "sequence_ordering", "asset_manifest",
                    "production_phases", "delivery_milestones"]
        for field in required:
            if field not in content:
                errors.append(f"Missing required field: {field}")
        return errors