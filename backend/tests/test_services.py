"""Unit tests for video and TTS services."""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from backend.app.services.video_service import (
    GenerationState,
    get_generation_state,
    remove_generation_state,
    _generation_states,
)


class TestGenerationState:
    def test_initial_state(self):
        state = GenerationState()
        assert state.get_all_clips() == []
        assert state.get_final_video() is None
        assert state.overall_progress() == 0.0
        assert state.is_done() is False

    def test_set_and_get_clip(self):
        state = GenerationState()
        state.set_clip(1, {
            "scene_number": 1,
            "status": "completed",
            "progress": 1.0,
        })
        clip = state.get_clip(1)
        assert clip is not None
        assert clip["scene_number"] == 1
        assert clip["status"] == "completed"

    def test_get_all_clips_sorted(self):
        state = GenerationState()
        state.set_clip(2, {"scene_number": 2, "status": "pending"})
        state.set_clip(1, {"scene_number": 1, "status": "completed"})
        clips = state.get_all_clips()
        assert clips[0]["scene_number"] == 1
        assert clips[1]["scene_number"] == 2

    def test_final_video(self):
        state = GenerationState()
        state.set_final_video({"status": "completed", "progress": 1.0})
        assert state.get_final_video()["status"] == "completed"
        assert state.is_done() is True

    def test_not_done_with_pending_clips(self):
        state = GenerationState()
        state.set_clip(1, {"scene_number": 1, "status": "pending"})
        assert state.is_done() is False

    def test_done_when_all_clips_completed(self):
        state = GenerationState()
        state.set_clip(1, {"scene_number": 1, "status": "completed"})
        state.set_clip(2, {"scene_number": 2, "status": "failed"})
        assert state.is_done() is True

    def test_overall_progress_partial(self):
        state = GenerationState()
        state.set_clip(1, {"scene_number": 1, "status": "completed", "progress": 1.0})
        state.set_clip(2, {"scene_number": 2, "status": "generating", "progress": 0.5})
        assert state.overall_progress() == 0.75

    def test_overall_progress_no_clips(self):
        state = GenerationState()
        assert state.overall_progress() == 0.0


class TestGenerationStateRegistry:
    def teardown_method(self):
        _generation_states.clear()

    def test_get_state_creates_new(self):
        state = get_generation_state("test-id")
        assert state is not None
        assert "test-id" in _generation_states

    def test_get_state_reuses_existing(self):
        state1 = get_generation_state("test-id")
        state2 = get_generation_state("test-id")
        assert state1 is state2

    def test_remove_state(self):
        get_generation_state("test-id")
        assert "test-id" in _generation_states
        remove_generation_state("test-id")
        assert "test-id" not in _generation_states

    def test_multiple_pipelines(self):
        s1 = get_generation_state("pipe-1")
        s2 = get_generation_state("pipe-2")
        assert s1 is not s2
        s1.set_clip(1, {"scene_number": 1, "status": "completed", "progress": 1.0})
        assert s2.get_all_clips() == []
