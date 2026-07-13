"""LangGraph state machine wiring for the multi-agent pipeline.

Two architecture paths are supported:

1. **Legacy path** (backward compatible): MovieAgent → Story → Visual → Voice → Music → QA → Publishing
2. **New path** (Cinema Production Engine): ProductionOrchestratorAgent → all 26 agents → Evaluation → Revision

The legacy path is used by default for backward compatibility with existing
productions (ew001, etc.). The new path is activated when:
    - use_new_architecture=True is passed to build_graph()
    - OR the production directory contains screenplay.md (auto-detect)

The graph is checkpointed via SQLite so a long render can resume
from the last successful node.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver


logger = logging.getLogger("movie_os.agents.graph")


def _route_after_qa(state: dict) -> str:
    """Decide where to go after QA (legacy path)."""
    errors = state.get("errors", [])
    if errors:
        return END
    qa = state.get("qa_report") or {}
    failed = qa.get("failed_scenes", [])
    attempts = state.get("render_attempts", {}) or {}
    max_retries = 2
    retryable = [
        s for s in failed
        if attempts.get(str(s), attempts.get(s, 0)) < max_retries
    ]
    if retryable:
        return "visual_agent"
    return "publishing_agent"


def _detect_architecture(production_dir: Path | None) -> str:
    """Auto-detect which architecture to use based on production files.

    Returns: 'new' if screenplay.md exists, 'legacy' otherwise.
    """
    if production_dir and (production_dir / "screenplay.md").exists():
        return "new"
    return "legacy"


def build_graph(
    checkpointer=None,
    config=None,
    skip_stages=None,
    only_stage=None,
    use_new_architecture: bool | None = None,
    production_dir: Path | str | None = None,
):
    """Build the LangGraph state machine.

    Args:
        checkpointer: LangGraph checkpointer for checkpointing
        config: Movie OS configuration
        skip_stages: List of stage names to skip (legacy path only)
        only_stage: If set, run ONLY this stage (legacy path only)
        use_new_architecture: Force new architecture ('new') or legacy ('legacy').
                              None = auto-detect based on production files.
        production_dir: Path to production directory (used for auto-detection)

    Returns:
        Compiled LangGraph graph (either legacy or new architecture)
    """
    # Determine which architecture to use
    if use_new_architecture is None:
        use_new_architecture = _detect_architecture(production_dir)

    arch = "new" if use_new_architecture else "legacy"
    print(f"\n🎬 Using architecture: {arch}")

    if arch == "new":
        return _build_new_graph(checkpointer, config, production_dir)
    else:
        return _build_legacy_graph(checkpointer, config, skip_stages, only_stage)


def _build_new_graph(checkpointer, config, production_dir):
    """Build the new Cinema Production Engine graph with all 26 agents."""
    from movie_os.agents.orchestration.production_orchestrator_agent import ProductionOrchestratorAgent
    from movie_os.agents.orchestration.revision_agent import RevisionAgent
    from movie_os.capabilities.agent_base import ProductionContext

    # Load config for context
    if config is None:
        try:
            from movie_os.config import load_config
            config = load_config()
        except Exception:
            config = None

    # Build production context
    prod_dir = Path(production_dir) if production_dir else Path.cwd() / "output" / "videos" / "final"
    context = ProductionContext(
        production_dir=str(prod_dir),
        grammar=config.get("grammar", "psychological_cinema") if config else "psychological_cinema",
    )

    # Create orchestrator and revision agents
    orchestrator = ProductionOrchestratorAgent()
    revision = RevisionAgent()

    graph = StateGraph(dict)  # Use dict state for flexibility

    graph.add_node("orchestrator", orchestrator.execute)
    graph.add_node("revision", revision.execute)

    graph.set_entry_point("orchestrator")

    # Orchestrator → END on success, or → revision on failure
    def _route_after_orchestrator(state: dict) -> str:
        result = state.get("result", {})
        status = result.get("status", "") if isinstance(result, dict) else str(result)
        if status == "REVISED":
            return "revision"
        return END

    graph.add_conditional_edges(
        "orchestrator",
        _route_after_orchestrator,
        {"revision": "revision", END: END},
    )

    # Revision → orchestrator (loop back for re-run) or END
    def _route_after_revision(state: dict) -> str:
        result = state.get("result", {})
        status = result.get("status", "") if isinstance(result, dict) else str(result)
        if status == "REVISED":
            return "orchestrator"  # Loop back for another pass
        return END

    graph.add_conditional_edges(
        "revision",
        _route_after_revision,
        {"orchestrator": "orchestrator", END: END},
    )

    if checkpointer is None:
        checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


def _build_legacy_graph(checkpointer, config, skip_stages, only_stage):
    """Build the legacy LangGraph state machine (backward compatible)."""
    from movie_os.agents.state import MovieState
    from movie_os.agents.story_agent import StoryAgent
    from movie_os.agents.visual_agent import VisualAgent
    from movie_os.agents.voice_agent import VoiceAgent
    from movie_os.agents.music_agent import MusicAgent
    from movie_os.agents.sfx_agent import SFXAgent
    from movie_os.agents.qa_agent import QAAgent
    from movie_os.agents.publishing_agent import PublishingAgent
    from movie_os.agents.movie_agent import MovieAgent
    from movie_os.agents.base import AgentContext
    from movie_os.capabilities import get_default_registry
    from movie_os.config import load_config

    # Determine which stages to include/exclude
    all_stages = {'story', 'visual', 'voice', 'music', 'sfx', 'qa', 'publishing'}
    
    if only_stage:
        included_stages = {only_stage}
    else:
        skip_stages = skip_stages or []
        excluded = {f"{s}_agent" for s in skip_stages}
        included_stages = all_stages - excluded

    print(f"\n🎬 Pipeline stages (legacy): {sorted(included_stages)}")
    if skip_stages:
        print(f"⏭️  Skipped: {skip_stages}")

    if config is None:
        try:
            config = load_config()
        except Exception:
            config = None

    quality = "draft"
    output_dir = "output"
    if config:
        quality = getattr(getattr(config, "rendering", None), "quality", None)
        if quality and hasattr(quality, "value"):
            quality = quality.value
        elif not quality:
            quality = "draft"
        output_dir = getattr(getattr(config, "project", None), "output_dir", "output")

    # Build a single shared context for all agents
    context = AgentContext(
        registry=get_default_registry(),
        quality=quality,
        output_dir=output_dir,
    )

    # Build agents for included stages only
    agents = {}
    if 'story' in included_stages: agents['story'] = StoryAgent(context)
    if 'visual' in included_stages: agents['visual'] = VisualAgent(context)
    if 'voice' in included_stages: agents['voice'] = VoiceAgent(context)
    if 'music' in included_stages: agents['music'] = MusicAgent(context)
    if 'sfx' in included_stages: agents['sfx'] = SFXAgent(context)
    if 'qa' in included_stages: agents['qa'] = QAAgent(context)
    if 'publishing' in included_stages: agents['publishing'] = PublishingAgent(context)
    
    # Movie agent always runs first (it decides the plan)
    movie = MovieAgent(context)

    graph = StateGraph(MovieState)

    graph.add_node("movie_agent", movie)
    if 'story' in included_stages: graph.add_node("story_agent", agents['story'])
    if 'visual' in included_stages: graph.add_node("visual_agent", agents['visual'])
    if 'voice' in included_stages: graph.add_node("voice_agent", agents['voice'])
    if 'music' in included_stages: graph.add_node("music_agent", agents['music'])
    if 'sfx' in included_stages: graph.add_node("sfx_agent", agents['sfx'])
    if 'qa' in included_stages: graph.add_node("qa_agent", agents['qa'])
    if 'publishing' in included_stages: graph.add_node("publishing_agent", agents['publishing'])

    # Always start with movie_agent
    graph.set_entry_point("movie_agent")
    
    # Wire edges conditionally based on included stages
    if only_stage:
        stage_node = f"{only_stage}_agent"
        if stage_node in [n for n in graph.nodes]:
            graph.add_edge("movie_agent", stage_node)
            if only_stage not in ['qa', 'publishing']:
                graph.add_edge(stage_node, END)
        else:
            if 'story' in included_stages:
                graph.add_edge("movie_agent", "story_agent")
    elif 'story' in included_stages:
        graph.add_edge("movie_agent", "story_agent")
        
        # Story agent fans out to production stages
        if 'visual' in included_stages: graph.add_edge("story_agent", "visual_agent")
        if 'voice' in included_stages: graph.add_edge("story_agent", "voice_agent")
        if 'music' in included_stages: graph.add_edge("story_agent", "music_agent")
        if 'sfx' in included_stages: graph.add_edge("story_agent", "sfx_agent")

    # Production stages converge into QA (if both exist)
    production_stages = ['visual', 'voice', 'music', 'sfx']
    if 'qa' in included_stages:
        for stage in production_stages:
            node_name = f"{stage}_agent"
            if node_name in [n for n in graph.nodes]:
                graph.add_edge(node_name, "qa_agent")
        
        # QA routes either back to visual (re-render) or to publishing
        graph.add_conditional_edges(
            "qa_agent",
            _route_after_qa,
            {"visual_agent": "visual_agent", "publishing_agent": "publishing_agent", END: END},
        )
    
    if 'publishing' in included_stages:
        if 'qa' not in included_stages and 'story' in included_stages:
            graph.add_edge("story_agent", "publishing_agent")
        elif 'qa' in included_stages:
            graph.add_edge("publishing_agent", END)
    elif 'story' in included_stages and 'qa' not in included_stages and 'publishing' not in included_stages:
        graph.add_edge("story_agent", END)

    if checkpointer is None:
        checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


async def make_sqlite_checkpointer(db_path: str | Path):
    """Build a SQLite-backed async checkpointer for resume support."""
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    cm = AsyncSqliteSaver.from_conn_string(str(db_path))
    saver = await cm.__aenter__()
    await saver.setup()
    return saver


async def run_graph(
    initial_state: dict,
    *,
    thread_id: str,
    checkpointer=None,
    config: dict | None = None,
) -> dict:
    """Run the graph from an initial state to completion."""
    graph = build_graph(checkpointer=checkpointer)
    cfg = {"configurable": {"thread_id": thread_id}}
    if config:
        cfg.update(config)
    result = await graph.ainvoke(initial_state, config=cfg)
    return result
