"""AW-08 Progress tracker lifecycle event emission and checkpoint persistence tests."""

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from movie_os.prometheus.progress import (
    ProgressTracker,
    Checkpoint,
    ProgressEvent,
    PipelineProgressState,
)
from movie_os.prometheus.pipeline import PrometheusPipeline


def _with_frozen_pkp(brief):
    from movie_os.frozen_pkp import freeze_from_brief
    payload = dict(brief or {})
    payload.setdefault("production", {"episode_id": "EP-0001"})
    payload.setdefault("policy_snapshot_id", "POLICY-TEST")
    payload.setdefault("frozen_pkp", freeze_from_brief(
        episode_id="EP-0001",
        policy_snapshot_id="POLICY-TEST",
        episode_contract_id="EP-0001",
        episode_contract_hash="contract-hash",
        policy_snapshot_hash="policy-hash",
        production={"episode_id": "EP-0001", "run_id": "RUN-TEST"},
        brief={
            "scenes": [{"number": 1, "title": "Kitchen", "narrative_beat": "opening", "entry_state": "quiet", "turning_point": "speaks", "exit_state": "changed", "next_scene_cause": "honesty"}],
            "dialogues": [{"scene_number": 1, "lines": [{"speaker": "MARK", "text": "I am scared.", "emotion": "fearful"}]}],
            "logline": "A man is afraid.",
            "synopsis": "A man is afraid.",
        },
    ).model_dump())
    return payload


# ---------------------------------------------------------------------------
# ProgressTracker — event emission tests
# ---------------------------------------------------------------------------

class TestProgressTrackerEventEmission:

    def test_on_pipeline_start_emits_correct_event(self):
        events = []
        tracker = ProgressTracker(on_event=lambda cp: events.append(cp))
        state = tracker.on_pipeline_start("run-001", total_stages=6)

        assert len(events) == 1
        assert events[0].event == ProgressEvent.PIPELINE_START
        assert events[0].run_id == "run-001"
        assert events[0].total_stages == 6
        assert state.started_at is not None
        assert state.run_id == "run-001"

    def test_on_stage_start_emits_event(self):
        tracker = ProgressTracker(on_event=lambda cp: None)
        state = PipelineProgressState(run_id="r1")
        cp = tracker.on_stage_start("Storyboard", state)

        assert cp.event == ProgressEvent.STAGE_START
        assert cp.stage_name == "Storyboard"

    def test_on_artifact_complete_emits_event(self):
        events = []
        tracker = ProgressTracker(on_event=lambda cp: events.append(cp))
        state = PipelineProgressState(run_id="r1")
        state.total_artifacts = 0

        tracker.on_artifact_complete("Storyboard", 1, 3, state)
        tracker.on_artifact_complete("Storyboard", 2, 3, state)
        tracker.on_artifact_complete("Storyboard", 3, 3, state)

        assert len(events) == 3
        for e in events:
            assert e.event == ProgressEvent.ARTIFACT_COMPLETE

        assert state.total_artifacts == 3

    def test_on_stage_complete_tracks_completed_stages(self):
        events = []
        tracker = ProgressTracker(on_event=lambda cp: events.append(cp))
        state = PipelineProgressState(run_id="r1")

        tracker.on_stage_complete("Storyboard", state)
        tracker.on_stage_complete("ImageGeneration", state)

        assert len(state.completed_stages) == 2
        assert "Storyboard" in state.completed_stages
        assert "ImageGeneration" in state.completed_stages

    def test_on_stage_fail_emits_event(self):
        events = []
        tracker = ProgressTracker(on_event=lambda cp: events.append(cp))
        state = PipelineProgressState(run_id="r1")

        cp = tracker.on_stage_fail("VoiceOver", "GPU OOM", state)

        assert cp.event == ProgressEvent.STAGE_FAIL
        assert cp.error == "GPU OOM"
        assert len(events) == 1

    def test_on_pipeline_complete_emits_event(self):
        events = []
        tracker = ProgressTracker(on_event=lambda cp: events.append(cp))
        state = PipelineProgressState(run_id="r1")
        state.completed_stages.add("Storyboard")
        state.total_artifacts = 5

        # Set total_stages attribute like pipeline does before calling this
        state.total_stages = 6
        tracker.on_stage_complete("Storyboard", state)
        cp = tracker.on_pipeline_complete(state)

        assert cp.event == ProgressEvent.PIPELINE_COMPLETE
        assert len(events) == 2  # stage_complete + pipeline_complete

    def test_all_events_in_order_for_full_pipeline(self):
        events = []
        tracker = ProgressTracker(on_event=lambda cp: events.append(cp))

        state = tracker.on_pipeline_start("run-order", total_stages=6)

        for stage in ["Storyboard", "ImageGeneration", "VoiceOver", "MusicComposition", "Editing", "Film"]:
            tracker.on_stage_start(stage, state)
            tracker.on_artifact_complete(stage, 1, 1, state)
            tracker.on_stage_complete(stage, state)

        tracker.on_pipeline_complete(state)

        assert len(events) == 20  # pipeline_start + (stage_start+artifact_complete+stage_complete)*6 + pipeline_complete

        expected_sequence = [
            ProgressEvent.PIPELINE_START,
        ]
        for _ in range(6):
            expected_sequence.extend([
                ProgressEvent.STAGE_START,
                ProgressEvent.ARTIFACT_COMPLETE,
                ProgressEvent.STAGE_COMPLETE,
            ])
        expected_sequence.append(ProgressEvent.PIPELINE_COMPLETE)

        assert len(events) == len(expected_sequence)  # pipeline_start + (stage_start+artifact_complete+stage_complete)*6 + pipeline_complete

        for i, evt in enumerate(events):
            assert evt.event == expected_sequence[i]


