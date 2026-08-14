"""Core Prometheus rendering pipeline — orchestrates the 6 production stages.

The pipeline: ProductionCertificate + brief → Storyboard → Images → Voice → Music
→ Editing → Film → final video output.
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Optional

from movie_os.frozen_pkp import validate_frozen_pkp

logger = logging.getLogger("movie_os.prometheus")

_DEFAULT_CHECKPOINT_DIR = "artifacts/checkpoints"


class StageError(Exception):
    """Raised when a stage fails during execution."""
    def __init__(self, stage_name: str, message: str):
        self.stage_name = stage_name
        super().__init__(f"Stage '{stage_name}' failed: {message}")


class PipelineConfig:
    """Runtime configuration for PrometheusPipeline."""
    def __init__(
        self,
        max_retries: int = 0,
        fail_fast: bool = True,
        parallel_image_count: int = 2,
        output_dir: str = "output/prometheus",
        progress_tracker: Any = None,
        image_provider: Any = None,
    ):
        self.max_retries = max_retries
        self.fail_fast = fail_fast
        self.parallel_image_count = parallel_image_count
        self.output_dir = output_dir
        self.progress_tracker = progress_tracker
        # Optional injected image provider (tests inject a mock; production
        # leaves None so ImageGenerationStage defaults to the real FLUX provider).
        self.image_provider = image_provider


class PrometheusPipeline:
    """The production department that executes GENESIS-certified blueprints."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()

    # ---- main entry point -------------------------------------------------

    async def execute(
        self,
        certificate: Any,
        brief: dict[str, Any],
    ) -> Any:
        """Execute the full production pipeline."""
        # Certificate validation
        if not hasattr(certificate, "production_ready") or not certificate.production_ready:
            raise ValueError(
                f"Cannot execute pipeline — certificate is not production-ready"
            )

        frozen_pkp = brief.get("frozen_pkp")
        if frozen_pkp is None:
            raise ValueError("Cannot execute pipeline — frozen PKP missing")
        validate_frozen_pkp(
            frozen_pkp if isinstance(frozen_pkp, dict) else frozen_pkp.model_dump(),
            expected_episode_id=brief.get("production", {}).get("episode_id") or (certificate.blueprint.get("episode_id") if isinstance(getattr(certificate, "blueprint", None), dict) else None),
            expected_policy_snapshot_id=brief.get("policy_snapshot_id") or (frozen_pkp.get("policy_snapshot_id") if isinstance(frozen_pkp, dict) else getattr(frozen_pkp, "policy_snapshot_id", None)),
        )

        context: dict[str, Any] = {
            "certificate": certificate,
            "brief": brief,
            "artifacts": [],
            "stage_contexts": {},
            "output_dir": self.config.output_dir,
        }

        # ── ProgressTracker injection (fail-closed via local-first only) ──
        tracker = None
        if getattr(self.config, "progress_tracker", None) is not None:
            tracker = self.config.progress_tracker
        else:
            try:
                from prometheus.progress import ProgressTracker, create_progress_tracker

                # If no explicit tracker was passed, instantiate a default local one
                tracker = create_progress_tracker(checkpoint_dir=_DEFAULT_CHECKPOINT_DIR)
            except (ImportError, Exception):
                # Fail-closed: continue without tracking if progress tools unavailable
                tracker = None

        pipeline_state: Any = None
        total_stages = 6
        
        # Emit PIPELINE_START
        if tracker is not None:
            try:
                pipeline_state = tracker.on_pipeline_start(total_stages=total_stages)
            except Exception:
                pipeline_state = type('NoopState', (), {
                    'completed_stages': set(),
                    'run_id': '',
                    'started_at': datetime.now(timezone.utc).isoformat(),
                    'total_artifacts': 0,
                    'total_stages': total_stages,
                })()

        stages_state: list[dict] = []
        start_time = time.monotonic()

        # Create stage instances
        stage_instances = self._create_stages(certificate, brief)

        # Run pipeline
        failed_stage: Optional[str] = None
        for idx, stage_obj in enumerate(stage_instances):
            name = _stage_name(idx + 1, type(stage_obj).__name__)

            stage_entry = {
                "name": name,
                "class_name": type(stage_obj).__name__,
                "stage": {
                    "name": name,
                    "status": "running",
                    "started_at": datetime.utcnow(),
                    "completed_at": None,
                    "artifacts": [],
                    "error": None,
                },
            }
            stages_state.append(stage_entry)

            if failed_stage and not self.config.fail_fast:
                stage_entry["stage"]["status"] = "skipped"
                continue

            # Emit STAGE_START
            if tracker is not None and pipeline_state is not None:
                try:
                    tracker.on_stage_start(name, pipeline_state)
                except Exception:
                    pass

            try:
                result = await asyncio.wait_for(
                    self._run_stage(stage_obj, context),
                    timeout=1800.0,  # 30 min per stage — FLUX renders are slow
                )
                stage_entry["stage"]["status"] = "completed"
                stage_entry["stage"]["completed_at"] = datetime.utcnow()
                stage_artifacts: list[dict] = result.get("artifacts", [])
                
                # Emit ARTIFACT_COMPLETE for each artifact
                if tracker is not None and pipeline_state is not None:
                    for art_idx, art in enumerate(stage_artifacts):
                        try:
                            tracker.on_artifact_complete(name, art_idx + 1, len(stage_artifacts), pipeline_state)
                        except Exception:
                            pass
                
                for art in stage_artifacts:
                    context["artifacts"].append(art)
                    stage_entry["stage"]["artifacts"].append(art)
                
                # Emit STAGE_COMPLETE
                if tracker is not None and pipeline_state is not None:
                    try:
                        tracker.on_stage_complete(name, pipeline_state)
                    except Exception:
                        pass
                
                # Pass stage output to next stage via brief
                stage_name = result.get("stage_name", name)
                if stage_name == "Storyboard":
                    context["brief"]["storyboard_artifacts"] = stage_artifacts
                elif stage_name == "ImageGeneration":
                    context["brief"]["image_artifacts"] = stage_artifacts
                elif stage_name == "VoiceOver":
                    context["brief"]["voice_artifacts"] = stage_artifacts
                elif stage_name == "MusicComposition":
                    context["brief"]["music_artifacts"] = stage_artifacts
                elif stage_name == "Editing":
                    context["brief"]["editing_artifacts"] = stage_artifacts
            except StageError as exc:
                failed_stage = name
                stage_entry["stage"]["status"] = "failed"
                stage_entry["stage"]["error"] = str(exc)
                stage_entry["stage"]["completed_at"] = datetime.utcnow()
                
                # Emit STAGE_FAIL
                if tracker is not None and pipeline_state is not None:
                    try:
                        tracker.on_stage_fail(name, str(exc), pipeline_state)
                    except Exception:
                        pass
                
                if self.config.fail_fast or idx == 0:
                    break
            except asyncio.TimeoutError:
                failed_stage = name
                stage_entry["stage"]["status"] = "failed"
                stage_entry["stage"]["error"] = f"Stage '{name}' timed out after 600s"
                stage_entry["stage"]["completed_at"] = datetime.utcnow()
                
                # Emit STAGE_FAIL
                if tracker is not None and pipeline_state is not None:
                    try:
                        tracker.on_stage_fail(name, f"timed out after 600s", pipeline_state)
                    except Exception:
                        pass
                
                break
            except Exception as exc:
                failed_stage = name
                stage_entry["stage"]["status"] = "failed"
                stage_entry["stage"]["error"] = str(exc)
                stage_entry["stage"]["completed_at"] = datetime.utcnow()
                
                # Emit STAGE_FAIL
                if tracker is not None and pipeline_state is not None:
                    try:
                        tracker.on_stage_fail(name, str(exc), pipeline_state)
                    except Exception:
                        pass
                
                if self.config.fail_fast:
                    break

        duration_seconds = time.monotonic() - start_time

        # Determine overall status
        if not failed_stage:
            overall_status = "completed"
        else:
            all_done = all(
                s["stage"]["status"] in ("completed", "skipped")
                for s in stages_state
            )
            overall_status = "partial" if all_done else "failed"

        # Emit PIPELINE_COMPLETE before building result
        if tracker is not None and pipeline_state is not None:
            try:
                pipeline_state.total_stages = total_stages
                tracker.on_pipeline_complete(pipeline_state)
            except Exception:
                pass

        return self._build_result(
            certificate=certificate,
            stages=stages_state,
            artifacts=context["artifacts"],
            duration_seconds=duration_seconds,
            overall_status=overall_status,
        )

    def _create_stages(self, certificate: Any, brief: dict) -> list[Any]:
        """Create stage instances in order."""
        from movie_os.prometheus.stages.storyboard_stage import StoryboardStage
        from movie_os.prometheus.stages.image_stage import ImageGenerationStage
        from movie_os.prometheus.stages.voice_stage import VoiceStage
        from movie_os.prometheus.stages.music_stage import MusicStage
        from movie_os.prometheus.stages.editing_stage import EditingStage
        from movie_os.prometheus.stages.film_stage import FilmStage

        stages = [
            StoryboardStage(certificate=certificate, brief=brief),
            ImageGenerationStage(certificate=certificate, brief=brief),
            VoiceStage(certificate=certificate, brief=brief),
            MusicStage(certificate=certificate, brief=brief),
            EditingStage(certificate=certificate, brief=brief),
            FilmStage(certificate=certificate, brief=brief),
        ]
        # Inject an image provider if one was configured (tests use a mock).
        if getattr(self.config, "image_provider", None) is not None:
            stages[1].set_image_provider(self.config.image_provider)
        return stages
    async def _run_stage(self, stage_obj: Any, context: dict) -> dict[str, Any]:
        """Run a single stage, handling both sync and async run methods."""
        result = stage_obj.run()
        if asyncio.iscoroutine(result):
            result = await result
        return result

    # ---- helpers ----------------------------------------------------------

    def _build_result(
        self,
        certificate: Any,
        stages: list,
        artifacts: list,
        duration_seconds: float,
        overall_status: str,
    ) -> Any:
        """Build the final PrometheusResult."""
        from movie_os.prometheus.models import (
            OverallStatus as _OS,
            PrometheusResult as _PR,
            ProductionStage as _PS,
        )

        stage_models = []
        for s in stages:
            stage_data = s["stage"]
            stage_models.append(_PS(
                name=stage_data["name"],
                status=stage_data["status"],
                started_at=stage_data["started_at"],
                completed_at=stage_data["completed_at"],
                artifacts=stage_data.get("artifacts", []),
                error=stage_data.get("error"),
            ))

        output_path = None
        if artifacts:
            last_art = artifacts[-1]
            if isinstance(last_art, dict) and last_art.get("type") == "film":
                output_path = last_art.get("path")

        return _PR(
            certificate_id=certificate.certificate_id,
            project_name=certificate.project_name,
            stages=stage_models,
            overall_status=_OS(overall_status),
            output_path=output_path,
            duration_seconds=duration_seconds,
            artifacts=artifacts,
        )


def _stage_name(idx: int, class_name: str) -> str:
    """Map canonical stage names to pipeline index."""
    mapping = {1: "Storyboard", 2: "ImageGeneration", 3: "VoiceOver",
               4: "MusicComposition", 5: "Editing", 6: "Film"}
    return mapping.get(idx, class_name)
