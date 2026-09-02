"""LLM-based GENESIS3 compilers.

Provides an LLMCompiler base class that uses a real LLM provider
to generate evidence, plus a MockLLMCompiler for testing.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from movie_os.genesis2.llm_providers import LLMConfig, LLMProvider, MockLLMProvider, _extract_json
from movie_os.genesis3.compilers.base import (
    BaseCompiler,
    CompilerEvidence,
    EvidenceItem,
    Finding,
)

logger = logging.getLogger("movie_os.genesis3.compilers.llm")


class LLMCompiler(BaseCompiler, ABC):
    """Abstract base for LLM-powered GENESIS3 compilers.

    Each LLMCompiler:
    1. Takes a synopsis + constraints
    2. Builds a prompt for its analysis dimension
    3. Calls llm.generate_json(prompt) to get structured evidence
    4. Parses the response into CompilerEvidence
    """

    name: str = ""
    dimension: str = ""
    system_prompt: str = ""

    def __init__(self, llm: LLMProvider | None = None, config: LLMConfig | None = None):
        """Initialize with an LLM provider.

        Args:
            llm: LLM provider instance. If None, uses MockLLMProvider.
            config: LLM configuration.
        """
        self._llm = llm or MockLLMProvider()
        self._config = config

    @property
    def llm(self) -> LLMProvider:
        """Get the LLM provider (lazy init to MockLLMProvider)."""
        return self._llm

    @abstractmethod
    def build_prompt(self, synopsis: str, constraints: dict[str, Any] | None = None) -> str:
        """Build the prompt for this compiler's analysis."""
        ...

    def compile(self, synopsis: str, constraints: dict[str, Any] | None = None) -> CompilerEvidence:
        """Run the LLM-based compilation.

        Args:
            synopsis: The story synopsis to analyze.
            constraints: Optional constraints dict.

        Returns:
            CompilerEvidence with findings and evidence items.
        """
        prompt = self.build_prompt(synopsis, constraints)

        try:
            result = self.llm.generate_json(prompt, self._config)
            return self.parse_result(result, synopsis)
        except Exception as e:
            logger.error("LLM compilation failed for %s: %s", self.name, e)
            # Fall back to keyword-based analysis
            return self._fallback_compile(synopsis, constraints)

    def parse_result(self, result: dict[str, Any], synopsis: str) -> CompilerEvidence:
        """Parse LLM JSON result into CompilerEvidence.

        The LLM should return a dict with:
        - findings: list of {category, status, statement, detail, references}
        - evidence_items: list of {claim, supporting_text, source}
        - confidence: float 0-1
        - summary: str
        """
        findings = []
        for f in result.get("findings", []):
            findings.append(Finding(
                category=f.get("category", "unknown"),
                status=f.get("status", "info"),
                statement=f.get("statement", ""),
                detail=f.get("detail", ""),
                references=f.get("references", []),
            ))

        evidence_items = []
        for e in result.get("evidence_items", []):
            evidence_items.append(EvidenceItem(
                claim=e.get("claim", ""),
                supporting_text=e.get("supporting_text", ""),
                source=e.get("source", "llm_analysis"),
            ))

        return CompilerEvidence(
            compiler_name=self.name,
            dimension=self.dimension,
            findings=findings,
            evidence_items=evidence_items,
            confidence=float(result.get("confidence", 0.0)),
            summary=result.get("summary", ""),
        )

    def _fallback_compile(self, synopsis: str, constraints: dict[str, Any] | None = None) -> CompilerEvidence:
        """Fallback keyword-based compilation when LLM is unavailable."""
        logger.warning("Using keyword-based fallback for %s", self.name)
        raw = (synopsis or "").strip().lower()
        return CompilerEvidence(
            compiler_name=self.name,
            dimension=self.dimension,
            findings=[Finding(
                category="llm_fallback",
                status="warning",
                statement="LLM unavailable — using keyword-based analysis",
                detail="Real LLM analysis was requested but the provider failed",
            )],
            confidence=0.0,
            summary=f"LLM compilation failed for {self.name}, using fallback.",
        )


class MockLLMCompiler(BaseCompiler):
    """LLM-based compiler that uses MockLLMProvider for testing.

    Produces deterministic, keyword-based evidence — same as the old
    MockCompiler but with the LLMCompiler interface.
    """

    name = "MockLLM"
    dimension = "Mock LLM Analysis"

    def __init__(self, responses: dict[str, str] | None = None):
        self._mock = MockLLMProvider(responses)
        self._default_responses = {
            "character": '{"findings": [{"category": "character_arc", "status": "pass", "statement": "Character arc present", "detail": "Growth markers found"}], "evidence_items": [{"claim": "Character development exists", "supporting_text": "Growth verbs detected", "source": "synopsis"}], "confidence": 0.7, "summary": "Character analysis complete"}',
            "narrative": '{"findings": [{"category": "structure", "status": "pass", "statement": "Narrative structure present", "detail": "Act markers found"}], "evidence_items": [{"claim": "Story has structure", "supporting_text": "Act structure detected", "source": "synopsis"}], "confidence": 0.7, "summary": "Narrative analysis complete"}',
            "emotion": '{"findings": [{"category": "emotional_range", "status": "pass", "statement": "Emotional range present", "detail": "Emotion words found"}], "evidence_items": [{"claim": "Emotional depth exists", "supporting_text": "Emotion vocabulary detected", "source": "synopsis"}], "confidence": 0.7, "summary": "Emotion analysis complete"}',
            "default": '{"findings": [{"category": "analysis", "status": "pass", "statement": "Analysis complete", "detail": "No specific markers found"}], "evidence_items": [{"claim": "Analysis completed", "supporting_text": "No specific signals", "source": "synopsis"}], "confidence": 0.5, "summary": "Mock LLM analysis complete"}',
        }

    def compile(self, synopsis: str, constraints: dict[str, Any] | None = None) -> CompilerEvidence:
        """Run mock LLM compilation."""
        raw = (synopsis or "").strip().lower()
        if not raw:
            return CompilerEvidence(
                compiler_name=self.name,
                dimension=self.dimension,
                findings=[Finding(
                    category="input",
                    status="fail",
                    statement="Empty synopsis provided",
                    detail="No text to analyze",
                )],
                confidence=0.0,
                summary="Cannot compile empty synopsis.",
            )

        # Determine which mock response to use based on compiler name
        compiler_name = self.name.lower()
        for key, response in self._default_responses.items():
            if key in compiler_name:
                self._mock.set_default(response)
                break

        prompt = f"Analyze this synopsis: {synopsis}"
        result = self._mock.generate_json(prompt)
        return self._parse_mock_result(result)

    def _parse_mock_result(self, result: dict[str, Any]) -> CompilerEvidence:
        """Parse mock LLM result into CompilerEvidence."""
        findings = [Finding(
            category=f.get("category", "unknown"),
            status=f.get("status", "info"),
            statement=f.get("statement", ""),
            detail=f.get("detail", ""),
            references=f.get("references", []),
        ) for f in result.get("findings", [])]

        evidence_items = [EvidenceItem(
            claim=e.get("claim", ""),
            supporting_text=e.get("supporting_text", ""),
            source=e.get("source", "mock_llm"),
        ) for e in result.get("evidence_items", [])]

        return CompilerEvidence(
            compiler_name=self.name,
            dimension=self.dimension,
            findings=findings,
            evidence_items=evidence_items,
            confidence=float(result.get("confidence", 0.5)),
            summary=result.get("summary", "Mock LLM analysis complete"),
        )
