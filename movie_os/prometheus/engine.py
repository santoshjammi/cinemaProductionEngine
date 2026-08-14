"""Prometheus Engine — high-level orchestrator that bridges GENESIS certificates to production."""

from __future__ import annotations

import logging
from typing import Any, Optional

from movie_os.prometheus.pipeline import PrometheusPipeline, PipelineConfig, StageError
from movie_os.prometheus.models import ProductionCertificate

logger = logging.getLogger("movie_os.prometheus.engine")


class PrometheusEngine:
    """Orchestrates the full PROMETHEUS production pipeline.

    Takes a GENESIS-certified blueprint (ProductionCertificate), validates it,
    configures the pipeline with appropriate providers, and runs all six stages
    in sequence: Storyboard → Images → Voice → Music → Editing → Film.
    """

    def __init__(
        self,
        config: Optional[PipelineConfig] = None,
    ):
        self.config = config
        self.pipeline = PrometheusPipeline(config)

    @property
    def image_provider(self) -> Any:
        """Access the pipeline's internal image provider reference for testing."""
        return getattr(self, "_image_provider", None)

    @image_provider.setter
    def image_provider(self, value: Any) -> None:
        self._image_provider = value  # type: ignore[assignment]

    async def produce(
        self,
        certificate: ProductionCertificate,
        brief: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run the full production pipeline.

        :param certificate: A GENESIS-certified blueprint (ProductionCertificate).
        :param brief: Optional overrides / context — provider URLs, mood notes, etc.
        :returns: Dict containing PrometheusResult plus intermediate artifact dicts.
        """
        if not self.can_produce(certificate):
            raise ValueError(
                f"Cannot produce — certificate '{certificate.certificate_id}' "
                f"is not production-ready (status={certificate.status})."
            )

        brief = brief or {}
        logger.info(f"[PrometheusEngine] Starting production pipeline for \"{certificate.project_name}\"")

        result = await self.pipeline.execute(certificate=certificate, brief=brief)

        # Collect artifact dicts from the result model into a convenient list.
        artifact_dicts: list[dict[str, Any]] = []
        for art in getattr(result, "artifacts", []):
            if hasattr(art, 'model_dump'):
                d = art.model_dump()  # type: ignore[attr-defined]
            else:
                d = dict(art) if isinstance(art, dict) else {
                    "type": art.type,
                    "path": getattr(art, "path", ""),
                    "url": getattr(art, "url", None),
                    "metadata": getattr(art, "metadata", {}),
                }
            artifact_dicts.append(d)

        stage_summary = [
            {
                "name": s.name if hasattr(s, 'name') else s.get("name"),
                "status": s.status if hasattr(s, 'status') else s.get("status"),
                "duration_seconds": (
                    0.0
                    if not getattr(s, "started_at", None) or not getattr(s, "completed_at", None) else
                    (getattr(s, "completed_at", None) - getattr(s, "started_at", None)).total_seconds()
                ) or 0.0,
            }
            for s in result.stages
        ]

        return {
            "result": result,
            "artifact_dicts": artifact_dicts,
            "stage_summary": stage_summary,
        }

    def can_produce(self, certificate: ProductionCertificate) -> bool:
        """Check whether the certificate permits production execution."""
        try:
            ready = getattr(certificate, "production_ready", False)
            return bool(ready)  # type: ignore[arg-type]
        except Exception:
            return False
