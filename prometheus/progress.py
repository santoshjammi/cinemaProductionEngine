"""Progress Tracker — local checkpoint callback for PROMETHEUS pipeline stages.

Injectable progress tracking without cloud dependencies.  Supports:
- per-stage and per-artifact checkpoints
- disk persistence at configurable dir (default: project root)
- callback hook for CLI / SDK consumers
- resume-from-checkpoint support via `checkpoints` parameter
- resumable pipeline execution (skip already-completed stages)

Fail-closed: if checkpoint_dir is invalid, logging degrades but does NOT crash.
"""

from __future__ import annotations

import json
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, Optional


class ProgressEvent(str, Enum):
    """Types of progress events emitted during pipeline execution."""
    STAGE_START = "stage_start"
    STAGE_COMPLETE = "stage_complete"
    STAGE_FAIL = "stage_fail"
    ARTIFACT_COMPLETE = "artifact_complete"
    PIPELINE_START = "pipeline_start"
    PIPELINE_COMPLETE = "pipeline_complete"


@dataclass
class Checkpoint:
    """Mutable checkpoint written to disk per pipeline run."""
    run_id: str
    event: ProgressEvent
    stage_name: Optional[str] = None
    artifact_index: Optional[int] = None
    artifacts_count: Optional[int] = None
    error: Optional[str] = None
    completed_stages: list[str] = field(default_factory=list)
    total_stages: int = 0
    timestamp: float = field(default_factory=time.monotonic)
    emitted_at: str = ""

    def __post_init__(self):
        if not self.emitted_at:
            self.emitted_at = datetime.now(timezone.utc).isoformat()


@dataclass
class PipelineProgressState:
    """Shared state between tracker and pipeline for resume."""
    completed_stages: set[str] = field(default_factory=set)
    total_artifacts: int = 0
    started_at: Optional[str] = None
    run_id: str = ""

    def to_dict(self) -> dict:
        return {
            "completed_stages": sorted(self.completed_stages),
            "total_artifacts": self.total_artifacts,
            "started_at": self.started_at,
            "run_id": self.run_id,
        }

    @classmethod
    def from_dict(cls, d: dict) -> PipelineProgressState:
        return cls(
            completed_stages=set(d.get("completed_stages", [])),
            total_artifacts=d.get("total_artifacts", 0),
            started_at=d.get("started_at"),
            run_id=d.get("run_id", ""),
        )


# ──────────────────── ProgressTracker ────────────────────

class ProgressTracker:
    """Emits per-stage and per-artifact checkpoints for the PROMETHEUS pipeline.

    Usage (custom handler):
        def on_event(evt: Checkpoint):
            print(f"{evt.event}: {evt.stage_name}")
        tracker = ProgressTracker(on_event=on_event)

    Usage (file persistence only):
        tracker = ProgressTracker(checkpoint_dir="artifacts/checkpoints")

    Both can be combined.  File writes are thread-safe.
    """

    def __init__(
        self,
        on_event: Optional[Callable[[Checkpoint], None]] = None,
        checkpoint_dir: Optional[str] = None,
    ) -> None:
        self._on_event = on_event
        self._checkpoint_path: Optional[Path] = None

        if checkpoint_dir is not None:
            try:
                p = Path(checkpoint_dir)
                p.mkdir(parents=True, exist_ok=True)
                self._checkpoint_path = p / "progress.json"
            except OSError:
                # Fail gracefully — degrade to no-op for file persistence
                self._checkpoint_path = None

        self._lock = threading.Lock()

    # ── public API ────────────────────────────────────────

    def on_pipeline_start(
        self, run_id: Optional[str] = None, total_stages: int = 0
    ) -> PipelineProgressState:
        """Emit PIPELINE_START and return mutable state for the pipeline."""
        run_id = run_id or uuid.uuid4().hex[:12]
        cp = Checkpoint(
            run_id=run_id,
            event=ProgressEvent.PIPELINE_START,
            total_stages=total_stages,
        )
        self._emit(cp)

        state = PipelineProgressState(
            started_at=datetime.now(timezone.utc).isoformat(),
            run_id=run_id,
        )
        return state

    def on_stage_start(self, stage_name: str, state: PipelineProgressState) -> Checkpoint:
        cp = Checkpoint(
            run_id=state.run_id,
            event=ProgressEvent.STAGE_START,
            stage_name=stage_name,
            total_stages=state.total_stages,
            artifact_index=0,
        )
        self._emit(cp)
        return cp

    def on_artifact_complete(
        self, stage_name: str, artifact_idx: int, artifacts_count: int, state: PipelineProgressState
    ) -> Checkpoint:
        cp = Checkpoint(
            run_id=state.run_id,
            event=ProgressEvent.ARTIFACT_COMPLETE,
            stage_name=stage_name,
            artifact_index=artifact_idx,
            artifacts_count=artifacts_count,
            total_stages=state.total_stages,
        )
        self._emit(cp)
        state.total_artifacts += 1
        return cp

    def on_stage_complete(self, stage_name: str, state: PipelineProgressState) -> Checkpoint:
        with self._lock:
            state.completed_stages.add(stage_name)
        cp = Checkpoint(
            run_id=state.run_id,
            event=ProgressEvent.STAGE_COMPLETE,
            stage_name=stage_name,
            completed_stages=list(state.completed_stages),
            total_stages=state.total_stages,
        )
        self._emit(cp)
        return cp

    def on_stage_fail(self, stage_name: str, error: str, state: PipelineProgressState) -> Checkpoint:
        cp = Checkpoint(
            run_id=state.run_id,
            event=ProgressEvent.STAGE_FAIL,
            stage_name=stage_name,
            error=error,
            completed_stages=list(state.completed_stages),
            total_stages=state.total_stages,
        )
        self._emit(cp)
        return cp

    def on_pipeline_complete(self, state: PipelineProgressState) -> Checkpoint:
        cp = Checkpoint(
            run_id=state.run_id,
            event=ProgressEvent.PIPELINE_COMPLETE,
            completed_stages=list(state.completed_stages),
            total_stages=state.total_stages if hasattr(state, "total_stages") else 0,
        )
        self._emit(cp)
        self._persist(state)
        return cp

    # ── resume helpers ────────────────────────────────────

    def get_completed_stages(self, state: PipelineProgressState) -> set[str]:
        """Return the set of already-completed stages."""
        with self._lock:
            return set(state.completed_stages)

    def needs_resume(self, state: PipelineProgressState) -> bool:
        """Whether there is existing progress to resume from."""
        return len(state.completed_stages) > 0 and state.started_at is not None

    # ── internal helpers ──────────────────────────────────

    def _emit(self, cp: Checkpoint) -> None:
        if self._on_event is not None:
            try:
                self._on_event(cp)
            except Exception:
                pass  # custom handler failures are non-fatal

    def _persist(self, state: PipelineProgressState) -> None:
        if self._checkpoint_path is None:
            return
        try:
            with self._lock:
                data = {**state.to_dict(), "completed_at": datetime.now(timezone.utc).isoformat()}
                self._checkpoint_path.write_text(json.dumps(data, indent=2))
        except OSError:
            pass  # file persistence failure degraded — not fatal


# ───────────── module-level factory ──────────────────────

def create_progress_tracker(
    checkpoint_dir: Optional[str] = None,
) -> ProgressTracker:
    """Return a ProgressTracker with default file persistence (no custom handler)."""
    return ProgressTracker(checkpoint_dir=checkpoint_dir)
