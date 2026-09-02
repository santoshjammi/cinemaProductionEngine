"""Runtime LLM Call Logger — saves all prompts and responses generated at runtime."""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("movie_os.llm.runtime_logger")


def log_runtime_llm_call(
    prompt: str,
    response: str,
    system_prompt: str = "",
    model: str = "",
    provider: str = "",
    success: bool = True,
    error: str = "",
) -> None:
    """Save the LLM prompt and response to a runtime log directory for auditing/debugging.

    Saved to `output/runtime_prompts/` in the project root.
    """
    try:
        # Find project root (3 levels up from movie_os/llm/runtime_logger.py)
        project_root = Path(__file__).resolve().parent.parent.parent
        log_dir = project_root / "output" / "runtime_prompts"
        log_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename based on time and hash
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        prompt_hash = hashlib.md5(prompt.encode("utf-8", errors="ignore")).hexdigest()[:8]
        filename = f"llm_{timestamp}_{prompt_hash}.json"
        log_file = log_dir / filename

        log_data = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "system_prompt": system_prompt,
            "user_prompt": prompt,
            "response": response,
            "success": success,
            "error": error,
            "phase": "",
            "target_unit": "",
            "context_sources": [],
            "estimated_input_tokens": 0,
            "output_tokens": 0,
            "duration_ms": 0,
            "retries": 0,
            "outcome": "success" if success else "error",
        }

        # Write atomically to prevent partial writes
        tmp_file = log_file.with_suffix(".tmp")
        tmp_file.write_text(json.dumps(log_data, indent=2, default=str), encoding="utf-8")
        tmp_file.rename(log_file)
    except Exception as e:
        logger.warning(f"Failed to log runtime LLM call: {e}")
