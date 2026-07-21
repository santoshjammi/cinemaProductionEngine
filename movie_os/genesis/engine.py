"""Genesis Engine — top-level orchestrator.

The GenesisEngine runs the full pre-production pipeline:
1. Discovery (7 agents)
2. PKP Generation (19 agents in dependency order)
3. Review (4 reviewers + ChiefArchitect)
4. Completion Gate (certify readiness)
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from .completion_gate import PreProductionCompletionGate
from .llm_client import LLMClient, MockLLMClient
from .models import AgentResult, PKGState
from .pkg import ProductionKnowledgeGraph
from .session import SessionManager


logger = logging.getLogger("movie_os.genesis.engine")


class GenesisEngine:
    """Top-level Genesis orchestrator.

    Usage:
        engine = GenesisEngine(llm=LLMClient())
        result = engine.run(synopsis="A man withdraws from his wife...")

    For tiered model routing (HF), pass a dict of LLM clients:
        engine = GenesisEngine(llm={
            "discovery": discovery_client,
            "pkp": pkp_client,
            "reviewer": reviewer_client,
            "chief": chief_client,
        })
    """

    def __init__(
        self,
        llm: LLMClient | MockLLMClient | dict[str, LLMClient | MockLLMClient] | None = None,
        db_path: str | Path = ":memory:",
        session_db: str | Path | None = None,
    ):
        self.db_path = str(db_path)
        self.session_manager = SessionManager(session_db or db_path)
        self.gate = PreProductionCompletionGate()

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
        """Get the LLM client for a given agent tier."""
        if self._tiered_llm:
            return self._tiered_llm.get(tier, self._llm)
        return self._llm

    def run(
        self,
        synopsis: str,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run the full Genesis pipeline. Returns the complete result."""
        return asyncio.run(self.run_async(synopsis, constraints))

    async def run_async(
        self,
        synopsis: str,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run the full Genesis pipeline asynchronously."""
        # 1. Create session
        session_id = self.session_manager.create_session(synopsis, constraints)
        logger.info(f"Genesis session: {session_id}")

        # 2. Initialize PKG
        pkg = ProductionKnowledgeGraph(self.db_path)
        pkg.synopsis = synopsis
        pkg.constraints = constraints or {}
        pkg.save_state()

        # 3. Run discovery
        self.session_manager.update_stage(session_id, "discovery")
        discovery_results = await self._run_discovery(pkg)
        logger.info(f"Discovery complete: {len(discovery_results)} agents ran")

        # 4. Run PKP generation
        self.session_manager.update_stage(session_id, "pkp")
        pkp_results = await self._run_pkp_generation(pkg)
        logger.info(f"PKP generation complete: {len(pkp_results)} agents ran")

        # 5. Run reviews
        self.session_manager.update_stage(session_id, "review")
        review_results = await self._run_reviews(pkg)
        logger.info(f"Review complete: {len(review_results)} reviewers ran")

        # 6. Compute knowledge completeness from spec validation status.
        # Each phase (A-G) contributes 1/7 to overall completeness. A phase
        # is "complete" when all its specs passed validation.
        phase_passes: dict[str, list[bool]] = {}
        for spec in pkg.get_all_specifications().values():
            phase_passes.setdefault(spec.phase, []).append(
                spec.validation_status == "passed"
            )
        for phase, results in phase_passes.items():
            if results:
                pkg.set_completeness(phase, sum(results) / len(results))

        # 7. Run completion gate
        self.session_manager.update_stage(session_id, "gate")
        gate_result = self.gate.check(pkg)
        logger.info(f"Completion gate: {'PASSED' if gate_result.passed else 'FAILED'}")

        # 7. Finalize
        self.session_manager.update_stage(session_id, "complete")
        pkg.save_state()

        return {
            "session_id": session_id,
            "discovery_results": discovery_results,
            "pkp_results": pkp_results,
            "review_results": review_results,
            "gate_result": gate_result.to_dict(),
            "specifications": {
                sid: {
                    "spec_name": s.spec_name,
                    "confidence": s.confidence.value,
                    "validation_status": s.validation_status,
                }
                for sid, s in pkg.get_all_specifications().items()
            },
            "overall_completeness": pkg.get_overall_completeness(),
            "_pkg": pkg,
        }

    async def _run_discovery(self, pkg: ProductionKnowledgeGraph) -> list[AgentResult]:
        """Run all 7 discovery agents in sequence."""
        from .discovery.intent_analyst import IntentAnalyst
        from .discovery.theme_analyst import ThemeAnalyst
        from .discovery.emotion_analyst import EmotionAnalyst
        from .discovery.conflict_analyst import ConflictAnalyst
        from .discovery.audience_analyst import AudienceAnalyst
        from .discovery.gap_analyst import GapAnalyst
        from .discovery.question_planner import QuestionPlanner

        agents = [
            IntentAnalyst(self._get_llm("discovery")),
            ThemeAnalyst(self._get_llm("discovery")),
            EmotionAnalyst(self._get_llm("discovery")),
            ConflictAnalyst(self._get_llm("discovery")),
            AudienceAnalyst(self._get_llm("discovery")),
            GapAnalyst(self._get_llm("discovery")),
            QuestionPlanner(self._get_llm("discovery")),
        ]

        results = []
        for agent in agents:
            result = await agent.run(pkg)
            results.append(result)
        return results

    async def _run_pkp_generation(self, pkg: ProductionKnowledgeGraph) -> list[AgentResult]:
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

        llm = self._get_llm("pkp")
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

        results = []
        for agent in agents:
            result = await agent.run(pkg)
            results.append(result)
        return results

    async def _run_reviews(self, pkg: ProductionKnowledgeGraph) -> list[AgentResult]:
        """Run all 4 review agents + the ChiefArchitect.

        Reviewers validate cross-spec consistency. The ChiefArchitect is the
        final supervisor that reviews ALL 19 PKP specs for readiness.
        """
        from .reviewers.story_reviewer import StoryReviewer
        from .reviewers.character_reviewer import CharacterReviewer
        from .reviewers.narrative_reviewer import NarrativeReviewer
        from .reviewers.psychology_reviewer import PsychologyReviewer
        from .chief_architect import ChiefArchitect

        reviewer_llm = self._get_llm("reviewer")
        chief_llm = self._get_llm("chief")
        agents = [
            StoryReviewer(reviewer_llm),
            CharacterReviewer(reviewer_llm),
            NarrativeReviewer(reviewer_llm),
            PsychologyReviewer(reviewer_llm),
            ChiefArchitect(chief_llm),
        ]

        results = []
        for agent in agents:
            result = await agent.run(pkg)
            results.append(result)
        return results