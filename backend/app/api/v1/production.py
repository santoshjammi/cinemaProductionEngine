"""Production router — exposes the canonical GENESIS2 → PROMETHEUS → MP4 path.

Endpoints:
    POST /api/v1/production/start   Queue a production run (synopsis → final MP4)
    GET  /api/v1/production/jobs    List all jobs
    GET  /api/v1/production/jobs/{job_id}   Get a single job's status
    GET  /api/v1/production/jobs/{job_id}/video   Stream the final MP4 (if ready)
"""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.app.services.production_service import (
    ProductionService,
    DEFAULT_SYNOPSIS,
    DEFAULT_CONSTRAINTS,
)

logger = logging.getLogger("production_router")

router = APIRouter(prefix="/api/v1/production", tags=["production"])

# Module-level service instance (single-flight job queue).
_service = ProductionService(max_concurrent=1)


class ProductionStartRequest(BaseModel):
    synopsis: str = Field(
        default=DEFAULT_SYNOPSIS,
        min_length=1,
        max_length=10_000,
        description="Story synopsis to produce into a film.",
    )
    constraints: dict[str, object] = Field(
        default_factory=lambda: dict(DEFAULT_CONSTRAINTS),
        description="Optional production constraints (characters, style, tone arc, etc.).",
    )


class ProductionJobResponse(BaseModel):
    job_id: str
    status: str
    stage: str
    error: str | None = None
    run_id: str | None = None
    output_path: str | None = None
    created_at: str
    updated_at: str
    phases: list[dict]
    prometheus_stages: list[dict]


@router.post("/start", response_model=ProductionJobResponse)
async def start_production(req: ProductionStartRequest):
    """Queue a production run. Returns immediately with the job id."""
    job = _service.submit(req.synopsis, req.constraints or {})
    logger.info("Production job %s queued (status=%s)", job.job_id, job.status)
    return job.to_dict()


@router.get("/jobs", response_model=list[ProductionJobResponse])
async def list_jobs():
    """List all production jobs (newest first)."""
    jobs = _service.list_jobs()
    jobs.sort(key=lambda j: j["created_at"], reverse=True)
    return jobs


@router.get("/jobs/{job_id}", response_model=ProductionJobResponse)
async def get_job(job_id: str):
    """Get a single production job's status."""
    job = _service.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Production job {job_id!r} not found")
    return job.to_dict()


@router.get("/jobs/{job_id}/video")
async def get_job_video(job_id: str):
    """Stream the final MP4 for a completed job."""
    job = _service.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Production job {job_id!r} not found")
    if job.status != "completed" or not job.output_path:
        raise HTTPException(status_code=409, detail=f"Job {job_id!r} has no final video yet (status={job.status})")
    path = Path(job.output_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Final video file missing: {path}")
    return FileResponse(str(path), media_type="video/mp4", filename=path.name)
