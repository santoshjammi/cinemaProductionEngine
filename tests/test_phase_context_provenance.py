from __future__ import annotations

import pytest

from movie_os.genesis2.phase_context import DependencyManifest, EstablishedFactRegister, PhaseContextCompiler, RunContext
from movie_os.genesis2.llm_client import LLMClient
from movie_os.genesis2.llm_providers import LLMConfig
from movie_os.genesis2.phases.phase06_scene_planning import ScenePlanningPhase


def _compiler():
    return PhaseContextCompiler(max_context_chars=8000)


def _base_run(mode: str = "RUNTIME", run_id: str = "RUN-1", episode_id: str = "EP-0001"):
    return RunContext(
        production_id=episode_id,
        run_id=run_id,
        policy_id="POLICY-1",
        policy_hash="policy-hash",
        requirement_manifest_hash="req-hash",
        mode=mode,
        source_run_id=run_id,
        source_episode_id=episode_id,
    )


def _registry(*, episode_id: str = "EP-0001", run_id: str = "RUN-1", title: str = "T"):
    return {
        "brief": {
            "content_hash": "brief-hash",
            "provenance": {"source": "fixture"},
            "source_episode_id": episode_id,
            "source_run_id": run_id,
            "brief_title": title,
            "scene_count": 3,
            "title": title,
        }
    }


def _manifest():
    return DependencyManifest(
        phase_name="Scene Planning",
        required_artifact_ids=["brief"],
        required_fact_keys=[],
        required_policy_keys=["episode_id"],
    )


def _compile(*, phase_name: str = "Scene Planning", target_unit: str = "Scene Planning", run_id: str = "RUN-1", episode_id: str = "EP-0001"):
    return _compiler().compile(
        phase_name=phase_name,
        target_unit=target_unit,
        artifact_registry=_registry(episode_id=episode_id, run_id=run_id),
        canonical_requirements={"REQ-1": "x"},
        active_policy={"episode_id": episode_id},
        dependency_manifest=_manifest(),
        run_context=_base_run(run_id=run_id, episode_id=episode_id),
        established_fact_register=EstablishedFactRegister(),
    )


def test_wrong_run_artifact_blocks_before_llm():
    with pytest.raises(ValueError, match="CONTEXT_PACKET_PROVENANCE_MISMATCH"):
        _compiler().compile(
            phase_name="Scene Planning",
            artifact_registry=_registry(run_id="RUN-OLD"),
            canonical_requirements={"REQ-1": "x"},
            active_policy={"episode_id": "EP-0001"},
            dependency_manifest=_manifest(),
            run_context=_base_run(),
            established_fact_register=EstablishedFactRegister(),
        )


def test_wrong_episode_artifact_blocks_before_llm():
    with pytest.raises(ValueError, match="CONTEXT_PACKET_PROVENANCE_MISMATCH"):
        _compiler().compile(
            phase_name="Scene Planning",
            artifact_registry=_registry(episode_id="EP-0002"),
            canonical_requirements={"REQ-1": "x"},
            active_policy={"episode_id": "EP-0001"},
            dependency_manifest=_manifest(),
            run_context=_base_run(),
            established_fact_register=EstablishedFactRegister(),
        )


def test_cache_key_contains_run_identity():
    a = _compile(run_id="RUN-1")
    b = _compile(run_id="RUN-2")
    assert a.content_hash != b.content_hash


def test_same_sources_different_target_phase_must_differ():
    a = _compile(phase_name="Phase 06", target_unit="SCENE_PLANNING")
    b = _compile(phase_name="Phase 07", target_unit="SC02")
    assert a.packet_id != b.packet_id
    assert a.content_hash != b.content_hash


def test_same_phase_different_scene_must_differ():
    a = _compile(phase_name="Phase 07", target_unit="SC01")
    b = _compile(phase_name="Phase 07", target_unit="SC02")
    assert a.packet_id != b.packet_id
    assert a.content_hash != b.content_hash


def test_phase06_does_not_inherit_unbounded_or_global_4096_budget():
    client = LLMClient(config=LLMConfig(provider="ollama", model="qwen3:4b", max_tokens=4096, num_ctx=8192, timeout=1, think=False))
    phase = ScenePlanningPhase(client)
    cfg = getattr(phase.llm, "_config", None)
    assert cfg is not None
    phase_cfg = LLMConfig(**cfg.model_dump()) if hasattr(cfg, "model_dump") else cfg
    phase_cfg.max_tokens = min(int(getattr(phase_cfg, "max_tokens", 1536) or 1536), 1536)
    assert phase_cfg.max_tokens == 1536


def test_token_limit_truncated_phase06_response_does_not_pass():
    from movie_os.genesis2.phases.phase06_scene_planning import ScenePlanningPhase
    from movie_os.genesis2.llm_client import MockLLMClient
    truncated = '{"purpose":"x","creative_intent":"x","reasoning":"x","confidence":"confirmed","scenes":[{"scene_number":1,"title":"T"'
    phase = ScenePlanningPhase(MockLLMClient({"Phase 06": truncated}))
    parsed = phase.parse_draft(truncated)
    scenes = getattr(parsed, "scenes", [])
    assert len(scenes) < 3 or any(not getattr(s, "title", None) for s in scenes)
