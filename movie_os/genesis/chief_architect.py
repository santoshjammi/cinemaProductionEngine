"""ChiefArchitect — supervises the entire PKP for cross-spec consistency and readiness."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from movie_os.genesis.master_prompt import build_agent_prompt
from movie_os.genesis.models import ConfidenceLevel, Specification
from movie_os.genesis.pkp_agents.base import PKPAgent

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


# All 19 PKP specifications
ALL_PKP_SPECS = [
    "PKP-00", "PKP-01", "PKP-02", "PKP-03", "PKP-04", "PKP-05",
    "PKP-06", "PKP-07", "PKP-08", "PKP-09", "PKP-10", "PKP-11",
    "PKP-12", "PKP-13", "PKP-14", "PKP-15", "PKP-16", "PKP-17",
    "PKP-18",
]


class ChiefArchitect(PKPAgent):
    name = "chief_architect"
    spec_id = "CHIEF"
    spec_name = "Chief Architect Review"
    phase = "G"
    expected_keys: list[str] = ["overall_assessment", "readiness"]
    dependencies = ALL_PKP_SPECS

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        # Provide every spec's content as context
        context: dict[str, Any] = {}
        for sid in ALL_PKP_SPECS:
            spec = pkg.get_specification(sid)
            if spec is not None:
                context[sid] = {
                    "spec_name": spec.spec_name,
                    "phase": spec.phase,
                    "content": spec.content,
                    "confidence": spec.confidence.value,
                    "validation_status": spec.validation_status,
                }
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "As the Chief Architect, review the entire Production Knowledge Package for: "
                "1) Cross-specification consistency, "
                "2) Creative vision preservation, "
                "3) Scope drift, "
                "4) Grammar compliance, "
                "5) Production readiness. "
                "Respond with JSON containing: overall_assessment, consistency_issues (array), "
                "scope_drift (array), readiness (boolean), confidence."
            ),
            synopsis=pkg.synopsis,
            context=context,
            constraints=pkg.constraints,
        )

    def parse_response(self, response: str, pkg: "ProductionKnowledgeGraph") -> dict[str, Any]:
        from movie_os.genesis.llm_client import LLMClient
        content = LLMClient._extract_json(response)
        content.setdefault("overall_assessment", "")
        content.setdefault("consistency_issues", [])
        content.setdefault("scope_drift", [])
        content.setdefault("readiness", False)
        content.setdefault("confidence", "unknown")
        return content

    def validate(self, content: dict[str, Any], pkg: "ProductionKnowledgeGraph") -> list[str]:
        errors = super().validate(content, pkg)
        if "overall_assessment" not in content:
            errors.append("Missing required field: overall_assessment")
        if "readiness" not in content:
            errors.append("Missing required field: readiness")
        return errors

    def assess_confidence(self, content: dict[str, Any], pkg: "ProductionKnowledgeGraph") -> ConfidenceLevel:
        if isinstance(content, dict) and "confidence" in content:
            try:
                return ConfidenceLevel(content["confidence"])
            except ValueError:
                pass
        return ConfidenceLevel.INFERRED