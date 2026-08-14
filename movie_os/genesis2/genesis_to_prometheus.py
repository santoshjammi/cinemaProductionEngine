"""Genesis-to-PROMETHEUS handoff adapter.

Converts Genesis PKG output (PKP specs, discovery results, review findings)
into a ProductionCertificate that the PROMETHEUS pipeline can consume.

Usage:
    from movie_os.genesis2.genesis_to_prometheus import GenesisPrometheusAdapter
    certificate = adapter.convert(pkg_result)
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from movie_os.prometheus.models import (
    CertificationStatus,
    CinematicReviewers,
    Director,
    ProductionCertificate,
)

logger = logging.getLogger("movie_os.genesis2.genesis_to_prometheus")


class GenesisPrometheusAdapter:
    """Converts Genesis PKG output into a PROMETHEUS ProductionCertificate."""

    def __init__(self, project_name: str = "Untitled Film"):
        self.project_name = project_name

    def convert(
        self,
        genesis_result: dict[str, Any],
    ) -> ProductionCertificate:
        """Convert a Genesis engine result dict into a ProductionCertificate.

        Args:
            genesis_result: The dict returned by GenesisEngine.run() or
                GenesisGraph.run(). Expected keys:
                - session_id
                - discovery_results (list of AgentResult)
                - pkp_results (list of AgentResult)
                - review_results (list of AgentResult)
                - gate_result (dict with 'passed' bool)
                - specifications (dict of spec_id -> spec_info)
                - overall_completeness (float 0-1)

        Returns:
            ProductionCertificate ready for PROMETHEUS pipeline consumption.
        """
        # Build the blueprint from the PKP specifications
        blueprint = self._build_blueprint(genesis_result)

        # Determine certification status
        gate_result = genesis_result.get("gate_result", {})
        gate_passed = gate_result.get("passed", False)
        completeness = genesis_result.get("overall_completeness", 0.0)

        if gate_passed and completeness >= 0.8:
            status = CertificationStatus.PRODUCTION_READY
        elif completeness >= 0.5:
            status = CertificationStatus.REVISION_REQUIRED
        else:
            status = CertificationStatus.DRAFT

        # Count success/fail
        discovery_results = genesis_result.get("discovery_results", [])
        pkp_results = genesis_result.get("pkp_results", [])
        review_results = genesis_result.get("review_results", [])
        all_results = discovery_results + pkp_results + review_results
        success_count = sum(1 for r in all_results if getattr(r, "status", "") == "success")
        total_count = len(all_results) or 1

        # Build a certificate
        cert_id = f"cert-{genesis_result.get('session_id', 'unknown')[:12]}"
        return ProductionCertificate(
            certificate_id=cert_id,
            project_name=self.project_name,
            version="1.0",
            blueprint=blueprint,
            status=status,
            reviewed_by=Director(name="Genesis Engine"),
            notes=(
                f"Genesis pipeline completed. "
                f"Gate: {'PASSED' if gate_passed else 'FAILED'}. "
                f"Completeness: {completeness:.0%}. "
                f"Agents: {success_count}/{total_count} passed."
            ),
        )

    def _build_blueprint(self, genesis_result: dict[str, Any]) -> dict[str, Any]:
        """Build the blueprint payload from Genesis output."""
        specs = genesis_result.get("specifications", {})
        discovery_results = genesis_result.get("discovery_results", [])
        pkp_results = genesis_result.get("pkp_results", [])
        review_results = genesis_result.get("review_results", [])

        # Extract scene descriptions from PKP-04 (story) and PKP-06 (scenes)
        scenes = []
        for pkp in pkp_results:
            output = getattr(pkp, "output", {}) or {}
            if isinstance(output, dict):
                if "scenes" in output:
                    for s in output["scenes"]:
                        scenes.append({
                            "id": s.get("scene_number", len(scenes) + 1),
                            "description": s.get("title", s.get("description", "")),
                            "characters": s.get("characters", []),
                            "setting": s.get("setting", ""),
                            "duration": s.get("duration", 60),
                        })

        # Build the blueprint
        return {
            "scenes": scenes or [{"id": 1, "description": "Auto-generated scene from Genesis"}],
            "specifications": {
                sid: {
                    "name": info.get("spec_name", ""),
                    "confidence": info.get("confidence", "unknown"),
                    "validation": info.get("validation_status", "unknown"),
                }
                for sid, info in specs.items()
            },
            "discovery_count": len(discovery_results),
            "pkp_count": len(pkp_results),
            "review_count": len(review_results),
            "overall_completeness": genesis_result.get("overall_completeness", 0.0),
            "generated_at": datetime.utcnow().isoformat(),
        }