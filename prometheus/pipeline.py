"""PROMETHEUS Rendering Pipeline — stages, artifacts, and result models.

Executes a GENESIS-certified ProductionCertificate through 6 production stages:
Storyboard → Images → Voice → Music → Editing → Film.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, Literal, Optional

from pydantic import BaseModel, Field


# ──────────────────────────── Enums ─────────────────────────────

class StageStatus(str, Enum):
    """Lifecycle status of a single production stage."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ──────────────────────────── Models ─────────────────────────────

class Artifact(BaseModel, frozen=True):
    """A single output artifact produced by a stage."""
    type: Literal["storyboard", "image", "audio", "music", "video", "film"]
    path: str
    url: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class ProductionStage(BaseModel):
    """Describes one phase of the production pipeline."""
    name: str
    status: StageStatus = StageStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    artifacts: list[Artifact] = Field(default_factory=list)
    error: Optional[str] = None

    def __hash__(self):
        return hash(self.name)


class PrometheusResult(BaseModel):
    """Complete result of executing the pipeline end-to-end."""
    certificate_id: str
    project_name: str
    stages: list[ProductionStage]
    overall_status: Literal["completed", "failed", "partial"]
    output_path: Optional[str] = None
    duration_seconds: float = 0.0
    artifacts: list[Artifact] = Field(default_factory=list)

    # Derived convenience accessor (doesn't require a setter because it's
    # computed during __init__ rather than being a plain field).
    class Config:
        arbitrary_types_allowed = True

    def model_post_init(self, __context) -> None:  # type: ignore[override]
        self._total_artifacts = sum(len(s.artifacts) for s in self.stages)

    @property
    def total_artifacts(self) -> int:
        """Total artifacts generated across all stages."""
        return getattr(self, "_total_artifacts", 0)


# ──────────────────────────── Stage definitions ─────────────────────

# Ordered list of production stages — the canonical pipeline.
STAGE_ORDER = [
    "storyboard",
    "images",
    "voice",
    "music",
    "editing",
    "film",
]


# Mapping from stage name → artifact-type literal expected from it.
ARTIFACT_TYPE_MAP: dict[str, Literal["storyboard", "image", "audio", "music", "video", "film"]] = {
    "storyboard": "storyboard",
    "images": "image",
    "voice": "audio",
    "music": "music",
    "editing": "video",
    "film": "film",
}


# ──────────────────────────── Pipeline ─────────────────────────────

