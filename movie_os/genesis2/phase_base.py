"""PhaseBase — shared scaffolding for all 12 Genesis phases.

Every phase follows the iteration loop:
  Draft → Review → Critique → Improve → Validate → Freeze

No phase proceeds until validation succeeds.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional, TYPE_CHECKING

from .models import (
    ConfidenceLevel,
    CritiqueFinding,
    KnowledgeObject,
    PhaseResult,
    PhaseStatus,
    ValidationIssue,
)

if TYPE_CHECKING:
    from .llm_client import LLMClient, MockLLMClient

logger = logging.getLogger("movie_os.genesis2.phase")


class PhaseBase(ABC):
    """Base class for all Genesis phases.

    Each phase:
    1. Drafts knowledge from previous phases
    2. Reviews its own output
    3. Gets critiqued by a separate model
    4. Improves based on critique
    5. Validates against schema + consistency rules
    6. Freezes when validation passes
    """

    phase_number: int = 0
    phase_name: str = ""
    max_iterations: int = 3
    model_tier: str = "planner"  # planner, reviewer, spec_generator, validator, integrator

    def __init__(self, llm: "LLMClient | MockLLMClient"):
        self.llm = llm
        self.result = PhaseResult(
            phase_number=self.phase_number,
            phase_name=self.phase_name,
        )

    @abstractmethod
    def draft(self, pkg: dict[str, Any]) -> KnowledgeObject:
        """Draft the phase's knowledge from previous phases."""
        ...

    @abstractmethod
    def build_draft_prompt(self, pkg: dict[str, Any]) -> str:
        """Build the prompt for the drafting step."""
        ...

    @abstractmethod
    def parse_draft(self, response: str) -> KnowledgeObject:
        """Parse the LLM response into a knowledge object."""
        ...

    def review(self, knowledge: KnowledgeObject) -> list[str]:
        """Self-review the drafted knowledge. Returns issues."""
        issues = []
        if not knowledge.purpose:
            issues.append("Missing purpose")
        if not knowledge.creative_intent:
            issues.append("Missing creative_intent")
        if not knowledge.reasoning:
            issues.append("Missing reasoning")
        return issues

    def critique(self, knowledge: KnowledgeObject) -> list[CritiqueFinding]:
        """Critique the knowledge using a separate model (reviewer tier)."""
        prompt = self.build_critique_prompt(knowledge)
        try:
            response = self.llm.generate(prompt, tier="reviewer")
            return self.parse_critique(response)
        except Exception as e:
            logger.warning(f"[{self.phase_name}] critique failed: {e}")
            return []

    def build_critique_prompt(self, knowledge: KnowledgeObject) -> str:
        """Build the critique prompt. Override in subclasses."""
        return (
            f"Critique the following {self.phase_name} output.\n"
            f"Output:\n{json.dumps(knowledge.model_dump(), indent=2, default=str)}\n\n"
            f"Questions:\n"
            f"- Is this emotionally believable?\n"
            f"- Are there any contradictions?\n"
            f"- Is anything missing?\n"
            f"- Could this be improved?\n\n"
            f"Respond with JSON: {{ \"findings\": [{{ \"question\": \"\", \"answer\": \"\", \"severity\": \"critical|major|minor\", \"recommendation\": \"\" }}], \"overall_assessment\": \"\", \"recommended_actions\": [] }}"
        )

    def parse_critique(self, response: str) -> list[CritiqueFinding]:
        """Parse the critique response."""
        from .llm_client import _extract_json
        try:
            data = _extract_json(response)
            findings = data.get("findings", [])
            return [
                CritiqueFinding(
                    question=f.get("question", ""),
                    answer=f.get("answer", ""),
                    severity=f.get("severity", "minor"),
                    recommendation=f.get("recommendation", ""),
                )
                for f in findings
            ]
        except Exception as e:
            logger.warning(f"[{self.phase_name}] parse_critique failed: {e}")
            return []

    def improve(self, knowledge: KnowledgeObject, critique: list[CritiqueFinding]) -> KnowledgeObject:
        """Improve knowledge based on critique findings (uses spec_generator tier)."""
        if not critique:
            return knowledge
        prompt = self.build_improve_prompt(knowledge, critique)
        try:
            response = self.llm.generate(prompt, tier="spec_generator")
            improved = self.parse_draft(response)
            return improved
        except Exception as e:
            logger.warning(f"[{self.phase_name}] improve failed: {e}")
            return knowledge

    def build_improve_prompt(self, knowledge: KnowledgeObject, critique: list[CritiqueFinding]) -> str:
        """Build the improvement prompt."""
        return (
            f"Improve the following {self.phase_name} output based on critique.\n\n"
            f"Current output:\n{json.dumps(knowledge.model_dump(), indent=2, default=str)}\n\n"
            f"Critique findings:\n{json.dumps([c.model_dump() for c in critique], indent=2)}\n\n"
            f"Respond with the improved JSON output only."
        )

    def validate(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:
        """Validate the knowledge. Returns issues (empty = passed)."""
        issues: list[ValidationIssue] = []
        if not knowledge:
            issues.append(ValidationIssue(
                category="missing_info", severity="error",
                location=self.phase_name,
                description="Empty knowledge object",
            ))
        return issues

    def freeze(self, knowledge: KnowledgeObject) -> KnowledgeObject:
        """Mark the knowledge as frozen (finalized)."""
        knowledge.metadata["frozen_at"] = datetime.utcnow().isoformat()
        knowledge.metadata["phase"] = self.phase_name
        knowledge.metadata["draft_count"] = self.result.draft_count
        return knowledge

    async def run(self, pkg: dict[str, Any]) -> PhaseResult:
        """Execute the full phase lifecycle: Draft → Review → Critique → Improve → Validate → Freeze."""
        logger.info(f"[{self.phase_name}] start")

        self.result.status = PhaseStatus.DRAFTING
        knowledge = self.draft(pkg)

        for iteration in range(self.max_iterations):
            self.result.draft_count = iteration + 1

            # Review
            self.result.status = PhaseStatus.REVIEWING
            review_issues = self.review(knowledge)
            if review_issues:
                logger.info(f"[{self.phase_name}] review found {len(review_issues)} issues")

            # Critique
            self.result.status = PhaseStatus.CRITIQUING
            critique_findings = self.critique(knowledge)
            self.result.critique_findings = critique_findings

            # Human-in-the-loop: surface questions from critique
            human_questions = self._get_human_questions(critique_findings)
            if human_questions:
                logger.info(f"[{self.phase_name}] {len(human_questions)} questions for human")
                # Store questions in result for the UI to surface
                self.result.errors.extend(
                    f"HUMAN_QUESTION: {q['question']} (default: {q.get('suggested_default', '')})"
                    for q in human_questions
                )

            # Improve
            if critique_findings or review_issues:
                self.result.status = PhaseStatus.IMPROVING
                knowledge = self.improve(knowledge, critique_findings)

            # Validate
            self.result.status = PhaseStatus.VALIDATING
            validation_issues = self.validate(knowledge)
            self.result.validation_issues = validation_issues

            if not validation_issues:
                break

            logger.info(f"[{self.phase_name}] validation failed ({len(validation_issues)} issues), iteration {iteration + 1}")

        # Freeze
        if not self.result.validation_issues:
            self.result.status = PhaseStatus.FREEZING
            knowledge = self.freeze(knowledge)
            self.result.status = PhaseStatus.COMPLETED
        else:
            self.result.status = PhaseStatus.FAILED

        self.result.knowledge = knowledge
        self.result.completed_at = datetime.utcnow().isoformat()

        logger.info(f"[{self.phase_name}] done (status={self.result.status.value})")
        return self.result

    def _get_human_questions(self, critique: list[CritiqueFinding]) -> list[dict[str, Any]]:
        """Extract questions that need human input from critique findings.

        Override in subclasses to surface specific questions.
        """
        questions = []
        for finding in critique:
            if finding.severity == "critical" and finding.recommendation:
                questions.append({
                    "question": finding.question or finding.recommendation,
                    "why_it_matters": finding.answer,
                    "confidence_pct": 0.0,
                    "suggested_default": "",
                })
        return questions
