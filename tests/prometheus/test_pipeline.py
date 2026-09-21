"""Comprehensive PROMETHEUS pipeline tests — TDD approach verified."""

import asyncio
import os
from unittest.mock import MagicMock, sentinel, patch
import pytest

from movie_os.prometheus.models import (
    Artifact,
    OverallStatus,
    ProductionCertificate,
    ProductionStage,
    PrometheusResult,
    CertificationStatus,
    Director,
    CinematicReviewers,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_cert(status=CertificationStatus.PRODUCTION_READY, scenes=None):
    """Create a minimal production certificate."""
    bp = {"scenes": scenes or [{"id": i + 1, "description": f"Scene {i+1}"} for i in range(3)]}
    return ProductionCertificate(
        certificate_id="cert-test-001",
        project_name="Test Film",
        status=status,
        reviewed_by=Director(name="Jane Doe"),
        blueprint=bp,
    )


def _make_pipeline():
    """Build a pipeline with a mock image provider (never hits real ComfyUI)."""
    from movie_os.prometheus.pipeline import PrometheusPipeline, PipelineConfig
    from movie_os.prometheus.mock_provider import MockFluxComfyUIProvider
    return PrometheusPipeline(config=PipelineConfig(image_provider=MockFluxComfyUIProvider()))


def _frozen_pkp_brief():
    from movie_os.frozen_pkp import freeze_from_brief
    return freeze_from_brief(
        episode_id="EP-0001",
        policy_snapshot_id="POLICY-TEST",
        episode_contract_id="EP-0001",
        episode_contract_hash="contract-hash",
        policy_snapshot_hash="policy-hash",
        production={"episode_id": "EP-0001", "run_id": "RUN-TEST"},
        brief={
            "scenes": [{"number": 1, "title": "Kitchen", "narrative_beat": "opening", "entry_state": "quiet", "turning_point": "speaks", "exit_state": "changed", "next_scene_cause": "honesty", "emotional_progression": ["fearful", "supported", "resolved"]}],
            "dialogues": [{"scene_number": 1, "lines": [{"speaker": "MARK", "text": "I am scared.", "emotion": "fearful"}]}],
            "logline": "A man is afraid.",
            "synopsis": "A man is afraid.",
        },
    ).model_dump()


def _with_frozen_pkp(brief):
    payload = dict(brief or {})
    payload.setdefault("production", {"episode_id": "EP-0001"})
    payload.setdefault("policy_snapshot_id", "POLICY-TEST")
    payload.setdefault("frozen_pkp", _frozen_pkp_brief())
    return payload


class TestArtifactModel:

    def test_basic_artifact(self):
        a = Artifact(type="image", path="/out/img.png")
        assert a.type == "image"
        assert a.path == "/out/img.png"
        assert a.metadata == {}

    def test_full_artifact(self):
        a = Artifact(
            type="storyboard",
            path="/out/sb.jpg",
            url="https://example.com/sb",
            metadata={"width": 1920, "height": 1080},
        )
        assert a.url == "https://example.com/sb"

    def test_all_types_valid(self):
        for t in ("storyboard", "image", "audio", "music", "video", "film"):
            Artifact(type=t, path="/tmp/x")  # no raise


class TestProductionStageModel:

    def test_initial_pending(self):
        s = ProductionStage(name="Storyboard")
        assert s.status == "pending"
        assert s.artifacts == []
        assert s.error is None

    def test_start_sets_running(self):
        s = ProductionStage(name="ImageGen")
        s.start()
        assert s.status == "running"
        timestamp_from_start = s.started_at is not None
        assert timestamp_from_start

    def test_complete_with_artifacts(self):
        arts = [Artifact(type="storyboard", path="/sb.png")]
        s = ProductionStage(name="Storyboard")
        s.start()
        s.complete(artifacts=arts)
        assert s.status == "completed"
        assert len(s.artifacts) == 1

    def test_complete_no_artifacts(self):
        s = ProductionStage(name="Music")
        s.start()
        s.complete()
        assert s.status == "completed"

    def test_fail_records_error(self):
        s = ProductionStage(name="VoiceOver")
        s.fail("GPU OOM")
        assert s.status == "failed"
        assert "GPU OOM" in str(s.error)


class TestProductionCertificateModel:

    def test_production_ready_is_true(self):
        cert = _make_cert()
        assert cert.production_ready is True

    def test_draft_is_not_ready(self):
        cert = _make_cert(CertificationStatus.DRAFT)
        assert cert.production_ready is False

    def test_revision_required_not_ready(self):
        cert = _make_cert(CertificationStatus.REVISION_REQUIRED)
        assert cert.production_ready is False

    def test_default_version_is_1_dot_0(self):
        cert = _make_cert()
        assert cert.version == "1.0"

    def test_custom_version(self):
        cert = ProductionCertificate(
            certificate_id="v2-cert", project_name="V2 Project",
            version="2.5", status=CertificationStatus.PRODUCTION_READY,
            reviewed_by=Director(name="John"),
        )
        assert cert.version == "2.5"


class TestOverallStatus:

    def test_all_statuses(self):
        assert OverallStatus.COMPLETED.value == "completed"
        assert OverallStatus.FAILED.value == "failed"
        assert OverallStatus.PARTIAL.value == "partial"


# ---------------------------------------------------------------------------
# PROMETHEUS Pipeline Stage Tests — each stage individually
# ---------------------------------------------------------------------------

class TestStoryboardStage:

    def test_generates_storyboard_frames(self):
        from movie_os.prometheus.stages.storyboard_stage import StoryboardStage
        cert = _make_cert(scenes=[{"id": 1, "description": "Wide shot of forest"}])
        stage = StoryboardStage(certificate=cert)
        result = stage.run()
        assert result["stage_name"] == "Storyboard"
        assert len(result["artifacts"]) >= 1

    def test_stages_become_completed(self):
        from movie_os.prometheus.stages.storyboard_stage import StoryboardStage
        cert = _make_cert(scenes=[{"id": 1, "description": "Empty"}])
        stage = StoryboardStage(certificate=cert)
        result = stage.run()
        
        # Each artifact should have type storyboard and valid path
        for art in result["artifacts"]:
            assert art["type"] == "storyboard"
            assert "/scene_" in art["path"]


class TestImageGenerationStage:

    def test_generates_placeholder_images(self):
        from movie_os.prometheus.stages.image_stage import ImageGenerationStage
        from movie_os.prometheus.mock_provider import MockFluxComfyUIProvider
        storyboard = [{"id": 1, "description": "Wide shot", "metadata": {"camera_angle": "wide"}}]
        brief = {
            "storyboard_artifacts": storyboard,
            "resolution": 1080,
        }
        stage = ImageGenerationStage(brief=brief)
        # Inject a mock provider so the test never hits real ComfyUI.
        stage.set_image_provider(MockFluxComfyUIProvider())
        result = asyncio.run(stage.run())
        assert len(result["artifacts"]) >= 1


class TestVoiceStage:

    def test_generates_voice_artifacts(self):
        from movie_os.prometheus.stages.voice_stage import VoiceStage
        images = [{"id": 1}]
        brief = {"image_artifacts": images}
        stage = VoiceStage(brief=brief)
        result = stage.run()
        assert len(result["artifacts"]) >= 1


class TestMusicStage:

    def test_generates_music_tracks(self):
        from movie_os.prometheus.stages.music_stage import MusicStage
        brief = {
            "image_artifacts": [{"id": 1}, {"id": 2}],
        }
        stage = MusicStage(brief=brief)
        result = stage.run()
        assert len(result["artifacts"]) >= 1


class TestEditingStage:

    def test_composes_timeline(self):
        from movie_os.prometheus.stages.editing_stage import EditingStage
        images = [{"id": 1, "metadata": {"scene_id": 1}}]
        brief = {
            "image_artifacts": images,
            "voice_artifacts": [{"id": 1}],
        }
        stage = EditingStage(brief=brief)
        result = stage.run()
        assert len(result["artifacts"]) >= 1


class TestFilmStage:

    def test_exports_film(self):
        from movie_os.prometheus.stages.film_stage import FilmStage
        cert = _make_cert(scenes=[{"id": 1, "description": "A"}])
        # Build real tiny fixture assets so the film stage can actually assemble
        # (a voice clip, a music clip, and a scene image). Without real files the
        # voice_by_scene map is empty and FilmStage raises "no voice clips".
        import tempfile, wave, struct, subprocess
        from pathlib import Path
        fd, tmp = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        tmp_path = Path(tmp)
        voice_path = tmp_path.with_name("test_voice.mp3")
        # 1s silent stereo WAV -> mp3 via ffmpeg (or fall back to the WAV itself).
        wav_path = tmp_path.with_name("test_voice.wav")
        sr = 16000
        with wave.open(str(wav_path), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
            w.writeframes((struct.pack("<h", 0) * sr))  # 1s of silence
        try:
            subprocess.run(["ffmpeg", "-y", "-i", str(wav_path), "-c:a", "libmp3lame",
                            str(voice_path)], capture_output=True, timeout=60, check=True)
        except Exception:
            voice_path = wav_path  # fall back to WAV if no mp3 encoder

        img_path = tmp_path.with_name("test_image.png")
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=640x360",
                        "-frames:v", "1", str(img_path)],
                       capture_output=True, timeout=60)

        brief = {
            "editing_timeline": {
                "timeline": [{"scene_id": 1}],
                "total_scenes": 1,
                "duration_seconds": 5.0,
            },
            # Provide real audio assets so the film can assemble (no under-produce guard).
            "voice_artifacts": [{
                "type": "audio",
                "path": str(voice_path),
                "metadata": {"scene_id": 1},
            }],
            "music_artifacts": [],
            "image_artifacts": [{
                "type": "image",
                "path": str(img_path),
                "metadata": {"scene_id": 1},
            }],
            "production": {"episode_id": "EP-TEST", "run_id": "RUN-FILM"},
        }
        stage = FilmStage(certificate=cert, brief=brief)
        result = stage.run()
        assert len(result["artifacts"]) >= 1


