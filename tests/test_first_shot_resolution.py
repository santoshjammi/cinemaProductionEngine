"""Regression test: PROMETHEUS first-shot asset resolution.

A selected first shot must always resolve to a valid visual asset:
- if a reusable scene image exists, reuse it;
- otherwise generate the selected shot image (never silently skip).
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from giri_ep0002_prometheus import generate_shot_images  # noqa: E402


class _FakeAsset:
    def __init__(self, path: Path):
        self.path = str(path)


class _FakeProvider:
    """Returns a fake asset written to the requested output path."""

    def __init__(self, img_dir: Path):
        self.img_dir = img_dir
        self.rendered: list[str] = []

    async def render(self, intent):
        # Simulate the provider writing the image to its output dir.
        out = self.img_dir / f"shot_{intent.metadata.get('scene_number', 0):03d}_gen.png"
        out.write_bytes(b"fake-image-bytes" * 100)
        self.rendered.append(intent.prompt[:40])
        return _FakeAsset(out)


def _shot(shot_id: str, scene_id: int, purpose: str = "SPEAKER_COVERAGE") -> dict:
    return {
        "shot_id": shot_id,
        "scene_id": scene_id,
        "purpose": purpose,
        "framing": {"type": "close-up"},
        "visual_subject": {"primary": "MARK"},
        "visual_action": "speaking",
        "emotional_intent": "tense",
        "composition": {"relationship": "single"},
    }


def _scene(scene_id: int) -> dict:
    return {"scene_id": scene_id, "title": f"Scene {scene_id}"}


def test_first_shot_generates_when_no_scene_image(tmp_path):
    """When scene_{id}.png does not exist, the first shot must be generated."""
    img_dir = tmp_path / "scene_images"
    img_dir.mkdir(parents=True)
    provider = _FakeProvider(img_dir)

    shots_by_id = {
        "SC01-SH01": _shot("SC01-SH01", 1, "ESTABLISHING"),
        "SC01-SH02": _shot("SC01-SH02", 1, "SPEAKER_COVERAGE"),
    }
    scenes = {1: _scene(1)}
    selection = {1: ["SC01-SH01", "SC01-SH02"]}

    result = asyncio.run(generate_shot_images(shots_by_id, scenes, selection, provider=provider, img_dir=img_dir))

    # Both shots must resolve to a real, existing file.
    assert "SC01-SH01" in result, "first shot must resolve to an asset"
    assert "SC01-SH02" in result, "second shot must resolve to an asset"
    for shot_id, path in result.items():
        assert path.exists(), f"{shot_id} resolved to a non-existent asset"
        assert path.stat().st_size > 0, f"{shot_id} resolved to an empty asset"
    # The first shot was generated (not silently skipped).
    assert len(provider.rendered) == 2, "both shots should be generated when no scene image exists"


def test_first_shot_reuses_existing_scene_image(tmp_path):
    """When scene_{id}.png exists, the first shot reuses it (no generation)."""
    img_dir = tmp_path / "scene_images"
    img_dir.mkdir(parents=True)
    scene_img = img_dir / "scene_001.png"
    scene_img.write_bytes(b"existing-scene-image" * 1000)  # > 10000 bytes
    provider = _FakeProvider(img_dir)

    shots_by_id = {
        "SC01-SH01": _shot("SC01-SH01", 1, "ESTABLISHING"),
        "SC01-SH02": _shot("SC01-SH02", 1, "SPEAKER_COVERAGE"),
    }
    scenes = {1: _scene(1)}
    selection = {1: ["SC01-SH01", "SC01-SH02"]}

    result = asyncio.run(generate_shot_images(shots_by_id, scenes, selection, provider=provider, img_dir=img_dir))

    assert result["SC01-SH01"] == scene_img, "first shot should reuse the existing scene image"
    assert result["SC01-SH01"].exists()
    # Only the second shot is generated.
    assert len(provider.rendered) == 1, "only the non-first shot should be generated"


def test_all_selected_shots_resolve(tmp_path):
    """Every selected shot across all scenes resolves to a valid asset (100%)."""
    img_dir = tmp_path / "scene_images"
    img_dir.mkdir(parents=True)
    provider = _FakeProvider(img_dir)

    shots_by_id = {
        "SC01-SH01": _shot("SC01-SH01", 1, "ESTABLISHING"),
        "SC01-SH02": _shot("SC01-SH02", 1, "SPEAKER_COVERAGE"),
        "SC02-SH05": _shot("SC02-SH05", 2, "ESTABLISHING"),
        "SC02-SH06": _shot("SC02-SH06", 2, "LISTENER_REACTION"),
    }
    scenes = {1: _scene(1), 2: _scene(2)}
    selection = {1: ["SC01-SH01", "SC01-SH02"], 2: ["SC02-SH05", "SC02-SH06"]}

    result = asyncio.run(generate_shot_images(shots_by_id, scenes, selection, provider=provider, img_dir=img_dir))

    selected = [s for ids in selection.values() for s in ids]
    assert set(result.keys()) == set(selected), "every selected shot must resolve"
    for shot_id in selected:
        assert result[shot_id].exists(), f"{shot_id} must resolve to an existing asset"
    # No silent skips: all 4 shots generated (no scene images exist).
    assert len(provider.rendered) == 4
