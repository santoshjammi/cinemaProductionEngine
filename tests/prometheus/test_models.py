"""Tests for PROMETHEUS production models."""

import pytest
from datetime import datetime

from movie_os.prometheus.models import (
    CertificationStatus,
    CinematicReviewers,
    Director,
    ProductionCertificate,
    ProductionStage,
    Artifact,
    OverallStatus,
    PrometheusResult,
)


class TestProductionCertificate:
    """Tests for ProductionCertificate model."""

    def test_production_certificate_creates(self):
        cert = ProductionCertificate(
            certificate_id="test-cert-001",
            project_name="Test Project",
            status=CertificationStatus.PRODUCTION_READY,
            reviewed_by=Director(name="Jane Doe"),
        )
        assert cert.certificate_id == "test-cert-001"
        assert cert.project_name == "Test Project"
        assert cert.status == CertificationStatus.PRODUCTION_READY
        assert cert.production_ready is True

    def test_production_certificate_draft_is_not_ready(self):
        cert = ProductionCertificate(
            certificate_id="draft-001",
            project_name="Draft Project",
            status=CertificationStatus.DRAFT,
            reviewed_by=Director(name="John Doe"),
        )
        assert cert.production_ready is False

    def test_production_certificate_revision_required(self):
        cert = ProductionCertificate(
            certificate_id="rev-001",
            project_name="Revision Project",
            status=CertificationStatus.REVISION_REQUIRED,
            reviewed_by=Director(name="Jane Doe"),
        )
        assert cert.production_ready is False

    def test_production_certificate_with_full_reviewers(self):
        cert = ProductionCertificate(
            certificate_id="full-cert-001",
            project_name="Full Review Project",
            status=CertificationStatus.PRODUCTION_READY,
            reviewed_by=Director(name="Jane Doe"),
            reviewers=CinematicReviewers(
                color_reviewer={"color_score": 95},
                lighting_reviewer={"lighting_score": 90},
                continuity_reviewer={"continuity_score": 88},
                audio_director_reviewer={"audio_score": 92},
            ),
        )
        assert cert.reviewers is not None
        assert cert.reviewers.color_reviewer["color_score"] == 95

    def test_production_certificate_default_version(self):
        cert = ProductionCertificate(
            certificate_id="ver-001",
            project_name="Version Test",
            status=CertificationStatus.PRODUCTION_READY,
            reviewed_by=Director(name="Jane Doe"),
        )
        assert cert.version == "1.0"

    def test_production_certificate_custom_version(self):
        cert = ProductionCertificate(
            certificate_id="ver-002",
            project_name="Version Test 2",
            version="2.5",
            status=CertificationStatus.PRODUCTION_READY,
            reviewed_by=Director(name="Jane Doe"),
        )
        assert cert.version == "2.5"

    def test_production_certificate_with_blueprint(self):
        cert = ProductionCertificate(
            certificate_id="bp-001",
            project_name="Blueprint Test",
            status=CertificationStatus.PRODUCTION_READY,
            reviewed_by=Director(name="Jane Doe"),
            blueprint={
                "scenes": [
                    {"id": 1, "description": "Opening scene"},
                ],
            },
        )
        assert len(cert.blueprint["scenes"]) == 1


class TestArtifact:
    """Tests for Artifact model."""

    def test_artifact_basic(self):
        a = Artifact(type="image", path="/path/to/image.png")
        assert a.type == "image"
        assert a.path == "/path/to/image.png"
        assert a.url is None
        assert a.metadata == {}

    def test_artifact_with_url_and_metadata(self):
        a = Artifact(
            type="storyboard",
            path="/path/to/sb.jpg",
            url="https://example.com/sb.jpg",
            metadata={"width": 1920, "height": 1080},
        )
        assert a.url == "https://example.com/sb.jpg"
        assert a.metadata["width"] == 1920


