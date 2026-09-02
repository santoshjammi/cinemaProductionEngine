"""Continuity Constitution - evaluates timeline consistency, transitions, logical flow, visual/dialogue continuity."""

from __future__ import annotations

from typing import Any, Dict, List, Literal
from movie_os.genesis3.qa.base import BaseConstitution, ConstitutionReview, StandardCheck


class ContinuityConstitution(BaseConstitution):
    name = "continuity"
    standards = [
        "timeline_consistency",
        "transition_quality",
        "logical_flow",
        "visual_dialogue_continuity",
    ]

    _THRESHOLD_PASS = 0.7
    _THRESHOLD_CONDITIONAL = 0.4

    def review(self, evidence: Dict[str, Any]) -> ConstitutionReview:
        checked: List[StandardCheck] = []
        cont_data = evidence.get("continuity", {})

        # --- timeline_consistency ---
        events_timeline = cont_data.get("events_timeline", [])
        contradictions = cont_data.get("timeline_contradictions", []) or []
        time_jumps_respected = bool(cont_data.get("time_jump_rules_followed"))

        contradiction_penalty = min(len(contradictions) * 0.35, 0.7)
        timeline_events_ordered = any(
            isinstance(e, dict) and e.get("is_ordered") for e in events_timeline
        ) if events_timeline else False
        timeline_score_val = max(1 - contradiction_penalty + (0.3 if timeline_events_ordered else 0), 0.0)

        tl_score_val = 0.6 * max((1 - contradiction_penalty), 0.3) + \
                       (0.2 if time_jumps_respected else 0.0) + \
                       (0.2 if bool(events_timeline) else 0.0)

        checked.append(StandardCheck(
            standard_name="timeline_consistency",
            status=self._s(tl_score_val), score=round(tl_score_val, 4),
            evidence_used=[str(f"events={len(events_timeline)}"), str(f"contradictions={len(contradictions)}")],
            reasoning="Timeline must be internally consistent — no contradictory events, respected time jumps.",
            failure_reasons=[] if tl_score_val >= self._THRESHOLD_PASS else [
                str(len(contradictions)) + " timeline contradiction(s)"
            ],
        ))

        # --- transition_quality ---
        transitions = cont_data.get("transitions", [])
        smooth_transitions = sum(1 for t in transitions if isinstance(t, dict) and t.get("smooth"))
        total_transitions = len(transitions) if transitions else 1
        cut_type_consistent = bool(cont_data.get("cut_types_documented"))

        transition_score_val = (smooth_transitions / max(total_transitions, 1)) * 0.5 + \
                               (0.3 if cut_type_consistent else 0.0) + \
                               (0.2 if total_transitions > 2 else 0.05)

        checked.append(StandardCheck(
            standard_name="transition_quality",
            status=self._s(transition_score_val), score=round(transition_score_val, 4),
            evidence_used=[str(f"total={total_transitions}"), str(f"smooth={smooth_transitions}")],
            reasoning="Transitions between scenes must be smooth and purposeful.",
            failure_reasons=[] if transition_score_val >= self._THRESHOLD_PASS else [f"{total_transitions - smooth_transitions} rough transitions"],
        ))

        # --- logical_flow ---
        plot_threads = cont_data.get("plot_threads", [])
        resolved_threads = cont_data.get("resolved_plot_threads", []) or []
        dangling_subplots = cont_data.get("dangling_subplots", []) or []

        flow_score_val = min(len(resolved_threads) / max(len(plot_threads), 1), 1.0) * 0.5 + \
                         (0.3 if len(dangling_subplots) == 0 else 0.1) + \
                         (0.2 if bool(cont_data.get("chapter_summaries")) else 0.0)

        checked.append(StandardCheck(
            standard_name="logical_flow",
            status=self._s(flow_score_val), score=round(flow_score_val, 4),
            evidence_used=[str(f"plot_threads={len(plot_threads)}"), str(f"dangling={len(dangling_subplots)}")],
            reasoning="Story logic flows from thread to thread — all must be addressed.",
            failure_reasons=[] if flow_score_val >= self._THRESHOLD_PASS else [f"{len(dangling_subplots)} dangling subplot(s)"],
        ))

        # --- visual_dialogue_continuity ---
        character_appearances = cont_data.get("character_appearances", {}) or {}
        missing_entries = 0
        total_checks = 0
        for char in character_appearances:
            appearances = character_appearances[char]
            if isinstance(appearances, dict):
                total_checks += 1
                if not appearances.get("wardrobe_consistent") or not appearances.get("prop_consistent"):
                    missing_entries += 1

        continuity_score_val = max(1.0 - (missing_entries / max(total_checks, 1)), 0.5) * 0.4 + \
                               (0.3 if bool(cont_data.get("scene_locations_mapped")) else 0.0) + \
                               (0.3 if bool(cont_data.get("dialogue_references_validated")) else 0.0)

        checked.append(StandardCheck(
            standard_name="visual_dialogue_continuity",
            status=self._s(continuity_score_val), score=round(continuity_score_val, 4),
            evidence_used=[str(f"total_checks={total_checks}"), str(f"errors={missing_entries}")],
            reasoning="Characters must maintain consistent presence — wardrobe, props, dialogue references.",
            failure_reasons=[] if continuity_score_val >= self._THRESHOLD_PASS else [f"{missing_entries} character continuity error(s)"],
        ))

        status, overall, summary, recs = self._aggregate(checked)
        return ConstitutionReview(
            constitution_name=self.name, status=status,
            standards_checked=checked, overall_score=overall,
            summary=summary, recommendations=recs,
        )

    def _s(self: "ContinuityConstitution", score: float) -> Literal["PASS", "FAIL", "CONDITIONAL"]:
        if score >= self._THRESHOLD_PASS:
            return "PASS"
        if score >= self._THRESHOLD_CONDITIONAL:
            return "CONDITIONAL"
        return "FAIL"
