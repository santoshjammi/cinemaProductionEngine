"""GENESIS 2 — FastAPI router for the 12-phase Creative Intelligence Engine.

Endpoints:
    POST /api/v1/genesis2/run   Run the full 12-phase GENESIS2 pipeline on a synopsis
    GET  /api/v1/genesis2/health  Check the local LLM (Ollama) is reachable
"""
from __future__ import annotations

import asyncio
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

logger = logging.getLogger("genesis2_api")

router = APIRouter(prefix="/api/v1/genesis2", tags=["genesis2"])

# Local model preference — qwen3:4b is the primary local model for GENESIS2.
PREFERRED_MODELS = ["qwen3:4b", "qwen3.6:latest", "ornith:lite", "deepseek-coder-v2:latest"]


def _model_num_ctx(model_name: str) -> int:
    if model_name == "qwen3:4b":
        return 131072
    if model_name == "qwen3.6:latest":
        return 131072
    if model_name == "ornith:lite":
        return 65536
    return 4096


class Genesis2RunRequest(BaseModel):
    synopsis: str = Field(..., min_length=1, max_length=10_000)
    constraints: dict[str, Any] = Field(default_factory=dict)


class Genesis2PhaseResponse(BaseModel):
    phaseNumber: int
    phaseName: str
    status: str
    draftCount: int
    validationIssues: int
    critiqueFindings: int


class Genesis2RunResponse(BaseModel):
    synopsis: str
    version: str
    created_at: str
    phases: list[Genesis2PhaseResponse]
    totalPhases: int
    completedPhases: int
    failedPhases: int
    package: dict[str, Any] | None = None


@router.get("/health")
async def health():
    """Check the local LLM (Ollama) is reachable for GENESIS2."""
    import urllib.request

    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as resp:
            import json
            data = json.loads(resp.read().decode())
            models = [m.get("name") for m in data.get("models", [])]
            return {"ok": True, "models": models}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@router.post("/run", response_model=Genesis2RunResponse)
async def run_genesis2(req: Genesis2RunRequest):
    """Run the full 12-phase GENESIS2 pipeline on a synopsis (local Ollama)."""
    from movie_os.genesis2 import Genesis2Engine
    from movie_os.genesis2.llm_client import LLMClient
    from movie_os.genesis2.llm_providers import LLMConfig

    last_exc = None
    pkg = None
    for model_name in PREFERRED_MODELS:
        try:
            config = LLMConfig(provider="ollama", model=model_name, timeout=300, max_tokens=4096, num_ctx=_model_num_ctx(model_name))
            client = LLMClient(config=config)
            engine = Genesis2Engine(llm=client)
            logger.info("GENESIS2 using model %s", model_name)
            pkg = await engine.run_async(synopsis=req.synopsis, constraints=req.constraints or {})
            break
        except Exception as exc:
            last_exc = exc
            logger.warning("GENESIS2 failed with %s: %s", model_name, exc)
            pkg = None
    if pkg is None:
        raise HTTPException(status_code=500, detail=f"GENESIS2 failed with all local models: {last_exc}")

    phases = []
    for r in pkg.phase_results:
        phases.append(Genesis2PhaseResponse(
            phaseNumber=r.phase_number,
            phaseName=r.phase_name,
            status=r.status.value if hasattr(r.status, "value") else str(r.status),
            draftCount=r.draft_count,
            validationIssues=len(r.validation_issues),
            critiqueFindings=len(r.critique_findings),
        ))

    completed = sum(1 for p in phases if p.status == "completed")
    failed = sum(1 for p in phases if p.status == "failed")

    return Genesis2RunResponse(
        synopsis=req.synopsis,
        version=getattr(pkg, "version", "1"),
        created_at=datetime.now(timezone.utc).isoformat(),
        phases=phases,
        totalPhases=len(phases),
        completedPhases=completed,
        failedPhases=failed,
        package=pkg.model_dump() if hasattr(pkg, "model_dump") else None,
    )
