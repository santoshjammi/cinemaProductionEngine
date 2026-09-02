"""GENESIS 1 — FastAPI router for the pre-production intelligence engine.

Endpoints:
    POST /api/v1/genesis/run   Run the full Genesis pipeline (discovery → PKP → review → gate)
    GET  /api/v1/genesis/{session_id}  Retrieve a completed Genesis session result
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

logger = logging.getLogger("genesis_api")

router = APIRouter(prefix="/api/v1/genesis", tags=["genesis"])

# In-memory session store (sufficient for API demos / tests).
_session_store: dict[str, dict[str, Any]] = {}


class GenesisRunRequest(BaseModel):
    synopsis: str = Field(..., min_length=1, max_length=10_000)
    constraints: dict[str, Any] = Field(default_factory=dict)


def _map_specs(specifications: dict[str, Any]) -> list[dict[str, Any]]:
    """Map the engine's specifications dict to the frontend GenesisSpecGroup shape."""
    specs = []
    for sid, s in (specifications or {}).items():
        specs.append({
            "specId": sid,
            "specName": s.get("spec_name", sid),
            "phase": s.get("phase", ""),
            "fields": [],
            "validationStatus": s.get("validation_status", "pending"),
            "confidence": s.get("confidence", "unknown"),
        })
    return specs


@router.post("/run")
async def run_genesis(req: GenesisRunRequest):
    """Run the full Genesis pipeline on a synopsis."""
    from movie_os.genesis import GenesisEngine
    from movie_os.genesis.llm_ollama import OllamaClient

    try:
        llm = OllamaClient(model="qwen3.6:latest")
        engine = GenesisEngine(llm=llm)
        result = await engine.run_async(synopsis=req.synopsis, constraints=req.constraints or {})
    except Exception as exc:
        logger.exception("Genesis pipeline failed")
        raise HTTPException(status_code=500, detail=f"Genesis pipeline failed: {exc}")

    gate = result.get("gate_result", {})
    specs = _map_specs(result.get("specifications", {}))

    # Completeness: average of per-phase completeness (0..1).
    completeness = 0.0
    pkg_completeness = result.get("completeness", {})
    if isinstance(pkg_completeness, dict) and pkg_completeness:
        completeness = sum(pkg_completeness.values()) / len(pkg_completeness)

    payload = {
        "sessionId": result.get("session_id", ""),
        "completeness": completeness,
        "gatePassed": bool(gate.get("passed", False)),
        "specs": specs,
        "discovery": result.get("discovery_results", []),
        "reviews": result.get("review_results", []),
        "raw": result,
    }
    _session_store[payload["sessionId"]] = payload
    return payload


@router.get("/{session_id}")
async def get_genesis_result(session_id: str):
    """Retrieve a previously completed Genesis session result."""
    result = _session_store.get(session_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Genesis session {session_id!r} not found")
    return result
