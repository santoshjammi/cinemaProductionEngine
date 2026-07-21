"""Movie OS Agents — multi-agent orchestration.

Public API:
    from movie_os.agents import (
        MovieState, AgentBase, AgentContext,
        StoryAgent, VisualAgent, VoiceAgent, MusicAgent,
        SFXAgent, QAAgent, PublishingAgent, MovieAgent,
        build_graph, run_graph,
    )

Two architecture paths:
1. Legacy (backward compatible): MovieAgent → Story → Visual → Voice → Music → QA → Publishing
2. New (Cinema Production Engine): ProductionOrchestratorAgent → all 26 agents → Evaluation → Revision

Auto-detection: If production_dir/screenplay.md exists, uses new architecture.
"""

from .state import MovieState, MovieStateModel, new_state, validate_state
from .base import AgentBase, AgentContext, make_state_updater
from .movie_agent import MovieAgent
from .story_agent import StoryAgent
from .visual_agent import VisualAgent
from .voice_agent import VoiceAgent
from .music_agent import MusicAgent
from .sfx_agent import SFXAgent
from .qa_agent import QAAgent
from .publishing_agent import PublishingAgent


def build_graph(checkpointer=None, config=None, skip_stages=None, only_stage=None, use_new_architecture=None, production_dir=None):
    """Build the LangGraph state machine (re-exported from graph.py)."""
    from .graph import build_graph as _build_graph
    return _build_graph(
        checkpointer=checkpointer,
        config=config,
        skip_stages=skip_stages,
        only_stage=only_stage,
        use_new_architecture=use_new_architecture,
        production_dir=production_dir,
    )


def run_graph(initial_state, *, thread_id, checkpointer=None, config=None):
    """Run the graph (re-exported from graph.py)."""
    from .graph import run_graph as _run_graph
    return _run_graph(initial_state, thread_id=thread_id, checkpointer=checkpointer, config=config)


__all__ = [
    "MovieState", "MovieStateModel", "new_state", "validate_state",
    "AgentBase", "AgentContext", "make_state_updater",
    "MovieAgent", "StoryAgent", "VisualAgent", "VoiceAgent",
    "MusicAgent", "SFXAgent", "QAAgent", "PublishingAgent",
    "build_graph", "run_graph",
]