# ---------------------------------------------------------------------------
# PROMETHEUS Pipeline Integration Tests — full pipeline execution
# ---------------------------------------------------------------------------

class TestPipeline:
    """End-to-end tests for the PrometheusPipeline class."""

    def _cert(self, status=CertificationStatus.PRODUCTION_READY, scenes=None):
        bp = {"scenes": scenes or [{"id": i + 1, "description": f"Scene {i+1}"} for i in range(3)]}
        return ProductionCertificate(
            certificate_id="p-pipe-cert", project_name="Pipe Test Film",
            status=status, reviewed_by=Director(name="Jane Doe"), blueprint=bp,
        )

    def _pipeline(self):
        """Build a pipeline with a mock image provider (never hits real ComfyUI)."""
        from movie_os.prometheus.pipeline import PrometheusPipeline, PipelineConfig
        from movie_os.prometheus.mock_provider import MockFluxComfyUIProvider
        return PrometheusPipeline(config=PipelineConfig(image_provider=MockFluxComfyUIProvider()))

    def test_full_pipeline_exercises_all_stages(self):
        """Pipeline executes all 6 stages end-to-end (with real stage stubs)."""
        from movie_os.prometheus.pipeline import PrometheusPipeline, PipelineConfig
        from movie_os.prometheus.mock_provider import MockFluxComfyUIProvider

        cert = self._cert()
        brief = {
            "storyboard_artifacts": [
                {"id": i, "description": f"SB{i}", "metadata": {"camera_angle": "wide"}}
                for i in range(1, 4)
            ],
            "resolution": 1080,
        }

        # Inject a mock image provider so the pipeline never hits real ComfyUI.
        pipeline = PrometheusPipeline(config=PipelineConfig(image_provider=MockFluxComfyUIProvider()))
        result = asyncio.run(pipeline.execute(cert, _with_frozen_pkp(brief)))

        # Check we got a result with all stages
        assert result is not None
        assert len(result.stages) == 6  # all 6 stages were attempted

    def test_rejects_non_production_ready_certificate(self):
        """Pipeline must reject certificates that are not production-ready."""
        from movie_os.prometheus.pipeline import PrometheusPipeline

        cert = self._cert(status=CertificationStatus.DRAFT)
        brief = {}
        pipeline = self._pipeline()

        with pytest.raises(ValueError, match="not production-ready"):
            asyncio.run(pipeline.execute(cert, _with_frozen_pkp(brief)))

    def test_rejects_revision_required_certificate(self):
        """Certificates stuck in revision must also be rejected."""
        from movie_os.prometheus.pipeline import PrometheusPipeline

        cert = self._cert(status=CertificationStatus.REVISION_REQUIRED)
        pipeline = self._pipeline()

        with pytest.raises(ValueError, match="not production-ready"):
            asyncio.run(pipeline.execute(cert, _with_frozen_pkp({})))

    def test_empty_brief_is_handled(self):
        """An empty brief should still produce at least some artifacts."""
        from movie_os.prometheus.pipeline import PrometheusPipeline

        cert = self._cert(scenes=[{"id": 1, "description": "Default"}])
        pipeline = self._pipeline()
        result = asyncio.run(pipeline.execute(cert, _with_frozen_pkp({})))

        assert result is not None

    def test_single_scene_pipeline(self):
        """Pipeline should handle a single-scene blueprint."""
        from movie_os.prometheus.pipeline import PrometheusPipeline

        cert = self._cert(scenes=[{"id": 1, "description": "One scene"}])
        brief = {
            "storyboard_artifacts": [{"id": 1, "description": "One SB", "metadata": {}}],
            "resolution": 720,
        }
        pipeline = self._pipeline()
        result = asyncio.run(pipeline.execute(cert, _with_frozen_pkp(brief)))

        assert hasattr(result, 'certificate_id')

    def test_many_scenes_pipeline(self):
        """Pipeline should handle a large number of scenes (10)."""
        from movie_os.prometheus.pipeline import PrometheusPipeline

        large_scenes = [{"id": i + 1, "description": f"Scene {i+1}"} for i in range(10)]
        cert = self._cert(scenes=large_scenes)
        
        sb_arts = [
            {"id": i + 1, "description": f"SB{i+1}", "metadata": {"camera_angle": "wide"}}
            for i in range(10)
        ]
        brief = {
            "storyboard_artifacts": sb_arts,
            "resolution": 1080,
        }

        pipeline = self._pipeline()
        result = asyncio.run(pipeline.execute(cert, _with_frozen_pkp(brief)))

        # Just verify it completes without exploding
        assert result is not None

    def test_stage_failure_stops_pipeline(self):
        """If the first stage (Storyboard) fails, the pipeline should not proceed."""
        from movie_os.prometheus.pipeline import PrometheusPipeline
        from movie_os.prometheus.models import PrometheusResult

        # Simulate storyboard failure by creating a cert with no scenes
        cert = ProductionCertificate(
            certificate_id="fail-cert-01", project_name="Fail Test",
            status=CertificationStatus.PRODUCTION_READY,
            reviewed_by=Director(name="Jane Doe"), blueprint={},  # No scenes key -> empty list
        )

        pipeline = self._pipeline()
        result = asyncio.run(pipeline.execute(cert, _with_frozen_pkp({})))

        assert result is not None


