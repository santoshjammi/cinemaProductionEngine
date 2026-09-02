"""Character Constitution - evaluates arc completeness, growth tracking, consistency, relationship dynamics."""

from __future__ import annotations

from typing import Any, Dict, List, Literal
from movie_os.genesis3.qa.base import BaseConstitution, ConstitutionReview, StandardCheck


class CharacterConstitution(BaseConstitution):
    name = "character"
    standards = [
        "arc_completeness",
        "growth_tracking",
        "consistency",
        "relationship_dynamics",
    ]

    _THRESHOLD_PASS = 0.7
    _THRESHOLD_CONDITIONAL = 0.4

    def review(self, evidence: Dict[str, Any]) -> ConstitutionReview:
        checked: List[StandardCheck] = []
        char_data = evidence.get("character", {})
        characters = char_data.get("characters", [])

        # --- arc_completeness ---
        has_arc_start = all(c.get("initial_state") for c in characters if isinstance(c, dict))
        has_arc_end = all(c.get("final_state") for c in characters if isinstance(c, dict))
        transformation_present = any(
            c.get("transformation") or c.get("change_summary")
            for c in characters if isinstance(c, dict)
        )

        arc_score = 0.35 * (1.0 if has_arc_start else 0.0) + \
                     0.35 * (1.0 if has_arc_end else 0.0) + \
                     0.30 * (1.0 if transformation_present else 0.0)

        ev_arc = [str(f"characters={len(characters)}"), "transformation" if transformation_present else "no_transformation"]
        checked.append(StandardCheck(
            standard_name="arc_completeness",
            status=self._s(arc_score), score=round(arc_score, 4),
            evidence_used=ev_arc,
            reasoning="Character arcs require beginning state, ending state, and documented transformation.",
            failure_reasons=[] if arc_score >= self._THRESHOLD_PASS else ["arc score below threshold"],
        ))

        # --- growth_tracking ---
        growth_points = []
        for ch in characters:
            if isinstance(ch, dict):
                gp = ch.get("growth_points") or ch.get("development_milestones") or []
                growth_points.extend(gp)

        direction_score_val = 1.0 if any(
            isinstance(c, dict) and c.get("growth_direction") for c in characters) else 0.0
        growth_score = min(len(growth_points) / max(3, 1), 1.0) * (0.4 if len(characters) > 0 else 0.0) + \
                       0.6 * direction_score_val

        checked.append(StandardCheck(
            standard_name="growth_tracking",
            status=self._s(max(growth_score, 0.)),
            score=round(max(growth_score, 0.), 4),
            evidence_used=[str(f"growth_points={len(growth_points)}")],
            reasoning="Character growth needs multiple tracked milestones with clear direction.",
            failure_reasons=[] if growth_score >= self._THRESHOLD_PASS else ["Insufficient growth points or missing direction"],
        ))

        # --- consistency ---
        inconsistencies = char_data.get("inconsistencies") or []
        trait_stability = all(
            len(c.get("core_traits", [])) > 0 for c in characters if isinstance(c, dict)
        )
        behavior_aligned = char_data.get("behavior_alignment_score", 0.8) >= 0.7
        consistent_val = (1 - min(len(inconsistencies) * 0.25, 1.0)) * 0.5 + \
                         (0.3 if trait_stability else 0.0) + \
                         (0.2 if behavior_aligned else 0.0)
        consistent_val = max(consistent_val, 0.0)

        checked.append(StandardCheck(
            standard_name="consistency",
            status=self._s(consistent_val), score=round(consistent_val, 4),
            evidence_used=[str(f"inconsistencies={len(inconsistencies)}")],
            reasoning="Characters must stay internally consistent with established traits and behaviors.",
            failure_reasons=[] if consistent_val >= self._THRESHOLD_PASS else [str(len(inconsistencies)) + " inconsistency(s) detected"],
        ))

        # --- relationship_dynamics ---
        relationships = char_data.get("relationships", {})
        has_conflict_count = 0
        if isinstance(relationships, dict):
            conflicts = relationships.get("conflicts", [])
            if isinstance(conflicts, list):
                has_conflict_count = len(conflicts)
        has_conflict = has_conflict_count > 0

        has_evolution = False
        if isinstance(relationships, dict):
            for r in relationships.values():
                if isinstance(r, dict) and (r.get("evolves_over_time") or r.get("change_arc")):
                    has_evolution = True
                    break

        mutual_influence = char_data.get("mutual_influence_present", False)
        rel_score_val = 0.35 * (1.0 if has_conflict else 0.0) + \
                        0.35 * (1.0 if has_evolution else 0.0) + \
                        0.30 * (1.0 if mutual_influence else 0.0)

        checked.append(StandardCheck(
            standard_name="relationship_dynamics",
            status=self._s(rel_score_val), score=round(rel_score_val, 4),
            evidence_used=["conflict_present" if has_conflict else "no_conflict"],
            reasoning="Relationships need conflict, evolution, and mutual influence to feel alive.",
            failure_reasons=[] if rel_score_val >= self._THRESHOLD_PASS else ["Relationship dynamics underdeveloped"],
        ))

        status, overall, summary, recs = self._aggregate(checked)
        return ConstitutionReview(
            constitution_name=self.name, status=status,
            standards_checked=checked, overall_score=overall,
            summary=summary, recommendations=recs,
        )

    def _s(self: "CharacterConstitution", score: float) -> Literal["PASS", "FAIL", "CONDITIONAL"]:
        if score >= self._THRESHOLD_PASS:
            return "PASS"
        if score >= self._THRESHOLD_CONDITIONAL:
            return "CONDITIONAL"
        return "FAIL"
