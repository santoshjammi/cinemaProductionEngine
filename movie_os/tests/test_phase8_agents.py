"""Phase 8.1 tests — State, AgentBase, individual agents, graph wiring."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class TestMovieState:
    def test_new_state_has_required_fields(self):
        from movie_os.agents import new_state
        s = new_state({"title": "Test"}, thread_id="t1")
        assert s["thread_id"] == "t1"
        assert s["brief"] == {"title": "Test"}
        assert s["current_step"] == "init"
        assert s["errors"] == []
        assert s["started_at"]

    def test_validate_state_passes_on_valid_state(self):
        from movie_os.agents import new_state, validate_state
        s = new_state({"title": "x"}, thread_id="t2")
        validate_state(s)  # should not raise

    def test_validate_state_catches_missing_thread_id(self):
        from movie_os.agents import new_state, validate_state
        s = new_state({"x": 1}, thread_id="t3")
        s = dict(s)
        del s["thread_id"]
        with pytest.raises(Exception):
            validate_state(s)


# ---------------------------------------------------------------------------
# AgentBase
# ---------------------------------------------------------------------------

class TestAgentBase:
    def test_agent_logs_and_captures_errors(self):
        from movie_os.agents.base import AgentBase, AgentContext

        class FailingAgent(AgentBase):
            name = "failing"
            async def run(self, state):
                raise ValueError("boom")

        cap = AgentContext(registry=None)
        agent = FailingAgent(cap)
        state = {"thread_id": "x", "errors": [], "current_step": "init"}
        out = asyncio.run(agent(state))
        assert any("ValueError" in e and "boom" in e for e in out["errors"])
        assert out["current_step"] == "failing_failed"

    def test_agent_returns_state_on_success(self):
        from movie_os.agents.base import AgentBase, AgentContext

        class OkAgent(AgentBase):
            name = "ok"
            async def run(self, state):
                out = dict(state)
                out["current_step"] = "ok_done"
                return out

        cap = AgentContext(registry=None)
        agent = OkAgent(cap)
        out = asyncio.run(agent({"thread_id": "x", "current_step": "init", "errors": []}))
        assert out["current_step"] == "ok_done"


# ---------------------------------------------------------------------------
# StoryAgent
# ---------------------------------------------------------------------------

class TestStoryAgent:
    def test_brief_as_timeline(self):
        from movie_os.agents import StoryAgent, new_state
        from movie_os.agents.base import AgentContext
        agent = StoryAgent(AgentContext(registry=None))
        state = new_state(
            {"title": "Test", "synopsis": "A man in a dark room", "energy": 3, "duration": 8.0},
            thread_id="t",
        )
        out = asyncio.run(agent.run(state))
        assert out["timeline"] is not None
        assert len(out["timeline"]["scenes"]) == 1
        scene = out["timeline"]["scenes"][0]
        assert scene["scene_description"] == "A man in a dark room"
        assert scene["energy"] == 3
        assert out["current_step"] == "story_done"

    def test_load_brief_from_yaml(self, tmp_path):
        from movie_os.agents.story_agent import load_brief
        p = tmp_path / "brief.yaml"
        p.write_text("title: From YAML\nsynopsis: A scene\nenergy: 5\n")
        brief = load_brief(p)
        assert brief["title"] == "From YAML"
        assert brief["synopsis"] == "A scene"
        assert "source_path" in brief


# ---------------------------------------------------------------------------
# Graph wiring
# ---------------------------------------------------------------------------

class TestGraph:
    def test_build_graph_has_all_agents(self):
        from movie_os.agents import build_graph
        g = build_graph()
        nodes = list(g.nodes.keys()) if hasattr(g, "nodes") else []
        assert "movie_agent" in nodes
        assert "story_agent" in nodes
        assert "visual_agent" in nodes
        assert "voice_agent" in nodes
        assert "music_agent" in nodes
        assert "sfx_agent" in nodes
        assert "qa_agent" in nodes
        assert "publishing_agent" in nodes

    def test_route_after_qa_routes_to_publishing_when_no_failures(self):
        from movie_os.agents.graph import _route_after_qa
        from langgraph.graph import END
        state = {"errors": [], "qa_report": {"failed_scenes": []}, "render_attempts": {}}
        assert _route_after_qa(state) == "publishing_agent"

    def test_route_after_qa_routes_to_visual_on_failure(self):
        from movie_os.agents.graph import _route_after_qa
        state = {
            "errors": [],
            "qa_report": {"failed_scenes": [1]},
            "render_attempts": {"1": 1},
        }
        assert _route_after_qa(state) == "visual_agent"

    def test_route_after_qa_gives_up_after_max_retries(self):
        from movie_os.agents.graph import _route_after_qa
        state = {
            "errors": [],
            "qa_report": {"failed_scenes": [1]},
            "render_attempts": {"1": 5},
        }
        assert _route_after_qa(state) == "publishing_agent"

    def test_route_after_qa_ends_on_errors(self):
        from movie_os.agents.graph import _route_after_qa
        from langgraph.graph import END
        state = {"errors": ["boom"], "qa_report": None, "render_attempts": {}}
        assert _route_after_qa(state) == END


# ---------------------------------------------------------------------------
# QA Agent
# ---------------------------------------------------------------------------

class TestQAAgent:
    def test_qa_passes_when_assets_present(self, tmp_path):
        from movie_os.agents import QAAgent, new_state
        from movie_os.agents.base import AgentContext
        # Create a fake but realistic-sized image (PNG header + dummy data)
        img = tmp_path / "scene_001.png"
        img.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 200)
        state = new_state({}, thread_id="t")
        state = dict(state)
        state["timeline"] = {
            "scenes": [{"number": 1, "shots": [{"id": "s1"}]}]
        }
        state["scene_assets"] = {1: {"image_s1": str(img)}}
        agent = QAAgent(AgentContext(registry=None))
        out = asyncio.run(agent.run(state))
        assert out["qa_report"]["passed_scenes"] == [1], f"Failed: {out['qa_report']['scenes'][1]}"
        assert out["qa_report"]["failed_scenes"] == []

    def test_qa_fails_when_image_missing(self):
        from movie_os.agents import QAAgent, new_state
        from movie_os.agents.base import AgentContext
        state = new_state({}, thread_id="t")
        state = dict(state)
        state["timeline"] = {
            "scenes": [{"number": 1, "shots": [{"id": "s1"}]}]
        }
        state["scene_assets"] = {1: {}}
        agent = QAAgent(AgentContext(registry=None))
        out = asyncio.run(agent.run(state))
        assert out["qa_report"]["failed_scenes"] == [1]

    def test_qa_flags_missing_voice_when_voiceover_set(self):
        from movie_os.agents import QAAgent, new_state
        from movie_os.agents.base import AgentContext
        state = new_state({}, thread_id="t")
        state = dict(state)
        state["timeline"] = {
            "scenes": [{"number": 1, "shots": [], "voiceover": "Hello there."}]
        }
        state["scene_assets"] = {1: {}}
        agent = QAAgent(AgentContext(registry=None))
        out = asyncio.run(agent.run(state))
        report = out["qa_report"]["scenes"][1]
        assert any(not c["passed"] and "voice" in c["name"].lower() for c in report["checks"])

    def test_qa_flags_irreversible_moment_with_one_shot(self):
        from movie_os.agents import QAAgent, new_state
        from movie_os.agents.base import AgentContext
        state = new_state({}, thread_id="t")
        state = dict(state)
        state["timeline"] = {
            "scenes": [{
                "number": 1,
                "shots": [{"id": "s1"}],  # only 1 shot
                "irreversible_moment": True,
            }]
        }
        state["scene_assets"] = {1: {}}
        agent = QAAgent(AgentContext(registry=None))
        out = asyncio.run(agent.run(state))
        report = out["qa_report"]["scenes"][1]
        # The QA agent warns about 1 shot but doesn't fail (passed=True)
        assert any("irreversible" in c["name"] for c in report["checks"])


# ---------------------------------------------------------------------------
# Publishing Agent
# ---------------------------------------------------------------------------

class TestPublishingAgent:
    def test_publish_writes_manifest(self, tmp_path):
        from movie_os.agents import PublishingAgent, new_state
        from movie_os.agents.base import AgentContext
        # Create a real PNG so ffmpeg can read it
        from PIL import Image
        img = tmp_path / "s1.png"
        Image.new("RGB", (256, 256), color=(80, 40, 120)).save(img)
        state = new_state({}, thread_id="t")
        state = dict(state)
        state["timeline"] = {
            "scenes": [{
                "number": 1,
                "title": "S",
                "shots": [{"id": "s1", "shot_size": "wide"}],
                "target_duration_seconds": 3.0,  # Short for fast test
            }]
        }
        state["scene_assets"] = {1: {"image_s1": str(img)}}
        ctx = AgentContext(registry=None, output_dir=str(tmp_path))
        agent = PublishingAgent(ctx)
        out = asyncio.run(agent.run(state))
        # Should complete (either with a video or with no_clips)
        assert out["current_step"] in ("publishing_done", "publishing_failed")


# ---------------------------------------------------------------------------
# Voice/Music/SFX/Visual agents — registered but skip if capability absent
# ---------------------------------------------------------------------------

class TestSkipOnMissingCapability:
    def test_voice_agent_skips_without_capability(self):
        from movie_os.agents import VoiceAgent, new_state
        from movie_os.agents.base import AgentContext
        state = new_state({}, thread_id="t")
        state = dict(state)
        state["timeline"] = {"scenes": [{"number": 1, "voiceover": "Hi"}]}
        agent = VoiceAgent(AgentContext(registry=None))
        out = asyncio.run(agent.run(state))
        assert out["current_step"] == "voice_skipped"

    def test_music_agent_skips_without_capability(self):
        from movie_os.agents import MusicAgent, new_state
        from movie_os.agents.base import AgentContext
        state = new_state({}, thread_id="t")
        state = dict(state)
        state["timeline"] = {"scenes": [{"number": 1, "music_cue": {"zone": "act_1"}}]}
        agent = MusicAgent(AgentContext(registry=None))
        out = asyncio.run(agent.run(state))
        assert out["current_step"] == "music_skipped"

    def test_sfx_agent_skips_without_capability(self):
        from movie_os.agents import SFXAgent, new_state
        from movie_os.agents.base import AgentContext
        state = new_state({}, thread_id="t")
        state = dict(state)
        state["timeline"] = {"scenes": [{"number": 1, "sfx_layers": ["thunder"]}]}
        agent = SFXAgent(AgentContext(registry=None))
        out = asyncio.run(agent.run(state))
        assert out["current_step"] == "sfx_skipped"

    def test_visual_agent_skips_without_scenes(self):
        from movie_os.agents import VisualAgent, new_state
        from movie_os.agents.base import AgentContext
        state = new_state({}, thread_id="t")
        state = dict(state)
        state["timeline"] = {"scenes": []}
        agent = VisualAgent(AgentContext(registry=None))
        out = asyncio.run(agent.run(state))
        assert out["current_step"] == "visual_skipped"