class PrometheusPipeline:
    """The 6-stage production pipeline.

    Each stage receives the full brief dict; it may inspect scenes,
    project_id, and other keys produced by GENESIS.
    """

    stages: list[str] = STAGE_ORDER

    def __init__(
        self,
        progress_on_event: Optional[Callable] = None,
        progress_checkpoint_dir: Optional[str] = None,
    ) -> None:
        # Lazily imported to avoid circular import with prometheus.progress
        from prometheus.progress import ProgressTracker

        self._progress_tracker = ProgressTracker(
            on_event=progress_on_event,
            checkpoint_dir=progress_checkpoint_dir,
        )

    async def execute(self, certificate: dict, brief: dict) -> PrometheusResult:
        """Execute every stage in order and return a PrometheusResult.

        * Runs each stage sequentially.
        * On first failure the pipeline short-circuits (partial).
        * Duration is wall-clock across all executed stages.
        * Emits progress events to the injected `ProgressTracker`.
        * Binds canonical character identity data from the brief into every
          artifact metadata so downstream consumers can verify correctness.
        """
        from time import perf_counter  # local to avoid top-level import cost

        start = perf_counter()

        tracker_state = self._progress_tracker.on_pipeline_start(
            total_stages=len(self.stages),
        )

        stage_results: list[ProductionStage] = []
        all_artifacts: list[Artifact] = []
        overall: Literal["completed", "failed", "partial"] = "completed"

        for stage_name in self.stages:
            if tracker_state and self._progress_tracker.needs_resume(tracker_state) \
                    and stage_name in self._progress_tracker.get_completed_stages(tracker_state):
                continue  # skip already-completed stages on resume

            stage = ProductionStage(
                name=stage_name,
                status=StageStatus.RUNNING,
                started_at=datetime.now(timezone.utc),
            )
            self._progress_tracker.on_stage_start(stage_name, tracker_state)

            try:
                artifacts = await self._execute_stage(stage_name, brief)
                stage.status = StageStatus.COMPLETED
                stage.completed_at = datetime.now(timezone.utc)
                stage.artifacts = artifacts
                all_artifacts.extend(artifacts)

                for idx, art in enumerate(artifacts):
                    self._progress_tracker.on_artifact_complete(
                        stage_name, idx + 1, len(artifacts), tracker_state,
                    )

                self._progress_tracker.on_stage_complete(stage_name, tracker_state)

            except Exception as exc:
                stage.status = StageStatus.FAILED
                stage.error = str(exc)
                stage.completed_at = datetime.now(timezone.utc)
                overall = "partial"  # first failure makes it partial, not full
                self._progress_tracker.on_stage_fail(stage_name, str(exc), tracker_state)
                break   # short-circuit on first error (per spec)

            stage_results.append(stage)

        if tracker_state:
            self._progress_tracker.on_pipeline_complete(tracker_state)

        duration = perf_counter() - start
        return PrometheusResult(
            certificate_id=certificate.get("certification_id", ""),
            project_name=certificate.get("project_name", ""),
            stages=stage_results,
            overall_status=overall,
            output_path=f"output/film/final.mp4",
            duration_seconds=duration,
            artifacts=all_artifacts,
        )

    # ── stage executors (one per phase) ────────────────────────

    async def _execute_stage(self, stage_name: str, brief: dict) -> list[Artifact]:
        """Dispatcher for each production phase.

        Binds canonical character identity / voice / visual / continuity data
        from the brief (set by GENESIS via resolve_policy) into every artifact
        metadata so downstream consumers can verify correctness at render time.
        """
        artifact_type = ARTIFACT_TYPE_MAP.get(stage_name)
        if artifact_type is None:
            raise ValueError(f"unknown stage: {stage_name!r}")

        # Canonical binding data — populated by GENESIS / resolve_policy
        policy_resolved = brief.get("resolved_rules", {})
        canonical_bindings = policy_resolved.get("canonical_character_bindings", [])
        canonical_continuity = policy_resolved.get("canonical_continuity_binding", {})
        universe_id = canonical_continuity.get("universe_id", "UNIVERSE-MARK-SARAH")
        identity_refs = [b for b in canonical_bindings] if isinstance(canonical_bindings, list) else []

        # shared metadata injected into every artifact from canon registries
        _canon_meta: dict = {
            "universe_id": universe_id,
            "identity_locks": {},
            "hard_failures": [],
        }
        for cbind in identity_refs:
            cid = cbind.get("character_id", "UNKNOWN")
            _canon_meta["identity_locks"][cid] = cbind.get("identity_lock", True)
            _canon_meta["hard_failures"].extend(cbind.get("hard_failures", []))

        def _with_canon(m: dict) -> dict:
            """Deep-merge canonical metadata into an artifact's metadata dict."""
            out = dict(m)
            for k, v in _canon_meta.items():
                if k not in out:
                    out[k] = v
            if not isinstance(out.get("canonical_continuity"), dict):
                out["canonical_continuity"] = canonical_continuity
            return out

        if stage_name == "storyboard":
            project_id = brief.get("project_id", "unknown")
            return [Artifact(
                type="storyboard",
                path=f"output/storyboard/{project_id}.json",
                metadata=_with_canon({"stages_count": 6, "source": "genesis3"}),
            )]

        elif stage_name == "images":
            scenes: list[dict] = brief.get("scenes", [])
            return [
                Artifact(
                    type="image",
                    path=f"output/images/scene_{i:03d}.png",
                    metadata=_with_canon({
                        "scene_index": i,
                        "visual_identity_refs": identity_refs,
                    }),
                )
                for i in range(max(len(scenes), 1))
            ]

        elif stage_name == "voice":
            voice_chars = {b["character_id"]: b.get("baseline_voice", {}) for b in identity_refs if "baseline_voice" in b}
            return [Artifact(
                type="audio",
                path="output/audio/narration.wav",
                metadata=_with_canon({
                    "format": "wav",
                    "sample_rate": 48000,
                    "voice_registry_refs": voice_chars,
                }),
            )]

        elif stage_name == "music":
            return [Artifact(
                type="music",
                path="output/music/score.wav",
                metadata=_with_canon({
                    "format": "wav",
                    "tempo": 120,
                }),
            )]

        elif stage_name == "editing":
            return [Artifact(
                type="video",
                path="output/video/rough_cut.mp4",
                metadata=_with_canon({
                    "codec": "h264",
                    "continuity_state": canonical_continuity,
                }),
            )]

        elif stage_name == "film":
            return [Artifact(
                type="film",
                path="output/film/final.mp4",
                metadata=_with_canon({
                    "codec": "hevc",
                    "resolution": "3840x2160",
                    "final_identity_refs": identity_refs,
                }),
            )]

        raise ValueError(f"unknown stage: {stage_name!r}")


# ──────────────────────────── module-level factory ────────────────────────

def create_pipeline() -> PrometheusPipeline:
    """Return a fresh pipeline instance."""
    return PrometheusPipeline()