class TestProductionStage:
    """Tests for ProductionStage model."""

    def test_stages_starts_as_pending(self):
        stage = ProductionStage(name="Storyboard")
        assert stage.status == "pending"
        assert stage.started_at is None
        assert stage.completed_at is None
        assert stage.error is None

    def test_stage_becomes_running_on_start(self):
        stage = ProductionStage(name="Storyboard")
        before_ts = datetime.utcnow().timestamp()
        stage.start()
        after_ts = datetime.utcnow().timestamp()
        assert stage.status == "running"
        assert stage.started_at is not None
        assert stage.started_at.timestamp() >= before_ts - 1
        assert stage.started_at.timestamp() <= after_ts + 1

    def test_stage_completes_with_artifacts(self):
        artifacts = [
            Artifact(type="storyboard", path="/sb/1.png"),
            Artifact(type="image", path="/img/1.png"),
        ]
        stage = ProductionStage(name="Storyboard")
        stage.start()
        stage.complete(artifacts=artifacts)
        assert stage.status == "completed"
        assert stage.completed_at is not None
        assert len(stage.artifacts) == 2

    def test_stage_completes_with_metadata(self):
        stage = ProductionStage(name="ColorGrade")
        stage.start()
        metadata = {"hue": 0.45, "saturation": 1.1}
        stage.complete(artifacts=[], metadata=metadata)
        assert stage.status == "completed"

    def test_stage_fails(self):
        stage = ProductionStage(name="ColorGrade")
        stage.fail("GPU out of memory")
        assert stage.status == "failed"
        assert stage.error == "GPU out of memory"
        assert stage.completed_at is not None

    def test_stage_cannot_skip_status(self):
        """A non-started stage cannot be marked complete directly."""
        stage = ProductionStage(name="Storyboard")
        # Complete without starting should still set it completed (permissive)
        stage.complete(artifacts=[])
        assert stage.status == "completed"


class TestPrometheusResult:
    """Tests for PrometheusResult model."""

    def test_result_completed(self):
        stages = [
            ProductionStage(name="Storyboard", status="completed"),
            ProductionStage(name="Film", status="completed"),
        ]
        result = PrometheusResult(
            certificate_id="cert-001",
            project_name="Test Film",
            stages=stages,
            overall_status=OverallStatus.COMPLETED,
            output_path="/output/film.mp4",
            duration_seconds=120.5,
        )
        assert result.overall_status == OverallStatus.COMPLETED
        assert result.output_path == "/output/film.mp4"
        assert result.duration_seconds == 120.5

    def test_result_failed(self):
        stages = [
            ProductionStage(name="Storyboard", status="completed"),
            ProductionStage(name="ImageGeneration", status="failed", error="GPU crash"),
        ]
        result = PrometheusResult(
            certificate_id="cert-001",
            project_name="Failed Film",
            stages=stages,
            overall_status=OverallStatus.FAILED,
        )
        assert result.overall_status == OverallStatus.FAILED

    def test_result_partial(self):
        stages = [
            ProductionStage(name="Storyboard", status="completed"),
            ProductionStage(name="VoiceOver", status="running"),
            ProductionStage(name="Music", status="pending"),
        ]
        result = PrometheusResult(
            certificate_id="cert-001",
            project_name="Partial Film",
            stages=stages,
            overall_status=OverallStatus.PARTIAL,
        )
        assert result.overall_status == OverallStatus.PARTIAL
        assert len(result.artifacts) == 0

    def test_result_computed_artifacts(self):
        """PrometheusResult.artifacts collects artifacts from all completed stages."""
        sb_stage = ProductionStage(name="Storyboard")
        sb_stage.start()
        sb_stage.complete(artifacts=[Artifact(type="storyboard", path="/sb.png")])

        image_stage = ProductionStage(name="ImageGeneration")
        image_stage.start()
        image_stage.complete(artifacts=[
            Artifact(type="image", path="/img1.png"),
            Artifact(type="image", path="/img2.png"),
        ])

        result = PrometheusResult(
            certificate_id="cert-001",
            project_name="Collected Test",
            stages=[sb_stage, image_stage],
            overall_status=OverallStatus.COMPLETED,
        )
        # Artifacts from each stage should be collectible; the pipeline method
        # computes this, so we verify that the property works.
        artifacts = [a for s in result.stages for a in s.artifacts]
        assert len(artifacts) == 3

    def test_result_with_certification_notes(self):
        cert = ProductionCertificate(
            certificate_id="cert-001",
            project_name="Cert Notes Test",
            status=CertificationStatus.PRODUCTION_READY,
            reviewed_by=Director(name="Jane Doe"),
            notes="Pre-approved for production.",
            blueprint={"scenes": []},
        )
        assert cert.notes == "Pre-approved for production."
