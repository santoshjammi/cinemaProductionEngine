"""Cinema Constitution - evaluates pacing, structure, scene value, dramatic tension."""

from __future__ import annotations

from typing import Any, Dict, List, Literal
from movie_os.genesis3.qa.base import BaseConstitution, ConstitutionReview, StandardCheck


class CinemaConstitution(BaseConstitution):
    name = "cinema"
    standards = [
        "pacing",
        "structure",
        "scene_value",
        "dramatic_tension",
    ]

    _THRESHOLD_PASS = 0.7
    _THRESHOLD_CONDITIONAL = 0.4

    def review(self, evidence: Dict[str, Any]) -> ConstitutionReview:
        checked: List[StandardCheck] = []
        cin_data = evidence.get("cinema", {})

        # --- pacing ---
        acts_count = len(cin_data.get("acts", [])) if isinstance(cin_data.get("acts"), (list, dict)) else 3
        act_details = cin_data.get("act_breakdowns") or {}
        scene_counts: List[int] = []
        for a_key in act_details:
            val = act_details[a_key] if isinstance(act_details, dict) else None
            if isinstance(val, list):
                scene_counts.append(len(val))

        avg_scenes_per_act = sum(scene_counts) / max(len(scene_counts), 1) if scene_counts else acts_count
        pacing_varied = bool(cin_data.get("pacing_variance_assessed") or cin_data.get("rhythm_changes"))
        no_boring = not bool(cin_data.get("boring_sections"))

        pacing_score_val = min(avg_scenes_per_act / max(acts_count + 2, 1), 1.0) * 0.4 + \
                           (0.35 if pacing_varied else 0.0) + \
                           (0.25 if no_boring else 0.0)

        checked.append(StandardCheck(
            standard_name="pacing",
            status=self._s(pacing_score_val), score=round(pacing_score_val, 4),
            evidence_used=[str(f"acts={acts_count}"), str(f"avg_scenes_per_act={avg_scenes_per_act:.1f}")],
            reasoning="Pacing requires varied rhythm across acts — no act should drag.",
            failure_reasons=[] if pacing_score_val >= self._THRESHOLD_PASS else ["Pacing is monotonous or dragged"],
        ))

        # --- structure ---
        has_three_acts = acts_count >= 3
        inciting_incident = bool(cin_data.get("inciting_incident"))
        midpoint_shift = bool(cin_data.get("midpoint_shift"))
        third_act_reversal = bool(cin_data.get("third_act_reversal"))

        structure_score_val = (0.25 if has_three_acts else 0.0) + \
                              (0.25 if inciting_incident else 0.0) + \
                              (0.25 if midpoint_shift else 0.0) + \
                              (0.25 if third_act_reversal else 0.0)

        checked.append(StandardCheck(
            standard_name="structure",
            status=self._s(structure_score_val), score=round(structure_score_val, 4),
            evidence_used=[str(f"three_acts={has_three_acts}"), "inciting" if inciting_incident else "no_inciting"],
            reasoning="Classical structure demands: three acts, inciting incident, midpoint shift.",
            failure_reasons=[] if structure_score_val >= self._THRESHOLD_PASS else ["Structure underdeveloped"],
        ))

        # --- scene_value ---
        scenes = cin_data.get("scenes", [])
        positive_scenes = sum(1 for s in scenes if isinstance(s, dict) and s.get("value_shift", 0) > 0)
        negative_scenes = sum(1 for s in scenes if isinstance(s, dict) and s.get("value_shift", 0) < 0)
        total_scn_val = max(len(scenes), 1)
        scene_value_score_val = (positive_scenes / total_scn_val) * 0.4 + \
                                (negative_scenes / total_scn_val) * 0.3 + \
                                (0.3 if len(set(str(s.get("value_shift", "")) for s in scenes)) > 3 else 0.15)

        checked.append(StandardCheck(
            standard_name="scene_value",
            status=self._s(scene_value_score_val), score=round(scene_value_score_val, 4),
            evidence_used=[str(f"total_scenes={len(scenes)}"), str(f"positive_shifts={positive_scenes}")],
            reasoning="Each scene must shift value positively or negatively — no neutral scenes.",
            failure_reasons=[] if scene_value_score_val >= self._THRESHOLD_PASS else [f"{total_scn_val - positive_scenes} neutral scenes detected"],
        ))

        # --- dramatic_tension ---
        tension_gradient = bool(cin_data.get("tension_gradient"))
        cliffhangers = len(cin_data.get("cliffhangers", [])) if isinstance(cin_data.get("cliffhangers"), list) else 0
        rising_action_present = bool(cin_data.get("rising_action_chains"))

        tension_score_val = (0.4 if tension_gradient else 0.0) + \
                            min(cliffhangers / max(2, 1), 1.0) * 0.3 + \
                            (0.3 if rising_action_present else 0.0)

        checked.append(StandardCheck(
            standard_name="dramatic_tension",
            status=self._s(tension_score_val), score=round(tension_score_val, 4),
            evidence_used=[str(f"tension_gradient={tension_gradient}"), str(f"cliffhangers={cliffhangers}")],
            reasoning="Tension must escalate throughout — cliffhangers and rising action sustain engagement.",
            failure_reasons=[] if tension_score_val >= self._THRESHOLD_PASS else ["Tension plateaus or dissipates"],
        ))

        status, overall, summary, recs = self._aggregate(checked)
        return ConstitutionReview(
            constitution_name=self.name, status=status,
            standards_checked=checked, overall_score=overall,
            summary=summary, recommendations=recs,
        )

    def _s(self: "CinemaConstitution", score: float) -> Literal["PASS", "FAIL", "CONDITIONAL"]:
        if score >= self._THRESHOLD_PASS:
            return "PASS"
        if score >= self._THRESHOLD_CONDITIONAL:
            return "CONDITIONAL"
        return "FAIL"
