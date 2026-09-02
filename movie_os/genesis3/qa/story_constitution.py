"""Story Constitution - evaluates premise satisfaction, plot integrity, climax quality, theme reinforcement."""

from __future__ import annotations

from typing import Any, Dict, List
from movie_os.genesis3.qa.base import BaseConstitution, ConstitutionReview, StandardCheck


class StoryConstitution(BaseConstitution):
    name = "story"
    standards = [
        "premise_satisfaction",
        "plot_integrity",
        "climax_quality",
        "theme_reinforcement",
    ]

    _THRESHOLD_PASS = 0.7
    _THRESHOLD_CONDITIONAL = 0.4

    def review(self, evidence: Dict[str, Any]) -> ConstitutionReview:
        checked: List[StandardCheck] = []
        story_data = evidence.get("story", {})

        # --- premise_satisfaction ---
        logline_match = self._matches_logline(story_data)
        goal_defined = bool(story_data.get("goal") or story_data.get("protagonist_desire"))
        conflict_present = bool(story_data.get("conflict") or story_data.get("obstacles"))

        premises_score = (1.0 if logline_match else 0.0) * 0.4 + \
                         (1.0 if goal_defined else 0.0) * 0.3 + \
                         (1.0 if conflict_present else 0.0) * 0.3
        premise_score_val = max(premises_score, self._THRESHOLD_CONDITIONAL)
        checked.append(
            StandardCheck(
                standard_name="premise_satisfaction",
                status=self._s(premise_score_val),
                score=round(premise_score_val, 4),
                evidence_used=[] if logline_match and goal_defined and conflict_present else [
                    "logline_match" if logline_match else "no_logline_match",
                    "goal_defined" if goal_defined else "goal_undefined",
                    "conflict_present" if conflict_present else "conflict_missing",
                ],
                reasoning="Premise is satisfied when the core promise is kept, protagonist goal is explicitly stated, and central conflict exists.",
                failure_reasons=[] if premise_score_val >= self._THRESHOLD_PASS else [
                    "Premise score (" + f"{premises_score:.2f}" + ") below PASS threshold",
                ],
            )
        )

        # --- plot_integrity ---
        causality = story_data.get("causality_map") or []
        foreshadowing = bool(story_data.get("foreshadowing"))
        plot_holes = len(story_data.get("plot_holes", []))
        causal_score = 0.3 if causality else 0.0
        forescore_val = 0.25 if foreshadowing else 0.0
        hole_penalty = min(plot_holes * 0.15, 0.6)
        plot_score = (causal_score + forescore_val - hole_penalty) if (causal_score + forescore_val - hole_penalty) > 0 else 0.0
        if not causality and not foreshadowing:
            plot_score = max(0.0, plot_score - 0.5)
        checked.append(
            StandardCheck(
                standard_name="plot_integrity",
                status=self._s(plot_score),
                score=round(plot_score, 4),
                evidence_used=[str(f"causal_links={len(causality)}"), "foreshadowing_present" if foreshadowing else "no_foreshadowing"],
                reasoning="Plot integrity requires causal chains (A causes B) and setup/payoff.",
                failure_reasons=[] if plot_score >= self._THRESHOLD_PASS else ["Score (" + f"{plot_score:.2f}" + ") below threshold"],
            )
        )

        # --- climax_quality ---
        climax_evidence = evidence.get("story_climax", {})
        has_climax = bool(story_data.get("climax") or climax_evidence.get("has_climax"))
        stakes_present = False
        if "stakes" in story_data:
            stakes_present = bool(story_data["stakes"])
        resolution_clear = bool(story_data.get("resolution") or climax_evidence.get("clear_resolution"))

        climax_score = (1.0 if has_climax else 0.0) * 0.4 + \
                       (1.0 if stakes_present else 0.0) * 0.3 + \
                       (1.0 if resolution_clear else 0.0) * 0.3

        evidence_climax = [
            "has_climax" if has_climax else "no_climax_detected",
            "stakes_present" if stakes_present else "stakes_undefined",
            "resolution_clear" if resolution_clear else "vague_resolution",
        ]
        checked.append(
            StandardCheck(
                standard_name="climax_quality",
                status=self._s(climax_score),
                score=round(climax_score, 4),
                evidence_used=evidence_climax,
                reasoning="A quality climax needs the dramatic peak, stakes that matter, and a clear resolution.",
                failure_reasons=[] if climax_score >= self._THRESHOLD_PASS else ["Score (" + f"{climax_score:.2f}" + ") below threshold"],
            )
        )

        # --- theme_reinforcement ---
        themes = story_data.get("themes", [])
        recurrent_motifs = bool(story_data.get("motifs") or story_data.get("recurring_symbols"))
        ending_resonates = bool(story_data.get("ending_theme_match"))

        thematic_score = (0.4 if len(themes) >= 1 else 0.0) + \
                         (0.3 if recurrent_motifs else 0.0) + \
                         (0.3 if ending_resonates else 0.0)

        checked.append(
            StandardCheck(
                standard_name="theme_reinforcement",
                status=self._s(thematic_score),
                score=round(thematic_score, 4),
                evidence_used=[f"themes={themes}", "motifs_present" if recurrent_motifs else "no_motifs"],
                reasoning="Theme must recur throughout the story, not just appear in dialogue.",
                failure_reasons=[] if thematic_score >= self._THRESHOLD_PASS else ["Score (" + f"{thematic_score:.2f}" + ") below threshold"],
            )
        )

        status, overall, summary, recs = self._aggregate(checked)
        return ConstitutionReview(
            constitution_name=self.name,
            status=status,
            standards_checked=checked,
            overall_score=overall,
            summary=summary,
            recommendations=recs,
        )

    def _s(self: "StoryConstitution", score: float) -> Literal["PASS", "FAIL", "CONDITIONAL"]:
        if score >= self._THRESHOLD_PASS:
            return "PASS"
        if score >= self._THRESHOLD_CONDITIONAL:
            return "CONDITIONAL"
        return "FAIL"

    @staticmethod
    def _matches_logline(story_data: dict) -> bool:
        premise = story_data.get("premise", "")
        event_summary = story_data.get("event_summary", "")
        if not premise or not event_summary:
            return False
        premise_words = set(premise.lower().split())
        event_words = set(event_summary.lower().split())
        return len(premise_words & event_words) >= 3
