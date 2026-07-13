"""Tests for the Movie OS Phase 3+4 deliverables (Provider ABCs + wrapping).

These tests verify:
- Provider ABCs exist with the right interface
- Concrete providers (SDXL, EdgeTTS, Procedural music/SFX, LMStudio story)
  can be instantiated and registered
- The built-in factory wires everything up correctly
- The CapabilityRegistry can use the built-in factory to wire providers
- Backward compat: the existing code still works (no regressions)

Run with:
    cd /Users/santosh/Desktop/projects/videoGen
    ./venv/bin/python -m pytest movie_os/tests/test_phase3_4.py -v --override-ini="addopts="
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest


# ---------------------------------------------------------------------------
# Provider ABC tests
# ---------------------------------------------------------------------------

class TestProviderABCs:
    """The provider ABCs exist with the right interface."""

    def test_image_provider_abc(self):
        from movie_os.providers import ImageProvider
        assert hasattr(ImageProvider, "render")
        assert hasattr(ImageProvider, "can_handle")
        assert hasattr(ImageProvider, "name")
        assert hasattr(ImageProvider, "backend")

    def test_voice_provider_abc(self):
        from movie_os.providers import VoiceProvider
        assert hasattr(VoiceProvider, "render")
        assert hasattr(VoiceProvider, "name")

    def test_music_provider_abc(self):
        from movie_os.providers import MusicProvider
        assert hasattr(MusicProvider, "render")
        assert hasattr(MusicProvider, "name")

    def test_sfx_provider_abc(self):
        from movie_os.providers import SFXProvider
        assert hasattr(SFXProvider, "render")
        assert hasattr(SFXProvider, "name")

    def test_story_provider_abc(self):
        from movie_os.providers import StoryProvider
        assert hasattr(StoryProvider, "render")
        assert hasattr(StoryProvider, "name")

    def test_translation_provider_abc(self):
        from movie_os.providers import TranslationProvider
        assert hasattr(TranslationProvider, "render")

    def test_research_provider_abc(self):
        from movie_os.providers import ResearchProvider
        assert hasattr(ResearchProvider, "render")


# ---------------------------------------------------------------------------
# Provider registry tests
# ---------------------------------------------------------------------------

class TestProviderRegistry:
    """The provider registry indexes (capability, label) -> maker."""

    def setup_method(self):
        from movie_os.providers import registry
        registry.reset()
        registry.register_builtin_providers()

    def test_builtin_providers_registered(self):
        from movie_os.providers import registry
        # All 5 built-in providers should be there
        assert registry.has("image", "sdxl_local")
        assert registry.has("voice", "edge_tts")
        assert registry.has("music", "procedural")
        assert registry.has("sfx", "procedural")
        assert registry.has("story", "lmstudio")

    def test_list_providers(self):
        from movie_os.providers import registry
        all_p = registry.list_providers()
        # 6 built-in providers: image(sdxl+flux), voice, music, sfx, story
        assert len(all_p) == 6
        image_p = registry.list_providers("image")
        assert len(image_p) == 2
        # Should have both SDXL and FLUX
        labels = {p["label"] for p in image_p}
        assert "sdxl_local" in labels
        assert "flux_comfyui" in labels

    def test_make_creates_provider(self):
        from movie_os.providers import registry
        provider = registry.make("image", "sdxl_local", {}, 0.0)
        assert provider is not None
        from movie_os.providers import ImageProvider
        assert isinstance(provider, ImageProvider)

    def test_make_unknown_returns_none(self):
        from movie_os.providers import registry
        assert registry.make("image", "nonexistent", {}, 0.0) is None
        assert registry.make("nonexistent", "anything", {}, 0.0) is None

    def test_register_and_unregister(self):
        from movie_os.providers import registry
        def my_maker(settings, cost):
            return "mock-provider"
        registry.register("image", "custom_test", my_maker)
        assert registry.has("image", "custom_test")
        registry.unregister("image", "custom_test")
        assert not registry.has("image", "custom_test")

    def test_make_failure_returns_none(self):
        """If the maker raises, registry returns None (doesn't crash)."""
        from movie_os.providers import registry
        def broken_maker(settings, cost):
            raise RuntimeError("simulated")
        registry.register("image", "broken_test", broken_maker)
        result = registry.make("image", "broken_test", {}, 0.0)
        assert result is None


# ---------------------------------------------------------------------------
# Concrete provider tests
# ---------------------------------------------------------------------------

class TestSDXLLocalProvider:
    """The SDXL provider wraps the legacy SDXLGenerator."""

    def test_make_with_defaults(self):
        from movie_os.providers import registry
        provider = registry.make("image", "sdxl_local", {}, 0.0)
        assert provider is not None
        assert provider.name == "sdxl_local"
        from movie_os.providers import ImageProvider
        assert isinstance(provider, ImageProvider)

    def test_make_with_custom_settings(self):
        from movie_os.providers import registry
        provider = registry.make("image", "sdxl_local", {
            "model": "custom-model",
            "device": "cpu",
            "resolution_width": 512,
            "resolution_height": 512,
        }, 0.0)
        assert provider.model == "custom-model"
        assert provider.device == "cpu"
        assert provider.resolution_width == 512
        assert provider.resolution_height == 512

    def test_can_handle_valid_intent(self):
        from movie_os.providers import registry
        from movie_os.capabilities.base import ImageIntent
        provider = registry.make("image", "sdxl_local", {}, 0.0)
        assert provider.can_handle(ImageIntent(prompt="x"))
        assert not provider.can_handle(ImageIntent(prompt=""))


class TestEdgeTTSProvider:
    """The Edge TTS provider wraps the legacy TTSService."""

    def test_make_with_defaults(self):
        from movie_os.providers import registry
        provider = registry.make("voice", "edge_tts", {}, 0.0)
        assert provider is not None
        assert provider.name == "edge_tts"
        from movie_os.providers import VoiceProvider
        assert isinstance(provider, VoiceProvider)

    def test_make_with_custom_voice(self):
        from movie_os.providers import registry
        provider = registry.make("voice", "edge_tts", {
            "default_voice": "en-US-JennyNeural",
        }, 0.0)
        assert provider.default_voice == "en-US-JennyNeural"

    def test_can_handle(self):
        from movie_os.providers import registry
        from movie_os.capabilities.base import VoiceIntent
        provider = registry.make("voice", "edge_tts", {}, 0.0)
        assert provider.can_handle(VoiceIntent(text="x"))
        assert not provider.can_handle(VoiceIntent(text=""))


class TestProceduralMusicProvider:
    """The procedural music provider wraps MusicGenerator."""

    def test_make_with_defaults(self):
        from movie_os.providers import registry
        provider = registry.make("music", "procedural", {}, 0.0)
        assert provider is not None
        from movie_os.providers import MusicProvider
        assert isinstance(provider, MusicProvider)

    def test_can_handle_zones(self):
        from movie_os.providers import registry
        from movie_os.capabilities.base import MusicIntent
        provider = registry.make("music", "procedural", {}, 0.0)
        for zone in ["act_1", "act_2", "act_3", "sting"]:
            assert provider.can_handle(MusicIntent(zone=zone))
        assert not provider.can_handle(MusicIntent(zone="unknown"))


class TestProceduralSFXProvider:
    """The procedural SFX provider wraps AmbientSFXGenerator."""

    def test_make_with_defaults(self):
        from movie_os.providers import registry
        provider = registry.make("sfx", "procedural", {}, 0.0)
        assert provider is not None
        from movie_os.providers import SFXProvider
        assert isinstance(provider, SFXProvider)


class TestLMStudioStoryProvider:
    """The LMStudio story provider wraps the story_factory."""

    def test_make_with_defaults(self):
        from movie_os.providers import registry
        provider = registry.make("story", "lmstudio", {}, 0.0)
        assert provider is not None
        from movie_os.providers import StoryProvider
        assert isinstance(provider, StoryProvider)

    def test_make_with_custom_url(self):
        from movie_os.providers import registry
        provider = registry.make("story", "lmstudio", {
            "base_url": "http://custom:1234",
            "narrative_model": "custom-model",
        }, 0.0)
        assert provider.base_url == "http://custom:1234"
        assert provider.narrative_model == "custom-model"

    def test_can_handle_tasks(self):
        from movie_os.providers import registry
        from movie_os.capabilities.base import StoryIntent
        provider = registry.make("story", "lmstudio", {}, 0.0)
        for task in ["dna", "context", "narrative", "scenes"]:
            assert provider.can_handle(StoryIntent(task=task))
        assert not provider.can_handle(StoryIntent(task="unknown"))


# ---------------------------------------------------------------------------
# Built-in factory + registry integration tests
# ---------------------------------------------------------------------------

class TestRegistryWithBuiltInFactory:
    """The CapabilityRegistry uses the built-in factory to wire providers."""

    def test_registry_with_built_in_factory(self):
        from movie_os.config import load_config
        from movie_os.capabilities import CapabilityRegistry
        from movie_os.providers import default_provider_factory

        config = load_config("movie_os/config/examples/movie_os.yaml")
        registry = CapabilityRegistry.from_config(
            config, provider_factory=default_provider_factory
        )

        # Image capability should have a real provider
        image_cap = registry.get("image")
        assert image_cap._provider is not None
        from movie_os.providers import SDXLLocalProvider
        assert isinstance(image_cap._provider, SDXLLocalProvider)

        # Voice capability should have a real provider
        voice_cap = registry.get("voice")
        assert voice_cap._provider is not None
        from movie_os.providers import EdgeTTSProvider
        assert isinstance(voice_cap._provider, EdgeTTSProvider)

        # Music capability should have a real provider
        music_cap = registry.get("music")
        assert music_cap._provider is not None
        from movie_os.providers import ProceduralMusicProvider
        assert isinstance(music_cap._provider, ProceduralMusicProvider)

        # Story capability should have a real provider
        story_cap = registry.get("story")
        assert story_cap._provider is not None
        from movie_os.providers import LMStudioStoryProvider
        assert isinstance(story_cap._provider, LMStudioStoryProvider)

    def test_disabled_provider_skipped(self):
        """If a provider is disabled in the config, the capability has no provider."""
        from movie_os.config import MovieOSConfig
        from movie_os.capabilities import CapabilityRegistry
        from movie_os.providers import default_provider_factory, registry as prov_registry

        # Reset and re-register
        prov_registry.reset()
        prov_registry.register_builtin_providers()

        config = MovieOSConfig.model_validate({
            "providers": {
                "image": {
                    "default": "sdxl_local",
                    "options": {
                        "sdxl_local": {"label": "SDXL", "enabled": False, "settings": {}},
                    },
                }
            }
        })
        registry = CapabilityRegistry.from_config(
            config, provider_factory=default_provider_factory
        )
        image_cap = registry.get("image")
        # Provider is None because it's disabled
        assert image_cap._provider is None


# ---------------------------------------------------------------------------
# Asset helper tests
# ---------------------------------------------------------------------------

class TestAssetHelpers:
    """The make_asset helper creates Asset objects correctly."""

    def test_make_asset_basic(self):
        from movie_os.providers.base import make_asset
        from movie_os.domain.asset import AssetType, RenderBackend
        asset = make_asset(
            path="/tmp/test.png",
            asset_type=AssetType.IMAGE,
            backend=RenderBackend.SDXL_LOCAL,
        )
        assert asset.type == AssetType.IMAGE
        assert asset.backend == RenderBackend.SDXL_LOCAL
        assert asset.path.name == "test.png"

    def test_make_asset_with_metadata(self):
        from movie_os.providers.base import make_asset
        from movie_os.domain.asset import AssetType, RenderBackend
        asset = make_asset(
            path="/tmp/test.png",
            asset_type=AssetType.IMAGE,
            backend=RenderBackend.SDXL_LOCAL,
            seed=42,
            clip_score=0.85,
            metadata={"prompt": "test"},
        )
        assert asset.seed == 42
        assert asset.clip_score == 0.85
        assert asset.metadata["prompt"] == "test"


# ---------------------------------------------------------------------------
# Backward compat
# ---------------------------------------------------------------------------

class TestBackwardCompat:
    """The existing code (story_factory, pipeline, openmontage_adapter) still works."""

    def test_story_factory_still_works(self):
        from story_factory import (
            generate_dna, generate_context, generate_story, structure_scenes,
        )
        import inspect
        sig = inspect.signature(generate_dna)
        assert "synopsis" in sig.parameters

    def test_pipeline_still_works(self):
        import sys
        sys.path.insert(0, "scripts")
        from psychological_pipeline import (
            NarrativeGenerator, MusicGenerator, DramaticStingGenerator,
        )
        assert MusicGenerator is not None

    def test_openmontage_still_works(self):
        from openmontage_adapter import (
            SceneIntent, SceneAsset, RenderBackend, SDXLLocalBackend, RenderOrchestrator,
        )
        # Can still create the legacy backend
        backend = SDXLLocalBackend(manifest_yaml="x.yaml", output_dir="output")
        assert backend is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
