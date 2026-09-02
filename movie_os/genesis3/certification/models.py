"""GENESIS 3 — Certification domain models.

Defines the two core Pydantic models that flow through the certification
pipeline:

* ``ProductionCertificate`` — the output of a successful (or failed, or
  conditional) certification decision.
* ``CertificationRequest`` — the input contract carrying synopsis, evidence,
  and QA review data into the engine.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Literal

from pydantic import BaseModel, Field


class ProductionCertificate(BaseModel):
    """A Production Readiness Certificate issued by the Certification Engine."""

    project_name: str = Field(
        default="", description="Name of the project being certified"
    )
    synopsis_summary: str = Field(
        default="", description="Synopsis of the story under review"
    )
    certification_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique UUID for this certificate",
    )
    issued_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # ── constitutional verdicts (one per dimension) ────────────────
    story_integrity: Literal["PASS", "FAIL", "CONDITIONAL"] = Field(
        default="PASS",
        description="Story integrity verdict",
    )
    psychology: Literal["PASS", "FAIL", "CONDITIONAL"] = Field(
        default="PASS",
        description="Psychological depth verdict",
    )
    character_development: Literal["PASS", "FAIL", "CONDITIONAL"] = Field(
        default="PASS",
        description="Character development verdict",
    )
    narrative_logic: Literal["PASS", "FAIL", "CONDITIONAL"] = Field(
        default="PASS",
        description="Narrative logic verdict",
    )
    emotional_resonance: Literal["PASS", "FAIL", "CONDITIONAL"] = Field(
        default="PASS",
        description="Emotional resonance verdict",
    )
    visual_readiness: Literal["PASS", "FAIL", "CONDITIONAL"] = Field(
        default="PASS",
        description="Visual readiness verdict",
    )
    continuity: Literal["PASS", "FAIL", "CONDITIONAL"] = Field(
        default="PASS",
        description="Continuity verdict",
    )

    # ── overall decision ────────────────────────────────────────────
    production_ready: bool = Field(
        default=False, description="Whether the project is cleared for rendering"
    )
    overall_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Weighted score across all dimensions"
    )

    # ── actionable output ───────────────────────────────────────────
    critical_issues: List[str] = Field(
        default_factory=list, description="Critical issues that must be resolved"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Recommendations for improvement"
    )
    qa_report_summary: str = Field(
        default="", description="Summary from the QA Department report"
    )

    # ── optional rendered form (filled by format_certificate) ───────
    certificate_body: str = Field(
        default="", description="Formatted text body of this certificate"
    )

    # ── mapping between constitution names and our dimension fields ─
    DIMENSION_MAP: ClassVar[Dict[str, str]] = {
        "story": "story_integrity",
        "psychology": "psychology",
        "character": "character_development",
        "narrative": "narrative_logic",
        "emotion": "emotional_resonance",
        "visual": "visual_readiness",
        "continuity": "continuity",
    }


class CertificationRequest(BaseModel):
    """Input to the Certification Engine."""

    synopsis: str = Field(
        description="Story synopsis under review",
    )
    constraints: Dict[str, Any] = Field(
        default_factory=dict, description="Production constraints"
    )
    compiler_evidence: Dict[str, Any] = Field(
        default_factory=dict, description="Evidence keyed by compilation dimension"
    )
    qa_report: Any = Field(
        description="QA Department report from the review phase",
    )
