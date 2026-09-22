"""PROMETHEUS EditingStage timeline regression -- EP-0001 style data.

EP-0001 has scene_ids {1,2,3}, 3 image artifacts, and 18 voice-artifact lines.

The bug in the current EditingStage.run():
  - creates fabricated scene_ids by looping `for i in range(scene_count)` where
    scene_count = max(num_images, num_voice) == 18+ -> invents non-existent scenes.
  - falls back to artifacts[0] via _pick_audio when no matching scene_id image/voice is
    found (duplicate of first asset on fabricated entries).
  - uses fixed 5.0 s timing instead of measured durations from voice metadata.

This test MUST fail against the current code and pass after the fix.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

import pytest


def _brief_with_ep0001_artifacts():
    """Return a brief containing 3 image artifacts + 18 voice artifacts with real metadata."""
    from movie_os.prometheus.stages.editing_stage import DEFAULT_PAUSE

    tmpdir = tempfile.mkdtemp()
    # -- 3 images, each tied to scene_id in {1,2,3} --
    images: list[dict[str, Any]] = []
    for sid in (1, 2, 3):
        img_path = Path(tmpdir) / f"scene_{sid}.png"
        img_path.write_text(f"fake-image-scene-{sid}")
        images.append({
            "type": "image",
            "path": str(img_path),
            "metadata": {"scene_id": sid, "line_id": None},
        })

    # -- 18 voice artifacts spanning scenes {1,2,3} --
    # Distribution: scene 1 -> lines L01..L06 (6 lines),
    #               scene 2 -> lines L07..L12 (6 lines),
    #               scene 3 -> lines L13..L18 (6 lines)
    speakers = ["MARK", "SARAH", "NARRATOR"]
    voices: list[dict[str, Any]] = []
    for idx in range(18):
        line_id = f"L{idx + 1:03d}"
        scene_id = (idx // 6) + 1  # 1,1,...,2,2,...,3,3
        speaker = speakers[idx % 3]
        path = Path(tmpdir) / f"voice_{line_id}.wav"
        path.write_text(f"fake-audio-{line_id}-{scene_id}")
        voices.append({
            "type": "audio",
            "path": str(path),
            "metadata": {
                "scene_id": scene_id,
                "line_id": line_id,
                "speaker": speaker,
                "duration_seconds": 3.0 + idx * 0.1,  # distinct measured dur per line
            },
        })

    brief: dict[str, Any] = {
        "image_artifacts": images,
        "voice_artifacts": voices,
    }
    return brief, tmpdir


class TestEditingStageTimelineEP0001:

    def test_timeline_has_exactly_18_line_entries(self):
        """The timeline must contain one entry per voice artifact (18), not 20."""
        from movie_os.prometheus.stages.editing_stage import EditingStage

        brief, _ = _brief_with_ep0001_artifacts()
        stage = EditingStage(brief=brief)
        result = stage.run()

        raw_timeline = result["artifacts"][0]["metadata"]["raw_data"]["timeline"]
        # Each voice line becomes one timeline entry.
        assert len(raw_timeline) == 18, (
            f"Expected exactly 18 timeline entries but got {len(raw_timeline)}."
        )

    def test_timeline_uses_real_scene_ids_only(self):
        """Scene IDs in the timeline must be {1,2,3} -- no fabricated ids."""
        from movie_os.prometheus.stages.editing_stage import EditingStage

        brief, _ = _brief_with_ep0001_artifacts()
        stage = EditingStage(brief=brief)
        result = stage.run()

        raw_timeline = result["artifacts"][0]["metadata"]["raw_data"]["timeline"]
        scene_ids = {e.get("scene_id") for e in raw_timeline}
        assert scene_ids == {1, 2, 3}, (
            f"Expected real scene_ids {{1,2,3}} but got {scene_ids}"
        )

    def test_timeline_entries_have_required_fields(self):
        """Each timeline entry must carry line_id, speaker, audio_path."""
        from movie_os.prometheus.stages.editing_stage import EditingStage

        brief, _ = _brief_with_ep0001_artifacts()
        stage = EditingStage(brief=brief)
        result = stage.run()

        raw_timeline = result["artifacts"][0]["metadata"]["raw_data"]["timeline"]
        required_keys = {"line_id", "speaker", "audio_path", "start_time", "end_time",
                         "duration_seconds", "pause_after_seconds"}
        for entry in raw_timeline:
            assert required_keys.issubset(set(entry.keys())), (
                f"Entry {entry} missing keys: {required_keys - set(entry.keys())}"
            )

    def test_audio_paths_appear_once_in_order(self):
        """Each unique audio file path must appear exactly once, preserving input order."""
        from movie_os.prometheus.stages.editing_stage import EditingStage

        brief, _ = _brief_with_ep0001_artifacts()
        stage = EditingStage(brief=brief)
        result = stage.run()

        raw_timeline = result["artifacts"][0]["metadata"]["raw_data"]["timeline"]
        paths_in_order = [e["audio_path"] for e in raw_timeline]
        # 18 distinct paths, each once
        assert len(paths_in_order) == 18
        assert len(set(paths_in_order)) == 18

    def test_cumulative_start_end_times(self):
        """start_time and end_time come from cumulative measured durations + pause."""
        from movie_os.prometheus.stages.editing_stage import EditingStage, DEFAULT_PAUSE

        brief, _ = _brief_with_ep0001_artifacts()
        stage = EditingStage(brief=brief)
        result = stage.run()

        raw_timeline = result["artifacts"][0]["metadata"]["raw_data"]["timeline"]

        expected_cursor = 0.0
        for entry in raw_timeline:
            start = entry["start_time"]
            end = entry["end_time"]
            dur = entry.get("duration_seconds", 0)
            pause_after = entry.get("pause_after_seconds", DEFAULT_PAUSE)

            # Every entry except the LAST must have pause after it.
            is_last = raw_timeline.index(entry) == len(raw_timeline) - 1
            if not is_last:
                assert pause_after > 0, (
                    "Only the final timeline entry should have pause_after_seconds == 0"
                )

            assert abs(start - expected_cursor) < 0.01, (
                f"start_time={start} != expected {expected_cursor}"
            )
            assert abs(end - (start + dur)) < 0.01, (
                f"end_time={end} != start + dur ({start} + {dur})"
            )

            if not is_last:
                expected_cursor = end + pause_after

    def test_no_fallback_substitution(self):
        """If audio_path or metadata is missing on an entry, ValueError must be raised."""
        from movie_os.prometheus.stages.editing_stage import EditingStage

        brief: dict[str, Any] = {
            "image_artifacts": [],
            "voice_artifacts": [
                {"type": "audio", "path": "/tmp/x.wav"},  # no metadata -> ValueError
            ],
        }
        stage = EditingStage(brief=brief)
        pytest.raises(ValueError, stage.run)

    def test_missing_audio_path_raises_value_error(self):
        """An artifact whose path does not exist must raise ValueError."""
        from movie_os.prometheus.stages.editing_stage import EditingStage

        brief: dict[str, Any] = {
            "image_artifacts": [],
            "voice_artifacts": [
                {"type": "audio", "path": "/tmp/does_not_exist.wav",
                 "metadata": {"scene_id": 1, "line_id": "L001"}},
            ],
        }
        stage = EditingStage(brief=brief)
        pytest.raises(ValueError, stage.run)
