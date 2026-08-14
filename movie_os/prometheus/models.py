"""PROMETHEUS production models.

Pydantic models shared across the Prometheus pipeline: certificates, stages,
artifacts, and results.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Production Certificate (GENESIS2 output)
# ---------------------------------------------------------------------------

class CertificationStatus(str, Enum):
    DRAFT = "draft"
    REVISION_REQUIRED = "revision_required"
    PRODUCTION_READY = "production_ready"


class Director(BaseModel):
    """The director who approved the blueprint."""
    name: str
    role: str = "director"


class CinematicReviewers(BaseModel):
    """Review results from GENESIS2's automated reviewers."""
    color_reviewer: dict[str, Any]
    lighting_reviewer: dict[str, Any]
    continuity_reviewer: dict[str, Any]
    audio_director_reviewer: dict[str, Any]


class ProductionCertificate(BaseModel):
    """A GENESIS-certified blueprint that has passed all cinematic reviews.

    Only production-ready certificates can be handed off to PROMETHEUS
    for rendering.
    """
    certificate_id: str
    project_name: str
    version: str = "1.0"

    # Blueprint payload — the structured plan from GENESIS2
    blueprint: dict[str, Any] = Field(default_factory=dict)

    # Certification metadata
    status: CertificationStatus
    reviewed_by: Director
    reviewers: Optional[CinematicReviewers] = None
    notes: str = ""

    @property
    def production_ready(self) -> bool:
        return self.status == CertificationStatus.PRODUCTION_READY


# ---------------------------------------------------------------------------
# Production Stage (per-stage bookkeeping)
# ---------------------------------------------------------------------------

class Artifact(BaseModel):
    """A produced artifact within a stage."""
    type: str          # "storyboard", "image", "audio", "music", "video", "film"
    path: str
    url: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProductionStage(BaseModel):
    """Bookkeeping for a single production stage."""

    name: str
    status: str = "pending"            # "pending" | "running" | "completed" | "failed"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    artifacts: list[Artifact] = Field(default_factory=list)
    error: Optional[str] = None

    def start(self) -> None:
        self.status = "running"
        self.started_at = datetime.utcnow()

    def complete(self, artifacts: list[Artifact] | None = None, metadata: dict[str, Any] | None = None) -> None:
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        if artifacts:
            self.artifacts.extend(artifacts)
        if metadata:
            for d in artifacts or []:
                if metadata and (m := metadata.get(d.type, metadata)):  # type: ignore[assignment]
                    d.metadata.update(m)

    def fail(self, error: str) -> None:
        self.status = "failed"
        self.completed_at = datetime.utcnow()
        self.error = error


# ---------------------------------------------------------------------------
# PipelineResult (final output of PrometheusPipeline.execute)
# ---------------------------------------------------------------------------

class OverallStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class PrometheusResult(BaseModel):
    """Result of executing a full production pipeline."""
    certificate_id: str
    project_name: str
    stages: list[ProductionStage]
    overall_status: OverallStatus
    output_path: Optional[str] = None
    duration_seconds: float = 0.0
    artifacts: list[Artifact] = Field(default_factory=list)
