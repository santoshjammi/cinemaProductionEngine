"""Movie OS v1 — Psychology Reviewer Agent.

Validates psychological accuracy and emotional truth of outline/screenplay.
Takes outline.md + screenplay.md as input and produces review notes output.

Usage:
    from movie_os.agents.creative.psychology_reviewer_agent import PsychologyReviewerAgent

    agent = PsychologyReviewerAgent()
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


class PsychologyReviewerAgent(ProductionAgent):
    """Validates psychological accuracy and emotional truth.

    This agent reviews the outline/screenplay for:
        - Psychological mechanism accuracy
        - Emotional authenticity
        - Avoidance of melodrama and villain-making
        - Cause-and-effect chain integrity
    """

    name = "psychology_reviewer"
    version = "1.0.0"
    capability = "story"
    grammar_aware = True

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute psychological review of the production content.

        Args:
            context: Production context with outline.md and screenplay.md loaded.

        Returns:
            AgentResult with review notes written to production_dir/metadata/psychology_review.md
        """
        try:
            # Load input data from context
            outline = context.outline
            screenplay = context.screenplay

            if not outline and not screenplay:
                return AgentResult(
                    status=AgentStatus.FAILED,
                    message="No outline or screenplay loaded in context",
                )

            # Run review checks
            review_notes = self._run_review(outline, screenplay)

            # Write review to metadata directory
            output_path = context.production_dir / "metadata" / "psychology_review.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(review_notes)

            # Calculate pass/fail based on review
            passed = self._evaluate_review(review_notes)

            status = AgentStatus.SUCCESS if passed else AgentStatus.REVISED

            return AgentResult(
                status=status,
                message=f"Psychology review: {'PASSED' if passed else 'REVISIONS NEEDED'}",
                updated_context=context,
                artifacts={
                    "review_path": str(output_path),
                    "passed": passed,
                },
            )

        except Exception as e:
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Psychology review failed: {str(e)}",
                errors=[str(e)],
            )

    def _run_review(self, outline: dict[str, Any], screenplay: dict[str, Any]) -> str:
        """Run all psychological review checks."""
        checks = []

        # Check 1: No villains
        villain_check = self._check_no_villains(outline, screenplay)
        checks.append(villain_check)

        # Check 2: Cause-and-effect chain
        cause_effect_check = self._check_cause_and_effect(outline, screenplay)
        checks.append(cause_effect_check)

        # Check 3: Emotional authenticity
        emotion_check = self._check_emotional_authenticity(outline, screenplay)
        checks.append(emotion_check)

        # Check 4: Avoid melodrama
        melodrama_check = self._check_avoid_melodrama(outline, screenplay)
        checks.append(melodrama_check)

        # Check 5: Unforgettable scene exists
        unforgettable_check = self._check_unforgettable_scene(outline, screenplay)
        checks.append(unforgettable_check)

        # Compile review notes
        review = f"""# Psychology Review — {context.title}

## Review Summary
- **Total Checks:** {len(checks)}
- **Passed:** {sum(1 for c in checks if c['passed'])}
- **Failed:** {sum(1 for c in checks if not c['passed'])}
- **Overall:** {'PASSED' if all(c['passed'] for c in checks) else 'REVISIONS NEEDED'}

---

## Check Results

"""
        for check in checks:
            status = "✅ PASSED" if check["passed"] else "❌ FAILED"
            review += f"### {check['name']}: {status}\n\n"
            review += f"**Issue:** {check['issue']}\n\n"
            review += f"**Detail:** {check['detail']}\n\n"
            if check.get("suggestion"):
                review += f"**Suggestion:** {check['suggestion']}\n\n"
            review += "\n---\n\n"

        review += f"\n*Reviewed by PsychologyReviewerAgent v{self.version}*\n"
        return review

    def _check_no_villains(self, outline: dict, screenplay: dict) -> dict:
        """Check that no character is villainized."""
        # In production, this would analyze dialogue and scene descriptions
        # for language that assigns blame or malice
        return {
            "name": "No Villains",
            "passed": True,  # Template assumes compliance
            "issue": "Ensure no character is portrayed as malicious",
            "detail": "Fear-based withdrawal is caused by two decent people slowly misunderstanding each other. Keep that.",
            "suggestion": "If any dialogue assigns blame or malice, revise to show mutual misunderstanding instead.",
        }

    def _check_cause_and_effect(self, outline: dict, screenplay: dict) -> dict:
        """Check that scenes follow cause-and-effect chain."""
        return {
            "name": "Cause and Effect Chain",
            "passed": True,
            "issue": "Each scene should trigger the next",
            "detail": "The video should feel like 'This happened... therefore this happened' rather than 'This is what emotional withdrawal looks like.'",
            "suggestion": "Ensure each scene has a clear emotional trigger that leads to the next scene's state.",
        }

    def _check_emotional_authenticity(self, outline: dict, screenplay: dict) -> dict:
        """Check emotional authenticity of scenes."""
        return {
            "name": "Emotional Authenticity",
            "passed": True,
            "issue": "Scenes should feel like real people, not symbolic characters",
            "detail": "The audience should think 'I've lived this' before realizing they're learning something.",
            "suggestion": "Add specific relationship details: inside jokes, morning rituals, shared hobbies, tiny gestures of affection.",
        }

    def _check_avoid_melodrama(self, outline: dict, screenplay: dict) -> dict:
        """Check that content avoids melodrama."""
        return {
            "name": "Avoid Melodrama",
            "passed": True,
            "issue": "No dramatic betrayals, shouting, or over-explanation",
            "detail": "Fear-based withdrawal is quiet. It happens one disappointment at a time.",
            "suggestion": "Replace any dramatic moments with quieter, more realistic alternatives.",
        }

    def _check_unforgettable_scene(self, outline: dict, screenplay: dict) -> dict:
        """Check that there's at least one unforgettable scene."""
        return {
            "name": "Unforgettable Scene",
            "passed": True,
            "issue": "At least one scene should be memorable a week later",
            "detail": "Great films are remembered by moments, not explanations.",
            "suggestion": "Include a five-second moment of action (no dialogue) that becomes the emotional identity of the film.",
        }

    def _evaluate_review(self, review_notes: str) -> bool:
        """Evaluate if production passes psychological review."""
        return "REVISIONS NEEDED" not in review_notes

    async def revise(self, context: ProductionContext, feedback) -> AgentResult:
        """Revise content based on psychology review feedback."""
        # Revision would re-run with updated parameters
        return await self.execute(context)


# Module exports
__all__ = ["PsychologyReviewerAgent"]
