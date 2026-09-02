"""Visual Constitution - evaluates visual language, imagery depth, metaphor use, shot potential."""

from __future__ import annotations

from typing import Any, Dict, List, Literal
from movie_os.genesis3.qa.base import BaseConstitution, ConstitutionReview, StandardCheck


class VisualConstitution(BaseConstitution):
    name = "visual"
    standards = [
        "visual_language",
        "imagery_depth",
        "metaphor_use",
        "shot_potential",
    ]

    _THRESHOLD_PASS = 0.7
    _THRESHOLD_CONDITIONAL = 0.4

    def review(self, evidence: Dict[str, Any]) -> ConstitutionReview:
        checked: List[StandardCheck] = []
        visual_data = evidence.get("visual", {})

        # --- visual_language ---
        shots_list = visual_data.get("shots", [])
        color_palette_defined = bool(visual_data.get("color_palette"))
        lighting_consistent = bool(visual_data.get("lighting_scheme"))
        framing_present = all(
            isinstance(s, dict) and s.get("framing") for s in shots_list if isinstance(s, dict)
        )

        visual_score_val = (0.35 if color_palette_defined else 0.0) + \
                           (0.35 if lighting_consistent else 0.0) + \
                           (0.3 if framing_present and len(shots_list) > 0 else 0.0)

        checked.append(StandardCheck(
            standard_name="visual_language",
            status=self._s(visual_score_val), score=round(visual_score_val, 4),
            evidence_used=[str(f"shots={len(shots_list)}"), "palette" if color_palette_defined else "no_palette"],
            reasoning="Visual language needs color palette, lighting, and framing choices that serve the story.",
            failure_reasons=[] if visual_score_val >= self._THRESHOLD_PASS else ["Visual design underdeveloped"],
        ))

        # --- imagery_depth ---
        symbols_count = len(visual_data.get("symbols", [])) if isinstance(visual_data.get("symbols"), (list, dict)) else 0
        recurring_images = bool(visual_data.get("recurring_visual_elements"))
        sensory_details_present = bool(visual_data.get("sensory_detail_score", 0.5)) >= 0.4

        imagery_score_val = min(symbols_count / max(3, 1), 1.0) * (0.3 if len(shots_list) > 0 else 0.0) + \
                            (0.35 if recurring_images else 0.0) + \
                            (0.35 if sensory_details_present else 0.0)

        checked.append(StandardCheck(
            standard_name="imagery_depth",
            status=self._s(max(imagery_score_val, 0.0)), score=round(max(imagery_score_val, 0.0), 4),
            evidence_used=[str(f"symbols={symbols_count}"), "recurring" if recurring_images else "one-off"],
            reasoning="Imagery should recur and evolve — visual poetry that deepens with each appearance.",
            failure_reasons=[] if imagery_score_val >= self._THRESHOLD_PASS else ["Imagery too sparse or static"],
        ))

        # --- metaphor_use ---
        explicit_metaphors = len(visual_data.get("explicit_metaphors", [])) if isinstance(visual_data.get("explicit_metaphors"), list) else 0
        visual_analogies = bool(visual_data.get("visual_analogies"))
        allegorical_layers = visual_data.get("allegorical_layers", 0) or 0

        metaphor_score_val = min(explicit_metaphors / max(1, 2), 1.0) * 0.3 + \
                             (0.35 if visual_analogies else 0.0) + \
                             (min(allegorical_layers / max(1, 3), 1.0)) * 0.35

        checked.append(StandardCheck(
            standard_name="metaphor_use",
            status=self._s(metaphor_score_val), score=round(metaphor_score_val, 4),
            evidence_used=[str(f"metaphors={explicit_metaphors}"), str(f"allegorical_layers={allegorical_layers}")],
            reasoning="Visual metaphors must be layered — surface meaning plus deeper symbolic resonance.",
            failure_reasons=[] if metaphor_score_val >= self._THRESHOLD_PASS else ["Metaphor is too literal or absent"],
        ))

        # --- shot_potential ---
        camera_movements = visual_data.get("camera_movements", [])
        unique_angles = len(visual_data.get("unique_angles", set())) if isinstance(visual_data.get("unique_angles"), (set, list)) else 0
        composition_rich = bool(visual_data.get("composition_notes"))

        shot_score_val = (1.0 if len(camera_movements) > 2 else min(len(camera_movements) / max(3, 1), 1.0)) * 0.3 + \
                         (0.35 if unique_angles > 3 else min(unique_angles / max(4, 1), 0.8) * 0.875) + \
                         (0.35 if composition_rich else 0.0)

        checked.append(StandardCheck(
            standard_name="shot_potential",
            status=self._s(shot_score_val), score=round(shot_score_val, 4),
            evidence_used=[str(f"camera_moves={len(camera_movements)}"), str(f"unique_angles={unique_angles}")],
            reasoning="Each shot must have intentional camera movement, angle, and composition.",
            failure_reasons=[] if shot_score_val >= self._THRESHOLD_PASS else ["Shot design too uniform or planar"],
        ))

        status, overall, summary, recs = self._aggregate(checked)
        return ConstitutionReview(
            constitution_name=self.name, status=status,
            standards_checked=checked, overall_score=overall,
            summary=summary, recommendations=recs,
        )

    def _s(self: "VisualConstitution", score: float) -> Literal["PASS", "FAIL", "CONDITIONAL"]:
        if score >= self._THRESHOLD_PASS:
            return "PASS"
        if score >= self._THRESHOLD_CONDITIONAL:
            return "CONDITIONAL"
        return "FAIL"
