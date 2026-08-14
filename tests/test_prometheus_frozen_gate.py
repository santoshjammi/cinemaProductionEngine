from __future__ import annotations

import asyncio

import pytest

from movie_os.frozen_pkp import freeze_from_brief
from movie_os.prometheus.models import CertificationStatus, Director, ProductionCertificate
from movie_os.prometheus.pipeline import PipelineConfig, PrometheusPipeline


def _pkp():
    return freeze_from_brief(
        episode_id="EP-0001",
        policy_snapshot_id="POLICY-1",
        episode_contract_id="EP-0001",
        episode_contract_hash="c1",
        policy_snapshot_hash="p1",
        production={"episode_id": "EP-0001", "run_id": "RUN-1"},
        brief={
            "scenes": [{"number": 1, "title": "Kitchen", "narrative_beat": "opening", "entry_state": "quiet", "turning_point": "Mark speaks", "exit_state": "Sarah listens", "next_scene_cause": "honesty", "emotional_progression": ["fearful", "supported", "resolved"]}],
            "dialogues": [{"scene_number": 1, "lines": [{"speaker": "MARK", "text": "I am scared.", "emotion": "fearful"}]}],
            "logline": "A man is afraid.",
            "synopsis": "A man is afraid.",
        },
    )


def _cert():
    return ProductionCertificate(
        certificate_id="cert-1",
        project_name="Test",
        status=CertificationStatus.PRODUCTION_READY,
        reviewed_by=Director(name="Dir"),
        blueprint={"scenes": [{"id": 1}]},
    )


def test_unfrozen_pkp_blocked():
    pipeline = PrometheusPipeline(PipelineConfig(image_provider=None))
    pkp = _pkp().model_copy(update={"status": "DRAFT"})
    with pytest.raises(ValueError, match="frozen PKP"):
        asyncio.run(pipeline.execute(_cert(), {"frozen_pkp": pkp.model_dump(), "scenes": [], "dialogues": [], "production": {"episode_id": "EP-0001"}, "policy_snapshot_id": "POLICY-1"}))


def test_tampered_pkp_blocked():
    pipeline = PrometheusPipeline(PipelineConfig(image_provider=None))
    pkp = _pkp().model_copy(update={"content_hash": "tampered"})
    with pytest.raises(ValueError, match="content hash mismatch"):
        asyncio.run(pipeline.execute(_cert(), {"frozen_pkp": pkp.model_dump(), "scenes": [], "dialogues": [], "production": {"episode_id": "EP-0001"}, "policy_snapshot_id": "POLICY-1"}))


def test_wrong_episode_blocked():
    pipeline = PrometheusPipeline(PipelineConfig(image_provider=None))
    pkp = _pkp().model_copy(update={"episode_id": "EP-9999"})
    with pytest.raises(ValueError, match="episode"):
        asyncio.run(pipeline.execute(_cert(), {"frozen_pkp": pkp.model_dump(), "scenes": [], "dialogues": [], "production": {"episode_id": "EP-0001"}, "policy_snapshot_id": "POLICY-1"}))


def test_wrong_policy_snapshot_blocked():
    pipeline = PrometheusPipeline(PipelineConfig(image_provider=None))
    pkp = _pkp().model_copy(update={"policy_snapshot_id": "POLICY-X"})
    with pytest.raises(ValueError, match="policy_snapshot_id"):
        asyncio.run(pipeline.execute(_cert(), {"frozen_pkp": pkp.model_dump(), "scenes": [], "dialogues": [], "production": {"episode_id": "EP-0001"}, "policy_snapshot_id": "POLICY-1"}))


def test_valid_frozen_pkp_accepted(monkeypatch):
    pipeline = PrometheusPipeline(PipelineConfig(image_provider=None))
    pkp = _pkp()
    pipeline._create_stages = lambda certificate, brief: []  # type: ignore[method-assign]
    result = asyncio.run(pipeline.execute(_cert(), {"frozen_pkp": pkp.model_dump(), "scenes": [], "dialogues": [], "production": {"episode_id": "EP-0001"}, "policy_snapshot_id": "POLICY-1"}))
    assert result.overall_status.value == "completed"
