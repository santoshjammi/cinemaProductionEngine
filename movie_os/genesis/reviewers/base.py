"""Review Agent base class — shared scaffolding for all 3 review agents."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

from movie_os.genesis.models import AgentResult, ConfidenceLevel

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph
    from movie_os.genesis.llm_client import LLMClient, MockLLMClient


logger = logging.getLogger("movie_os.genesis.reviewers")


class ReviewAgent(ABC):
    """Base class for all review agents.

    Review agents don't create content — they validate consistency
    across specifications and can request revisions.
    """

    name: str = "review_agent"
    review_key: str = ""  # Key for storing review result in PKG
    specs_to_review: list[str] = []  # Which spec IDs to check
    model_tier: str = "reviewer"  # Which HF model tier to use

    def __init__(self, llm: "LLMClient | MockLLMClient"):
        self.llm = llm

    @abstractmethod
    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        """Build the review prompt."""
        ...

    @abstractmethod
    def parse_response(self, response: str, pkg: "ProductionKnowledgeGraph") -> dict[str, Any]:
        """Parse the review response into structured findings."""
        ...

    def validate(self, findings: dict[str, Any]) -> list[str]:
        """Validate the parsed findings. Returns list of errors (empty = passed)."""
        errors = []
        if not findings:
            errors.append("Empty review findings")
        return errors

    async def run(self, pkg: "ProductionKnowledgeGraph") -> AgentResult:
        """Execute the review lifecycle."""
        logger.info(f"[{self.name}] start")

        # 1. Build review prompt
        prompt = self.build_prompt(pkg)

        # 2. Call LLM
        try:
            response = self.llm.generate(prompt)
        except Exception as e:
            logger.error(f"[{self.name}] LLM call failed: {e}")
            return AgentResult(
                agent_name=self.name, status="failed",
                errors=[str(e)], confidence=ConfidenceLevel.UNKNOWN,
            )

        # 3. Parse response
        try:
            findings = self.parse_response(response, pkg)
        except Exception as e:
            logger.error(f"[{self.name}] parse failed: {e}")
            return AgentResult(
                agent_name=self.name, status="failed",
                errors=[str(e)], confidence=ConfidenceLevel.UNKNOWN,
            )

        # 4. Validate
        validation_errors = self.validate(findings)
        if validation_errors:
            logger.warning(f"[{self.name}] validation failed: {validation_errors}")
            return AgentResult(
                agent_name=self.name, status="failed",
                errors=validation_errors, confidence=ConfidenceLevel.UNKNOWN,
            )

        # 5. Store review result
        if self.review_key:
            pkg.set_discovery_result(self.review_key, findings)

        # 6. Determine if revisions are needed
        contradictions = findings.get("contradictions", [])
        # Normalize: LLM may return strings instead of dicts
        normalized_errors: list[str] = []
        for c in contradictions:
            if isinstance(c, dict):
                normalized_errors.append(c.get("description", ""))
            else:
                normalized_errors.append(str(c))
        status = "revision_needed" if contradictions else "success"

        logger.info(
            f"[{self.name}] done "
            f"(contradictions={len(contradictions)}, status={status})"
        )
        return AgentResult(
            agent_name=self.name, status=status,
            confidence=ConfidenceLevel.CONFIRMED,
            output=findings, errors=normalized_errors,
        )