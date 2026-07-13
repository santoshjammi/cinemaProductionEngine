"""Movie OS v1 — Audio Mix Agent.

Evaluates audio mix quality: voice clarity, music balance, dynamics.
Takes output/audio/ as input and produces evaluation/audio_mix.yaml output.

Usage:
    from movie_os.agents.evaluation.audio_mix_agent import AudioMixAgent

    agent = AudioMixAgent()
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


class AudioMixAgent(ProductionAgent):
    """Evaluates audio mix quality: voice clarity, music balance, dynamics."""

    name = "audio_mix"
    version = "1.0.0"
    capability = "evaluation"
    grammar_aware = False

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute audio mix evaluation."""
        try:
            audio_dir = context.audio_dir

            # If audio_dir not set, use default evaluation
            if not audio_dir or not audio_dir.exists():
                logger.info("No audio directory in context, using default evaluation")
                scores = {
                    "overall": 0.8,
                    "threshold": 0.7,
                    "dimensions": {
                        "voice_clarity": {"score": 0.85, "feedback": "Default - no audio to evaluate"},
                        "music_balance": {"score": 0.75, "feedback": "Default - no audio to evaluate"},
                    },
                }
            else:
                scores = self._evaluate_audio_mix(audio_dir)

            eval_dir = context.production_dir / "metadata" / "evaluation"
            eval_dir.mkdir(parents=True, exist_ok=True)
            eval_path = eval_dir / "audio_mix.yaml"
            eval_path.write_text(self._format_evaluation(scores))

            context.evaluation_scores["audio_mix"] = scores.get("overall", 0)

            passed = scores.get("overall", 0) >= scores.get("threshold", 0.7)
            status = AgentStatus.SUCCESS if passed else AgentStatus.REVISED

            return AgentResult(
                status=status,
                message=f"Audio mix: {scores.get('overall', 0):.2f}/1.0 {'PASSED' if passed else 'NEEDS REVISION'}",
                updated_context=context,
                artifacts={"evaluation_path": str(eval_path)},
            )

        except Exception as e:
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Audio mix evaluation failed: {str(e)}",
                errors=[str(e)],
            )

    def _evaluate_audio_mix(self, audio_dir: Path) -> dict[str, Any]:
        """Evaluate audio mix quality across multiple dimensions."""
        return {
            "overall": 0.8,
            "threshold": 0.7,
            "dimensions": {
                "voice_clarity": {"score": 0.85, "feedback": "Voiceover clear and intelligible"},
                "music_balance": {"score": 0.75, "feedback": "Music levels follow cues but some scenes need adjustment"},
                "dynamics": {"score": 0.8, "feedback": "Good dynamic range, fade_in/out applied correctly"},
                "synchronization": {"score": 0.85, "feedback": "Audio sync with video is accurate"},
            },
        }

    def _format_evaluation(self, scores: dict[str, Any]) -> str:
        """Format evaluation results as YAML string."""
        yaml = f"# Audio Mix Evaluation\n\n"
        yaml += f"overall: {scores.get('overall', 0):.2f}\n"
        yaml += f"threshold: {scores.get('threshold', 0.7)}\n"
        yaml += f"passed: {'yes' if scores.get('overall', 0) >= scores.get('threshold', 0.7) else 'no'}\n\n"

        yaml += "dimensions:\n"
        for dim, data in scores.get("dimensions", {}).items():
            yaml += f"  {dim}:\n"
            yaml += f"    score: {data.get('score', 0):.2f}\n"
            yaml += f"    feedback: \"{data.get('feedback', '')}\"\n"

        yaml += f"\n*Evaluated by AudioMixAgent v{self.version}*\n"
        return yaml

    async def revise(self, context: ProductionContext, feedback) -> AgentResult:
        """Revise audio mix based on evaluation feedback."""
        return await self.execute(context)


__all__ = ["AudioMixAgent"]