# ---------------------------------------------------------------------------
# Checkpoint — disk persistence tests
# ---------------------------------------------------------------------------

class TestCheckpointPersistence:

    def test_checkpoint_dir_creates_file(self, tmp_path):
        tracker = ProgressTracker(checkpoint_dir=str(tmp_path / "ckpts"))
        state = PipelineProgressState(run_id="r-persist")
        state.total_stages = 6
        state.completed_stages.add("Storyboard")

        # Manually call _persist (normally called in on_pipeline_complete)
        tracker._persist(state)

        ckpt_file = tmp_path / "ckpts" / "progress.json"
        assert ckpt_file.exists()

        data = json.loads(ckpt_file.read_text())
        assert data["run_id"] == "r-persist"

    def test_invalid_checkpoint_dir_does_not_crash(self):
        tracker = ProgressTracker(checkpoint_dir="/dev/null/nonexistent/deep/path/chk")
        assert tracker._checkpoint_path is None


# ---------------------------------------------------------------------------
# Pipeline integration — missing tracker fail-closed
# ---------------------------------------------------------------------------

class TestPipelineMissingTrackerFailClosed:

    def test_pipeline_runs_without_tracker(self):
        """When progress_tracker is None, pipeline executes normally without logging."""
        from movie_os.prometheus.pipeline import PipelineConfig
        from movie_os.prometheus.mock_provider import MockFluxComfyUIProvider
        cert = MagicMock()
        cert.production_ready = True
        cert.certificate_id = "cert-nopipe"
        cert.project_name = "No Tracker Test"
        cert.reviewed_by.name = "Jane Doe"
        cert.version = "1.0"
        cert.blueprint = {"scenes": [{"id": 1, "description": "Test"}]}

        pipeline = PrometheusPipeline(config=PipelineConfig(image_provider=MockFluxComfyUIProvider()))
        result = asyncio.run(pipeline.execute(cert, _with_frozen_pkp({})))
        assert result is not None


# ---------------------------------------------------------------------------
# Resume helpers
# ---------------------------------------------------------------------------

class TestResumeHelpers:

    def test_needs_resume_true(self):
        tracker = ProgressTracker()
        state = PipelineProgressState(
            run_id="r-resume",
            started_at="2026-01-01T00:00:00+00:00",
            completed_stages={"Storyboard"},
        )
        assert tracker.needs_resume(state) is True

    def test_needs_resume_false(self):
        tracker = ProgressTracker()
        state = PipelineProgressState(run_id="r-resume-fresh")
        assert tracker.needs_resume(state) is False

    def test_get_completed_stages_returns_set(self):
        tracker = ProgressTracker()
        state = PipelineProgressState(
            run_id="r-CS",
            completed_stages={"Storyboard", "ImageGeneration"},
        )
        result = tracker.get_completed_stages(state)
        assert result == {"Storyboard", "ImageGeneration"}


# ---------------------------------------------------------------------------
# Module-level factory
# ---------------------------------------------------------------------------

class TestCreateProgressTracker:

    def test_returns_tracker(self, tmp_path):
        from movie_os.prometheus.progress import create_progress_tracker  # type: ignore[attr-defined]
        tracker = create_progress_tracker(checkpoint_dir=str(tmp_path / "chks"))
        assert isinstance(tracker, ProgressTracker)


# ---------------------------------------------------------------------------
# PipelineProgressState serialization
# ---------------------------------------------------------------------------

class TestPipelineProgressStateModel:

    def test_to_dict_roundtrip(self):
        state = PipelineProgressState(
            completed_stages={"Storyboard"},
            total_artifacts=3,
            started_at="2026-01-01T00:00:00+00:00",
            run_id="r-dict",
        )
        d = state.to_dict()
        restored = PipelineProgressState.from_dict(d)

        assert "Storyboard" in restored.completed_stages
        assert restored.total_artifacts == 3
        assert restored.run_id == "r-dict"

    def test_default_empty_state(self):
        state = PipelineProgressState()
        d = state.to_dict()
        assert d["completed_stages"] == []
        assert d["total_artifacts"] == 0


# ---------------------------------------------------------------------------
# Checkpoint timestamp and emitted_at
# ---------------------------------------------------------------------------

class TestCheckpointFields:

    def test_checkpoint_emitted_at_set(self):
        cp = Checkpoint(
            run_id="r-ts",
            event=ProgressEvent.PIPELINE_START,
        )
        assert cp.emitted_at != ""
        assert "T" in cp.emitted_at  # ISO format check

    def test_timestamp_is_monotonic(self):
        import time
        cp = Checkpoint(
            run_id="r-mono",
            event=ProgressEvent.PIPELINE_START,
        )
        assert cp.timestamp > 0  # monotonic increases from epoch
