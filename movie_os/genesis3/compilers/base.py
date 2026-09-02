"""GENESIS 3 — Quality Assurance Compilers base models.

Every compiler takes a story synopsis and produces structured
evidence about one dimension of story quality. This is not
"checking" — it is Quality Assurance, like Pixar's story department.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Literal

from pydantic import BaseModel, Field


class Finding(BaseModel):
    """A single finding from a compiler's analysis."""

    category: str
    status: Literal["pass", "fail", "warning", "info"]
    statement: str  # e.g. "Character arc complete"
    detail: str
    references: list[str] = Field(default_factory=list)


class EvidenceItem(BaseModel):
    """One piece of supporting evidence attached to a finding."""

    claim: str  # e.g. "Emotional payoff earned"
    supporting_text: str  # excerpt from analysis
    source: str  # which part of the story this comes from


class CompilerEvidence(BaseModel):
    """Structured evidence output by any compiler."""

    compiler_name: str
    dimension: str
    findings: list[Finding] = Field(default_factory=list)
    evidence_items: list[EvidenceItem] = Field(default_factory=list)
    confidence: float = 0.0  # 0.0-1.0
    summary: str = ""


class BaseCompiler(ABC):
    """Abstract base for all GENESIS story-quality compilers.

    Each compiler:
    1. Takes a synopsis + constraints
    2. Analyzes its dimension
    3. Produces structured evidence (not scores)
    4. Evidence is used by the QA Department for constitutional review
    """

    name: str = ""
    dimension: str = ""

    @abstractmethod
    def compile(self, synopsis: str, constraints: dict[str, Any] | None = None) -> CompilerEvidence: ...