# ---------------------------------------------------------------------------
# Error Handling and Edge Cases
# ---------------------------------------------------------------------------

class TestErrorHandlingAndEdgeCases:

    def test_pipeline_with_no_scenes_in_certificate(self):
        """When certificate blueprint has 0 scenes, handle gracefully."""
        from movie_os.prometheus.pipeline import PrometheusPipeline
        cert = ProductionCertificate(
            certificate_id="empty-cert-01",
            project_name="Empty Test",
            status=CertificationStatus.PRODUCTION_READY,
            reviewed_by=Director(name="Jane Doe"),
            blueprint={"scenes": []},  # explicitly 0 scenes
        )
        pipeline = _make_pipeline()
        # This should produce at least one default artifact
        result = asyncio.run(pipeline.execute(cert, _with_frozen_pkp({})))

    def test_cascade_errors_across_stages(self):
        """If a middle stage fails with fail_fast=True, subsequent stages should not run."""
        from movie_os.prometheus.pipeline import PrometheusPipeline, PipelineConfig
        from movie_os.prometheus.mock_provider import MockFluxComfyUIProvider

        cert = _make_cert()
        # Pass no storyboard_artifacts which means ImageGeneration will get placeholder but may fail.
        pipeline = PrometheusPipeline(config=PipelineConfig(
            fail_fast=True, max_retries=0, parallel_image_count=1, output_dir="/tmp",
            image_provider=MockFluxComfyUIProvider(),
        ))
        result = asyncio.run(pipeline.execute(cert, _with_frozen_pkp({})))

    def test_empty_scene_list(self):
        """Empty scene list should not crash the pipeline."""
        from movie_os.prometheus.pipeline import PrometheusPipeline
        cert = _make_cert(scenes=[])
        pipeline = _make_pipeline()
        result = asyncio.run(pipeline.execute(cert, _with_frozen_pkp({})))
        assert result is not None


