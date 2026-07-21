"""Unit tests for movie_os.genesis.master_prompt."""

from __future__ import annotations

import json

import pytest

from movie_os.genesis.master_prompt import (
    MASTER_SYSTEM_PROMPT,
    build_agent_prompt,
)


class TestMasterSystemPrompt:
    def test_is_nonempty(self):
        assert len(MASTER_SYSTEM_PROMPT) > 100

    def test_contains_rules(self):
        for keyword in ("DISCOVER", "INFER", "CONFIDENCE", "JSON"):
            assert keyword in MASTER_SYSTEM_PROMPT

    def test_contains_five_confidence_levels(self):
        for level in ("explicit", "inferred", "confirmed", "assumed", "unknown"):
            assert level in MASTER_SYSTEM_PROMPT


class TestBuildAgentPrompt:
    def test_minimal(self):
        result = build_agent_prompt(
            agent_name="TestAgent",
            agent_instructions="Do something",
            synopsis="A story",
        )
        assert "# Agent: TestAgent" in result
        assert "Do something" in result
        assert "A story" in result
        assert "Respond with valid JSON" in result

    def test_with_context_serialized_as_json(self):
        ctx = {"PKP-00": {"vision_statement": "test"}}
        result = build_agent_prompt(
            agent_name="X", agent_instructions="i", synopsis="s", context=ctx
        )
        assert "## CONTEXT" in result
        assert "PKP-00" in result
        # Must be valid JSON inside the fence
        import re
        m = re.search(r"```json\n(.*?)\n```", result, re.DOTALL)
        assert m is not None
        parsed = json.loads(m.group(1))
        assert "PKP-00" in parsed

    def test_with_constraints(self):
        result = build_agent_prompt(
            agent_name="X", agent_instructions="i", synopsis="s",
            constraints={"runtime": "15min"},
        )
        assert "## CONSTRAINTS" in result
        assert "runtime" in result
        assert "15min" in result

    def test_no_context_or_constraints(self):
        result = build_agent_prompt(
            agent_name="X", agent_instructions="i", synopsis="s"
        )
        assert "## CONTEXT" not in result
        assert "## CONSTRAINTS" not in result

    def test_context_with_non_serializable_defaults_to_str(self):
        # datetime objects should not crash; default=str used
        from datetime import datetime
        ctx = {"timestamp": datetime(2026, 7, 20, 12, 0)}
        result = build_agent_prompt(
            agent_name="X", agent_instructions="i", synopsis="s", context=ctx
        )
        assert "2026" in result
