"""Movie OS Workflows — ComfyUI workflow templates and client.

Public API:
    from movie_os.workflows import (
        ComfyUIClient, ComfyUIError,
        load_workflow, list_workflows,
    )

Workflows are JSON files in movie_os/workflows/flux/ that follow
ComfyUI's standard format. The FluxComfyUIProvider loads them
and fills in placeholders before submitting to ComfyUI.
"""

from .comfyui_client import ComfyUIClient, ComfyUIError
from pathlib import Path
import json
import logging
from typing import Any


logger = logging.getLogger("movie_os.workflows")


def _workflows_dir() -> Path:
    """Path to the bundled workflows directory."""
    return Path(__file__).parent


def load_workflow(name: str) -> dict:
    """Load a workflow JSON by name (e.g., 'flux_txt2img').

    Raises FileNotFoundError if the workflow doesn't exist.
    """
    path = _workflows_dir() / "flux" / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Workflow '{name}' not found at {path}. "
            f"Available: {[p.stem for p in (_workflows_dir() / 'flux').glob('*.json')]}"
        )
    with open(path) as f:
        return json.load(f)


def list_workflows() -> list[str]:
    """List all available workflow names."""
    flux_dir = _workflows_dir() / "flux"
    if not flux_dir.exists():
        return []
    return sorted(p.stem for p in flux_dir.glob("*.json"))


def fill_placeholders(workflow: dict, replacements: dict[str, Any]) -> dict:
    """Replace PLACEHOLDER_* strings in a workflow.

    Walks the entire workflow tree and replaces any string matching
    'PLACEHOLDER_<key>' with replacements[key].

    Args:
        workflow: The workflow dict (modified in place AND returned).
        replacements: Map of placeholder name (without PLACEHOLDER_ prefix)
            to replacement value.

    Returns:
        The same workflow dict, mutated.
    """
    def _replace(value):
        if isinstance(value, str):
            for key, replacement in replacements.items():
                placeholder = f"PLACEHOLDER_{key.upper()}"
                if placeholder in value:
                    value = value.replace(placeholder, str(replacement))
        elif isinstance(value, dict):
            return {k: _replace(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [_replace(v) for v in value]
        return value

    mutated = _replace(workflow)
    workflow.clear()
    workflow.update(mutated)
    return workflow


__all__ = [
    "ComfyUIClient", "ComfyUIError",
    "load_workflow", "list_workflows", "fill_placeholders",
]
