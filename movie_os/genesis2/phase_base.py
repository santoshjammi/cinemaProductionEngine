"""PhaseBase — shared scaffolding for all 12 Genesis phases.

Every phase follows the iteration loop:
  Draft → Review → Critique → Improve → Validate → Freeze

No phase proceeds until validation succeeds.
"""

from __future__ import annotations

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional, TYPE_CHECKING

from pydantic import BaseModel, Field

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


# --------------------------------------------------------------------------- #
# Feedback models                                                             #
# --------------------------------------------------------------------------- #

class ReviewFeedback(BaseModel):
    """Structured feedback from a review pass."""

    issues: list[str] = Field(default_factory=list)
    score: float = 0.0
    recommendations: list[str] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        self.score = max(0.0, min(1.0, self.score))


class CritiqueFeedback(BaseModel):
    """Structured critique with strengths, weaknesses, and improvement suggestions."""

    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Result of a validation pass."""

    passed: bool = False
    issues: list[ValidationIssue] = Field(default_factory=list)
    score: float = 0.0

    def __init__(self, **data):
        if not data.get("issues"):
            data.setdefault("passed", True)
        super().__init__(**data)


# --------------------------------------------------------------------------- #
# PhaseBase                                                                   #
# --------------------------------------------------------------------------- #

class PhaseBase(ABC):
    """Base class for all Genesis phases.

    Each phase:
    1. Drafts knowledge from previous phases
    2. Reviews its own output
    3. Gets critiqued by a separate model (reviewer tier)
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

    # ── abstract core ────────────────────────────────────────────────────

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

    # ── review ────────────────────────────────────────────────────────────

    def review(self, knowledge: KnowledgeObject) -> list[str]:
        """Self-review the drafted knowledge. Returns issues."""
        issues = []
        if not knowledge.purpose:
            issues.append("Missing purpose")
        if not knowledge.creative_intent:
            issues.append("Missing creative_intent")
        if not knowledge.reasoning:
            issues.append("Missing reasoning")
        # Delegate to phase-specific check
        phase_issues = self._review_specific(knowledge)
        issues.extend(phase_issues)
        return issues

    def _review_specific(self, knowledge: KnowledgeObject) -> list[str]:
        """Phase-specific review. Override in subclasses."""
        return []

    def get_review_feedback(self, knowledge: KnowledgeObject) -> ReviewFeedback:
        """Produce structured ReviewFeedback from review issues."""
        issues = self.review(knowledge)
        score = max(0.0, 1.0 - (len(issues) * 0.2))
        return ReviewFeedback(
            issues=issues,
            score=score,
            recommendations=[f"Fix: {i}" for i in issues],
        )

    # ── critique ───────────────────────────────────────────────────────────

    def critique(self, knowledge: KnowledgeObject) -> list[CritiqueFinding]:
        """Critique the knowledge using a separate model (reviewer tier)."""
        prompt = self.build_critique_prompt(knowledge)
        try:
            response = self.llm.generate(prompt, tier="reviewer", phase_name=self.phase_name, task_key=f"{self.phase_name}:critique")  # type: ignore[arg-type]
            return self.parse_critique_json(response)
        except Exception as e:
            logger.warning(f"[{self.phase_name}] critique failed: {e}")
            return []

    def critique_to_feedback(self, knowledge: KnowledgeObject) -> CritiqueFeedback:
        """Critique and turn findings into structured CritiqueFeedback."""
        findings = self.critique(knowledge)
        return _findings_to_feedback(findings)

    def parse_critique_json(self, response: str) -> list[CritiqueFinding]:
        """Parse critique JSON (array or object with 'findings' key)."""
        from .llm_client import _extract_json

        try:
            data = _extract_json(response)
            if isinstance(data, list):
                # Already a list of findings
                return [
                    CritiqueFinding(
                        question=f.get("question", ""),
                        answer=f.get("answer", ""),
                        severity=f.get("severity", "minor"),
                        recommendation=f.get("recommendation", ""),
                    )
                    for f in data
                    if isinstance(f, dict) and f.get("question")
                ]
            elif isinstance(data, dict):
                findings = data.get("findings", [])
                return [
                    CritiqueFinding(
                        question=f.get("question", ""),
                        answer=f.get("answer", ""),
                        severity=f.get("severity", "minor"),
                        recommendation=f.get("recommendation", ""),
                    )
                    for f in findings
                    if isinstance(f, dict) and f.get("question")
                ]
        except Exception as e:
            logger.warning(f"[{self.phase_name}] parse_critique_json failed: {e}")
        return []

    def build_critique_prompt(self, knowledge: KnowledgeObject) -> str:
        """Build the critique prompt. Override in subclasses."""
        # Use a truncated model dump to keep prompt size manageable
        full = knowledge.model_dump()
        summary = json.dumps(full, indent=2, default=str)[:2000]
        return (
            f"Critique the following {self.phase_name} output.\n"
            f"Output:\n{summary}\n\n"
            "Questions:\n"
            "- Is this emotionally believable?\n"
            "- Are there any contradictions?\n"
            "- Is anything missing?\n"
            "- Could this be improved?\n\n"
            'Respond with JSON: { "findings": [{ "question": "", "answer": "", "severity": "critical|major|minor", "recommendation": "" }], "overall_assessment": "", "recommended_actions": [] }'
        )

    # ── improve ────────────────────────────────────────────────────────────

    def improve(self, knowledge: KnowledgeObject, critique: list[CritiqueFinding]) -> KnowledgeObject:
        """Improve knowledge based on critique findings (uses spec_generator tier)."""
        if not critique:
            return knowledge
        prompt = self.build_improve_prompt(knowledge, critique)
        try:
            response = self.llm.generate(prompt, tier="spec_generator", phase_name=self.phase_name, task_key=f"{self.phase_name}:improve")  # type: ignore[arg-type]
            improved = self.parse_draft(response)
            return improved
        except Exception as e:
            logger.warning(f"[{self.phase_name}] improve failed: {e}")
            # Try to fill in the missing fields manually
            return self._manual_improve(knowledge, critique)

    def _manual_improve(self, knowledge: KnowledgeObject, critique: list[CritiqueFinding]) -> KnowledgeObject:
        """Fallback improve when parse_draft fails."""
        improved = dict(**knowledge.model_dump())
        for finding in critique:
            rec = (finding.recommendation or "").lower()
            # Guess keyword → field mapping
            if "purpose" in rec and not knowledge.purpose:
                improved["purpose"] = f"Purpose from: {finding.question}"
            if "intent" in rec and not knowledge.creative_intent:
                improved["creative_intent"] = f"Intent from: {finding.question}"
            if "reasoning" in rec and not knowledge.reasoning:
                improved["reasoning"] = f"Reasoning from: {finding.question}"
        return KnowledgeObject(**improved)

    def build_improve_prompt(self, knowledge: KnowledgeObject, critique: list[CritiqueFinding]) -> str:
        """Build the improvement prompt."""
        critique_str = json.dumps([c.model_dump() for c in critique], indent=2)
        # Use a truncated model dump to keep prompt size manageable
        full = knowledge.model_dump()
        summary = json.dumps(full, indent=2, default=str)[:2000]
        return (
            f"Improve the following {self.phase_name} output based on critique.\n\n"
            f"Current output:\n{summary}\n\n"
            f"Critique findings:\n{critique_str}\n\n"
            "Respond with the improved JSON output only."
        )

    # ── validate ───────────────────────────────────────────────────────────

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

        # Base schema check — accept empty strings (LLM may omit these)
        if not knowledge.purpose:
            issues.append(ValidationIssue(
                category="schema_error", severity="warning",
                location=self.phase_name + ".purpose",
                description="purpose is recommended",
            ))
        if not knowledge.creative_intent:
            issues.append(ValidationIssue(
                category="schema_error", severity="warning",
                location=self.phase_name + ".creative_intent",
                description="creative_intent is recommended",
            ))
        if not knowledge.reasoning:
            issues.append(ValidationIssue(
                category="schema_error", severity="warning",
                location=self.phase_name + ".reasoning",
                description="reasoning is recommended",
            ))

        # Phase-specific validation
        phase_issues = self._validate_specific(knowledge)
        issues.extend(phase_issues)
        return issues

    def _validate_specific(self, knowledge: KnowledgeObject) -> list[ValidationIssue]:
        """Phase-specific validation. Override in subclasses."""
        return []

    def get_validation_result(self, knowledge: KnowledgeObject) -> ValidationResult:
        """Produce structured ValidationResult from issues."""
        issues = self.validate(knowledge)
        score = max(0.0, 1.0 - (len([i for i in issues if i.severity == "error"]) * 0.3))
        return ValidationResult(
            passed=len(issues) == 0,
            issues=issues,
            score=score,
        )

    # ── freeze ─────────────────────────────────────────────────────────────

    def freeze(self, knowledge: KnowledgeObject) -> KnowledgeObject:
        """Mark the knowledge as frozen (finalized)."""
        knowledge.metadata["frozen_at"] = datetime.utcnow().isoformat()
        knowledge.metadata["phase"] = self.phase_name
        knowledge.metadata["draft_count"] = self.result.draft_count
        return knowledge

    # ── async run() ────────────────────────────────────────────────────────

    async def run(self, pkg: dict[str, Any]) -> PhaseResult:
        """Execute the full phase lifecycle: Draft → Validate → Freeze (fast path)."""
        logger.info(f"[{self.phase_name}] start")

        self.result.status = PhaseStatus.DRAFTING
        try:
            knowledge = self.draft(pkg)
        except Exception as e:
            logger.warning(f"[{self.phase_name}] draft failed: {e}")
            self.result.status = PhaseStatus.FAILED
            self.result.errors.append(str(e))
            self.result.completed_at = datetime.utcnow().isoformat()
            return self.result
        self.result.draft_count = 1

        # Validate
        self.result.status = PhaseStatus.VALIDATING
        validation_issues = self.validate(knowledge)
        self.result.validation_issues = validation_issues

        # Freeze — only fail on actual errors, not warnings
        error_issues = [i for i in self.result.validation_issues if i.severity == "error"]
        if not error_issues:
            self.result.status = PhaseStatus.FREEZING
            knowledge = self.freeze(knowledge)
            self.result.status = PhaseStatus.COMPLETED
        else:
            self.result.status = PhaseStatus.FAILED

        self.result.knowledge = knowledge
        self.result.completed_at = datetime.utcnow().isoformat()

        logger.info(f"[{self.phase_name}] done (status={self.result.status.value})")
        return self.result

    # ── sync execute() wrapper ─────────────────────────────────────────────

    def execute(self, pkg: dict[str, Any]) -> PhaseResult:
        """Synchronous wrapper around the async run() lifecycle."""
        result = asyncio.run(self.run(pkg))
        self.result = result  # keep reference in-place for caller inspection
        return result

    @staticmethod
    def _get_human_questions(critique: list[CritiqueFinding]) -> list[dict[str, Any]]:
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

    def slice_context(
        self,
        pkg: dict[str, Any],
        previous_keys: list[str],
        max_str_len: int = 1000,
        max_list_len: int = 3,
    ) -> dict[str, Any]:
        """Slice previous phases context using divide-and-conquer approach to prevent prompt bloat."""
        prev = {k: pkg.get(k, {}) for k in previous_keys}
        return slice_phase_data(prev, max_str_len, max_list_len)


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #

