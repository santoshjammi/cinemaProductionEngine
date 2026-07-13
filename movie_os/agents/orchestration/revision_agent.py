"""Movie OS v1 — Revision Agent.

Auto-revises low-scoring elements based on evaluation feedback.
Triggers when any evaluation score falls below threshold.

Usage:
    from movie_os.agents.orchestration.revision_agent import RevisionAgent

    agent = RevisionAgent()
    result = await agent.execute(context, failed_categories)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from movie_os.capabilities.agent_base import (
    AgentResult,
    AgentStatus,
    ProductionAgent,
    ProductionContext,
    EvaluationFeedback,
)


class RevisionAgent(ProductionAgent):
    """Auto-revises low-scoring elements based on evaluation feedback.

    This agent is triggered when any evaluation score falls below threshold.
    It determines which phase to re-run based on the failed category and
    executes revision logic for that phase.

    Revision Rules:
        - story_quality < 0.7 → Re-run StoryArchitectAgent + ScreenplayWriterAgent
        - dialogue_quality < 0.7 → Re-run DialogueWriterAgent
        - visual_consistency < 0.7 → Regenerate images with updated prompts
        - audio_mix < 0.7 → Re-mix audio with adjusted levels
        - emotion_score < 0.7 → Revise screenplay emotional beats
        - character_consistency < 0.7 → Update character definitions
    """

    name = "revision"
    version = "1.0.0"
    capability = "orchestration"
    grammar_aware = True

    async def execute(self, context: ProductionContext, failed_categories: list[str] | None = None) -> AgentResult:
        """Execute revision for failed evaluation categories.

        Args:
            context: Production context with evaluation scores loaded.
            failed_categories: List of failed evaluation category names.

        Returns:
            AgentResult with revised artifacts.
        """
        try:
            if not failed_categories:
                # Auto-detect failed categories from context
                failed_categories = context.get_failed_categories()

            if not failed_categories:
                return AgentResult(
                    status=AgentStatus.SUCCESS,
                    message="No revisions needed",
                    updated_context=context,
                )

            revision_results = {}
            for category in failed_categories:
                result = await self._revise_category(context, category)
                revision_results[category] = result
                if result.updated_context:
                    context = result.updated_context

            # Check if revisions passed
            all_passed = all(
                r.status == AgentStatus.SUCCESS
                for r in revision_results.values()
            )

            status = AgentStatus.SUCCESS if all_passed else AgentStatus.REVISED

            return AgentResult(
                status=status,
                message=f"Revision completed: {sum(1 for r in revision_results.values() if r.status == AgentStatus.SUCCESS)}/{len(revision_results)} categories fixed",
                updated_context=context,
                artifacts={"revision_results": revision_results},
            )

        except Exception as e:
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Revision failed: {str(e)}",
                errors=[str(e)],
            )

    async def _revise_category(self, context: ProductionContext, category: str) -> AgentResult:
        """Revise a specific evaluation category."""
        # Import agents for revision
        from movie_os.agents.creative import StoryArchitectAgent, ScreenplayWriterAgent, DialogueWriterAgent
        from movie_os.agents.generation import ImageGeneratorAgent

        if category == "story_quality":
            # Re-run story architecture and screenplay writing
            story_agent = StoryArchitectAgent()
            story_result = await story_agent.execute(context)

            screenplay_agent = ScreenplayWriterAgent()
            screenplay_result = await screenplay_agent.execute(story_result.updated_context or context)

            return AgentResult(
                status=story_result.status and screenplay_result.status,
                message=f"Story revision: {'PASSED' if story_result.status == AgentStatus.SUCCESS else 'FAILED'}",
                updated_context=screenplay_result.updated_context or story_result.updated_context or context,
            )

        elif category == "dialogue_quality":
            # Re-run dialogue refinement
            dialogue_agent = DialogueWriterAgent()
            result = await dialogue_agent.execute(context)
            return result

        elif category == "visual_consistency":
            # Regenerate images with updated prompts
            image_agent = ImageGeneratorAgent()
            result = await image_agent.execute(context)
            return result

        elif category == "emotion_score":
            # Revise screenplay emotional beats (re-run story + screenplay)
            story_agent = StoryArchitectAgent()
            story_result = await story_agent.execute(context)

            screenplay_agent = ScreenplayWriterAgent()
            screenplay_result = await screenplay_agent.execute(story_result.updated_context or context)

            return AgentResult(
                status=story_result.status and screenplay_result.status,
                message=f"Emotion revision: {'PASSED' if story_result.status == AgentStatus.SUCCESS else 'FAILED'}",
                updated_context=screenplay_result.updated_context or story_result.updated_context or context,
            )

        elif category == "character_consistency":
            # Update character definitions and regenerate images
            from movie_os.agents.generation import CharacterManagerAgent
            char_agent = CharacterManagerAgent()
            char_result = await char_agent.execute(context)

            image_agent = ImageGeneratorAgent()
            image_result = await image_agent.execute(char_result.updated_context or context)

            return AgentResult(
                status=char_result.status and image_result.status,
                message=f"Character revision: {'PASSED' if char_result.status == AgentStatus.SUCCESS else 'FAILED'}",
                updated_context=image_result.updated_context or char_result.updated_context or context,
            )

        elif category == "audio_mix":
            # Re-mix audio with adjusted levels
            from movie_os.agents.post_production import AudioMixingAgent
            audio_agent = AudioMixingAgent()
            result = await audio_agent.execute(context)
            return result

        else:
            # Unknown category — return revised status
            return AgentResult(
                status=AgentStatus.REVISED,
                message=f"Unknown revision category: {category}",
                updated_context=context,
            )

    async def revise(self, context: ProductionContext, feedback: EvaluationFeedback) -> AgentResult:
        """Revise based on specific evaluation feedback."""
        return await self.execute(context, [feedback.category])


__all__ = ["RevisionAgent"]
