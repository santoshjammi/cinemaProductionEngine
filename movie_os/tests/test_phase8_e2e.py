"""Phase 8 e2e tests — full graph runs and SQLite checkpointing."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest


def test_graph_runs_end_to_end(tmp_path):
    """Run the graph on a 1-scene brief and verify it completes."""
    from movie_os.agents import build_graph, new_state
    graph = build_graph()
    brief = {
        "title": "A Quiet Moment",
        "synopsis": "A man sits alone in a dimly lit room.",
        "energy": 3,
        "duration": 6.0,
    }
    state = new_state(brief, thread_id="pytest_e2e")
    result = asyncio.run(graph.ainvoke(
        state,
        config={"configurable": {"thread_id": "pytest_e2e"}},
    ))
    # Without real image/voice/music capabilities, the publishing
    # agent can't produce a final video — but the graph still
    # completes and we have a timeline + QA report.
    assert result["current_step"] == "publishing_done"
    assert result["errors"] == []
    assert result["timeline"] is not None
    assert len(result["timeline"]["scenes"]) == 1
    qa = result.get("qa_report") or {}
    # When no images are rendered, QA has no failed_scenes (nothing to check)
    assert len(qa.get("failed_scenes", [])) == 0


def test_graph_resume_from_checkpoint(tmp_path):
    """Run the graph with a memory checkpointer, then verify get_state works."""
    from movie_os.agents.graph import build_graph
    from movie_os.agents import new_state
    from langgraph.checkpoint.memory import MemorySaver
    checkpointer = MemorySaver()
    graph = build_graph(checkpointer=checkpointer)

    brief = {"title": "Resume", "synopsis": "Test resume", "energy": 3}
    state = new_state(brief, thread_id="resume_thread")

    result = asyncio.run(graph.ainvoke(
        state,
        config={"configurable": {"thread_id": "resume_thread"}},
    ))
    assert result["current_step"] == "publishing_done"

    # Get state from the checkpointer
    state_snapshot = graph.get_state({"configurable": {"thread_id": "resume_thread"}})
    assert state_snapshot is not None
    assert state_snapshot.values["current_step"] == "publishing_done"


def test_make_sqlite_checkpointer_factory(tmp_path):
    """The sqlite checkpointer factory returns a working saver."""
    from movie_os.agents.graph import make_sqlite_checkpointer
    db_path = tmp_path / "ckpt_factory.db"
    cm = asyncio.run(make_sqlite_checkpointer(db_path))
    assert cm is not None
    # The returned saver should have setup, aget, aput methods
    assert hasattr(cm, "setup")
    assert hasattr(cm, "aget")


def test_graph_writes_publishing_manifest(tmp_path):
    """The publishing manifest is written to the output dir."""
    from movie_os.agents.graph import build_graph
    from movie_os.agents import new_state
    import movie_os.agents.publishing_agent as pub
    # Force the publishing agent to use a known output dir
    # (We can't easily change the AgentContext post-build, so check
    # the default output dir)
    graph = build_graph()
    brief = {"title": "Manifest test", "synopsis": "x", "energy": 3}
    state = new_state(brief, thread_id="manifest_thread")
    asyncio.run(graph.ainvoke(
        state,
        config={"configurable": {"thread_id": "manifest_thread"}},
    ))
    manifest = Path("output/final/manifest.json")
    assert manifest.exists()
    m = json.loads(manifest.read_text())
    assert "scenes" in m
    assert len(m["scenes"]) >= 1