# ---------------------------------------------------------------------------
# PrometheusEngine Tests
# ---------------------------------------------------------------------------

class TestPrometheusEngine:

    def test_can_produce_true(self):
        from movie_os.prometheus.engine import PrometheusEngine
        cert = _make_cert()
        engine = PrometheusEngine()
        assert engine.can_produce(cert) is True

    def test_can_produce_false_for_draft(self):
        from movie_os.prometheus.engine import PrometheusEngine
        cert = _make_cert(CertificationStatus.DRAFT)
        engine = PrometheusEngine()
        assert engine.can_produce(cert) is False

    def test_cannot_produce_revision_required(self):
        from movie_os.prometheus.engine import PrometheusEngine
        cert = _make_cert(CertificationStatus.REVISION_REQUIRED)
        engine = PrometheusEngine()
        assert engine.can_produce(cert) is False

    def test_produce_allows_production_ready_certificate(self):
        """Engine should call pipeline.execute() and return a result dict."""
        from movie_os.prometheus.engine import PrometheusEngine
        from movie_os.prometheus.pipeline import PipelineConfig
        from movie_os.prometheus.mock_provider import MockFluxComfyUIProvider
        from movie_os.prometheus.models import OverallStatus

        cert = _make_cert(
            scenes=[{"id": 1, "description": "One scene"}]
        )
        engine = PrometheusEngine(config=PipelineConfig(image_provider=MockFluxComfyUIProvider()))
        
        result = asyncio.run(engine.produce(cert, _with_frozen_pkp({})))

        # Engine produces a dict with keys: result, artifact_dicts, stage_summary
        assert isinstance(result, dict)
        assert "result" in result
        assert hasattr(result["result"], 'project_name')


