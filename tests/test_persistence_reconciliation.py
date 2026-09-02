"""P0-03R-SER-01: persistence reconciliation + freeze-gate integration."""
from __future__ import annotations

import json

import pytest

from movie_os.genesis2 import models as M
from movie_os.genesis2.serialization_reconciliation import (
    serialize_reconcile_package,
    load_and_reconcile,
)
from movie_os.genesis2.freeze_gate import evaluate_genesis_freeze_eligibility


def _pkg_with_phase8():
    """A ProductionKnowledgePackage with a rich VisualLanguage phase-8."""
    vl = M.VisualLanguage(color="TEST_COLOR_SENTINEL", lighting="TEST_LIGHTING_SENTINEL",
                          composition="TEST_COMPOSITION_SENTINEL")
    pr8 = M.PhaseResult(phase_number=8, phase_name="Visual Language")
    pr8.knowledge = vl
    pkg = M.ProductionKnowledgePackage(episode_id="EP-0001", run_id="R1")
    pkg.phase_results.append(pr8)
    return pkg


def test_serialization_reconciliation_passes_with_zero_loss():
    pkg = _pkg_with_phase8()
    report = serialize_reconcile_package(pkg)
    assert report["semantic_information_loss"] == 0
    assert report["passed"] is True
    pr = report["phase_results"]["phase_8"]
    assert pr["match"] is True
    assert pr["knowledge_type"] == "VisualLanguage"


def test_load_and_reconcile_identity():
    pkg = _pkg_with_phase8()
    bytes_ = pkg.model_dump_json(indent=2).encode()
    rep = load_and_reconcile(pkg, bytes_)
    assert rep["passed"] is True
    assert rep["semantic_fields_expected"] > 0
    assert rep["missing_fields"] == []


def test_persistence_loss_blocks_freeze():
    pkg = _pkg_with_phase8()
    # Simulate a persistence report with loss detected.
    brief = {
        "scenes": [{"scene_number": 1, "title": "A", "realizes_requirements": ["REQ-001"]}],
        "canonical_requirements": [{"id": "REQ-001", "obligation": "MUST"}],
        "narrative_contract": {"resolution_requirement": "REQUIRED", "narrative_structure": "LINEAR"},
        "ending": "They reconnect.",
        "serialization_reconciliation": {"semantic_information_loss": 1, "passed": False},
    }
    res = evaluate_genesis_freeze_eligibility(pkg, brief)
    assert res.freeze_allowed is False
    assert any(b["code"] == "PERSISTED_KNOWLEDGE_MISMATCH" for b in res.blocking_reasons)


def test_persistence_no_loss_does_not_block():
    pkg = _pkg_with_phase8()
    brief = {
        "scenes": [{"scene_number": 1, "title": "A", "realizes_requirements": ["REQ-001"]}],
        "canonical_requirements": [{"id": "REQ-001", "obligation": "MUST"}],
        "narrative_contract": {"resolution_requirement": "REQUIRED", "narrative_structure": "LINEAR"},
        "ending": "They reconnect.",
        "serialization_reconciliation": {"semantic_information_loss": 0, "passed": True},
    }
    res = evaluate_genesis_freeze_eligibility(pkg, brief)
    assert not any(b["code"] == "PERSISTED_KNOWLEDGE_MISMATCH" for b in res.blocking_reasons)


def test_file_persist_reload_reconcile(tmp_path):
    pkg = _pkg_with_phase8()
    p = tmp_path / "pkg.json"
    p.write_bytes(pkg.model_dump_json(indent=2).encode())
    rep = load_and_reconcile(pkg, p.read_bytes())
    assert rep["passed"] is True
    assert rep["missing_fields"] == []
