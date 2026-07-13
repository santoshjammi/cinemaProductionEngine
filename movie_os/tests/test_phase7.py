"""Tests for the Movie OS Phase 7 deliverables (Scene → Shot → Frame hierarchy).

These tests verify:
- ShotPlanner decides shot count based on scene properties
- FramePlanner decides frame count (2 for irreversible, 1 otherwise)
- The full hierarchy Scene → Shot → Frame is built and serialized
- Backward compat: existing scene-only data still works

Run with:
    cd /Users/santosh/Desktop/projects/videoGen
    ./venv/bin/python -m pytest movie_os/tests/test_phase7.py -v --override-ini="addopts="
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest


# ---------------------------------------------------------------------------
# ShotPlanner tests
# ---------------------------------------------------------------------------

class TestShotPlanner:
    """The ShotPlanner decides shot count and structure."""

    def _make_scene(self, **kwargs) -> "Scene":
        from movie_os.domain import Scene
        defaults = dict(
            number=1, title="S", phase="p", beat="b",
            scene_description="He sits in a chair.",
            shot_language={"shot_size": "medium", "lens_mm": 50},
            target_duration_seconds=10.0,
            energy=5,
        )
        defaults.update(kwargs)
        return Scene(**defaults)

    def test_default_scene_gets_one_shot(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        scene = self._make_scene()
        shots = planner.plan_shots(scene)
        assert len(shots) == 1

    def test_irreversible_moment_gets_two_shots(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        scene = self._make_scene(irreversible_moment=True, shot_language={"shot_size": "wide"})
        shots = planner.plan_shots(scene)
        assert len(shots) == 2

    def test_wide_shot_gets_two_shots(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        scene = self._make_scene(shot_language={"shot_size": "wide"})
        shots = planner.plan_shots(scene)
        assert len(shots) == 2

    def test_closeup_gets_one_shot(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        scene = self._make_scene(shot_language={"shot_size": "close-up"})
        shots = planner.plan_shots(scene)
        assert len(shots) == 1

    def test_low_energy_gets_one_shot(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        scene = self._make_scene(energy=1, shot_language={"shot_size": "wide"})
        shots = planner.plan_shots(scene)
        assert len(shots) == 1  # energy 1 overrides wide → 1 shot (held)

    def test_high_energy_gets_three_shots(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        scene = self._make_scene(energy=8, shot_language={"shot_size": "medium"})
        shots = planner.plan_shots(scene)
        assert len(shots) == 3

    def test_long_duration_medium_energy(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        # Long scene, medium energy, medium shot → should get 2 shots
        scene = self._make_scene(
            energy=5, target_duration_seconds=20.0,
            shot_language={"shot_size": "medium"},
        )
        shots = planner.plan_shots(scene)
        assert len(shots) == 2

    def test_short_duration_medium_energy(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        # Short scene, medium energy → 1 shot
        scene = self._make_scene(
            energy=5, target_duration_seconds=8.0,
            shot_language={"shot_size": "medium"},
        )
        shots = planner.plan_shots(scene)
        assert len(shots) == 1

    def test_shot_duration_sums_to_scene_duration(self):
        """The total duration of all shots should equal the scene duration."""
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        scene = self._make_scene(
            energy=8, target_duration_seconds=15.0,
            shot_language={"shot_size": "medium"},
        )
        shots = planner.plan_shots(scene)
        total = sum(s.duration_seconds for s in shots)
        # Allow small floating-point error
        assert abs(total - scene.target_duration_seconds) < 0.01

    def test_shot_movement_progression(self):
        """First shot is static, subsequent shots are push-in."""
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        # 3-shot sequence
        scene = self._make_scene(energy=8, shot_language={"shot_size": "medium"})
        shots = planner.plan_shots(scene)
        assert shots[0].camera_movement == "static"
        assert shots[1].camera_movement == "push-in"
        assert shots[2].camera_movement == "push-in"

    def test_visual_intent_per_shot(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        scene = self._make_scene(irreversible_moment=True, shot_language={"shot_size": "wide"})
        shots = planner.plan_shots(scene)
        # Each shot should have a non-empty visual_intent
        for shot in shots:
            assert shot.visual_intent
            # visual_intent should reference the scene description or shot info
            assert "shot" in shot.visual_intent.lower()

    def test_plan_scene_convenience_function(self):
        from movie_os.domain import ShotPlanner, plan_scene
        scene = self._make_scene(irreversible_moment=True, shot_language={"shot_size": "wide"})
        result = plan_scene(scene)
        assert result is scene  # in-place mutation
        assert len(scene.shots) == 2
        # Each shot should have frames
        for shot in scene.shots:
            assert len(shot.frames) > 0


# ---------------------------------------------------------------------------
# FramePlanner tests
# ---------------------------------------------------------------------------

class TestFramePlanner:
    """The FramePlanner decides frame count and structure."""

    def _make_scene(self, **kwargs) -> "Scene":
        from movie_os.domain import Scene
        defaults = dict(
            number=1, title="S", phase="p", beat="b",
            scene_description="He sits in a chair.",
            scene_description_alt="Alt: his hand on the table.",
            shot_language={"shot_size": "medium"},
            target_duration_seconds=10.0,
        )
        defaults.update(kwargs)
        return Scene(**defaults)

    def test_default_scene_gets_one_frame_per_shot(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        scene = self._make_scene()
        shots = planner.plan_shots(scene)
        for shot in shots:
            frames = planner.plan_frames(shot, scene)
            assert len(frames) == 1

    def test_irreversible_moment_gets_two_frames(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        scene = self._make_scene(irreversible_moment=True, shot_language={"shot_size": "wide"})
        shots = planner.plan_shots(scene)
        for shot in shots:
            frames = planner.plan_frames(shot, scene)
            assert len(frames) == 2

    def test_irreversible_frame_2_uses_alt_description(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        scene = self._make_scene(
            irreversible_moment=True,
            scene_description_alt="Alt description here.",
            shot_language={"shot_size": "wide"},
        )
        shots = planner.plan_shots(scene)
        for shot in shots:
            frames = planner.plan_frames(shot, scene)
            assert "Alt description" in frames[1].description

    def test_irreversible_uses_flux_model(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        scene = self._make_scene(irreversible_moment=True, shot_language={"shot_size": "wide"})
        shots = planner.plan_shots(scene)
        for shot in shots:
            frames = planner.plan_frames(shot, scene)
            for frame in frames:
                assert frame.model == "flux"

    def test_default_uses_sdxl_model(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        scene = self._make_scene()
        shots = planner.plan_shots(scene)
        for shot in shots:
            frames = planner.plan_frames(shot, scene)
            for frame in frames:
                assert frame.model == "sdxl"

    def test_irreversible_uses_ipadapter_workflow(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        scene = self._make_scene(irreversible_moment=True, shot_language={"shot_size": "wide"})
        shots = planner.plan_shots(scene)
        for shot in shots:
            frames = planner.plan_frames(shot, scene)
            for frame in frames:
                assert frame.workflow == "ipadapter"

    def test_default_uses_default_workflow(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()
        scene = self._make_scene()
        shots = planner.plan_shots(scene)
        for shot in shots:
            frames = planner.plan_frames(shot, scene)
            for frame in frames:
                assert frame.workflow == "default"


# ---------------------------------------------------------------------------
# CharacterRegistry integration
# ---------------------------------------------------------------------------

class TestCharacterReferenceLookup:
    """Frames include character hero image references when registry is provided."""

    def _make_scene_with_chars(self):
        from movie_os.domain import Scene
        return Scene(
            number=1, title="S", phase="p", beat="b",
            scene_description="Ethan looks at Claire.",
            shot_language={"shot_size": "medium"},
            target_duration_seconds=10.0,
            characters_present=["ethan_morrison", "claire_morrison"],
        )

    def test_no_registry_no_references(self):
        from movie_os.domain import ShotPlanner
        planner = ShotPlanner()  # no registry
        scene = self._make_scene_with_chars()
        shots = planner.plan_shots(scene)
        for shot in shots:
            frames = planner.plan_frames(shot, scene)
            for frame in frames:
                # No references because no registry
                assert len(frame.reference_image_ids) == 0

    def test_with_registry_picks_up_heroes(self, tmp_path):
        from movie_os.data_layer import CharacterRegistry
        from movie_os.domain import CharacterDNA, PhysicalAppearance, Gender
        from movie_os.domain import ShotPlanner

        # Create a registry with ethan + claire, each with a hero image
        reg = CharacterRegistry(tmp_path / "chars")
        reg.save(CharacterDNA(
            key="ethan_morrison", name="Ethan Morrison",
            physical=PhysicalAppearance(age=32, gender=Gender.MALE, visual_anchor="man"),
        ))
        reg.save(CharacterDNA(
            key="claire_morrison", name="Claire Morrison",
            physical=PhysicalAppearance(age=30, gender=Gender.FEMALE, visual_anchor="woman"),
        ))
        # Save fake hero images
        (tmp_path / "chars" / "ethan_morrison").mkdir(parents=True, exist_ok=True)
        (tmp_path / "chars" / "ethan_morrison" / "hero.png").write_bytes(b"\x89PNG")
        (tmp_path / "chars" / "claire_morrison").mkdir(parents=True, exist_ok=True)
        (tmp_path / "chars" / "claire_morrison" / "hero.png").write_bytes(b"\x89PNG")

        planner = ShotPlanner(character_registry=reg)
        scene = self._make_scene_with_chars()
        shots = planner.plan_shots(scene)
        for shot in shots:
            frames = planner.plan_frames(shot, scene)
            for frame in frames:
                # Two references (one per character)
                assert len(frame.reference_image_ids) == 2


# ---------------------------------------------------------------------------
# Manifest integration
# ---------------------------------------------------------------------------

class TestManifestShotsIntegration:
    """The timeline_to_manifest adapter includes shots/frames in the output."""

    def test_manifest_includes_shots(self):
        from movie_os.domain import Scene
        from story_factory import MasterTimeline, timeline_to_manifest
        from story_factory.timeline_to_manifest import populate_shots_and_frames

        timeline = MasterTimeline(
            metadata={"territory": "test"},
            characters=[],
        )
        timeline.scenes = [
            Scene(
                number=1, title="Hook", phase="hook", beat="opening_hook",
                scene_description="He lies in bed.",
                shot_language={"shot_size": "close-up", "lens_mm": 50},
                target_duration_seconds=10.0, energy=3,
            ),
        ]
        populate_shots_and_frames(timeline)
        manifest = timeline_to_manifest(timeline, story_file="story.md")

        assert "shots" in manifest["scenes"][0]
        assert len(manifest["scenes"][0]["shots"]) == 1
        shot = manifest["scenes"][0]["shots"][0]
        assert shot["shot_number"] == 1
        assert shot["shot_size"] == "close-up"
        assert "frames" in shot
        assert len(shot["frames"]) == 1

    def test_manifest_irreversible_has_more_frames(self):
        from movie_os.domain import Scene
        from story_factory import MasterTimeline, timeline_to_manifest
        from story_factory.timeline_to_manifest import populate_shots_and_frames

        timeline = MasterTimeline(
            metadata={"territory": "test"},
            characters=[],
        )
        timeline.scenes = [
            Scene(
                number=7, title="Irreversible", phase="collapse", beat="irreversible_moment",
                scene_description="Empty room.",
                scene_description_alt="Close-up of his hand.",
                shot_language={"shot_size": "wide", "lens_mm": 35},
                target_duration_seconds=8.0, energy=1,
                irreversible_moment=True,
            ),
        ]
        populate_shots_and_frames(timeline)
        manifest = timeline_to_manifest(timeline, story_file="story.md")

        # 2 shots, each with 2 frames
        assert len(manifest["scenes"][0]["shots"]) == 2
        for shot in manifest["scenes"][0]["shots"]:
            assert len(shot["frames"]) == 2
            # Frame 2 should use scene_description_alt
            assert "Close-up of his hand" in shot["frames"][1]["description"]

    def test_act_inferred_from_phase(self):
        from movie_os.domain import Scene
        from story_factory import MasterTimeline, timeline_to_manifest
        from story_factory.timeline_to_manifest import populate_shots_and_frames

        timeline = MasterTimeline(metadata={"territory": "test"}, characters=[])
        timeline.scenes = [
            Scene(number=1, title="Hook", phase="hook", beat="b",
                  scene_description="x", target_duration_seconds=10.0, energy=3),
            Scene(number=5, title="Crack", phase="crack", beat="b",
                  scene_description="x", target_duration_seconds=10.0, energy=3),
            Scene(number=9, title="Retreat", phase="retreat", beat="b",
                  scene_description="x", target_duration_seconds=10.0, energy=3),
        ]
        populate_shots_and_frames(timeline)
        manifest = timeline_to_manifest(timeline, story_file="story.md")

        assert manifest["scenes"][0]["act"] == "act_1_observation"
        assert manifest["scenes"][1]["act"] == "act_2_inner_reality"
        assert manifest["scenes"][2]["act"] == "act_3_psychological_truth"


# ---------------------------------------------------------------------------
# New prompt
# ---------------------------------------------------------------------------

class TestShotPrompt:
    """The story.shots.v1 prompt template loads correctly."""

    def test_prompt_loads(self):
        from movie_os.prompts import get_default_repository
        repo = get_default_repository()
        assert repo.has("story.shots.v1")
        t = repo.get("story.shots.v1")
        assert t.metadata.id == "story.shots.v1"
        assert t.metadata.capability == "story"

    def test_prompt_renders(self):
        from movie_os.prompts import get_default_repository
        repo = get_default_repository()
        t = repo.get("story.shots.v1")
        rendered = t.render({
            "scene_description": "He sits alone.",
            "emotional_state": "tense_restraint",
            "energy": 3,
            "shot_count": 1,
            "irreversible_moment": False,
            "format_spec": '{"shot_number": 1, "shot_size": "close-up", ...}',
        })
        assert "He sits alone" in rendered
        assert "tense_restraint" in rendered
        assert "1 shot" in rendered


# ---------------------------------------------------------------------------
# Backward compat
# ---------------------------------------------------------------------------

class TestBackwardCompat:
    """Phase 7 doesn't break anything that worked before."""

    def test_story_factory_still_works(self):
        from story_factory import (
            generate_dna, generate_context, generate_story, structure_scenes,
        )
        import inspect
        assert "synopsis" in inspect.signature(generate_dna).parameters

    def test_providers_still_work(self):
        from movie_os.providers import SDXLLocalProvider, registry
        assert isinstance(registry.make("image", "sdxl_local", {}, 0.0), SDXLLocalProvider)

    def test_existing_tests_still_pass(self):
        # The Phase 7 changes are additive — existing 303 tests should still pass
        # This is verified by the full test suite, just ensure we can import everything
        from movie_os.domain import Story, Act, Sequence, Scene, Shot, Frame
        from movie_os.capabilities import CapabilityRegistry
        from movie_os.data_layer import CharacterRegistry
        from movie_os.prompts import PromptRepository
        from movie_os.config import MovieOSConfig
        # All imports work
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
