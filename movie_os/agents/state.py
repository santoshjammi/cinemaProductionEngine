"""MovieState — the shared state passed between agents.

The state is a TypedDict so LangGraph can serialize it. The
underlying Pydantic model (`MovieStateModel`) validates the data
whenever an agent finishes — this catches schema bugs before they
propagate.
"""

from __future__ import annotations

from datetime import datetime
from operator import add
from typing import Annotated, Any, Optional, TypedDict

from pydantic import BaseModel, Field


def _merge_dicts(left: dict, right: dict) -> dict:
    """Reducer that merges two dicts (right wins on conflict)."""
    if not left:
        return right or {}
    if not right:
        return left or {}
    out = dict(left)
    out.update(right)
    return out


def _last(left, right):
    """Reducer that always returns the right value (overwrites on conflict)."""
    return right if right is not None else left


class MovieStateModel(BaseModel):
    """Pydantic validation model for MovieState.

    Not the same as the TypedDict that the graph uses — this
    model is for validation, the TypedDict is for LangGraph
    serialization. They must stay in sync.
    """
    thread_id: str
    brief: dict[str, Any] = Field(default_factory=dict)
    dna: dict[str, Any] = Field(default_factory=dict)
    timeline: Optional[dict[str, Any]] = None
    scene_assets: dict[int, dict[str, Any]] = Field(default_factory=dict)
    qa_report: Optional[dict[str, Any]] = None
    errors: list[str] = Field(default_factory=list)
    current_step: str = "init"
    next_action: Optional[str] = None
    render_attempts: dict[int, int] = Field(default_factory=dict)
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    final_video: Optional[str] = None
    final_video_duration: Optional[float] = None
    final_video_asset_id: Optional[str] = None
    publishing_manifest: Optional[str] = None


class MovieState(TypedDict, total=False):
    """LangGraph state — passed between nodes.

    All keys are optional so a node can return a partial update
    (LangGraph merges updates into the prior state).

    Concurrent branches (visual/voice/music/sfx all run after story)
    need Annotated reducers to merge their writes.
    """
    thread_id: str
    brief: dict[str, Any]
    dna: dict[str, Any]
    timeline: Optional[dict[str, Any]]
    scene_assets: Annotated[dict[int, dict[str, Any]], _merge_dicts]
    qa_report: Optional[dict[str, Any]]
    errors: Annotated[list[str], add]
    current_step: Annotated[str, _last]
    next_action: Optional[str]
    render_attempts: Annotated[dict[int, int], _merge_dicts]
    started_at: Optional[str]
    finished_at: Optional[str]
    final_video: Optional[str]
    final_video_duration: Optional[float]
    final_video_asset_id: Optional[str]
    publishing_manifest: Optional[str]


def new_state(brief: dict[str, Any], thread_id: str) -> MovieState:
    """Build a fresh state for a new run."""
    return MovieState(
        thread_id=thread_id,
        brief=brief,
        dna={},
        timeline=None,
        scene_assets={},
        qa_report=None,
        errors=[],
        current_step="init",
        next_action=None,
        render_attempts={},
        started_at=datetime.utcnow().isoformat(),
        finished_at=None,
    )


def validate_state(state: MovieState) -> None:
    """Validate the state against MovieStateModel. Raises pydantic ValidationError."""
    MovieStateModel.model_validate(dict(state))


def mark_finished(state: MovieState) -> MovieState:
    """Stamp finished_at on the state."""
    state = dict(state)
    state["finished_at"] = datetime.utcnow().isoformat()
    return state  # type: ignore[return-value]
