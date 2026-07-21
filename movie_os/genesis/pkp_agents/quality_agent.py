"""QualityAgent — generates PKP-17 Quality Specification."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING
from movie_os.genesis.pkp_agents.base import PKPAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class QualityAgent(PKPAgent):
    name = "quality_agent"
    spec_id = "PKP-17"
    spec_name = "Quality Specification"
    phase = "G"
    expected_keys: list[str] = ["quality_criteria", "consistency_checks", "continuity_rules", "performance_quality", "acceptance_gates"]
    dependencies = ["PKP-09", "PKP-10", "PKP-06"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Generate the Quality Specification. Define: quality criteria across narrative, "
                "directorial, and character dimensions; consistency checks; continuity rules; "
                "performance quality bars; technical quality bars; and acceptance gates. "
                "Establish how the production will be evaluated against its own intent. "
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
        required = ["quality_criteria", "consistency_checks", "continuity_rules",
                    "performance_quality", "acceptance_gates"]
        for field in required:
            if field not in content:
                errors.append(f"Missing required field: {field}")
        return errors