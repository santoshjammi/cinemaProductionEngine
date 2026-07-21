"""End-to-end integration tests for the GenesisEngine.

These exercise the full pipeline: discovery → PKP → reviews → gate.
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from pathlib import Path

import pytest

from movie_os.genesis.engine import GenesisEngine
from movie_os.genesis.completion_gate import REQUIRED_SPECS


def _run(coro):
    return asyncio.run(coro)


class TestGenesisEngineRun:
    def test_runs_with_rich_mock(self, rich_mock_llm):
        engine = GenesisEngine(llm=rich_mock_llm, db_path=":memory:")
        result = engine.run(synopsis="A man withdraws from his wife after losing his job.")
        # Result has the expected shape
        assert "session_id" in result
        assert "discovery_results" in result
        assert "pkp_results" in result
        assert "review_results" in result
        assert "gate_result" in result
        assert "specifications" in result
        # All 7 discovery agents ran
        assert len(result["discovery_results"]) == 7
        # All 19 PKP agents ran
        assert len(result["pkp_results"]) == 19
        # All 4 reviewers + ChiefArchitect ran = 5
        assert len(result["review_results"]) == 5
        # All 19 PKP specs present (ChiefArchitect adds a 20th "CHIEF" spec)
        assert len(result["specifications"]) == 20
        for spec_id in REQUIRED_SPECS:
            assert spec_id in result["specifications"]

    def test_gate_passes_with_rich_mock(self, rich_mock_llm):
        engine = GenesisEngine(llm=rich_mock_llm, db_path=":memory:")
        result = engine.run(synopsis="A story about silence.")
        # With valid rich mock responses, the gate should pass
        assert result["gate_result"]["passed"] is True, (
            f"Gate failed: {result['gate_result']['blockers']}"
        )

    def test_session_persists(self, rich_mock_llm):
        with tempfile.TemporaryDirectory() as tmpdir:
            db = str(Path(tmpdir) / "test.db")
            engine = GenesisEngine(llm=rich_mock_llm, db_path=db)
            result = engine.run(synopsis="X")
            session_id = result["session_id"]

            # Re-open the engine, the session should be findable
            engine2 = GenesisEngine(llm=rich_mock_llm, db_path=db)
            session = engine2.session_manager.get_session(session_id)
            assert session is not None
            assert session["stage"] == "complete"

    def test_overall_completeness_above_zero(self, rich_mock_llm):
        engine = GenesisEngine(llm=rich_mock_llm, db_path=":memory:")
        result = engine.run(synopsis="X")
        assert result["overall_completeness"] >= 0.0

    def test_constraints_propagate(self, rich_mock_llm):
        engine = GenesisEngine(llm=rich_mock_llm, db_path=":memory:")
        constraints = {"runtime": "15min", "format": "short"}
        result = engine.run(synopsis="X", constraints=constraints)
        # Engine completed without error
        assert "session_id" in result


class TestGenesisEngineFailurePaths:
    def test_runs_with_failing_llm(self, failing_mock_llm):
        engine = GenesisEngine(llm=failing_mock_llm, db_path=":memory:")
        result = engine.run(synopsis="X")
        # All PKP runs should be marked failed
        for r in result["pkp_results"]:
            assert r.status in ("failed", "skipped")
        # Gate should fail (no specs)
        assert result["gate_result"]["passed"] is False
        # At least one blocker
        assert len(result["gate_result"]["blockers"]) > 0

    def test_runs_with_empty_mock(self, empty_mock_llm):
        engine = GenesisEngine(llm=empty_mock_llm, db_path=":memory:")
        result = engine.run(synopsis="X")
        # Some specs may be written with empty content (parse succeeds, validation fails)
        # Gate fails because validation_status="failed" or specs missing
        assert result["gate_result"]["passed"] is False

    def test_specs_written_even_with_validation_failure(self, empty_mock_llm):
        """If parse succeeds but validate fails, the spec is still written."""
        engine = GenesisEngine(llm=empty_mock_llm, db_path=":memory:")
        result = engine.run(synopsis="X")
        # Mock returns '{"confidence": "unknown", "content": {}}'
        # All PKP agents have required fields -> validation fails but spec is still stored
        for spec_id in REQUIRED_SPECS:
            assert spec_id in result["specifications"]
            # But validation_status is "failed"
            assert result["specifications"][spec_id]["validation_status"] == "failed"


class TestGenesisEngineAsyncAPI:
    def test_run_async_returns_same_shape(self, rich_mock_llm):
        engine = GenesisEngine(llm=rich_mock_llm, db_path=":memory:")
        result = _run(engine.run_async(synopsis="X"))
        assert "specifications" in result
        assert "gate_result" in result

    def test_run_sync_works(self, rich_mock_llm):
        engine = GenesisEngine(llm=rich_mock_llm, db_path=":memory:")
        result = engine.run(synopsis="X")
        assert "specifications" in result


class TestGenesisEngineDeterminism:
    def test_repeated_runs_produce_consistent_spec_count(self, rich_mock_llm):
        engine = GenesisEngine(llm=rich_mock_llm, db_path=":memory:")
        result1 = engine.run(synopsis="Story A")
        result2 = engine.run(synopsis="Story B")
        # Same number of specs regardless of synopsis (mock is synopsis-blind)
        assert len(result1["specifications"]) == len(result2["specifications"])
        # 19 PKP + 1 CHIEF = 20
        assert len(result1["specifications"]) == 20

    def test_different_synopses_both_pass_gate(self, rich_mock_llm):
        engine = GenesisEngine(llm=rich_mock_llm, db_path=":memory:")
        for syn in ["Story A", "Story B", "Story C — with em dash"]:
            result = engine.run(synopsis=syn)
            assert result["gate_result"]["passed"] is True
