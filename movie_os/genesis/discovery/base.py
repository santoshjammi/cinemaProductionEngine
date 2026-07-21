"""Discovery Agent base class — shared scaffolding for all 7 discovery agents."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

from movie_os.genesis.models import AgentResult, ConfidenceLevel

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph
    from movie_os.genesis.llm_client import LLMClient, MockLLMClient


logger = logging.getLogger("movie_os.genesis.discovery")


class DiscoveryAgent(ABC):
    """Base class for all discovery agents.

    Each discovery agent:
    1. Reads the synopsis from the PKG
    2. Calls the LLM with its specific prompt
    3. Parses the response into structured knowledge
    4. Validates the parsed result
    5. Writes the result to the PKG's discovery_results
    6. Returns an AgentResult
    """

    name: str = "discovery_agent"
    analysis_key: str = ""  # Key for storing result in PKG
    model_tier: str = "discovery"  # Which HF model tier to use

    def __init__(self, llm: "LLMClient | MockLLMClient"):
        self.llm = llm

    @abstractmethod
    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        """Build the LLM prompt for this agent."""
        ...

    @abstractmethod
    def parse_response(self, response: str, pkg: "ProductionKnowledgeGraph") -> dict[str, Any]:
        """Parse the LLM response into structured knowledge."""
        ...

    def validate(self, content: dict[str, Any]) -> list[str]:
        """Validate the parsed content. Returns list of errors (empty = passed).

        Override in subclasses to add field-specific validation.
        """
        errors = []
        if not content:
            errors.append("Empty discovery result")
        return errors

    async def run(self, pkg: "ProductionKnowledgeGraph") -> AgentResult:
        """Execute the agent lifecycle."""
        logger.info(f"[{self.name}] start")

        # 1. Build prompt
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
            result = self.parse_response(response, pkg)
        except Exception as e:
            logger.error(f"[{self.name}] parse failed: {e}")
            return AgentResult(
                agent_name=self.name, status="failed",
                errors=[str(e)], confidence=ConfidenceLevel.UNKNOWN,
            )

        # 4. Validate
        validation_errors = self.validate(result)
        if validation_errors:
            logger.warning(f"[{self.name}] validation failed: {validation_errors}")
            return AgentResult(
                agent_name=self.name, status="failed",
                errors=validation_errors, confidence=ConfidenceLevel.UNKNOWN,
            )

        # 5. Store in PKG
        if self.analysis_key:
            pkg.set_discovery_result(self.analysis_key, result)

        # 6. Determine confidence
        confidence = self._assess_confidence(result)

        # 7. Summarize (for logging / CLI display)
        summary = self._summarize(result) if hasattr(self, "_summarize") else ""

        logger.info(f"[{self.name}] done (confidence={confidence.value})")
        return AgentResult(
            agent_name=self.name, status="success",
            confidence=confidence, output=result,
        )

    def _assess_confidence(self, result: dict[str, Any]) -> ConfidenceLevel:
        """Assess the confidence level of the discovery result."""
        # If the result has explicit confidence, use it
        if "confidence" in result:
            try:
                return ConfidenceLevel(result["confidence"])
            except ValueError:
                pass
        # Default: inferred (since we extracted it from the synopsis)
        return ConfidenceLevel.INFERRED