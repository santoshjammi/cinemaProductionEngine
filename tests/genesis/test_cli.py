"""Smoke tests for the Genesis CLI.

Exercises the arg parser and command handlers without invoking real LLMs.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

import pytest

from movie_os.genesis import cli
from movie_os.genesis.cli import (
    _read_synopsis_file,
    _check_llm,
    _format_result,
    cmd_run,
    cmd_agents,
    cmd_discover,
    cmd_spec,
    cmd_gate,
    cmd_validate,
    cmd_state,
    main,
)


class TestSynopsisFileParser:
    def test_plain_text(self, tmp_path):
        p = tmp_path / "syn.txt"
        p.write_text("A man withdraws from his wife after losing his job.")
        syn, cons = _read_synopsis_file(str(p))
        assert "man withdraws" in syn
        assert cons == {}

    def test_with_constraints(self, tmp_path):
        p = tmp_path / "syn.txt"
        p.write_text(
            "SYNOPSIS\nA man withdraws from his wife.\n\n"
            "OPTIONAL CONSTRAINTS\n"
            "runtime: 15min\n"
            "format: short\n"
            "target_audience: adults\n"
        )
        syn, cons = _read_synopsis_file(str(p))
        assert "man withdraws" in syn
        assert cons["runtime"] == "15min"
        assert cons["format"] == "short"
        assert cons["target_audience"] == "adults"

    def test_constraints_typed(self, tmp_path):
        p = tmp_path / "syn.txt"
        p.write_text(
            "SYNOPSIS\nS\n\nOPTIONAL CONSTRAINTS\n"
            "duration_minutes: 15\n"
            "is_short: true\n"
            "aspect_ratio: 1.78\n"
        )
        _, cons = _read_synopsis_file(str(p))
        assert cons["duration_minutes"] == 15
        assert cons["is_short"] is True
        assert cons["aspect_ratio"] == 1.78

    def test_comments_ignored(self, tmp_path):
        p = tmp_path / "syn.txt"
        p.write_text(
            "SYNOPSIS\nS\n\nOPTIONAL CONSTRAINTS\n"
            "# this is a comment\n"
            "runtime: 15min\n"
        )
        _, cons = _read_synopsis_file(str(p))
        assert "comment" not in str(cons)
        assert cons["runtime"] == "15min"


class TestLLMCheck:
    def test_unreachable_url_returns_false(self):
        # Use an unlikely port
        assert _check_llm("http://127.0.0.1:1") is False

    def test_reachable_url_attempts(self):
        # We don't test a real server; just verify the function is callable
        result = _check_llm("http://127.0.0.1:1")
        assert isinstance(result, bool)


class TestFormatResult:
    def test_format_with_passing_gate(self, capsys, rich_mock_llm, tmp_path):
        from movie_os.genesis.engine import GenesisEngine
        engine = GenesisEngine(llm=rich_mock_llm, db_path=":memory:")
        result = engine.run(synopsis="X")
        _format_result(result, str(tmp_path))
        out = capsys.readouterr().out
        assert "GENESIS" in out
        assert "Discovery Agents" in out
        assert "PKP Specifications" in out
        assert "Completion Gate" in out
        # Output file was written
        assert (tmp_path / "genesis_result.json").exists()

    def test_format_with_failing_gate(self, capsys, failing_mock_llm, tmp_path):
        from movie_os.genesis.engine import GenesisEngine
        engine = GenesisEngine(llm=failing_mock_llm, db_path=":memory:")
        result = engine.run(synopsis="X")
        _format_result(result)
        out = capsys.readouterr().out
        assert "FAILED" in out
        assert "Blockers" in out

    def test_output_dir_must_be_creatable(self, capsys, rich_mock_llm, tmp_path):
        from movie_os.genesis.engine import GenesisEngine
        engine = GenesisEngine(llm=rich_mock_llm, db_path=":memory:")
        result = engine.run(synopsis="X")
        out_dir = tmp_path / "deep" / "nested" / "output"
        _format_result(result, str(out_dir))
        assert out_dir.exists()
        assert (out_dir / "genesis_result.json").exists()


class TestCmdAgents:
    def test_agents_lists_known_agents(self, capsys):
        args = argparse.Namespace()
        rc = cmd_agents(args)
        assert rc == 0
        out = capsys.readouterr().out
        # Should list at least the major agent categories
        assert "intent_analyst" in out
        assert "vision_agent" in out
        assert "story_reviewer" in out
        assert "chief_architect" in out


class TestCmdRunWithMock:
    def test_run_with_synopsis_file(self, tmp_path, capsys):
        syn = tmp_path / "syn.md"
        syn.write_text("A man withdraws from his wife after losing his job.")
        out_dir = tmp_path / "out"

        args = argparse.Namespace(
            synopsis=str(syn),
            constraints=None,
            mock=True,
            llm_url="http://127.0.0.1:1",
            llm_key=None,
            model="qwen3-coder",
            output=str(out_dir),
            db=None,
        )
        rc = cmd_run(args)
        # With mock + rich responses, gate should pass
        assert rc == 0
        assert out_dir.exists()
        assert (out_dir / "genesis_result.json").exists()
        # Verify result is valid JSON
        result = json.loads((out_dir / "genesis_result.json").read_text())
        assert "specifications" in result
        assert result["gate_result"]["passed"] is True

    def test_run_returns_zero_when_gate_passes_with_rich_mock(self, tmp_path):
        """--mock uses the rich mock by default, so gate should pass."""
        syn = tmp_path / "syn.md"
        syn.write_text("X")
        args = argparse.Namespace(
            synopsis=str(syn),
            constraints=None,
            mock=True,
            llm_url="http://127.0.0.1:1",
            llm_key=None,
            model="qwen3-coder",
            output=None,
            db=None,
        )
        rc = cmd_run(args)
        assert rc == 0


class TestMainArgParser:
    def test_no_args_shows_help(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main([])
        # argparse exits with code 0 for --help, 2 for missing required
        assert exc.value.code in (0, 2)

    def test_run_subcommand(self, capsys, tmp_path):
        syn = tmp_path / "syn.md"
        syn.write_text("X")
        rc = main(["--mock", "run", "--synopsis", str(syn)])
        # Should return 0 (gate passes with mock)
        assert rc == 0

    def test_agents_subcommand(self, capsys):
        rc = main(["agents"])
        assert rc == 0

    def test_unknown_subcommand_exits_with_code(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["nonexistent_subcommand_xyz"])
        assert exc.value.code != 0


class TestCmdDiscover:
    def test_discover_runs_seven_agents(self, tmp_path, capsys):
        from movie_os.genesis.mock_data import build_rich_mock_llm
        syn = tmp_path / "syn.md"
        syn.write_text("A man withdraws from his wife.")
        args = argparse.Namespace(
            synopsis=str(syn),
            constraints=None,
            mock=True,
            llm_url="http://127.0.0.1:1",
            llm_key=None,
            model="qwen3-coder",
            db=None,
        )
        # Patch the engine's LLM by monkeypatching the engine creation
        import movie_os.genesis.cli as cli_mod
        original_build = cli_mod._build_llm
        cli_mod._build_llm = lambda a: build_rich_mock_llm()
        try:
            rc = cmd_discover(args)
            out = capsys.readouterr().out
            assert rc == 0
            assert "Discovery Results" in out
        finally:
            cli_mod._build_llm = original_build
