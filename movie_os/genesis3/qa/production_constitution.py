"""Production Constitution - evaluates feasibility, scope, resource requirements, constraints."""

from __future__ import annotations

from typing import Any, Dict, List, Literal
from movie_os.genesis3.qa.base import BaseConstitution, ConstitutionReview, StandardCheck


class ProductionConstitution(BaseConstitution):
    name = "production"
    standards = [
        "feasibility",
        "scope",
        "resource_requirements",
        "constraints_compliance",
    ]

    _THRESHOLD_PASS = 0.7
    _THRESHOLD_CONDITIONAL = 0.4

    def review(self, evidence: Dict[str, Any]) -> ConstitutionReview:
        checked: List[StandardCheck] = []
        prod_data = evidence.get("production", {})

        # --- feasibility ---
        available_resources = prod_data.get("available_budget") or 100
        estimated_cost = prod_data.get("estimated_budget") or 50
        budget_coverage = min(available_resources / max(estimated_cost, 1), 1.0) if estimated_cost > 0 else 1.0

        location_access = bool(prod_data.get("locations_approved"))
        availability_ok = bool(prod_data.get("talent_availability_assessed"))

        feasibility_score_val = budget_coverage * 0.4 + \
                                (0.3 if location_access else 0.0) + \
                                (0.3 if availability_ok else 0.0)

        checked.append(StandardCheck(
            standard_name="feasibility",
            status=self._s(feasibility_score_val), score=round(feasibility_score_val, 4),
            evidence_used=[str(f"budget_coverage={budget_coverage:.2f}"), "locations_approved" if location_access else "locations_pending"],
            reasoning="Production must be feasible within available budget and resources.",
            failure_reasons=[] if feasibility_score_val >= self._THRESHOLD_PASS else [
                f"Budget coverage only {budget_coverage:.0%}"
            ],
        ))

        # --- scope ---
        total_scenes = prod_data.get("total_scenes") or 0
        vfx_scenes = prod_data.get("vfx_scene_count") or 0
        complex_sequences = prod_data.get("complex_sequences") or []
        script_pages = prod_data.get("script_pages") or 90

        scope_feasible = total_scenes <= 120 if total_scenes > 0 else True
        vfx_ratio_ok = (vfx_scenes / max(total_scenes, 1)) <= 0.3 if total_scenes > 0 else True
        script_length_ok = 80 <= script_pages <= 130

        scope_score_val = (0.4 if scope_feasible else 0.1) + \
                          (0.3 if vfx_ratio_ok else 0.1) + \
                          (0.3 if script_length_ok else 0.1)

        checked.append(StandardCheck(
            standard_name="scope",
            status=self._s(scope_score_val), score=round(scope_score_val, 4),
            evidence_used=[str(f"total_scenes={total_scenes}"), str(f"vfx_ratio={vfx_scenes/max(total_scenes,1):.2f}")],
            reasoning="Production scope must be manageable — too many VFX or scenes breaks feasibility.",
            failure_reasons=[] if scope_score_val >= self._THRESHOLD_PASS else ["Scope exceeds manageable limits"],
        ))

        # --- resource_requirements ---
        crew_size = prod_data.get("estimated_crew_size") or 20
        equipment_needed = prod_data.get("equipment_list", []) or []
        permits_required = len(prod_data.get("permits_required", [])) if isinstance(prod_data.get("permits_required"), list) else 0
        special_expertise = bool(prod_data.get("specialized_skills_available"))

        resource_score_val = (1.0 - min(crew_size / max(200, 1), 0.4)) * 0.3 + \
                             (0.3 if len(equipment_needed) <= 15 else 0.15) + \
                             (0.2 if permits_required <= 5 else 0.05) + \
                             (0.2 if special_expertise else 0.0)

        checked.append(StandardCheck(
            standard_name="resource_requirements",
            status=self._s(resource_score_val), score=round(resource_score_val, 4),
            evidence_used=[str(f"crew={crew_size}"), str(f"equipment={len(equipment_needed)}"), str(f"permits={permits_required}")],
            reasoning="Resource needs must match what's available — crew, equipment, permits.",
            failure_reasons=[] if resource_score_val >= self._THRESHOLD_PASS else ["Resource requirements overreach available capacity"],
        ))

        # --- constraints_compliance ---
        rating_target = prod_data.get("target_rating") or "PG-13"
        age_appropriate = bool(prod_data.get("age_rating_checked"))
        content_warnings_set = set(prod_data.get("content_warnings", [])) if isinstance(prod_data.get("content_warnings"), list) else set()

        restricted_content = content_warnings_set & {"gore", "sexual_explicitness"}
        compliance_violating = bool(prod_data.get("regulatory_review_findings"))

        constraints_score_val = (0.4 if age_appropriate else 0.1) + \
                                (0.3 if rating_target in ["G", "PG", "PG-13"] else 0.15) + \
                                (0.2 if len(restricted_content) == 0 else 0.05) + \
                                (0.1 if not compliance_violating else 0.0)

        checked.append(StandardCheck(
            standard_name="constraints_compliance",
            status=self._s(constraints_score_val), score=round(constraints_score_val, 4),
            evidence_used=[str(f"target_rating={rating_target}"), str(f"restricted={restricted_content}")],
            reasoning="Production must comply with rating, regulatory, and content constraints.",
            failure_reasons=[] if constraints_score_val >= self._THRESHOLD_PASS else [
                f"Rating target {rating_target} may require rework"
            ],
        ))

        status, overall, summary, recs = self._aggregate(checked)
        return ConstitutionReview(
            constitution_name=self.name, status=status,
            standards_checked=checked, overall_score=overall,
            summary=summary, recommendations=recs,
        )

    def _s(self: "ProductionConstitution", score: float) -> Literal["PASS", "FAIL", "CONDITIONAL"]:
        if score >= self._THRESHOLD_PASS:
            return "PASS"
        if score >= self._THRESHOLD_CONDITIONAL:
            return "CONDITIONAL"
        return "FAIL"
