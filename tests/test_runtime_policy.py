from __future__ import annotations

import json
from pathlib import Path

import pytest

from movie_os.runtime_policy import (
    EpisodeContract,
    canonical_episode_contract,
    canonical_ontology_selection,
    load_and_resolve_canonical_policy,
    persist_production_policy,
    resolve_policy,
    validate_episode_contract,
)


def test_valid_episode_contract_loads():
    contract = validate_episode_contract(canonical_episode_contract())
    assert contract.episode_id == "EP-0001"
    assert contract.working_title == "The Email Mark Wouldn't Open"


def test_missing_required_contract_field_fails():
    data = canonical_episode_contract()
    data.pop("episode_id")
    with pytest.raises(Exception):
        validate_episode_contract(data)


def test_valid_rpco_resolution_by_ids():
    contract = validate_episode_contract(canonical_episode_contract())
    snapshot = resolve_policy(contract, canonical_ontology_selection())
    assert snapshot.resolved_rules["problem_family_id"] == "RP-01"
    assert snapshot.resolved_rules["sub_series_id"] == "RP-01-S01"
    bindings = snapshot.resolved_rules["canonical_character_bindings"]
    assert [b["character_id"] for b in bindings] == ["MARK", "SARAH"]
    assert bindings[0]["visual_identity_registry_ref"].endswith("03_MARK_SARAH_VISUAL_IDENTITY_REGISTRY.yaml")
    assert snapshot.resolved_rules["canonical_continuity_binding"]["continuity_registry_ref"] == "MSCR-001"
    assert snapshot.resolved_rules["canonical_continuity_binding"]["continuity_path"].endswith("04_MARK_SARAH_CONTINUITY_REGISTRY.yaml")


def test_valid_rpco_resolution_by_names():
    contract = validate_episode_contract(canonical_episode_contract())
    snapshot = resolve_policy(
        contract,
        {"niche": "Psychology", "domain": "Relationship & Emotional Psychology", "problem_family": "Emotional Withdrawal", "sub_series": "Fear-Based Withdrawal"},
    )
    assert snapshot.resolved_rules["problem_family_id"] == "RP-01"
    assert snapshot.resolved_rules["sub_series_id"] == "RP-01-S01"


def test_invalid_rpco_family_rejected():
    contract = validate_episode_contract(canonical_episode_contract())
    with pytest.raises(ValueError, match="Invalid RPCO problem family"):
        resolve_policy(contract, {"niche": "Psychology", "domain": "Relationship & Emotional Psychology", "problem_family": "Nope", "sub_series": "Fear-Based Withdrawal"})


def test_invalid_rpco_sub_series_rejected():
    contract = validate_episode_contract(canonical_episode_contract())
    with pytest.raises(ValueError, match="Invalid RPCO sub-series"):
        resolve_policy(contract, {"niche": "Psychology", "domain": "Relationship & Emotional Psychology", "problem_family": "Emotional Withdrawal", "sub_series": "Nope"})


def test_snapshot_is_deterministic_and_hashable():
    contract = validate_episode_contract(canonical_episode_contract())
    s1 = resolve_policy(contract, canonical_ontology_selection(), source_versions={"a": "1"})
    s2 = resolve_policy(contract, canonical_ontology_selection(), source_versions={"a": "1"})
    assert s1.snapshot_hash == s2.snapshot_hash


def test_changed_policy_source_changes_hash():
    contract = validate_episode_contract(canonical_episode_contract())
    s1 = resolve_policy(contract, canonical_ontology_selection(), source_versions={"a": "1"})
    s2 = resolve_policy(contract, canonical_ontology_selection(), source_versions={"a": "2"})
    assert s1.snapshot_hash != s2.snapshot_hash


def test_policy_persistence(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    contract, snapshot, paths = load_and_resolve_canonical_policy()
    assert paths["contract_path"].exists()
    assert paths["policy_path"].exists()
    assert paths["contract_path"].read_text()
    assert paths["policy_path"].read_text()


@pytest.mark.asyncio
async def test_genesis_blocked_without_policy(monkeypatch):
    import run_space_between_us as runner

    called = {"genesis": False}

    async def fake_run_async(*args, **kwargs):
        called["genesis"] = True
        raise AssertionError("Genesis should not run")

    monkeypatch.setattr(runner, "load_and_resolve_canonical_policy", lambda: (_ for _ in ()).throw(ValueError("policy missing")))
    monkeypatch.setattr("movie_os.genesis2.Genesis2Engine.run_async", fake_run_async, raising=False)
    with pytest.raises(ValueError, match="policy missing"):
        await runner.main()
    assert called["genesis"] is False


def test_persistence_root_is_productions(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    contract = validate_episode_contract(canonical_episode_contract())
    snapshot = resolve_policy(contract, canonical_ontology_selection())
    paths = persist_production_policy(contract, snapshot)
    assert str(paths["contract_path"]).startswith("productions/EP-0001/contract")
    assert str(paths["policy_path"]).startswith("productions/EP-0001/policy")
