"""Story Standards — plot integrity, premise satisfaction, climax quality."""
from __future__ import annotations
from typing import Any
from .base import Standard, QualityCriterion, ValidationRule, StandardResult


class StoryStandard(Standard):
    name = "story"
    purpose = "Ensure the story has a coherent plot, satisfying premise, and quality climax."
    principles = [
        "Every story must have a clear premise that is satisfied by the ending.",
        "Plot events must follow a logical cause-effect chain.",
        "The climax must be the highest point of dramatic tension.",
        "Theme must be reinforced throughout, not just stated.",
    ]
    criteria = [
        QualityCriterion(name="premise_satisfaction", description="The core promise of the story is kept", weight=0.3),
        QualityCriterion(name="plot_integrity", description="Cause-effect chain is valid and complete", weight=0.3),
        QualityCriterion(name="climax_quality", description="Climax is earned and dramatically satisfying", weight=0.2),
        QualityCriterion(name="theme_reinforcement", description="Theme recurs and is reinforced by the ending", weight=0.2),
    ]
    validation_rules = [
        ValidationRule(rule_id="story-001", description="Premise must be stated and resolved", evaluator="check_premise_resolution", severity="critical"),
        ValidationRule(rule_id="story-002", description="Plot must have no unresolved threads", evaluator="check_plot_completeness", severity="major"),
    ]
    failure_conditions = [
        "Premise is not satisfied by the ending",
        "Major plot holes exist",
        "Climax does not resolve the central conflict",
        "Theme is absent or contradicted",
    ]
    required_evidence = [
        "Premise statement",
        "Plot outline with cause-effect chain",
        "Climax scene description",
        "Theme analysis",
    ]
    certification_threshold = 0.7

    def evaluate(self, evidence: dict[str, Any]) -> StandardResult:
        story_data = evidence.get("story", {})
        premise_ok = bool(story_data.get("premise")) and bool(story_data.get("premise_resolved"))
        plot_ok = bool(story_data.get("plot_outline")) and len(story_data.get("plot_holes", [])) == 0
        climax_ok = bool(story_data.get("climax"))
        theme_ok = bool(story_data.get("theme")) and bool(story_data.get("theme_reinforced"))
        scores = [
            (self._score_from_bool(premise_ok), 0.3),
            (self._score_from_bool(plot_ok), 0.3),
            (self._score_from_bool(climax_ok), 0.2),
            (self._score_from_bool(theme_ok), 0.2),
        ]
        score = self._weighted_score(scores)
        failures = []
        if not premise_ok: failures.append("Premise not satisfied")
        if not plot_ok: failures.append("Plot integrity issues")
        if not climax_ok: failures.append("Climax missing or weak")
        if not theme_ok: failures.append("Theme not reinforced")
        return StandardResult(
            standard_name=self.name,
            passed=score >= self.certification_threshold,
            score=round(score, 4),
            evidence=[f"premise={premise_ok}", f"plot={plot_ok}", f"climax={climax_ok}", f"theme={theme_ok}"],
            failures=failures,
            details=f"Story evaluation: {len(failures)} failure(s) out of 4 criteria",
        )
