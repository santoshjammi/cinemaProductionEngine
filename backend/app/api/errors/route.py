"""Client error report route for the frontend ErrorBoundary reporter."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, FastAPI, Request
from pydantic import BaseModel

logger = logging.getLogger("error_report")

router = APIRouter()


class ClientErrorPayload(BaseModel):
    type: str  # 'react', 'unhandled_rejection', or generic
    message: str
    stack: str | None = None
    component_stack: str | None = None
    url: str = ""
    timestamp: str = ""
    user_agent: str = ""
    environment: str = "production"


_ERRORS_DIR = Path(__file__).parent.parent / ".." / "errors"


def _get_error_path() -> Path:
    _ERRORS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d")
    return _ERRORS_DIR / f"client-errors-{ts}.jsonl"


@router.post("/api/errors/report")
async def report_error(request: Request):
    """Accept a client-side error payload and persist it as JSONL."""
    raw = await request.body()

    try:
        payload = ClientErrorPayload.model_validate_json(raw)
    except Exception:
        # Malformed — still write the raw blob so nothing is lost
        return {"status": "unparsed", "reason": "Invalid JSON"}

    record = {
        "type": payload.type,
        "message": payload.message,
        "stack": payload.stack,
        "component_stack": payload.component_stack,
        "url": payload.url,
        "timestamp": payload.timestamp,
        "user_agent": payload.user_agent,
        "environment": payload.environment,
    }

    fp = _get_error_path()
    try:
        with open(fp, "a") as fh:
            fh.write(json.dumps(record) + "\n")
    except OSError as exc:
        logger.error("Failed to write error file %s: %s", fp, exc)
        return {"status": "error", "detail": str(exc)}

    logger.info(
        "client_error: %s (%s) env=%s url=%s",
        payload.message,
        payload.type,
        payload.environment,
        payload.url[:80],
    )
    return {"status": "logged"}