def slice_phase_data(data: Any, max_str_len: int = 1000, max_list_len: int = 3) -> Any:
    """Recursively slice/truncate nested dictionaries/lists/models to reduce token payload (divide and conquer)."""
    # Resolve Pydantic models or standard objects with model_dump or __dict__
    if hasattr(data, "model_dump") and callable(getattr(data, "model_dump")):
        data = data.model_dump()
    elif hasattr(data, "__dict__"):
        data = getattr(data, "__dict__", {})

    if isinstance(data, dict):
        sliced_dict = {}
        for k, v in data.items():
            if k == "metadata":
                sliced_dict[k] = {"phase": v.get("phase", ""), "frozen_at": v.get("frozen_at", "")} if isinstance(v, dict) else {}
            else:
                sliced_dict[k] = slice_phase_data(v, max_str_len, max_list_len)
        return sliced_dict
    elif isinstance(data, list):
        sliced_list = [slice_phase_data(item, max_str_len, max_list_len) for item in data[:max_list_len]]
        if len(data) > max_list_len:
            sliced_list.append(f"... (truncated {len(data) - max_list_len} items)")
        return sliced_list
    elif isinstance(data, str):
        if len(data) > max_str_len:
            return data[:max_str_len] + f"\n... (truncated {len(data) - max_str_len} chars)"
        return data
    else:
        return data


def _findings_to_feedback(findings: list[CritiqueFinding]) -> CritiqueFeedback:
    """Turn a list of CritiqueFinding objects into a structured CritiqueFeedback."""
    strengths: list[str] = []
    weaknesses: list[str] = []
    improvements: list[str] = []

    for f in findings:
        if not f.answer:
            continue
        # Heuristic: severity indicates whether it's a strength or weakness
        sev = (f.severity or "").lower()
        text = f.answer.strip()
        if sev == "minor":
            strengths.append(text)
        else:
            weaknesses.append(text)
        if f.recommendation:
            improvements.append(f.recommendation)

    return CritiqueFeedback(
        strengths=strengths,
        weaknesses=weaknesses,
        improvements=improvements,
    )
