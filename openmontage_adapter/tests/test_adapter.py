"""Unit tests for the OpenMontage adapter layer.

Tests cover:
- SceneIntent / SceneAsset dataclasses
- RenderBackend interface
- SDXLLocalBackend (without actually loading SDXL — mocked)
- RenderOrchestrator (selection + fallback)
- OpenMontageAdapter (bidirectional translation)
- videogen_adapter (manifest YAML → SceneIntents)

Run with:
    cd /Users/santosh/Desktop/projects/videoGen
    ./venv/bin/python -m pytest openmontage_adapter/tests/test_adapter.py -v
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from openmontage_adapter import (
    BackendError,
    OpenMontageAdapter,
    RenderBackend,
    RenderDecision,
    RenderOrchestrator,
    SceneAsset,
    SceneIntent,
    SDXLLocalBackend,
    manifest_to_intents,
)


# ---------- FIXTURES ----------

@pytest.fixture
def sample_scene_intent():
    """A minimal SceneIntent for testing."""
    return SceneIntent(
        scene_id="test-001",
        title="Test Scene",
        emotional_state="restrained",
        visual_symbolism=["physical_distance", "low_light"],
        camera_language={"shot_size": "medium", "movement": "static"},
        duration_seconds=5.0,
        index=1,
        beat="opening_hook",
        act="act_1_observation",
        phase="hook",
        energy=3,
    )


@pytest.fixture
def sample_irreversible_intent():
    """A SceneIntent for the irreversible moment."""
    return SceneIntent(
        scene_id="test-008",
        title="Setting the Table",
        emotional_state="interrupted",
        visual_symbolism=["unfinished_gesture", "imperfection"],
        camera_language={"shot_size": "medium", "movement": "static"},
        duration_seconds=12.0,
        index=8,
        beat="irreversible_moment",
        act="act_2_inner_reality",
        phase="almost",
        energy=5,
        irreversible_moment=True,
        silence_after_seconds=3.0,
        vocal_fracture=True,
        narration_text="She stopped. The second fork... she didn't know why.",
        soundtrack_zone="silent",
        music_volume=0.0,
    )


@pytest.fixture
def sample_om_scene():
    """A sample OpenMontage scene dict (per scene_plan.schema.json)."""
    return {
        "id": "scene-008",
        "type": "generated",
        "description": "A woman setting a table, frozen mid-action at the second fork, low light, kitchen, unwashed mug",
        "start_seconds": 40.0,
        "end_seconds": 52.0,
        "shot_language": {
            "shot_size": "medium",
            "camera_movement": "static",
            "lens_mm": 50,
            "lighting_key": "low_key",
            "depth_of_field": "shallow",
            "color_temperature": "cool",
        },
        "shot_intent": "The irreversible moment",
        "narrative_role": "deliver_payload",
        "hero_moment": True,
        "character_actions": [
            {
                "character_id": "wife",
                "emotion": "tense",
                "action_sequence": ["sets down plate", "picks up fork", "stops mid-reach"],
            }
        ],
        "texture_keywords": ["grain", "gritty", "wrinkled"],
        "required_assets": [
            {"type": "image", "description": "Woman at kitchen table, fork frozen", "source": "generate"}
        ],
        "transition_in": "fade_to_black",
        "transition_out": "hard_cut",
    }


# ---------- MOCK BACKEND ----------

class MockBackend(RenderBackend):
    """A mock backend for testing the orchestrator without real rendering."""

    name = "mock"
    cost_per_scene_usd = 0.01
    quality_score = 0.5
    supports_img2img = False

    def __init__(self, should_fail=False, can_render_value=True):
        self.should_fail = should_fail
        self.can_render_value = can_render_value
        self.render_calls: list[SceneIntent] = []

    def can_render(self, scene_intent):
        return self.can_render_value

    def render(self, scene_intent):
        self.render_calls.append(scene_intent)
        if self.should_fail:
            raise BackendError(self.name, scene_intent.scene_id, "mock failure")
        # Create a dummy file
        scene_intent.output_path.parent.mkdir(parents=True, exist_ok=True)
        scene_intent.output_path.write_bytes(b"mock image")
        return SceneAsset(
            scene_id=scene_intent.scene_id,
            image_path=scene_intent.output_path,
            duration_seconds=scene_intent.duration_seconds,
            backend=self.name,
            cost_usd=self.cost_per_scene_usd,
            metadata={"mock": True},
        )


class HighQualityMockBackend(MockBackend):
    name = "mock-hq"
    cost_per_scene_usd = 0.10
    quality_score = 0.95
    supports_img2img = True


# ---------- SCENE INTENT TESTS ----------

class TestSceneIntent:
    def test_creation(self, sample_scene_intent):
        assert sample_scene_intent.scene_id == "test-001"
        assert sample_scene_intent.emotional_state == "restrained"
        assert sample_scene_intent.visual_symbolism == ["physical_distance", "low_light"]

    def test_defaults(self):
        intent = SceneIntent(scene_id="test")
        assert intent.style_anchor.startswith("cinematic photorealism")
        assert intent.resolution == (1024, 576)
        assert intent.beat == "internal_collapse"
        assert intent.duration_seconds == 5.0

    def test_to_dict(self, sample_scene_intent):
        d = sample_scene_intent.to_dict()
        assert d["scene_id"] == "test-001"
        assert isinstance(d["resolution"], list)
        assert d["emotional_state"] == "restrained"

    def test_irreversible_flags(self, sample_irreversible_intent):
        assert sample_irreversible_intent.irreversible_moment is True
        assert sample_irreversible_intent.vocal_fracture is True
        assert sample_irreversible_intent.soundtrack_zone == "silent"
        assert sample_irreversible_intent.music_volume == 0.0
        assert sample_irreversible_intent.silence_after_seconds == 3.0


# ---------- SCENE ASSET TESTS ----------

class TestSceneAsset:
    def test_creation(self):
        asset = SceneAsset(
            scene_id="test-001",
            image_path=Path("/tmp/test.png"),
            duration_seconds=5.0,
            backend="sdxl-local",
        )
        assert asset.scene_id == "test-001"
        assert asset.cost_usd == 0.0
        assert asset.metadata == {}

    def test_to_dict(self):
        asset = SceneAsset(
            scene_id="test-001",
            image_path=Path("/tmp/test.png"),
            backend="sdxl-local",
            metadata={"clip_score": 0.65},
        )
        d = asset.to_dict()
        assert d["image_path"] == "/tmp/test.png"
        assert d["metadata"]["clip_score"] == 0.65


# ---------- RENDER BACKEND TESTS ----------

class TestRenderBackend:
    def test_mock_backend(self, sample_scene_intent, tmp_path):
        backend = MockBackend()
        sample_scene_intent.output_path = tmp_path / "scene_001.png"
        assert backend.can_render(sample_scene_intent) is True
        asset = backend.render(sample_scene_intent)
        assert asset.scene_id == "test-001"
        assert asset.backend == "mock"
        assert asset.cost_usd == 0.01

    def test_backend_error(self, sample_scene_intent):
        backend = MockBackend(should_fail=True)
        with pytest.raises(BackendError) as exc_info:
            backend.render(sample_scene_intent)
        assert "mock" in str(exc_info.value)
        assert exc_info.value.backend_name == "mock"


# ---------- ORCHESTRATOR TESTS ----------

class TestRenderOrchestrator:
    def test_primary_selection(self, sample_scene_intent, tmp_path):
        mock = MockBackend()
        orch = RenderOrchestrator(backends=[mock], primary="mock")
        sample_scene_intent.output_path = tmp_path / "scene_001.png"
        asset = orch.render_scene(sample_scene_intent)
        assert asset.backend == "mock"
        assert len(mock.render_calls) == 1

    def test_fallback_on_failure(self, sample_scene_intent, tmp_path):
        failing = MockBackend(should_fail=True)
        working = MockBackend()
        working.name = "mock-fallback"
        orch = RenderOrchestrator(backends=[failing, working], primary="mock")
        sample_scene_intent.output_path = tmp_path / "scene_001.png"
        asset = orch.render_scene(sample_scene_intent)
        assert asset.backend == "mock-fallback"
        decisions = orch.get_decisions()
        assert decisions[0].fallback_used is True

    def test_irreversible_uses_highest_quality(self, sample_irreversible_intent, tmp_path):
        low_q = MockBackend()
        low_q.name = "low-q"
        high_q = HighQualityMockBackend()
        orch = RenderOrchestrator(backends=[low_q, high_q], primary="low-q")
        sample_irreversible_intent.output_path = tmp_path / "scene_008.png"
        asset = orch.render_scene(sample_irreversible_intent)
        # Should use the higher quality backend
        assert asset.backend == "mock-hq"

    def test_all_backends_fail(self, sample_scene_intent):
        failing1 = MockBackend(should_fail=True)
        failing1.name = "fail-1"
        failing2 = MockBackend(should_fail=True)
        failing2.name = "fail-2"
        orch = RenderOrchestrator(backends=[failing1, failing2], primary="fail-1")
        with pytest.raises(BackendError) as exc_info:
            orch.render_scene(sample_scene_intent)
        assert "All backends failed" in str(exc_info.value)

    def test_budget_limit(self, sample_scene_intent, tmp_path):
        expensive = HighQualityMockBackend()
        orch = RenderOrchestrator(
            backends=[expensive], primary="mock-hq", max_budget_usd=0.001,
        )
        sample_scene_intent.output_path = tmp_path / "scene_001.png"
        with pytest.raises(BackendError):
            orch.render_scene(sample_scene_intent)

    def test_backend_hint_override(self, sample_scene_intent, tmp_path):
        mock1 = MockBackend()
        mock1.name = "mock-1"
        mock2 = MockBackend()
        mock2.name = "mock-2"
        orch = RenderOrchestrator(backends=[mock1, mock2], primary="mock-1")
        sample_scene_intent.output_path = tmp_path / "scene_001.png"
        sample_scene_intent.backend_hint = "mock-2"
        asset = orch.render_scene(sample_scene_intent)
        assert asset.backend == "mock-2"


# ---------- OPENMONTAGE ADAPTER TESTS ----------

class TestOpenMontageAdapter:
    def test_om_to_intent(self, sample_om_scene):
        adapter = OpenMontageAdapter(
            territory="emotional_withdrawal",
            archetype="slow_withdrawal",
        )
        intent = adapter.to_scene_intent(sample_om_scene, index=8, pipeline_id="vid01")
        assert intent.scene_id == "vid01-scene-008"
        assert intent.irreversible_moment is True  # hero_moment → irreversible
        assert intent.beat == "irreversible_moment"  # deliver_payload → irreversible
        assert intent.act == "act_2_inner_reality"
        assert intent.energy == 5
        assert intent.soundtrack_zone == "silent"
        assert intent.music_volume == 0.0
        assert intent.silence_after_seconds == 3.0
        assert intent.vocal_fracture is True
        assert intent.duration_seconds == 12.0  # 52 - 40

    def test_om_to_intent_normal_scene(self):
        om_scene = {
            "id": "scene-001",
            "type": "generated",
            "description": "A man in bed, phone glow on his face",
            "start_seconds": 0.0,
            "end_seconds": 5.0,
            "shot_language": {"shot_size": "close_up", "camera_movement": "static"},
            "narrative_role": "establish_context",
            "hero_moment": False,
        }
        adapter = OpenMontageAdapter()
        intent = adapter.to_scene_intent(om_scene, index=1, pipeline_id="vid01")
        assert intent.irreversible_moment is False
        assert intent.beat == "opening_hook"  # establish_context → opening_hook
        assert intent.act == "act_1_observation"
        assert intent.energy == 3
        assert intent.soundtrack_zone == "act_1"

    def test_intent_to_om(self, sample_irreversible_intent):
        adapter = OpenMontageAdapter()
        om_scene = adapter.from_scene_intent(sample_irreversible_intent)
        assert om_scene["id"] == "test-008"
        assert om_scene["hero_moment"] is True
        assert om_scene["type"] == "generated"
        assert "shot_language" in om_scene
        assert om_scene["required_assets"][0]["source"] == "generate"

    def test_asset_manifest(self, sample_scene_intent, tmp_path):
        adapter = OpenMontageAdapter()
        asset = SceneAsset(
            scene_id="test-001",
            image_path=tmp_path / "scene_001.png",
            backend="sdxl-local",
            metadata={"clip_score": 0.65, "model": "sdxl"},
        )
        manifest = adapter.to_asset_manifest([asset], total_cost=0.0)
        assert manifest["version"] == "1.0"
        assert len(manifest["assets"]) == 1
        assert manifest["assets"][0]["id"] == "test-001"
        assert manifest["assets"][0]["source_tool"] == "sdxl-local"

    def test_emotion_translation(self):
        adapter = OpenMontageAdapter()
        assert adapter._translate_emotion("sad") == "grief"
        assert adapter._translate_emotion("happy") == "warmth"
        assert adapter._translate_emotion("tired") == "exhausted"
        assert adapter._translate_emotion("ashamed") == "shame"

    def test_action_to_behavior(self):
        adapter = OpenMontageAdapter()
        assert adapter._translate_action_to_behavior("reaches for her hand, then stops") == "unfinished_movements"
        assert adapter._translate_action_to_behavior("almost touches her") == "almost_touching"
        assert adapter._translate_action_to_behavior("looks away quickly") == "redirected_attention"
        assert adapter._translate_action_to_behavior("opens mouth to speak, then closes") == "almost_speaking"


# ---------- VIDEOGEN ADAPTER TESTS ----------

class TestVideogenAdapter:
    def test_manifest_to_intents(self):
        manifest_path = "videoContentStructure/Psychology/EmotionalWithdrawal/VID01_template_refined.yaml"
        if not Path(manifest_path).exists():
            pytest.skip(f"Manifest not found: {manifest_path}")
        intents = manifest_to_intents(manifest_path)
        assert len(intents) == 11
        # Check scene 8 is irreversible
        s8 = next(i for i in intents if i.index == 8)
        assert s8.irreversible_moment is True
        assert s8.vocal_fracture is True
        assert s8.soundtrack_zone == "silent"
        # Check scene 1 is the hook
        s1 = next(i for i in intents if i.index == 1)
        assert s1.beat == "opening_hook"
        assert s1.act == "act_1_observation"
        # Check character references
        assert len(s1.character_references) > 0
        assert "husband" in s1.characters_present

    def test_break_words_extraction(self):
        from openmontage_adapter.videogen_adapter import _extract_break_words
        words = _extract_break_words("She stopped. The second fork... she didn't know why.")
        assert "stopped" in words

    def test_emphasis_words_extraction(self):
        from openmontage_adapter.videogen_adapter import _extract_emphasis_words
        words = _extract_emphasis_words({"voiceover": "He almost reached for her hand, then stopped."})
        assert "almost" in words
        assert "stopped" in words


# ---------- SDXL LOCAL BACKEND TESTS (no actual rendering) ----------

class TestSDXLLocalBackend:
    def test_initialization(self):
        backend = SDXLLocalBackend(
            manifest_yaml="videoContentStructure/Psychology/EmotionalWithdrawal/VID01_template_refined.yaml",
            output_dir="output/videos",
        )
        assert backend.name == "sdxl-local"
        assert backend.cost_per_scene_usd == 0.0
        assert backend.quality_score == 0.75

    def test_can_render(self, sample_scene_intent):
        backend = SDXLLocalBackend(
            manifest_yaml="videoContentStructure/Psychology/EmotionalWithdrawal/VID01_template_refined.yaml",
        )
        # Can render if the script exists
        assert backend.can_render(sample_scene_intent) is True

    def test_intent_to_scene_dict(self, sample_irreversible_intent):
        backend = SDXLLocalBackend(
            manifest_yaml="videoContentStructure/Psychology/EmotionalWithdrawal/VID01_template_refined.yaml",
        )
        scene_dict = backend._intent_to_scene_dict(sample_irreversible_intent)
        assert scene_dict["scene_number"] == 8
        assert scene_dict["beat"] == "irreversible_moment"
        assert "scene_description" in scene_dict
        assert "characters_present" in scene_dict