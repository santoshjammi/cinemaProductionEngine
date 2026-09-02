"""Server-side middleware for tracking application errors."""

import json
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)

_ERRORS_DIR: Path | None = None


def _ensure_errors_dir(path: Path) -> Path:
    global _ERRORS_DIR
    _ERRORS_DIR = path
    return path


def get_error_file_path() -> str | None:
    if _ERRORS_DIR is None:
        return None

    ts = time.strftime("%Y%m%d")
    fp = _ERRORS_DIR / f"errors-{ts}.jsonl"
    return str(fp)


async def log_server_error(
    request_data: dict,
    error_type: str,
    error_message: str,
    stack_trace: str | None = None,
    user_id: str | None = None,
) -> dict[str, object]:
    """Persist a server-side error (JSONL file-based; easily pluggable for Sentry)."""

    payload = {
        "type": error_type,
        "message": error_message,
        "stack_trace": stack_trace,
        "user_id": user_id,
        "url": request_data.get("url", ""),
        "method": request_data.get("method", ""),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "environment": request_data.get("environment", "production"),
    }

    fp = get_error_file_path()
    if fp is not None:
        try:
            with open(fp, "a") as fh:
                fh.write(json.dumps(payload) + "\n")
        except OSError:
            logger.warning("Failed to write error to %s", fp)

    logger.error("%s (%s)", error_message, error_type)
    return {"status": "logged"}