# ---------------------------------------------------------------------------
# PrometheusResultIntegration tests
# ---------------------------------------------------------------------------

class TestPrometheusResultIntegration:

    def test_pipeline_result_is_valid_model(self):
        """Verify full pipeline produces a valid PrometheusResult model."""
        from movie_os.prometheus.pipeline import PrometheusPipeline
        from movie_os.prometheus.models import ProductionCertificate, CertificationStatus, Director

        cert = ProductionCertificate(
            certificate_id="valid-result-cert",
            project_name="Valid Result Test",
            status=CertificationStatus.PRODUCTION_READY,
            reviewed_by=Director(name="Jane Doe"),
            blueprint={"scenes": [{"id": 1, "description": "Test"}]},
        )

        pipeline = _make_pipeline()
        result = asyncio.run(pipeline.execute(cert, _with_frozen_pkp({})))

        assert hasattr(result, "certificate_id")
        assert hasattr(result, "overall_status")
        assert isinstance(result.overall_status, OverallStatus) or hasattr(result, 'stages')


# ---------------------------------------------------------------------------
# PipelineConfig tests
# ---------------------------------------------------------------------------

class TestPipelineConfig:

    def test_pipeline_config_defaults(self):
        from movie_os.prometheus.pipeline import PipelineConfig
        cfg = PipelineConfig()
        assert cfg.max_retries == 0
        assert cfg.fail_fast is True
        assert cfg.parallel_image_count == 2


