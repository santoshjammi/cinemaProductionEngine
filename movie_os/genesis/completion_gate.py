"""Pre-Production Completion Gate — certifies readiness for Studio Engine.

The gate checks 8 criteria before allowing the production to proceed
to the Studio Engine. All must pass.
"""

from __future__ import annotations

import logging
from typing import Any

from .models import ConfidenceLevel, PKGState
from .pkg import ProductionKnowledgeGraph


logger = logging.getLogger("movie_os.genesis.gate")


# All 19 PKP specification IDs that must exist
REQUIRED_SPECS = [
    "PKP-00", "PKP-01", "PKP-02", "PKP-03", "PKP-04", "PKP-05",
    "PKP-06", "PKP-07", "PKP-08", "PKP-09", "PKP-10", "PKP-11",
    "PKP-12", "PKP-13", "PKP-14", "PKP-15", "PKP-16", "PKP-17",
    "PKP-18",
]

# Keys under which review agents store their findings in the PKG
REVIEW_KEYS = [
    "story_review",
    "character_review",
    "narrative_review",
    "psychology_review",
]


class GateResult:
    """Result of the completion gate check."""

    def __init__(self):
        self.passed: bool = True
        self.criteria: list[dict[str, Any]] = []
        self.blockers: list[str] = []
        self.warnings: list[str] = []

    def add_check(self, name: str, passed: bool, detail: str = "") -> None:
        self.criteria.append({
            "name": name,
            "passed": passed,
            "detail": detail,
        })
        if not passed:
            self.passed = False
            self.blockers.append(f"{name}: {detail}")

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "criteria": self.criteria,
            "blockers": self.blockers,
            "warnings": self.warnings,
        }


class PreProductionCompletionGate:
    """The final gate before a production enters the Studio Engine."""

    def __init__(self, min_completeness: float = 0.8):
        self.min_completeness = min_completeness

    def check(self, pkg: ProductionKnowledgeGraph) -> GateResult:
        """Run all 8 gate checks. Returns GateResult."""
        result = GateResult()

        # 1. All 19 PKP specifications exist
        missing = [s for s in REQUIRED_SPECS if not pkg.has_specification(s)]
        result.add_check(
            "all_specifications_exist",
            len(missing) == 0,
            f"Missing: {missing}" if missing else "All 19 specifications present",
        )

        # 2. All dependencies are satisfied
        dep_errors = []
        for spec_id, spec in pkg.get_all_specifications().items():
            for dep_id in spec.dependencies:
                if not pkg.has_specification(dep_id):
                    dep_errors.append(f"{spec_id} depends on {dep_id} which is missing")
        result.add_check(
            "dependencies_satisfied",
            len(dep_errors) == 0,
            "; ".join(dep_errors) if dep_errors else "All dependencies satisfied",
        )

        # 3. Cross-validation has passed
        validation_errors = []
        for spec_id, spec in pkg.get_all_specifications().items():
            if spec.validation_status == "failed":
                validation_errors.append(f"{spec_id}: {spec.validation_errors}")
        result.add_check(
            "cross_validation_passed",
            len(validation_errors) == 0,
            "; ".join(validation_errors) if validation_errors else "All validations passed",
        )

        # 4. No critical contradictions remain (aggregated from all review keys)
        all_contradictions = []
        for key in REVIEW_KEYS:
            findings = pkg.get_discovery_result(key)
            if findings and isinstance(findings, dict):
                all_contradictions.extend(findings.get("contradictions", []))
        critical = [c for c in all_contradictions if c.get("severity") == "critical"]
        result.add_check(
            "no_critical_contradictions",
            len(critical) == 0,
            f"{len(critical)} critical contradictions" if critical else "No critical contradictions",
        )

        # 5. Confidence scores meet thresholds
        low_confidence = []
        for spec_id, spec in pkg.get_all_specifications().items():
            if spec.confidence == ConfidenceLevel.UNKNOWN:
                low_confidence.append(f"{spec_id} has UNKNOWN confidence")
        result.add_check(
            "confidence_thresholds_met",
            len(low_confidence) == 0,
            "; ".join(low_confidence) if low_confidence else "All confidence levels met",
        )

        # 6. Required reviews have been completed (all review keys present in PKG)
        missing_reviews = [k for k in REVIEW_KEYS if pkg.get_discovery_result(k) is None]
        result.add_check(
            "reviews_completed",
            len(missing_reviews) == 0,
            f"Missing reviews: {missing_reviews}" if missing_reviews else "All reviews completed",
        )

        # 7. Knowledge Graph is complete
        completeness = pkg.get_overall_completeness()
        result.add_check(
            "knowledge_graph_complete",
            completeness >= self.min_completeness,
            f"Completeness: {completeness:.1%} (min: {self.min_completeness:.0%})",
        )

        # 8. Production Blueprint is fully derived
        blueprint = pkg.get_specification("PKP-15")
        result.add_check(
            "blueprint_derived",
            blueprint is not None and blueprint.validation_status == "passed",
            "Blueprint missing or not validated" if not blueprint
            else "Production Blueprint fully derived",
        )

        if result.passed:
            logger.info("Pre-Production Completion Gate: PASSED")
        else:
            logger.warning(f"Pre-Production Completion Gate: FAILED — {len(result.blockers)} blockers")

        return result