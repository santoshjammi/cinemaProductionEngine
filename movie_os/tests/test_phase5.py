"""Tests for the Movie OS Phase 5 deliverables (ComfyUI + FLUX).

These tests verify:
- The ComfyUI HTTP client constructs correct requests
- The workflow JSON files are valid and loadable
- The FluxComfyUIProvider builds correct workflows
- Placeholder filling works
- Quality modes (draft/production/high_quality) select the right workflow
- The provider is registered and instantiable from config

We can't actually run ComfyUI in CI, so end-to-end rendering is
verified via mocking. The tests focus on:
- HTTP request construction
- Workflow validation
- Intent -> workflow mapping
- Provider wiring

Run with:
    cd /Users/santosh/Desktop/projects/videoGen
    ./venv/bin/python -m pytest movie_os/tests/test_phase5.py -v --override-ini="addopts="
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest


# ---------------------------------------------------------------------------
# ComfyUI Client tests
# ---------------------------------------------------------------------------

class TestComfyUIClient:
    """The ComfyUI HTTP client."""

    def test_health_returns_true_when_reachable(self):
        from movie_os.workflows import ComfyUIClient
        client = ComfyUIClient(base_url="http://localhost:8188")
        with patch.object(client, "_request", return_value={}):
            assert client.health() is True

    def test_health_returns_false_when_unreachable(self):
        from movie_os.workflows import ComfyUIClient, ComfyUIError
        client = ComfyUIClient(base_url="http://localhost:8188")
        with patch.object(client, "_request", side_effect=ComfyUIError("unreachable")):
            assert client.health() is False

    def test_submit_returns_prompt_id(self):
        from movie_os.workflows import ComfyUIClient
        client = ComfyUIClient(base_url="http://localhost:8188")
        with patch.object(client, "_request", return_value={"prompt_id": "abc-123"}):
            prompt_id = client.submit({"some": "workflow"})
            assert prompt_id == "abc-123"

    def test_submit_raises_on_bad_response(self):
        from movie_os.workflows import ComfyUIClient, ComfyUIError
        client = ComfyUIClient(base_url="http://localhost:8188")
        with patch.object(client, "_request", return_value={"error": "something"}):
            with pytest.raises(ComfyUIError):
                client.submit({"some": "workflow"})

    def test_get_history(self):
        from movie_os.workflows import ComfyUIClient
        client = ComfyUIClient(base_url="http://localhost:8188")
        with patch.object(client, "_request", return_value={
            "abc-123": {"status": {"completed": True}}
        }):
            history = client.get_history("abc-123")
            assert history["status"]["completed"] is True

    def test_get_outputs_extracts_images(self):
        from movie_os.workflows import ComfyUIClient
        client = ComfyUIClient(base_url="http://localhost:8188")
        history = {
            "outputs": {
                "9": {"images": [{"filename": "out.png", "subfolder": "", "type": "output"}]},
                "11": {"images": [{"filename": "out2.png", "subfolder": "", "type": "output"}]},
            }
        }
        outputs = client.get_outputs(history)
        assert len(outputs) == 2
        assert outputs[0]["filename"] == "out.png"

    def test_wait_for_result_returns_on_completion(self):
        from movie_os.workflows import ComfyUIClient
        client = ComfyUIClient(base_url="http://localhost:8188")
        # Simulate: first call -> not complete, second call -> complete
        with patch.object(client, "get_history") as mock_history:
            mock_history.side_effect = [
                None,  # not in history yet
                {"status": {"completed": True}, "outputs": {"9": {"images": []}}},
            ]
            with patch("time.sleep"):  # skip the sleep
                result = client.wait_for_result("abc-123", timeout=10)
            assert result["status"]["completed"] is True

    def test_wait_for_result_times_out(self):
        from movie_os.workflows import ComfyUIClient, ComfyUIError
        client = ComfyUIClient(base_url="http://localhost:8188")
        with patch.object(client, "get_history", return_value=None):
            with patch("time.sleep"):
                with pytest.raises(ComfyUIError):
                    client.wait_for_result("abc-123", timeout=0.1)


# ---------------------------------------------------------------------------
# Workflow tests
# ---------------------------------------------------------------------------

class TestWorkflows:
    """The workflow JSON files."""

    def test_list_workflows(self):
        from movie_os.workflows import list_workflows
        workflows = list_workflows()
        assert "flux_txt2img" in workflows
        assert "flux_img2img" in workflows
        assert "flux_with_ipadapter" in workflows
        assert "flux_with_lora" in workflows

    def test_load_workflow(self):
        from movie_os.workflows import load_workflow
        workflow = load_workflow("flux_txt2img")
        # Should have several nodes
        assert len(workflow) >= 5
        # Should be a dict of node_id -> node_config
        for node_id, node in workflow.items():
            assert "class_type" in node, f"Node {node_id} missing class_type"

    def test_load_nonexistent_workflow_raises(self):
        from movie_os.workflows import load_workflow
        with pytest.raises(FileNotFoundError):
            load_workflow("nonexistent_workflow")

    def test_all_workflows_valid_json(self):
        """Every workflow JSON is valid and has the expected structure."""
        from movie_os.workflows import list_workflows, load_workflow
        for name in list_workflows():
            workflow = load_workflow(name)
            # Must have a SaveImage node (the final output)
            has_save = any(
                node.get("class_type") == "SaveImage"
                for node in workflow.values()
            )
            assert has_save, f"Workflow {name} has no SaveImage node"
            # Must have a KSampler
            has_sample = any(
                node.get("class_type") == "KSampler"
                for node in workflow.values()
            )
            assert has_sample, f"Workflow {name} has no KSampler node"


class TestFillPlaceholders:
    """The placeholder replacement utility."""

    def test_simple_replacement(self):
        from movie_os.workflows import fill_placeholders
        workflow = {"a": "PLACEHOLDER_FOO"}
        fill_placeholders(workflow, {"foo": "bar"})
        assert workflow["a"] == "bar"

    def test_nested_replacement(self):
        from movie_os.workflows import fill_placeholders
        workflow = {
            "1": {"inputs": {"text": "PLACEHOLDER_PROMPT"}},
            "2": {"inputs": {"seed": 42}},
        }
        fill_placeholders(workflow, {"prompt": "a man sitting"})
        assert workflow["1"]["inputs"]["text"] == "a man sitting"

    def test_list_replacement(self):
        from movie_os.workflows import fill_placeholders
        workflow = {"list": ["PLACEHOLDER_A", "PLACEHOLDER_B"]}
        fill_placeholders(workflow, {"a": "1", "b": "2"})
        assert workflow["list"] == ["1", "2"]

    def test_partial_replacement(self):
        """A string with multiple placeholders gets all replaced."""
        from movie_os.workflows import fill_placeholders
        workflow = {"a": "PLACEHOLDER_A and PLACEHOLDER_B"}
        fill_placeholders(workflow, {"a": "first", "b": "second"})
        assert workflow["a"] == "first and second"

    def test_unfilled_placeholder_stays(self):
        """A placeholder with no replacement stays as-is."""
        from movie_os.workflows import fill_placeholders
        workflow = {"a": "PLACEHOLDER_MISSING"}
        fill_placeholders(workflow, {})
        assert workflow["a"] == "PLACEHOLDER_MISSING"


# ---------------------------------------------------------------------------
# FluxComfyUIProvider tests
# ---------------------------------------------------------------------------

class TestFluxComfyUIProvider:
    """The FLUX provider."""

    def test_make_with_defaults(self):
        from movie_os.providers import FluxComfyUIProvider, registry
        provider = registry.make("image", "flux_comfyui", {}, 0.0)
        assert provider is not None
        assert isinstance(provider, FluxComfyUIProvider)
        assert provider.name == "flux_comfyui"
        assert provider.comfyui_url == "http://localhost:8188"

    def test_make_with_custom_settings(self):
        from movie_os.providers import registry
        provider = registry.make("image", "flux_comfyui", {
            "comfyui_url": "http://custom:9999",
            "model": "flux1-schnell-fp8.safetensors",
            "ipadapter_strength": 0.8,
        }, 0.0)
        assert provider.comfyui_url == "http://custom:9999"
        assert provider.model == "flux1-schnell-fp8.safetensors"
        assert provider.ipadapter_strength == 0.8

    def test_workflow_selection_default(self):
        """No reference image, no explicit quality -> flux_txt2img."""
        from movie_os.providers import registry
        from movie_os.capabilities.base import ImageIntent
        provider = registry.make("image", "flux_comfyui", {}, 0.0)
        intent = ImageIntent(prompt="a man sitting", quality="production")
        assert provider._select_workflow(intent) == "flux_txt2img"

    def test_workflow_selection_with_reference_ipadapter(self):
        """Reference image + IPAdapter (default) -> flux_with_ipadapter."""
        from movie_os.providers import registry
        from movie_os.capabilities.base import ImageIntent
        provider = registry.make("image", "flux_comfyui", {}, 0.0)
        intent = ImageIntent(
            prompt="a man sitting",
            reference_image_paths=["/tmp/ref.png"],
            metadata={},
        )
        assert provider._select_workflow(intent) == "flux_with_ipadapter"

    def test_workflow_selection_with_reference_img2img(self):
        """Reference image + use_img2img=True (and use_ipadapter=False) -> flux_img2img."""
        from movie_os.providers import registry
        from movie_os.capabilities.base import ImageIntent
        provider = registry.make("image", "flux_comfyui", {}, 0.0)
        intent = ImageIntent(
            prompt="a man sitting",
            reference_image_paths=["/tmp/ref.png"],
            metadata={"use_img2img": True, "use_ipadapter": False},
        )
        assert provider._select_workflow(intent) == "flux_img2img"

    def test_workflow_selection_quality_modes(self):
        from movie_os.providers import registry
        from movie_os.capabilities.base import ImageIntent
        provider = registry.make("image", "flux_comfyui", {}, 0.0)
        # draft -> flux_txt2img (Schnell, 4 steps)
        intent = ImageIntent(prompt="x", metadata={"quality": "draft"})
        assert provider._select_workflow(intent) == "flux_txt2img"
        # high_quality -> flux_with_lora
        intent = ImageIntent(prompt="x", metadata={"quality": "high_quality"})
        assert provider._select_workflow(intent) == "flux_with_lora"

    def test_build_workflow_fills_placeholders(self):
        from movie_os.providers import registry
        from movie_os.capabilities.base import ImageIntent
        provider = registry.make("image", "flux_comfyui", {}, 0.0)
        intent = ImageIntent(
            prompt="a man sitting alone",
            width=1024, height=576, seed=42,
            metadata={"quality": "production"},
        )
        workflow = provider._build_workflow(intent, "flux_txt2img")
        # The prompt should be in node 5 (CLIPTextEncode positive)
        assert "a man sitting alone" in workflow["5"]["inputs"]["text"]
        # The seed should be in node 8 (KSampler)
        assert workflow["8"]["inputs"]["seed"] == 42
        # The width should be in node 4 (EmptyLatentImage)
        assert workflow["4"]["inputs"]["width"] == 1024
        # The unet should match the model name
        assert workflow["1"]["inputs"]["unet_name"] == "flux1-dev-fp8.safetensors"
        # Draft quality should produce 4 steps
        intent_draft = ImageIntent(
            prompt="x", width=256, height=256, seed=1,
            quality="draft",
        )
        wf_draft = provider._build_workflow(intent_draft, "flux_txt2img")
        for node in wf_draft.values():
            if node.get("class_type") == "KSampler":
                assert node["inputs"]["steps"] == 4

    def test_render_fails_if_comfyui_unreachable(self):
        from movie_os.providers import registry
        from movie_os.capabilities.base import ImageIntent
        from movie_os.workflows import ComfyUIError
        provider = registry.make("image", "flux_comfyui", {
            "comfyui_url": "http://nonexistent-host-abc123.invalid",
        }, 0.0)
        intent = ImageIntent(prompt="x")
        # Render should fail (ComfyUI unreachable)
        # The async render wraps _render_sync in to_thread
        import asyncio
        with pytest.raises((ComfyUIError, Exception)):
            asyncio.run(provider.render(intent))

    def test_render_success_path_mocked(self):
        """When ComfyUI is mocked to return success, the provider completes the flow."""
        from movie_os.providers import registry
        provider = registry.make("image", "flux_comfyui", {
            "comfyui_url": "http://localhost:8188",
        }, 0.0)
        # Mock the ComfyUI client
        mock_client = MagicMock()
        mock_client.submit.return_value = "test-prompt-id"
        mock_client.wait_for_result.return_value = {
            "status": {"completed": True},
            "outputs": {
                "9": {"images": [{"filename": "out.png", "subfolder": "", "type": "output"}]}
            },
        }
        mock_client.save_image.return_value = Path("/tmp/out.png")
        provider._client = mock_client

        from movie_os.capabilities.base import ImageIntent
        intent = ImageIntent(
            prompt="a man sitting",
            width=512, height=512,
            metadata={"output_dir": "/tmp", "pipeline_id": "test", "scene_number": 1},
        )
        import asyncio
        asset = asyncio.run(provider.render(intent))
        assert asset is not None
        assert asset.type.value == "image"
        assert mock_client.submit.called
        assert mock_client.save_image.called

    def test_can_handle(self):
        from movie_os.providers import registry
        from movie_os.capabilities.base import ImageIntent
        provider = registry.make("image", "flux_comfyui", {}, 0.0)
        assert provider.can_handle(ImageIntent(prompt="x"))
        assert not provider.can_handle(ImageIntent(prompt=""))


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

class TestFluxIntegration:
    """FLUX integrates with the registry and config."""

    def test_flux_registered_as_builtin(self):
        from movie_os.providers import registry
        assert registry.has("image", "flux_comfyui")

    def test_flux_via_config(self):
        """Setting flux_comfyui as default in config wires it up."""
        from movie_os.config import MovieOSConfig
        from movie_os.capabilities import CapabilityRegistry
        from movie_os.providers import default_provider_factory, FluxComfyUIProvider

        config = MovieOSConfig.model_validate({
            "providers": {
                "image": {
                    "default": "flux_comfyui",
                    "options": {
                        "flux_comfyui": {
                            "label": "FLUX",
                            "enabled": True,
                            "settings": {
                                "comfyui_url": "http://localhost:8188",
                                "model": "flux1-dev-fp8.safetensors",
                                "quality": "production",
                            },
                        },
                    },
                }
            }
        })
        registry = CapabilityRegistry.from_config(
            config, provider_factory=default_provider_factory
        )
        image_cap = registry.get("image")
        assert isinstance(image_cap._provider, FluxComfyUIProvider)

    def test_quality_profiles_complete(self):
        """The quality profile table has all 3 modes."""
        from movie_os.providers.image.flux_comfyui import _QUALITY_PROFILES
        assert "draft" in _QUALITY_PROFILES
        assert "production" in _QUALITY_PROFILES
        assert "high_quality" in _QUALITY_PROFILES
        for mode, profile in _QUALITY_PROFILES.items():
            assert "workflow" in profile
            assert "unet" in profile
            assert "steps" in profile
            assert "cfg" in profile
            assert "guidance" in profile


# ---------------------------------------------------------------------------
# Backward compat
# ---------------------------------------------------------------------------

class TestBackwardCompat:
    """Existing code still works."""

    def test_sdxl_still_works(self):
        from movie_os.providers import SDXLLocalProvider, registry
        provider = registry.make("image", "sdxl_local", {}, 0.0)
        assert isinstance(provider, SDXLLocalProvider)

    def test_other_capabilities_still_work(self):
        from movie_os.providers import (
            EdgeTTSProvider, ProceduralMusicProvider,
            ProceduralSFXProvider, LMStudioStoryProvider, registry,
        )
        assert isinstance(registry.make("voice", "edge_tts", {}, 0.0), EdgeTTSProvider)
        assert isinstance(registry.make("music", "procedural", {}, 0.0), ProceduralMusicProvider)
        assert isinstance(registry.make("sfx", "procedural", {}, 0.0), ProceduralSFXProvider)
        assert isinstance(registry.make("story", "lmstudio", {}, 0.0), LMStudioStoryProvider)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
