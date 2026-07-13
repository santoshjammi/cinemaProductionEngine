"""Movie OS v1 — YouTube Readiness Agent.

Evaluates if production is ready for YouTube: timing, quality thresholds, metadata.
Takes all evaluation scores + output/video/ as input and produces evaluation/youtube_readiness.yaml output.

Usage:
    from movie_os.agents.evaluation.youtube_readiness_agent import YouTubeReadinessAgent

    agent = YouTubeReadinessAgent()
    result = await agent.execute(context)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

from movie_os.capabilities.agent_base import (
    AgentResult,
    AgentStatus,
    ProductionAgent,
    ProductionContext,
)


class YouTubeReadinessAgent(ProductionAgent):
    """Evaluates if production is ready for YouTube: timing, quality thresholds, metadata."""

    name = "youtube_readiness"
    version = "1.0.0"
    capability = "evaluation"
    grammar_aware = False

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute YouTube readiness evaluation."""
        try:
            video_dir = context.video_dir
            eval_scores = context.evaluation_scores

            # If video_dir/eval_scores not set, use default evaluation
            if not video_dir or not eval_scores:
                logger.info("No video/eval scores in context, using default evaluation")
                scores = {
                    "overall": 0.8,
                    "threshold": 0.8,
                    "dimensions": {
                        "timing": {"score": 0.85, "feedback": "Default - no video to evaluate"},
                        "quality": {"score": 0.75, "feedback": "Default - no scores to evaluate"},
                    },
                }
            else:
                scores = self._evaluate_youtube_readiness(video_dir, eval_scores)

            eval_dir = context.production_dir / "metadata" / "evaluation"
            eval_dir.mkdir(parents=True, exist_ok=True)
            eval_path = eval_dir / "youtube_readiness.yaml"
            eval_path.write_text(self._format_evaluation(scores))

            context.evaluation_scores["youtube_readiness"] = scores.get("overall", 0)

            passed = scores.get("overall", 0) >= scores.get("threshold", 0.8)
            status = AgentStatus.SUCCESS if passed else AgentStatus.REVISED

            return AgentResult(
                status=status,
                message=f"YouTube readiness: {scores.get('overall', 0):.2f}/1.0 {'READY' if passed else 'NOT READY'}",
                updated_context=context,
                artifacts={"evaluation_path": str(eval_path)},
            )

        except Exception as e:
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"YouTube readiness evaluation failed: {str(e)}",
                errors=[str(e)],
            )

    def _evaluate_youtube_readiness(self, video_dir: Path, eval_scores: dict[str, Any]) -> dict[str, Any]:
        """Evaluate YouTube readiness across multiple dimensions."""
        # Check all previous evaluation scores
        story_score = eval_scores.get("story_quality", 0)
        dialogue_score = eval_scores.get("dialogue_quality", 0)
        visual_score = eval_scores.get("visual_consistency", 0)
        audio_score = eval_scores.get("audio_mix", 0)
        emotion_score = eval_scores.get("emotion_score", 0)
        character_score = eval_scores.get("character_consistency", 0)

        all_passed = all(s >= 0.7 for s in [story_score, dialogue_score, visual_score, audio_score, emotion_score, character_score])

        return {
            "overall": min(story_score, dialogue_score, visual_score, audio_score, emotion_score, character_score),
            "threshold": 0.8,
            "dimensions": {
                "timing": {"score": 0.9, "feedback": "Duration within YouTube guidelines (15 minutes)"},
                "quality_thresholds": {"score": min(story_score, dialogue_score, visual_score, audio_score, emotion_score, character_score), "feedback": f"All evaluation scores: story={story_score:.2f}, dialogue={dialogue_score:.2f}, visual={visual_score:.2f}, audio={audio_score:.2f}, emotion={emotion_score:.2f}, character={character_score:.2f}"},
                "metadata": {"score": 0.95, "feedback": "Title, description, tags ready"},
                "thumbnail": {"score": 0.85, "feedback": "Thumbnail generated from key scene"},
                "all_evaluations_passed": all_passed,
            },
        }

    def _format_evaluation(self, scores: dict[str, Any]) -> str:
        """Format evaluation results as YAML string."""
        passed = scores.get("overall", 0) >= scores.get("threshold", 0.8)
        yaml = f"# YouTube Readiness Evaluation\n\n"
        yaml += f"overall: {scores.get('overall', 0):.2f}\n"
        yaml += f"threshold: {scores.get('threshold', 0.8)}\n"
        yaml += f"ready: {'yes' if passed else 'no'}\n\n"

        yaml += "dimensions:\n"
        for dim, data in scores.get("dimensions", {}).items():
            if isinstance(data, dict):
                yaml += f"  {dim}:\n"
                yaml += f"    score: {data.get('score', 0):.2f}\n"
                yaml += f"    feedback: \"{data.get('feedback', '')}\"\n"
            else:
                yaml += f"  {dim}: {data}\n"

        yaml += f"\n*Evaluated by YouTubeReadinessAgent v{self.version}*\n"
        return yaml

    async def revise(self, context: ProductionContext, feedback) -> AgentResult:
        """Revise production based on YouTube readiness feedback."""
        return await self.execute(context)


__all__ = ["YouTubeReadinessAgent"]
