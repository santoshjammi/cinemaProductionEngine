"""Emotion Constitution - evaluates emotional arc, payoff delivery, catharsis quality, intended emotion alignment."""

from __future__ import annotations

from typing import Any, Dict, List, Literal
from movie_os.genesis3.qa.base import BaseConstitution, ConstitutionReview, StandardCheck


class EmotionConstitution(BaseConstitution):
    name = "emotion"
    standards = [
        "emotional_arc",
        "emotional_payoff",
        "catharsis_quality",
        "intended_emotion_alignment",
    ]

    _THRESHOLD_PASS = 0.7
    _THRESHOLD_CONDITIONAL = 0.4

    def review(self, evidence: Dict[str, Any]) -> ConstitutionReview:
        checked: List[StandardCheck] = []
        emo_data = evidence.get("emotion", {})

        # --- emotional_arc ---
        arc_phases = emo_data.get("arc_phases", [])
        has_peaks = len(emo_data.get("emotional_peaks", [])) > 1
        has_valleys = len(emo_data.get("emotional_lows", [])) > 0
        gradient_defined = bool(emo_data.get("gradient_map"))

        arc_score_val = min(len(arc_phases) / max(4, 1), 1.0) * 0.3 + \
                        (0.35 if has_peaks else 0.0) + \
                        (0.25 if has_valleys else 0.0)

        checked.append(StandardCheck(
            standard_name="emotional_arc",
            status=self._s(arc_score_val), score=round(arc_score_val, 4),
            evidence_used=[str(f"phases={len(arc_phases)}"), "peaks" if has_peaks else "flat"],
            reasoning="Emotional arc needs distinct phases: setup, build, peak, resolution.",
            failure_reasons=[] if arc_score_val >= self._THRESHOLD_PASS else ["Emotional arc too flat or underdeveloped"],
        ))

        # --- emotional_payoff ---
        payoffs_delivered = emo_data.get("payoffs_delivered", 0) or 0
        setup_count = len(emo_data.get("emotional_setups", [])) if isinstance(emo_data.get("emotional_setups"), list) else 0
        unresolved_tensions = emo_data.get("unresolved_emotional_tensions", []) or []

        payoff_score_val = min(payoffs_delivered / max(setup_count, 1), 1.0) * 0.5 + \
                           (0.3 if len(unresolved_tensions) == 0 else 0.15) + \
                           (0.2 if bool(emo_data.get("closure_score", 0.6)) >= 0.5 else 0.0)

        checked.append(StandardCheck(
            standard_name="emotional_payoff",
            status=self._s(payoff_score_val), score=round(payoff_score_val, 4),
            evidence_used=[str(f"setups={setup_count}"), str(f"delivered={payoffs_delivered}")],
            reasoning="Every emotional setup must earn its payoff — no unresolved tension without purpose.",
            failure_reasons=[] if payoff_score_val >= self._THRESHOLD_PASS else [
                f"{len(unresolved_tensions)} unresolved tension(s) left behind"
            ],
        ))

        # --- catharsis_quality ---
        has_cathartic_moment = bool(emo_data.get("cathartic_scene"))
        release_type = emo_data.get("catharsis_type", "")  # "purge", "relief", "triumph"
        timing_resonant = bool(emo_data.get("catharsis_timing"))

        catharsis_score_val = (0.4 if has_cathartic_moment else 0.0) + \
                              (0.35 if release_type in ["purge", "relief", "triumph"] else 0.15) + \
                              (0.25 if timing_resonant else 0.0)

        checked.append(StandardCheck(
            standard_name="catharsis_quality",
            status=self._s(catharsis_score_val), score=round(catharsis_score_val, 4),
            evidence_used=[f"has_catharsis={has_cathartic_moment}", str(f"type={release_type}")],
            reasoning="Catharsis must feel earned and delivered at the right dramatic moment.",
            failure_reasons=[] if catharsis_score_val >= self._THRESHOLD_PASS else ["Catharsis feels premature or unearned"],
        ))

        # --- intended_emotion_alignment ---
        intended = emo_data.get("intended_emotions", [])
        delivered = [e for e in intended if bool(emo_data.get(f"delivered_{e}"))]
        alignment_score_val = len(delivered) / max(len(intended), 1)

        checked.append(StandardCheck(
            standard_name="intended_emotion_alignment",
            status=self._s(alignment_score_val), score=round(alignment_score_val, 4),
            evidence_used=[str(f"intended={len(intended)}"), str(f"delivered={len(delivered)}")],
            reasoning="The intended emotional response must match what the audience actually receives.",
            failure_reasons=[] if alignment_score_val >= self._THRESHOLD_PASS else [
                f"{len(intended) - len(delivered)} emotion(s) not delivered"
            ],
        ))

        status, overall, summary, recs = self._aggregate(checked)
        return ConstitutionReview(
            constitution_name=self.name, status=status,
            standards_checked=checked, overall_score=overall,
            summary=summary, recommendations=recs,
        )

    def _s(self: "EmotionConstitution", score: float) -> Literal["PASS", "FAIL", "CONDITIONAL"]:
        if score >= self._THRESHOLD_PASS:
            return "PASS"
        if score >= self._THRESHOLD_CONDITIONAL:
            return "CONDITIONAL"
        return "FAIL"
