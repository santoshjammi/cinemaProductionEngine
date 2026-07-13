"""Movie OS v1 — Production Orchestrator Agent.

Coordinates all agents, manages pipeline state from DNA to final video.
Takes dna.yaml + creative_brief.md as input and orchestrates the full production pipeline.

Usage:
    from movie_os.agents.orchestration.production_orchestrator_agent import ProductionOrchestratorAgent

    agent = ProductionOrchestratorAgent()
    result = await agent.execute(context)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from movie_os.capabilities.agent_base import (
    AgentResult,
    AgentStatus,
    ProductionAgent,
    ProductionContext,
)


class ProductionOrchestratorAgent(ProductionAgent):
    """Coordinates all agents, manages pipeline state.

    This is the main orchestrator that runs the full production pipeline:
        1. Research → Story Architecture → Psychology Review
        2. Screenplay Writing → Dialogue Refinement
        3. Scene Planning → Shot Planning → Prompt Building → Music Composition
        4. Character Management → Environment Management
        5. Image Generation → Voice Generation → Music Generation
        6. Audio Mixing → Video Composition → Subtitle Generation
        7. Evaluation (all 7 agents)
        8. YouTube Readiness Check

    If any evaluation fails, the RevisionAgent is triggered for revision.
    """

    name = "production_orchestrator"
    version = "1.0.0"
    capability = "orchestration"
    grammar_aware = True

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute the full production pipeline."""
        try:
            # Import all agents
            from movie_os.agents.creative import (
                ResearchAgent,
                StoryArchitectAgent,
                PsychologyReviewerAgent,
                ScreenplayWriterAgent,
                DialogueWriterAgent,
            )
            from movie_os.agents.planning import (
                ScenePlannerAgent,
                ShotPlannerAgent,
                PromptBuilderAgent,
                MusicComposerAgent,
            )
            from movie_os.agents.generation import (
                CharacterManagerAgent,
                EnvironmentManagerAgent,
                ImageGeneratorAgent,
                VoiceGeneratorAgent,
                MusicGeneratorAgent,
            )
            from movie_os.agents.post_production import (
                AudioMixingAgent,
                VideoComposerAgent,
                SubtitleAgent,
            )
            from movie_os.agents.evaluation import (
                StoryQualityAgent,
                DialogueQualityAgent,
                VisualConsistencyAgent,
                AudioMixAgent,
                EmotionScoreAgent,
                CharacterConsistencyAgent,
                YouTubeReadinessAgent,
            )

            # Phase 1: Creative (Research → Story → Review)
            context.phase = "creative"
            await self._run_phase(context, [
                ("research", ResearchAgent()),
                ("story", StoryArchitectAgent()),
                ("psychology_review", PsychologyReviewerAgent()),
            ])

            # Phase 2: Writing (Screenplay → Dialogue)
            context.phase = "writing"
            await self._run_phase(context, [
                ("screenplay", ScreenplayWriterAgent()),
                ("dialogue", DialogueWriterAgent()),
            ])

            # Phase 3: Planning (Scene → Shot → Prompt → Music)
            context.phase = "planning"
            await self._run_phase(context, [
                ("scene_plan", ScenePlannerAgent()),
                ("shot_plan", ShotPlannerAgent()),
                ("prompts", PromptBuilderAgent()),
                ("music_score", MusicComposerAgent()),
            ])

            # Phase 4: Generation Prep (Characters → Environments)
            context.phase = "generation_prep"
            await self._run_phase(context, [
                ("characters", CharacterManagerAgent()),
                ("environments", EnvironmentManagerAgent()),
            ])

            # Phase 5: Generation (Images → Voice → Music)
            context.phase = "generation"
            await self._run_phase(context, [
                ("images", ImageGeneratorAgent()),
                ("voice", VoiceGeneratorAgent()),
                ("music", MusicGeneratorAgent()),
            ])

            # Phase 6: Post-Production (Audio → Video → Subtitles)
            context.phase = "post_production"
            await self._run_phase(context, [
                ("audio_mix", AudioMixingAgent()),
                ("video_compose", VideoComposerAgent()),
                ("subtitles", SubtitleAgent()),
            ])

            # Phase 7: Evaluation (All 7 agents)
            context.phase = "evaluation"
            eval_results = await self._run_evaluation(context, [
                ("story_quality", StoryQualityAgent()),
                ("dialogue_quality", DialogueQualityAgent()),
                ("visual_consistency", VisualConsistencyAgent()),
                ("audio_mix", AudioMixAgent()),
                ("emotion_score", EmotionScoreAgent()),
                ("character_consistency", CharacterConsistencyAgent()),
            ])

            # Phase 8: YouTube Readiness
            youtube_agent = YouTubeReadinessAgent()
            youtube_result = await youtube_agent.execute(context)
            eval_results["youtube_readiness"] = youtube_result

            # Determine final status
            all_passed = all(
                r.status == AgentStatus.SUCCESS
                for r in eval_results.values()
            )

            if all_passed:
                return AgentResult(
                    status=AgentStatus.SUCCESS,
                    message=f"Production pipeline completed successfully for '{context.title}'",
                    updated_context=context,
                    artifacts={
                        "output_video": context.output_video,
                        "subtitles_dir": str(context.subtitles_dir) if context.subtitles_dir else None,
                        "all_evaluations_passed": True,
                    },
                )
            else:
                # Trigger revision for failed evaluations
                return AgentResult(
                    status=AgentStatus.REVISED,
                    message=f"Production pipeline completed with revisions needed for '{context.title}'",
                    updated_context=context,
                    artifacts={
                        "failed_evaluations": [k for k, v in eval_results.items() if v.status != AgentStatus.SUCCESS],
                        "all_evaluations_passed": False,
                    },
                )

        except Exception as e:
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Production orchestration failed: {str(e)}",
                errors=[str(e)],
            )

    async def _run_phase(self, context: ProductionContext, agents: list[tuple[str, Any]]) -> dict[str, AgentResult]:
        """Run a phase of agents sequentially."""
        results = {}
        for name, agent in agents:
            result = await agent.execute(context)
            results[name] = result
            if result.updated_context:
                context = result.updated_context
        return results

    async def _run_evaluation(self, context: ProductionContext, agents: list[tuple[str, Any]]) -> dict[str, AgentResult]:
        """Run evaluation agents and collect results."""
        results = {}
        for name, agent in agents:
            result = await agent.execute(context)
            results[name] = result
            if result.updated_context:
                context = result.updated_context
        return results

    async def revise(self, context: ProductionContext, feedback) -> AgentResult:
        """Revise production based on evaluation feedback."""
        # Revision would re-run failed phases
        return await self.execute(context)


__all__ = ["ProductionOrchestratorAgent"]
