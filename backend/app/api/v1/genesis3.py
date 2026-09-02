"""GENESIS 3 — FastAPI router for the full compilers → QA → certification pipeline.

Endpoints:
    POST /api/v1/genesis3/analyze      Run compilers only (returns evidence)
    POST /api/v1/genesis3/review       Run compilers + QA (returns QA report)
    POST /api/v1/genesis3/certify      Run full pipeline (returns certificate)
    GET  /api/v1/genesis3/certificate/{id}  Retrieve a certificate by ID
    GET  /api/v1/genesis3/standards         List all standards
    GET  /api/v1/genesis3/compilers          List all compilers
    GET  /api/v1/genesis3/constitutions     List all constitutions
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from movie_os.genesis3.service import Genesis3Result, Genesis3Service

logger = logging.getLogger("genesis3_api")

router = APIRouter(prefix="/api/v1/genesis3", tags=["genesis3"])

# Module-level service instance (lazily initialised)
_service: Genesis3Service | None = None


def _get_service() -> Genesis3Service:
    global _service
    if _service is None:
        _service = Genesis3Service()
    return _service


# ── Request / response schemas ───────────────────────────────────────────────


class PipelineRequest(BaseModel):
    """Input for analyze, review and certify endpoints."""

    synopsis: str = Field(
        ..., min_length=1, max_length=10_000,
        description="Story synopsis to evaluate.",
    )
    constraints: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional production constraints.",
    )


class AnalyzeResponse(BaseModel):
    pipeline_id: str
    created_at: str
    evidence: dict[str, Any]


class ReviewResponse(BaseModel):
    pipeline_id: str
    created_at: str
    qa_report: Any


class CertifyResponse(BaseModel):
    """Combined full-pipeline output including certificate."""

    pipeline_id: str
    created_at: str
    evidence: dict[str, Any]
    qa_report: dict[str, Any]
    certificate_data: dict[str, Any]


class CertificateResponse(BaseModel):
    certificate_data: Any


# ── In-memory certificate store (sufficient for tests / API demos) ───────────

_certificate_store: dict[str, Any] = {}


def _save_certificate(key: str, cert: Any) -> None:
    """Persist a certificate reference in-process."""
    _certificate_store[key] = cert


# ── Metadata endpoints ───────────────────────────────────────────────────────


@router.get("/compilers")
async def get_compilers():
    """Return the list of available compilers."""
    svc = _get_service()
    return {"compilers": svc.list_compilers()}


@router.get("/standards")
async def get_standards():
    """Return the list of available standards."""
    svc = _get_service()
    return svc.list_standards()


@router.get("/constitutions")
async def get_constitutions():
    """Return the list of available constitutions."""
    svc = _get_service()
    return {"constitutions": svc.list_constitutions()}


# ── Pipeline endpoints ───────────────────────────────────────────────────────


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_endpoint(req: dict[str, Any]):
    """Run all GENESIS 3 compilers on *synopsis* and return structured evidence."""
    synopsis = req.get("synopsis", "") if isinstance(req, dict) else getattr(req, "synopsis", "")
    constraints = req.get("constraints", {}) if isinstance(req, dict) else getattr(getattr(req, "constraints", {}), "model_dump", lambda **kw: {})(**{})
    synopsis_str = str(synopsis).strip()
    if not synopsis_str:
        raise HTTPException(status_code=422, detail="synopsis is required and must be non-empty")

    svc = _get_service()
    evidence = svc.run_compilers_only(synopsis_str, constraints or {})

    return AnalyzeResponse(
        pipeline_id="",
        created_at=datetime.now(timezone.utc).isoformat(),
        evidence=evidence,
    )


@router.post("/review", response_model=ReviewResponse)
async def review_endpoint(req: dict[str, Any]):
    """Run compilers + QA Department and return the full QA report."""
    synopsis = req.get("synopsis", "") if isinstance(req, dict) else getattr(req, "synopsis", "")
    constraints = req.get("constraints", {}) if isinstance(req, dict) else {}
    synopsis_str = str(synopsis).strip()
    if not synopsis_str:
        raise HTTPException(status_code=422, detail="synopsis is required and must be non-empty")

    svc = _get_service()
    evidence = svc.run_compilers_only(synopsis_str, constraints or {})
    # Use run_qa(evidence=...) which internally runs constitutions via _constitutions dict
    qa_report = svc.run_qa(evidence=evidence)

    # Serialize the QA report for JSON transport
    if hasattr(qa_report, "model_dump"):
        qa_data = qa_report.model_dump()
    else:
        qa_data = dict(qa_report.__dict__) if hasattr(qa_report, "__dict__") else qa_report

    return ReviewResponse(
        pipeline_id="",
        created_at=datetime.now(timezone.utc).isoformat(),
        qa_report=qa_data,
    )


@router.post("/certify", response_model=CertifyResponse)
async def certify_endpoint(req: dict[str, Any]):
    """Run the full pipeline and return a Production Readiness Certificate."""
    synopsis = req.get("synopsis", "") if isinstance(req, dict) else getattr(req, "synopsis", "")
    constraints = req.get("constraints", {}) if isinstance(req, dict) else {}
    synopsis_str = str(synopsis).strip()
    if not synopsis_str:
        raise HTTPException(status_code=422, detail="synopsis is required and must be non-empty")

    svc = _get_service()
    # Run the full pipeline in one call
    result = svc.run_full_pipeline(synopsis_str, constraints or {})

    cert_data = {}
    if hasattr(result.certificate, "model_dump"):
        cert_data = result.certificate.model_dump()
    elif hasattr(result.certificate, "__dict__"):
        cert_data = dict(result.certificate.__dict__)
    elif isinstance(result.certificate, dict):
        cert_data = result.certificate

    # Persist for later /certificate/{id} retrieval
    _save_certificate(cert_data.get("certification_id", ""), cert_data)

    return CertifyResponse(
        pipeline_id=result.pipeline_id,
        created_at=result.created_at,
        evidence=result.evidence,
        qa_report=result.qa_report if isinstance(result.qa_report, dict) else {},
        certificate_data=cert_data,
    )


@router.get("/certificate/{cert_id}")
async def get_certificate(cert_id: str):
    """Retrieve a previously issued certificate by its ID."""
    cert = _certificate_store.get(cert_id)

    if cert is None:
        raise HTTPException(status_code=404, detail=f"Certificate {cert_id!r} not found")

    if hasattr(cert, "model_dump"):
        return {"certificate_data": cert.model_dump()}
    elif hasattr(cert, "__dict__"):
        return {"certificate_data": dict(cert.__dict__)}
    else:
        return {"certificate_data": cert}
