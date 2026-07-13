"""Tests for the Movie OS Phase 0 deliverables.

These tests verify:
- Domain models (Story, CharacterDNA, EnvironmentDNA, Asset, Prompt) can be instantiated
- Domain models roundtrip through JSON serialization
- CapabilityRegistry works (register, get, list, has, unregister)
- Capability stubs are importable and can_handle correctly
- PromptTemplate loads, validates, and renders correctly
- PromptBuilder assembles context from Scene objects
- PromptValidator catches constraint violations
- PromptRenderer is the end-to-end pipeline

Run with:
    cd /Users/santosh/Desktop/projects/videoGen
    ./venv/bin/python -m pytest movie_os/tests/ -v --override-ini="addopts="
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest


# ---------------------------------------------------------------------------
# Domain model tests
# ---------------------------------------------------------------------------

class TestStoryHierarchy:
    """Story → Act → Sequence → Scene → Shot → Frame roundtrip."""

    def test_story_creation(self):
        from movie_os.domain import Story, Act, Sequence, Scene
        story = Story(title="Test")
        assert story.title == "Test"
        assert story.acts == []

    def test_full_hierarchy_construction(self):
        from movie_os.domain import Story, Act, Sequence, Scene
        story = Story(title="Test", logline="A test logline", territory="test")
        act = Act(number=1, title="Act 1", viewer_response="Setup")
        story.acts.append(act)
        seq = Sequence(title="Sequence 1")
        act.sequences.append(seq)
        scene = Scene(
            number=1, title="Scene 1", phase="hook", beat="opening_hook",
            voiceover="He almost reached.", target_duration_seconds=15.0,
        )
        seq.scenes.append(scene)
        # Total duration computes from the leaf
        assert story.acts[0].sequences[0].scenes[0].target_duration_seconds == 15.0

    def test_hierarchy_roundtrip_json(self):
        from movie_os.domain import Story
        story = Story(
            title="Test", logline="L", territory="t", ending="quiet_realization",
            target_duration_seconds=60.0,
        )
        data = story.model_dump(mode="json")
        restored = Story.model_validate(data)
        assert restored.title == "Test"
        assert restored.ending == "quiet_realization"

    def test_scene_with_shot_and_frame(self):
        from movie_os.domain import Scene, Shot, Frame
        scene = Scene(number=1, title="S", phase="p", beat="b", target_duration_seconds=10.0)
        shot = Shot(number=1, shot_size="close-up", duration_seconds=10.0)
        frame = Frame(number=1, description="Main frame", model="sdxl", seed=42)
        shot.frames.append(frame)
        scene.shots.append(shot)
        assert scene.shots[0].frames[0].seed == 42


class TestCharacterDNA:
    """CharacterDNA has 9 facets."""

    def test_minimal_construction(self):
        from movie_os.domain import CharacterDNA, PhysicalAppearance
        char = CharacterDNA(
            key="husband", name="Ethan",
            physical=PhysicalAppearance(age=32, visual_anchor="man mid-30s"),
        )
        assert char.key == "husband"
        assert char.physical.age == 32
        assert char.psychological.personality_traits == []

    def test_all_nine_facets(self):
        from movie_os.domain import (
            CharacterDNA, PhysicalAppearance, PsychologicalProfile,
            SpeechProfile, VoiceProfile, Wardrobe, ExpressionRange,
            CharacterHistory, DevelopmentArc, Gender,
        )
        char = CharacterDNA(
            key="wife", name="Sarah", role="partner",
            physical=PhysicalAppearance(age=30, gender=Gender.FEMALE, hair="auburn"),
            psychological=PsychologicalProfile(
                personality_traits=["warm", "intuitive"],
                core_fear="being unwanted",
            ),
            speech=SpeechProfile(speaking_style="soft, short sentences"),
            voice=VoiceProfile(tts_voice="en-US-JennyNeural", pitch="medium"),
            wardrobe=Wardrobe(default_outfit="white shirt, cardigan"),
            expressions=ExpressionRange(expressions=["warmth: leaning in"]),
            history=CharacterHistory(backstory="Married 8 years"),
            arc=DevelopmentArc(starting_state="secure", ending_state="grieving"),
        )
        assert char.psychological.core_fear == "being unwanted"
        assert char.voice.tts_voice == "en-US-JennyNeural"
        assert char.wardrobe.default_outfit == "white shirt, cardigan"

    def test_relationships(self):
        from movie_os.domain import CharacterDNA, PhysicalAppearance, Relationship
        import uuid
        wife = CharacterDNA(
            key="wife", name="Sarah",
            physical=PhysicalAppearance(age=30, visual_anchor="woman"),
        )
        husband = CharacterDNA(
            key="husband", name="Ethan",
            physical=PhysicalAppearance(age=32, visual_anchor="man"),
        )
        husband.relationships.append(Relationship(
            other_character_id=wife.id,
            relationship_type="wife",
            emotional_dynamic="protective but distant",
        ))
        assert husband.relationships[0].relationship_type == "wife"


class TestEnvironmentDNA:
    """EnvironmentDNA has 8 facets."""

    def test_minimal_construction(self):
        from movie_os.domain import EnvironmentDNA
        env = EnvironmentDNA(key="bedroom", name="Bedroom")
        assert env.key == "bedroom"
        assert env.lighting.primary_source == "natural"

    def test_all_facets(self):
        from movie_os.domain import (
            EnvironmentDNA, LightingProfile, ColorPalette, SoundAmbience,
            CameraPosition, EnvironmentVariant, TimeOfDay, Weather,
        )
        env = EnvironmentDNA(
            key="bedroom", name="Bedroom",
            lighting=LightingProfile(
                primary_source="bedside lamp",
                color_temperature="warm amber",
                practical_lights=["lamp", "phone glow"],
            ),
            palette=ColorPalette(
                dominant="cool blue", accent="warm amber",
                shadows="deep", highlights="soft",
            ),
            ambience=SoundAmbience(
                room_tone="fan hum",
                primary_sounds=["fan", "breathing"],
            ),
            camera_positions=[
                CameraPosition(name="bedside", description="low angle"),
            ],
            variants=[
                EnvironmentVariant(time_of_day=TimeOfDay.NIGHT, weather=Weather.CLEAR),
            ],
        )
        assert env.lighting.practical_lights == ["lamp", "phone glow"]
        assert env.ambience.room_tone == "fan hum"


class TestAsset:
    """Asset, Render, Reference."""

    def test_asset_creation(self):
        from movie_os.domain import Asset, AssetType, AssetStatus
        asset = Asset(type=AssetType.IMAGE, status=AssetStatus.COMPLETED, path=Path("/tmp/x.png"))
        assert asset.type == AssetType.IMAGE
        assert asset.status == AssetStatus.COMPLETED

    def test_render_creation(self):
        from movie_os.domain import Render, AssetType, RenderBackend
        render = Render(
            type=AssetType.IMAGE, prompt="test", model="sdxl", seed=42,
            backend=RenderBackend.SDXL_LOCAL,
        )
        assert render.prompt == "test"
        assert render.seed == 42


# ---------------------------------------------------------------------------
# Capability Registry tests
# ---------------------------------------------------------------------------

class TestCapabilityRegistry:
    """The registry is the plug-in hub."""

    def setup_method(self):
        from movie_os.capabilities import CapabilityRegistry
        self.registry = CapabilityRegistry()

    def test_register_and_get(self):
        from movie_os.capabilities import ImageCapability
        cap = ImageCapability(provider=None)
        self.registry.register(cap)
        assert self.registry.get("image") is cap

    def test_get_missing_raises(self):
        with pytest.raises(KeyError):
            self.registry.get("voice")

    def test_try_get_missing_returns_none(self):
        assert self.registry.try_get("voice") is None

    def test_has(self):
        from movie_os.capabilities import ImageCapability
        self.registry.register(ImageCapability(provider=None))
        assert self.registry.has("image")
        assert not self.registry.has("voice")

    def test_unregister(self):
        from movie_os.capabilities import ImageCapability
        self.registry.register(ImageCapability(provider=None))
        self.registry.unregister("image")
        assert "image" not in self.registry.list()

    def test_list_returns_sorted(self):
        from movie_os.capabilities import ImageCapability, MusicCapability
        self.registry.register(ImageCapability(provider=None))
        self.registry.register(MusicCapability())
        assert self.registry.list() == ["image", "music"]

    def test_info(self):
        from movie_os.capabilities import ImageCapability
        self.registry.register(ImageCapability(provider=None))
        info = self.registry.info()
        assert info[0]["name"] == "image"
        assert info[0]["class"] == "ImageCapability"

    def test_global_default_registry(self):
        from movie_os.capabilities import get_default_registry
        g1 = get_default_registry()
        g2 = get_default_registry()
        assert g1 is g2  # singleton


class TestCapabilityStubs:
    """Each capability stub can_handle correctly."""

    def test_image_can_handle(self):
        from movie_os.capabilities import ImageCapability, ImageIntent
        cap = ImageCapability(provider=None)
        assert cap.can_handle(ImageIntent(prompt="x"))
        assert not cap.can_handle(ImageIntent(prompt=""))

    def test_voice_can_handle(self):
        from movie_os.capabilities import VoiceCapability, VoiceIntent
        cap = VoiceCapability()
        assert cap.can_handle(VoiceIntent(text="hello"))
        assert not cap.can_handle(VoiceIntent(text=""))

    def test_music_can_handle(self):
        from movie_os.capabilities import MusicCapability, MusicIntent
        cap = MusicCapability()
        assert cap.can_handle(MusicIntent(zone="act_1"))
        assert not cap.can_handle(MusicIntent(zone=""))

    def test_story_can_handle(self):
        from movie_os.capabilities import StoryCapability, StoryIntent
        cap = StoryCapability()
        assert cap.can_handle(StoryIntent(task="dna"))
        assert not cap.can_handle(StoryIntent(task=""))

    def test_stubs_raise_not_implemented(self):
        """All stubs should raise NotImplementedError on execute."""
        import asyncio
        from movie_os.capabilities import (
            VoiceCapability, VoiceIntent,
            MusicCapability, MusicIntent,
            StoryCapability, StoryIntent,
            VideoCapability, VideoIntent,
            TranslationCapability, TranslationIntent,
            ResearchCapability, ResearchIntent,
        )
        for cap, intent in [
            (VoiceCapability(), VoiceIntent(text="x")),
            (MusicCapability(), MusicIntent(zone="act_1")),
            (StoryCapability(), StoryIntent(task="dna")),
            (VideoCapability(), VideoIntent(image_path="/tmp/x.png")),
            (TranslationCapability(), TranslationIntent(text="x", target_language="es")),
            (ResearchCapability(), ResearchIntent(query="x")),
        ]:
            with pytest.raises(NotImplementedError):
                asyncio.run(cap.execute(intent))


# ---------------------------------------------------------------------------
# Prompt system tests
# ---------------------------------------------------------------------------

class TestPromptTemplate:
    """The structured prompt format."""

    def test_load_cinematic_template(self):
        from movie_os.prompts import load_prompt_template
        t = load_prompt_template("movie_os/prompts/image/cinematic.yaml")
        assert t.metadata.id == "image.cinematic.v1"
        assert len(t.variables) >= 5
        assert len(t.constraints) >= 1
        assert len(t.negative_prompts) > 0

    def test_render_with_context(self):
        from movie_os.prompts import load_prompt_template
        t = load_prompt_template("movie_os/prompts/image/cinematic.yaml")
        rendered = t.render({
            "subject": "a man sitting alone",
            "mood": "tense_restraint",
            "shot_size": "close-up",
            "lens_mm": 50,
            "lighting_key": "practical_lighting",
        })
        assert "a man sitting alone" in rendered
        assert "tense_restraint" in rendered
        assert "{{" not in rendered  # all placeholders filled

    def test_render_uses_defaults(self):
        from movie_os.prompts import load_prompt_template
        t = load_prompt_template("movie_os/prompts/image/cinematic.yaml")
        # Only provide required variables — defaults should fill the rest
        rendered = t.render({
            "subject": "a couple",
            "mood": "warm",
        })
        assert "a couple" in rendered
        assert "warm" in rendered
        # style_anchor has a default — should be filled
        assert "{{style_anchor}}" not in rendered

    def test_missing_required_raises(self):
        from movie_os.prompts import load_prompt_template
        t = load_prompt_template("movie_os/prompts/image/cinematic.yaml")
        with pytest.raises(ValueError, match="Missing required variable"):
            t.render({"mood": "tense"})  # missing 'subject'

    def test_undeclared_variable_in_body_raises(self):
        """If the body uses a variable not in the variables list, raise on load."""
        from movie_os.domain import PromptTemplate, PromptMetadata, Variable, VariableType
        with pytest.raises(ValueError, match="undeclared variable"):
            PromptTemplate(
                metadata=PromptMetadata(id="x", capability="test"),
                variables=[Variable(name="foo", type=VariableType.STRING, required=True)],
                body="hello {{foo}} and {{bar}}",  # bar is undeclared
            )


class TestPromptBuilder:
    """Builds context from a Scene."""

    def test_build_from_scene_minimal(self):
        from movie_os.prompts import load_prompt_template, PromptBuilder
        from movie_os.domain import Scene
        t = load_prompt_template("movie_os/prompts/image/cinematic.yaml")
        scene = Scene(
            number=1, title="S", phase="p", beat="b",
            scene_description="a man in a dark room",
            emotional_state="tense_restraint", energy=3,
            voiceover="He almost reached.",
            shot_language={"shot_size": "close-up", "lens_mm": 50, "lighting_key": "practical"},
            characters_present=["husband"],
        )
        builder = PromptBuilder(t)
        ctx = builder.build_from_scene(scene)
        assert ctx["subject"] == "a man in a dark room"
        assert ctx["mood"] == "tense_restraint"
        assert ctx["shot_size"] == "close-up"
        assert ctx["lens_mm"] == 50
        assert ctx["lighting_key"] == "practical"


class TestPromptValidator:
    """Validates rendered prompts against constraints."""

    def test_pass_on_good_prompt(self):
        from movie_os.prompts import load_prompt_template, PromptValidator
        t = load_prompt_template("movie_os/prompts/image/cinematic.yaml")
        v = PromptValidator(t)
        rendered = "a man sitting in a room, tense_restraint mood, close-up shot, 50mm lens"
        result = v.validate(rendered, {"subject": "x", "mood": "tense_restraint"})
        assert result.passed

    def test_fail_on_undeclared_negative(self):
        from movie_os.prompts import load_prompt_template, PromptValidator
        t = load_prompt_template("movie_os/prompts/image/cinematic.yaml")
        v = PromptValidator(t)
        rendered = "a cartoon character sitting in a room"
        result = v.validate(rendered, {"subject": "x", "mood": "tense_restraint"})
        # "cartoon" is in negative_prompts
        assert any("cartoon" in w for w in result.warnings)

    def test_fail_on_word_count(self):
        from movie_os.prompts import load_prompt_template, PromptValidator
        t = load_prompt_template("movie_os/prompts/image/cinematic.yaml")
        v = PromptValidator(t)
        # Render a very long prompt
        long_prompt = " ".join(["word"] * 100)
        result = v.validate(long_prompt, {"subject": "x", "mood": "tense_restraint"})
        # The "max 50 words" constraint is a "must" — so it's an issue
        assert any("50 words" in i for i in result.issues)


class TestPromptRenderer:
    """End-to-end: template → builder → validator → renderer."""

    def test_render_from_context(self):
        from movie_os.prompts import load_prompt_template, PromptRenderer
        t = load_prompt_template("movie_os/prompts/image/cinematic.yaml")
        renderer = PromptRenderer(t)
        rendered, validation = renderer.render({
            "subject": "a man sitting",
            "mood": "tense_restraint",
        })
        assert "a man sitting" in rendered
        assert validation.passed

    def test_render_from_scene(self):
        from movie_os.prompts import load_prompt_template, PromptRenderer
        from movie_os.domain import Scene
        t = load_prompt_template("movie_os/prompts/image/cinematic.yaml")
        scene = Scene(
            number=1, title="S", phase="p", beat="b",
            scene_description="a man in a dark room",
            emotional_state="tense_restraint", energy=3,
            shot_language={"shot_size": "close-up", "lens_mm": 50, "lighting_key": "practical"},
        )
        renderer = PromptRenderer(t)
        rendered, validation = renderer.render_from_scene(scene)
        assert "a man in a dark room" in rendered
        assert validation.passed


# ---------------------------------------------------------------------------
# End-to-end: load all prompts in the repo
# ---------------------------------------------------------------------------

class TestEndToEnd:
    """The whole Phase 0 system works together."""

    def test_load_all_prompts(self):
        from movie_os.prompts import load_all_prompts
        templates = load_all_prompts("movie_os/prompts")
        assert "image.cinematic.v1" in templates
        assert templates["image.cinematic.v1"].metadata.capability == "image"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
