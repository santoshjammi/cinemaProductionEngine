"""Psychology Reviewer — validates psychological consistency across specifications.

Reviews PKP-06 (Character), PKP-07 (Relationship), PKP-08 (Psychology),
and PKP-09 (Narrative) for psychological plausibility and consistency.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from movie_os.genesis.reviewers.base import ReviewAgent
from movie_os.genesis.master_prompt import build_agent_prompt

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph


class PsychologyReviewer(ReviewAgent):
    """Reviews psychological consistency across Character, Relationship,
    Psychology, and Narrative specifications."""

    name = "psychology_reviewer"
    review_key = "psychology_review"
    specs_to_review = ["PKP-06", "PKP-07", "PKP-08", "PKP-09"]

    def build_prompt(self, pkg: ProductionKnowledgeGraph) -> str:
        # Gather the specs to review
        specs = {}
        for spec_id in self.specs_to_review:
            spec = pkg.get_specification(spec_id)
            if spec:
                specs[spec_id] = spec.content

        return build_agent_prompt(
            agent_name=self.name,
            agent_instructions=(
                "Review the Character, Relationship, Psychology, and Narrative "
                "specifications for psychological consistency. Check:\n"
                "1. Are character motivations psychologically plausible?\n"
                "2. Do attachment styles align with relationship dynamics?\n"
                "3. Are defense mechanisms consistent with character behavior?\n"
                "4. Do emotional triggers match the narrative events?\n"
                "5. Is the psychological transformation believable?\n"
                "6. Are there any psychological contradictions between specs?\n"
                "7. Does the narrative respect the psychological patterns?\n\n"
                "Respond with JSON containing:\n"
                "- contradictions: array of {spec_ids, description, severity}\n"
                "- psychological_issues: array of {character, issue, recommendation}\n"
                "- recommendations: array of strings\n"
                "- confidence: explicit | inferred | confirmed | assumed | unknown"
            ),
            synopsis=pkg.synopsis,
            context=specs,
            constraints=pkg.constraints,
        )

    def parse_response(self, response: str, pkg: ProductionKnowledgeGraph) -> dict[str, Any]:
        from movie_os.genesis.llm_client import LLMClient
        result = LLMClient._extract_json(response)

        # Normalize the response
        if "contradictions" not in result:
            result["contradictions"] = []
        if "psychological_issues" not in result:
            result["psychological_issues"] = []
        if "recommendations" not in result:
            result["recommendations"] = []

        return result