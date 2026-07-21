"""StoryReviewer — reviews PKP-04, PKP-09, PKP-06 for story/narrative/character consistency."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from movie_os.genesis.master_prompt import build_agent_prompt
from movie_os.genesis.reviewers.base import ReviewAgent

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class StoryReviewer(ReviewAgent):
    name = "story_reviewer"
    review_key = "story_review"
    specs_to_review = ["PKP-04", "PKP-09", "PKP-06"]

    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        specs = {
            sid: pkg.get_specification(sid).content
            for sid in self.specs_to_review
            if pkg.has_specification(sid)
        }
        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Review the Story, Narrative, and Character specifications for consistency. "
                "Check: 1) Does the narrative structure support the story's themes? "
                "2) Are character arcs consistent with the story? "
                "3) Are there any contradictions between story and narrative? "
                "4) Is the emotional arc coherent? "
                "Respond with JSON containing: contradictions (array of "
                "{spec_ids, description, severity}), recommendations (array), confidence."
            ),
            synopsis=pkg.synopsis,
            context=specs,
            constraints=pkg.constraints,
        )

    def parse_response(self, response: str, pkg: "ProductionKnowledgeGraph") -> dict[str, Any]:
        from movie_os.genesis.llm_client import LLMClient
        findings = LLMClient._extract_json(response)
        # Normalize required keys
        findings.setdefault("contradictions", [])
        findings.setdefault("recommendations", [])
        findings.setdefault("confidence", "unknown")
        return findings