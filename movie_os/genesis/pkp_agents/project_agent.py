"""ProjectAgent — generates PKP-02 Project Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class ProjectAgent(PKPAgent):
    name = "project_agent"
    spec_id = "PKP-02"
    spec_name = "Project Specification"
    phase = "A"
    expected_keys: list[str] = ["title", "logline", "format", "target_runtime", "language", "target_audience", "platform", "budget_tier", "production_scope"]
    dependencies = ["PKP-00", "PKP-01"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Project Specification. Define: project title, logline, format "
                "(feature/short/series/episode), target runtime, language, target audience, "
                "platform/distribution target, budget tier, production scope, timeline, and "
                "deliverable specifications. Frame the operational envelope of the production. "
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
        required = ["title", "logline", "format", "target_runtime", "language",
                    "target_audience", "platform", "budget_tier", "production_scope"]
        for field in required:
            if field not in content:
                errors.append(f"Missing required field: {field}")
        return errors