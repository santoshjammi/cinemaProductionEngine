"""CharacterReviewer — reviews PKP-06, PKP-07, PKP-08 for character consistency."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from movie_os.genesis.master_prompt import build_agent_prompt
from movie_os.genesis.reviewers.base import ReviewAgent

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class CharacterReviewer(ReviewAgent):
    name = "character_reviewer"
    review_key = "character_review"
    specs_to_review = ["PKP-06", "PKP-07", "PKP-08"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        specs = {
            sid: pkg.get_specification(sid).content
            for sid in self.specs_to_review
            if pkg.has_specification(sid)
        }
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Review the Character, Relationship, and Psychology specifications for consistency. "
                "Check: 1) Are character motivations consistent with their psychology? "
                "2) Do relationships align with character traits? "
                "3) Are psychological patterns consistent with character behavior? "
                "4) Are there contradictions? "
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