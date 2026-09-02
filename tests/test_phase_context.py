from __future__ import annotations

import pytest

from movie_os.genesis2.phase_context import (
    DependencyManifest,
    EstablishedFactRegister,
    PhaseContextCompiler,
    RunContext,
)


@pytest.fixture()
def compiler() -> PhaseContextCompiler:
    return PhaseContextCompiler(max_context_chars=10_000)


def _run_context(episode_id: str = "EP-0001", run_id: str = "RUN-CTX-1") -> RunContext:
    return RunContext(
        production_id=episode_id,
        run_id=run_id,
        policy_id="POLICY-CTX-1",
        policy_hash="policy-hash-ctx",
        requirement_manifest_hash="req-hash-ctx",
        mode="RUNTIME",
        source_run_id=run_id,
        source_episode_id=episode_id,
    )


def test_context_compiler_preserves_provenance_and_size(compiler: PhaseContextCompiler):
    register = EstablishedFactRegister()
    register.add_fact(
        "job_loss",
        "Mark lost his job",
        source_artifact_id="artifact:req",
        source_content_hash="hash-req",
        source_field="facts.job_loss",
    )
    registry = {
        "artifact:req": {
            "content_hash": "hash-req",
            "provenance": {"source": "episode_contract"},
            "facts": {"job_loss": "Mark lost his job"},
        },
        "artifact:noise": {
            "content_hash": "hash-noise",
            "provenance": {"source": "unrelated"},
            "facts": {"other": "should not be injected"},
        },
    }
    manifest = DependencyManifest(
        phase_name="phase_03",
        required_artifact_ids=["artifact:req"],
        required_fact_keys=["job_loss"],
        required_policy_keys=["tone", "platform"],
    )
    packet = compiler.compile(
        phase_name="phase_03",
        target_unit="phase_03",
        artifact_registry=registry,
        canonical_requirements={"REQ-001": "job loss is established"},
        active_policy={"tone": "restrained", "platform": "youtube", "episode_id": "EP-0001"},
        dependency_manifest=manifest,
        run_context=_run_context(),
        established_fact_register=register,
    )

    assert packet.artifact_references[0].artifact_id == "artifact:req"
    assert packet.artifact_references[0].content_hash == "hash-req"
    assert packet.artifact_references[0].provenance == {"source": "episode_contract"}
    assert packet.artifact_references[0].fields_or_fragments_consumed == ["job_loss"]
    assert packet.context_size_chars > 0
    assert packet.context_size_bytes >= packet.context_size_chars
    assert packet.established_facts == {"job_loss": "Mark lost his job"}
    assert packet.packet_id


def test_context_compiler_rejects_mandatory_truncation(compiler: PhaseContextCompiler):
    manifest = DependencyManifest(
        phase_name="phase_04",
        required_artifact_ids=[],
        required_fact_keys=[],
        required_policy_keys=[],
    )
    with pytest.raises(ValueError, match="mandatory canonical requirements"):
        compiler.compile(
            phase_name="phase_04",
            target_unit="phase_04",
            artifact_registry={},
            canonical_requirements={"REQ-001": "x" * 20_000},
            active_policy={"episode_id": "EP-0001"},
            dependency_manifest=manifest,
            run_context=_run_context(),
        )


def test_context_compiler_ignores_unrelated_artifacts(compiler: PhaseContextCompiler):
    registry = {
        "artifact:needed": {
            "content_hash": "hash-needed",
            "provenance": {"source": "required"},
            "character": "Mark",
        },
        "artifact:unrelated": {
            "content_hash": "hash-unrelated",
            "provenance": {"source": "noise"},
            "character": "Noise",
        },
    }
    manifest = DependencyManifest(
        phase_name="phase_05",
        required_artifact_ids=["artifact:needed"],
        required_fact_keys=[],
        required_policy_keys=[],
    )
    packet = compiler.compile(
        phase_name="phase_05",
        target_unit="phase_05",
        artifact_registry=registry,
        canonical_requirements={"REQ-001": "keep the denominator"},
        active_policy={"policy": "active", "episode_id": "EP-0001"},
        dependency_manifest=manifest,
        run_context=_run_context(),
    )

    assert [ref.artifact_id for ref in packet.artifact_references] == ["artifact:needed"]
    assert all(ref.artifact_id != "artifact:unrelated" for ref in packet.artifact_references)