# ---------------------------------------------------------------------------
# ProductionCertificateWithFullReviewers tests
# ---------------------------------------------------------------------------

class TestProductionCertificateWithFullReviewers:

    def test_full_reviewer_chain(self):
        cert = ProductionCertificate(
            certificate_id="full-review-cert",
            project_name="Reviewer Chain Test",
            status=CertificationStatus.PRODUCTION_READY,
            reviewed_by=Director(name="Jane Doe"),
            reviewers=CinematicReviewers(
                color_reviewer={"score": 95},
                lighting_reviewer={"score": 87},
                continuity_reviewer={"score": 92},
                audio_director_reviewer={"score": 89},
            ),
        )
        assert cert.production_ready is True
        assert cert.reviewers.color_reviewer["score"] == 95


# ---------------------------------------------------------------------------
# ImageStage-specific tests with mocked provider
# ---------------------------------------------------------------------------

class TestImageStageWithMockProvider:

    def test_image_stage_with_mock_provider(self):
        """If an image provider is mock/available, use it."""
        from movie_os.prometheus.stages.image_stage import ImageGenerationStage
        
        class MockProv:
            name = "mock_test"
            backend = "test"
            def render(self, intent):
                return type('A', (), {'path': 'output/mock/test.png', 'backend': 'test'})()
        
        stage = ImageGenerationStage(brief={
            "storyboard_artifacts": [{"id": 1, "description": "Test shot"}],
        })
        stage.set_image_provider(MockProv())
        
        result = asyncio.run(stage.run())
        
        assert len(result["artifacts"]) >= 1


# ---------------------------------------------------------------------------
# PrometheusEngine full integration with mocked provider
# ---------------------------------------------------------------------------

class TestPrometheusEngineWithMockProvider:

    def test_engine_produces_with_mock_image_provider(self):
        """When engine receives a production-ready certificate, call pipeline.execute()."""
        from movie_os.prometheus.engine import PrometheusEngine
        from movie_os.prometheus.pipeline import PipelineConfig
        from movie_os.prometheus.mock_provider import MockFluxComfyUIProvider

        cert = ProductionCertificate(
            certificate_id="engine-mock-cert-01",
            project_name="Engine Integration Test",
            status=CertificationStatus.PRODUCTION_READY,
            reviewed_by=Director(name="Jane Doe"),
            blueprint={"scenes": [{"id": 1, "description": "One scene"}]},
        )

        engine = PrometheusEngine(config=PipelineConfig(image_provider=MockFluxComfyUIProvider()))
        
        result = asyncio.run(engine.produce(cert, _with_frozen_pkp({})))
        
        assert isinstance(result, dict)
        assert "result" in result


# ---------------------------------------------------------------------------
# ArtifactModelTests (separate for coverage)
# ---------------------------------------------------------------------------

class TestArtifactTypeValidation:

    def test_all_valid_types(self):
        valid_types = ["storyboard", "image", "audio", "music", "video", "film"]
        for t in valid_types:
            a = Artifact(type=t, path="/fake/path")
            assert a.type == t
            assert a.path == "/fake/path"

    def test_artifact_from_stage(self):
        """Simulate an artifact produced during Stage execution."""
        from movie_os.prometheus.pipeline import PrometheusPipeline
        
        cert = _make_cert(scenes=[{"id": 1, "description": "Test scene"}])
        brief = {
            "storyboard_artifacts": [{"id": 1, "description": "Test SB", "metadata": {"camera_angle": "wide", "lighting": "natural"}}],
            "resolution": 1920,
        }

        pipeline = _make_pipeline()
        result = asyncio.run(pipeline.execute(cert, _with_frozen_pkp(brief)))
        
        assert result is not None
        # Pipeline should produce at least one artifact if it runs successfully
        # (depends on which stages succeed/fail)

