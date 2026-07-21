"""NarrativeReviewer — reviews PKP-09, PKP-10, PKP-13 for narrative/directorial/editing consistency."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from movie_os.genesis.master_prompt import build_agent_prompt
from movie_os.genesis.reviewers.base import ReviewAgent

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class NarrativeReviewer(ReviewAgent):
    name = "narrative_reviewer"
    review_key = "narrative_review"
    specs_to_review = ["PKP-09", "PKP-10", "PKP-13"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        specs = {
            sid: pkg.get_specification(sid).content
            for sid in self.specs_to_review
            if pkg.has_specification(sid)
        }
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Review the Narrative, Directorial Language, and Editing specifications for consistency. "
                "Check: 1) Does the visual language support the narrative? "
                "2) Does the editing rhythm match the pacing? "
                "3) Are there contradictions between narrative and directorial intent? "
                "4) Is the emotional arc supported by the visual language? "
                "Respond with JSON containing: contradictions (array), "
                "recommendations (array), confidence."
            ),
            synopsis=pkg.synopsis,
            context=specs,
            constraints=pkg.constraints,
        )

    def parse_response(self, response: str, pkg: "ProductionKnowledgeGraph") -> dict[str, Any]:
        from movie_os.genesis.llm_client import LLMClient
        findings = LLMClient._extract_json(response)
        findings.setdefault("contradictions", [])
        findings.setdefault("recommendations", [])
        findings.setdefault("confidence", "unknown")
        return findings