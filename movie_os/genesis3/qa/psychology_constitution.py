"""Psychology Constitution - evaluates behavioral consistency, internal logic, motivation soundness."""

from __future__ import annotations

from typing import Any, Dict, List, Literal
from movie_os.genesis3.qa.base import BaseConstitution, ConstitutionReview, StandardCheck


class PsychologyConstitution(BaseConstitution):
    name = "psychology"
    standards = [
        "behavioral_consistency",
        "internal_logic",
        "motivation_soundness",
    ]

    _THRESHOLD_PASS = 0.7
    _THRESHOLD_CONDITIONAL = 0.4

    def review(self, evidence: Dict[str, Any]) -> ConstitutionReview:
        checked: List[StandardCheck] = []
        psy_data = evidence.get("psychology", {})

        # --- behavioral_consistency ---
        behaviors = psy_data.get("behaviors", [])
        expected_patterns = psy_data.get("expected_behavior_patterns", [])
        violations = psy_data.get("behavioral_violations", [])

        violation_penalty = min(len(violations) * 0.3, 0.6)
        pattern_match = len([b for b in behaviors if any(
            ep.lower() in str(b).lower() for ep in expected_patterns
        )]) / max(len(expected_patterns), 1) if expected_patterns else 0.5

        behavior_score_val = max((pattern_match * (1 - violation_penalty)), 0.0)
        checked.append(StandardCheck(
            standard_name="behavioral_consistency",
            status=self._s(behavior_score_val), score=round(behavior_score_val, 4),
            evidence_used=[str(f"behaviors={len(behaviors)}"), str(f"violations={len(violations)}")],
            reasoning="Behavior must align with established psychological patterns and not contradict itself.",
            failure_reasons=[] if behavior_score_val >= self._THRESHOLD_PASS else [
                f"{len(violations)} behavioral violation(s) detected"
            ],
        ))

        # --- internal_logic ---
        contradictions = psy_data.get("psychological_contradictions", [])
        decision_chain_consistent = bool(psy_data.get("decision_chains_validated"))
        trauma_responses_consistent = bool(psy_data.get("trauma_responses_aligned"))

        logic_score_val = (1.0 - min(len(contradictions) * 0.35, 1.0)) * 0.4 + \
                          (0.3 if decision_chain_consistent else 0.0) + \
                          (0.3 if trauma_responses_consistent else 0.0)
        logic_score_val = max(logic_score_val, 0.0)

        checked.append(StandardCheck(
            standard_name="internal_logic",
            status=self._s(logic_score_val), score=round(logic_score_val, 4),
            evidence_used=[str(f"contradictions={len(contradictions)}")],
            reasoning="Character logic must be internally consistent — decisions follow from established beliefs.",
            failure_reasons=[] if logic_score_val >= self._THRESHOLD_PASS else [
                f"{len(contradictions)} internal contradiction(s)"
            ],
        ))

        # --- motivation_soundness ---
        motivations = psy_data.get("motivations", {})
        has_goals = len(motivations) > 0 if isinstance(motivations, dict) else False
        goals_feasible = bool(psy_data.get("goals_feasible_in_world"))
        external_pressure_present = bool(psy_data.get("external_pressures"))

        motivation_score_val = (0.4 if has_goals else 0.0) + \
                               (0.3 if goals_feasible else 0.0) + \
                               (0.3 if external_pressure_present else 0.0)

        checked.append(StandardCheck(
            standard_name="motivation_soundness",
            status=self._s(motivation_score_val), score=round(motivation_score_val, 4),
            evidence_used=[str(f"named_motivations={len(motivations) if isinstance(motivations, (dict, list)) else 0}")],
            reasoning="Motivations must be clear, feasible in-world, and grounded in character psychology.",
            failure_reasons=[] if motivation_score_val >= self._THRESHOLD_PASS else ["Motivation insufficiently established"],
        ))

        status, overall, summary, recs = self._aggregate(checked)
        return ConstitutionReview(
            constitution_name=self.name, status=status,
            standards_checked=checked, overall_score=overall,
            summary=summary, recommendations=recs,
        )

    def _s(self: "PsychologyConstitution", score: float) -> Literal["PASS", "FAIL", "CONDITIONAL"]:
        if score >= self._THRESHOLD_PASS:
            return "PASS"
        if score >= self._THRESHOLD_CONDITIONAL:
            return "CONDITIONAL"
        return "FAIL"
