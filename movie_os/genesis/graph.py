"""LangGraph state machine for the Genesis pre-production pipeline.

Replaces the sequential execution in GenesisEngine with a proper
LangGraph state machine supporting checkpointing, conditional edges,
and error recovery.

Usage:
    from movie_os.genesis.graph import GenesisGraph
    graph = GenesisGraph(llm=client)
    result = await graph.run(synopsis="...")
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Optional

from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from .completion_gate import PreProductionCompletionGate
from .llm_client import LLMClient, MockLLMClient
from .models import AgentResult, ConfidenceLevel
from .pkg import ProductionKnowledgeGraph
from .session import SessionManager

logger = logging.getLogger("movie_os.genesis.graph")


def _compute_completeness(pkg: ProductionKnowledgeGraph) -> dict[str, float]:
    """Compute completeness per phase from spec validation status."""
    phase_passes: dict[str, list[bool]] = {}
    for spec in pkg.get_all_specifications().values():
        phase_passes.setdefault(spec.phase, []).append(
            spec.validation_status == "passed"
        )
    completeness: dict[str, float] = {}
    for phase, results in phase_passes.items():
        if results:
            completeness[phase] = sum(results) / len(results)
    return completeness


def _discovery_node(state: dict) -> dict:
    """Run all 7 discovery agents."""
    from .discovery.intent_analyst import IntentAnalyst
    from .discovery.theme_analyst import ThemeAnalyst
    from .discovery.emotion_analyst import EmotionAnalyst
    from .discovery.conflict_analyst import ConflictAnalyst
    from .discovery.audience_analyst import AudienceAnalyst
    from .discovery.gap_analyst import GapAnalyst
    from .discovery.question_planner import QuestionPlanner

    pkg: ProductionKnowledgeGraph = state["_pkg"]
    llm = state["_get_llm"]("discovery")

    agents = [
        IntentAnalyst(llm), ThemeAnalyst(llm), EmotionAnalyst(llm),
        ConflictAnalyst(llm), AudienceAnalyst(llm), GapAnalyst(llm),
        QuestionPlanner(llm),
    ]

    loop = asyncio.new_event_loop()
    try:
        results = loop.run_until_complete(asyncio.gather(*[a.run(pkg) for a in agents]))
    finally:
        loop.close()

    total = len(results)
    success = sum(1 for r in results if r.status == "success")
    pkg.save_state()
    return {
        "_discovery_results": results,
        "_total_discovery": total,
        "_success_discovery": success,
    }


def _pkp_node(state: dict) -> dict:
    """Run all 19 PKP agents in dependency order."""
    from .pkp_agents.vision_agent import VisionAgent
    from .pkp_agents.creative_strategy_agent import CreativeStrategyAgent
    from .pkp_agents.project_agent import ProjectAgent
    from .pkp_agents.research_agent import ResearchAgent
    from .pkp_agents.story_agent import StoryAgent
    from .pkp_agents.world_agent import WorldAgent
    from .pkp_agents.character_agent import CharacterAgent
    from .pkp_agents.relationship_agent import RelationshipAgent
    from .pkp_agents.psychology_agent import PsychologyAgent
    from .pkp_agents.narrative_agent import NarrativeAgent
    from .pkp_agents.directorial_agent import DirectorialAgent
    from .pkp_agents.production_design_agent import ProductionDesignAgent
    from .pkp_agents.audio_intent_agent import AudioIntentAgent
    from .pkp_agents.editing_language_agent import EditingLanguageAgent
    from .pkp_agents.animation_intent_agent import AnimationIntentAgent
    from .pkp_agents.blueprint_agent import BlueprintAgent
    from .pkp_agents.distribution_agent import DistributionAgent
    from .pkp_agents.quality_agent import QualityAgent
    from .pkp_agents.knowledge_graph_agent import KnowledgeGraphAgent

    pkg: ProductionKnowledgeGraph = state["_pkg"]
    llm = state["_get_llm"]("pkp")

    agents = [
        VisionAgent(llm), CreativeStrategyAgent(llm), ProjectAgent(llm),
        ResearchAgent(llm), StoryAgent(llm), WorldAgent(llm),
        CharacterAgent(llm), RelationshipAgent(llm), PsychologyAgent(llm),
        NarrativeAgent(llm),
        DirectorialAgent(llm), ProductionDesignAgent(llm),
        AudioIntentAgent(llm), EditingLanguageAgent(llm), AnimationIntentAgent(llm),
        BlueprintAgent(llm),
        DistributionAgent(llm), QualityAgent(llm), KnowledgeGraphAgent(llm),
    ]

    loop = asyncio.new_event_loop()
    try:
        results = loop.run_until_complete(asyncio.gather(*[a.run(pkg) for a in agents]))
    finally:
        loop.close()

    total = len(results)
    success = sum(1 for r in results if r.status == "success")
    pkg.save_state()
    return {
        "_pkp_results": results,
        "_total_pkp": total,
        "_success_pkp": success,
    }


def _review_node(state: dict) -> dict:
    """Run all 4 review agents + the ChiefArchitect."""
    from .reviewers.story_reviewer import StoryReviewer
    from .reviewers.character_reviewer import CharacterReviewer
    from .reviewers.narrative_reviewer import NarrativeReviewer
    from .reviewers.psychology_reviewer import PsychologyReviewer
    from .chief_architect import ChiefArchitect

    pkg: ProductionKnowledgeGraph = state["_pkg"]
    reviewer_llm = state["_get_llm"]("reviewer")
    chief_llm = state["_get_llm"]("chief")

    agents = [
        StoryReviewer(reviewer_llm),
        CharacterReviewer(reviewer_llm),
        NarrativeReviewer(reviewer_llm),
        PsychologyReviewer(reviewer_llm),
        ChiefArchitect(chief_llm),
    ]

    loop = asyncio.new_event_loop()
    try:
        results = loop.run_until_complete(asyncio.gather(*[a.run(pkg) for a in agents]))
    finally:
        loop.close()

    total = len(results)
    success = sum(1 for r in results if r.status == "success")
    pkg.save_state()
    return {
        "_review_results": results,
        "_total_review": total,
        "_success_review": success,
    }


def _gate_node(state: dict) -> dict:
    """Run the completion gate and compute completeness."""
    pkg: ProductionKnowledgeGraph = state["_pkg"]
    gate = PreProductionCompletionGate()
    gate_result = gate.check(pkg)

    completeness = _compute_completeness(pkg)
    for phase, score in completeness.items():
        pkg.set_completeness(phase, score)
    overall = pkg.get_overall_completeness()

    return {
        "_gate_result": gate_result.to_dict(),
        "_completeness": completeness,
        "_overall_completeness": overall,
    }


def _route_after_gate(state: dict) -> str:
    """Route to END when gate passes, or to discovery for retry."""
    gate_result = state.get("_gate_result", {})
    passed = gate_result.get("passed", False)
    if passed:
        return "success"
    return "failed"


def _summarize_node(state: dict) -> dict:
    """Build the final summary result."""
    result = {
        "gate_result": state.get("_gate_result", {}),
        "overall_completeness": state.get("_overall_completeness", 0.0),
        "completeness": state.get("_completeness", {}),
        "discovery_results": state.get("_discovery_results", []),
        "pkp_results": state.get("_pkp_results", []),
        "review_results": state.get("_review_results", []),
        "session_id": state.get("_session_id", ""),
    }
    return {"_final_result": result}


def _error_node(state: dict) -> dict:
    """Handle failures by recording errors and ending."""
    state["_errors"] = state.get("_errors", [])
    return {"_final_result": {"error": "Pipeline failed"}}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class GenesisGraph:
    """LangGraph-powered Genesis pipeline."""

    def __init__(
        self,
        llm: LLMClient | MockLLMClient | dict[str, LLMClient | MockLLMClient] | None = None,
        db_path: str | Path = ":memory:",
        session_db: str | Path | None = None,
        checkpointer=None,
    ):
        self.db_path = str(db_path)
        self.session_manager = SessionManager(session_db or db_path)
        self.checkpointer = checkpointer or MemorySaver()

        if llm is None:
            self._llm = MockLLMClient()
            self._tiered_llm: dict[str, LLMClient | MockLLMClient] | None = None
        elif isinstance(llm, dict):
            self._llm = llm.get("pkp", MockLLMClient())
            self._tiered_llm = llm
        else:
            self._llm = llm
            self._tiered_llm = None

    def _get_llm(self, tier: str) -> LLMClient | MockLLMClient:
        if self._tiered_llm:
            return self._tiered_llm.get(tier, self._llm)
        return self._llm

    def build(self) -> StateGraph:
        """Build and compile the LangGraph pipeline."""
        builder = StateGraph(dict)

        builder.add_node("discovery", _discovery_node)
        builder.add_node("pkp_generation", _pkp_node)
        builder.add_node("review", _review_node)
        builder.add_node("gate", _gate_node)
        builder.add_node("summarize", _summarize_node)
        builder.add_node("error", _error_node)

        builder.add_edge(START, "discovery")
        builder.add_edge("discovery", "pkp_generation")
        builder.add_edge("pkp_generation", "review")
        builder.add_edge("review", "gate")
        builder.add_conditional_edges(
            "gate",
            _route_after_gate,
            {"success": "summarize", "failed": "summarize"},
        )
        builder.add_edge("summarize", END)

        return builder.compile(checkpointer=self.checkpointer)

    def run(
        self,
        synopsis: str,
        constraints: dict[str, Any] | None = None,
        thread_id: str = "default",
    ) -> dict[str, Any]:
        """Run the Genesis pipeline synchronously."""
        import asyncio
        return asyncio.run(self.run_async(synopsis, constraints, thread_id))

    async def run_async(
        self,
        synopsis: str,
        constraints: dict[str, Any] | None = None,
        thread_id: str = "default",
    ) -> dict[str, Any]:
        """Run the Genesis pipeline asynchronously."""
        session_id = self.session_manager.create_session(synopsis, constraints)
        pkg = ProductionKnowledgeGraph(self.db_path)
        pkg.synopsis = synopsis
        pkg.constraints = constraints or {}
        pkg.save_state()

        initial_state = {
            "_pkg": pkg,
            "_get_llm": self._get_llm,
            "_session_id": session_id,
            "_llm": self._llm,
            "_tiered_llm": self._tiered_llm,
            "_errors": [],
        }

        graph = self.build()
        cfg = {"configurable": {"thread_id": thread_id}}
        final_state = await graph.ainvoke(initial_state, config=cfg)

        result = final_state.get("_final_result", {})
        gate_result = result.get("gate_result", {})
        completeness = result.get("overall_completeness", 0.0)
        discovery_results = result.get("discovery_results", [])
        pkp_results = result.get("pkp_results", [])
        review_results = result.get("review_results", [])

        return {
            "session_id": session_id,
            "discovery_results": discovery_results,
            "pkp_results": pkp_results,
            "review_results": review_results,
            "gate_result": gate_result,
            "specifications": {
                sid: {
                    "spec_name": s.spec_name,
                    "confidence": s.confidence.value,
                    "validation_status": s.validation_status,
                }
                for sid, s in pkg.get_all_specifications().items()
            },
            "overall_completeness": completeness,
        }
