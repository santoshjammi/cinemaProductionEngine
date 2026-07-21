"""PKP Agent base class — shared scaffolding for all 19 PKP domain agents."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

from movie_os.genesis.models import AgentResult, ConfidenceLevel, Specification

if TYPE_CHECKING:
    from movie_os.genesis.pkg import ProductionKnowledgeGraph
    from movie_os.genesis.llm_client import LLMClient, MockLLMClient


logger = logging.getLogger("movie_os.genesis.pkp")


class PKPAgent(ABC):
    """Base class for all PKP domain agents.

    Each PKP agent:
    1. Reads its dependencies from the PKG
    2. Calls the LLM with its specific prompt
    3. Parses the response into a specification
    4. Validates the specification
    5. Writes it to the PKG
    6. Returns an AgentResult
    """

    name: str = "pkp_agent"
    spec_id: str = ""          # e.g. "PKP-06"
    spec_name: str = ""        # e.g. "Character Specification"
    phase: str = ""            # e.g. "C"
    dependencies: list[str] = []  # e.g. ["PKP-04", "PKP-05"]
    model_tier: str = "pkp"    # Which HF model tier to use

    def __init__(self, llm: "LLMClient | MockLLMClient"):
        self.llm = llm

    @abstractmethod
    def build_prompt(self, pkg: "ProductionKnowledgeGraph") -> str:
        """Build the LLM prompt for this agent."""
        ...

    @abstractmethod
    def parse_response(self, response: str, pkg: "ProductionKnowledgeGraph") -> dict[str, Any]:
        """Parse the LLM response into specification content."""
        ...

    async def run(self, pkg: "ProductionKnowledgeGraph") -> AgentResult:
        """Execute the agent lifecycle."""
        logger.info(f"[{self.name}] start (spec={self.spec_id})")

        # 1. Check dependencies
        for dep_id in self.dependencies:
            if not pkg.has_specification(dep_id):
                logger.warning(f"[{self.name}] dependency {dep_id} not satisfied")
                return AgentResult(
                    agent_name=self.name, spec_id=self.spec_id,
                    status="skipped",
                    errors=[f"Dependency {dep_id} not satisfied"],
                    confidence=ConfidenceLevel.UNKNOWN,
                )

        # 2. Build prompt
        prompt = self.build_prompt(pkg)

        # 3. Call LLM
        try:
            response = self.llm.generate(prompt)
        except Exception as e:
            logger.error(f"[{self.name}] LLM call failed: {e}")
            return AgentResult(
                agent_name=self.name, spec_id=self.spec_id,
                status="failed", errors=[str(e)],
                confidence=ConfidenceLevel.UNKNOWN,
            )

        # 4. Parse response
        try:
            content = self.parse_response(response, pkg)
        except Exception as e:
            logger.error(f"[{self.name}] parse failed: {e}")
            return AgentResult(
                agent_name=self.name, spec_id=self.spec_id,
                status="failed", errors=[str(e)],
                confidence=ConfidenceLevel.UNKNOWN,
            )

        # 4a. Normalize field names to match expected keys
        content = self._normalize_fields(content)

        # 5. Self-review
        validation_errors = self.validate(content, pkg)
        validation_status = "passed" if not validation_errors else "failed"

        # 6. Assess confidence
        confidence = self.assess_confidence(content, pkg)

        # 7. Create specification
        spec = Specification(
            spec_id=self.spec_id,
            spec_name=self.spec_name,
            phase=self.phase,
            content=content,
            confidence=confidence,
            dependencies=self.dependencies,
            validation_status=validation_status,
            validation_errors=validation_errors,
        )

        # 8. Write to PKG
        pkg.set_specification(spec)

        logger.info(
            f"[{self.name}] done (spec={self.spec_id}, "
            f"confidence={confidence.value}, validation={validation_status})"
        )
        return AgentResult(
            agent_name=self.name, spec_id=self.spec_id,
            status="success" if validation_status == "passed" else "revision_needed",
            confidence=confidence, output=content,
            errors=validation_errors,
        )

    def _normalize_fields(self, content: dict[str, Any]) -> dict[str, Any]:
        """Normalize LLM output field names to match expected keys.

        LLMs often produce variations like 'genre_and_tone_strategy' when
        the agent expects 'genre_tone_strategy'. This method tries to match
        each LLM key to the closest expected key using word-level matching.
        """
        if not content:
            return content

        expected_keys = self._get_expected_keys()
        if not expected_keys:
            return content

        mapping: dict[str, str] = {}
        for llm_key in list(content.keys()):
            if llm_key in expected_keys:
                continue
            llm_words = set(llm_key.lower().replace("-", "_").split("_"))
            llm_words.discard("")
            for exp_key in expected_keys:
                exp_words = set(exp_key.lower().replace("-", "_").split("_"))
                exp_words.discard("")
                # Check if expected words are a subset of LLM words
                if exp_words and exp_words.issubset(llm_words):
                    mapping[llm_key] = exp_key
                    break

        for old_key, new_key in mapping.items():
            if old_key != new_key and new_key not in content:
                content[new_key] = content.pop(old_key)
                logger.debug(f"[{self.name}] normalized field '{old_key}' -> '{new_key}'")

        return content

    def _get_expected_keys(self) -> list[str]:
        """Get the list of expected field keys from the subclass's expected_keys attribute."""
        if hasattr(self, 'expected_keys') and self.expected_keys:
            return list(self.expected_keys)
        return []

    def validate(self, content: dict[str, Any], pkg: "ProductionKnowledgeGraph") -> list[str]:
        """Validate the specification content. Returns list of errors (empty = passed)."""
        errors = []
        if not content:
            errors.append("Empty specification content")
        return errors

    def assess_confidence(self, content: dict[str, Any], pkg: "ProductionKnowledgeGraph") -> ConfidenceLevel:
        """Assess the confidence level of the specification."""
        if isinstance(content, dict) and "confidence" in content:
            raw = content["confidence"]
            # Handle numeric confidence (e.g. 0.8 -> INFERRED)
            if isinstance(raw, (int, float)):
                if raw >= 0.8:
                    return ConfidenceLevel.EXPLICIT
                elif raw >= 0.6:
                    return ConfidenceLevel.INFERRED
                elif raw >= 0.4:
                    return ConfidenceLevel.ASSUMED
                else:
                    return ConfidenceLevel.UNKNOWN
            # Handle string confidence
            try:
                return ConfidenceLevel(raw)
            except ValueError:
                pass
        return ConfidenceLevel.INFERRED

    def get_dependency_content(self, pkg: "ProductionKnowledgeGraph") -> dict[str, Any]:
        """Get the content of all dependency specifications."""
        deps = {}
        for dep_id in self.dependencies:
            spec = pkg.get_specification(dep_id)
            if spec:
                deps[dep_id] = spec.content
        return deps