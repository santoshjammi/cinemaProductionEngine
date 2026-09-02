"""ProductionService — drives the proven GENESIS2 → PROMETHEUS → final MP4 path.

This is the canonical runtime path (the one validated end-to-end in
`run_space_between_us.py`), exposed as a reusable service with a job queue so
the FastAPI app can drive it. It replaces the ad-hoc runner sprawl with a
single, traceable entry point.

Flow per job:
    synopsis + constraints
        → resolve canonical policy (contract + effective policy snapshot)
        → GENESIS2 (12 phases, local Ollama)
        → bridge → movie_os brief
        → freeze PKP (immutable production contract)
        → PROMETHEUS pipeline (storyboard → images → voice → music → editing → film)
        → final MP4 under productions/<episode>/runs/<run_id>/render/
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

logger = logging.getLogger("production_service")

# Local model preference — qwen3:4b is the primary local model for GENESIS2.
PREFERRED_MODELS = ["qwen3:4b", "qwen3.6:latest", "ornith:lite", "deepseek-coder-v2:latest"]


def _model_num_ctx(model_name: str) -> int:
    if model_name == "qwen3:4b":
        return 131072
    if model_name == "qwen3.6:latest":
        return 131072
    if model_name == "ornith:lite":
        return 65536
    return 4096

# Default synopsis/constraints mirror the validated "Space Between Us" run.
DEFAULT_SYNOPSIS = (
    "After losing his job, a husband named Mark becomes terrified that his wife Sarah will "
    "eventually see him as a failure. Instead of admitting the fear, he slowly withdraws — "
    "short answers at dinner, avoiding eye contact, sleeping in another room, rejecting small "
    "moments of affection. His wife initially thinks he no longer loves her. The emotional "
    "turning point comes when she quietly says, 'You don't have to disappear just because "
    "you're hurting.' He almost responds, but fear wins for one more moment — until he finally "
    "reaches for her hand."
)

DEFAULT_CONSTRAINTS = {
    "runtime": "3-5 minutes",
    "platform": "youtube",
    "grammar": "psychological_cinema",
    "tone_arc": "secure → uneasy → painfully distant → vulnerable → cautiously hopeful",
    "characters": (
        "MARK (38, responsible, loving, proud, emotionally contained; fears being seen as inadequate), "
        "SARAH (36, perceptive, patient, affectionate, increasingly hurt by his silence)"
    ),
    "style": (
        "Cinematic psychological realism. Warm domestic lighting gradually becomes colder as Mark withdraws. "
        "Minimal narration, strong facial micro-expressions, meaningful blocking and distance, restrained piano score."
    ),
}


class ProductionJob:
    """In-memory job record for a production run."""

    def __init__(self, job_id: str, synopsis: str, constraints: dict[str, Any]):
        self.job_id = job_id
        self.synopsis = synopsis
        self.constraints = constraints or {}
        self.status = "queued"  # queued | running | completed | failed
        self.stage = "queued"
        self.error: Optional[str] = None
        self.run_id: Optional[str] = None
        self.output_path: Optional[str] = None
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at
        self.phases: list[dict[str, Any]] = []  # GENESIS2 phase progress
        self.prometheus_stages: list[dict[str, Any]] = []  # stage progress

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "stage": self.stage,
            "error": self.error,
            "run_id": self.run_id,
            "output_path": self.output_path,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "phases": self.phases,
            "prometheus_stages": self.prometheus_stages,
        }


def _ensure_scene_state_fields(brief: dict) -> dict:
    """Fill frozen-PKP scene-state and dialogue fields from the bridged brief.

    Mirrors the logic in run_space_between_us.py so the service produces the
    same validated brief shape.
    """
    scenes = []
    for scene in brief.get("scenes", []) or []:
        scene = dict(scene)
        title = str(scene.get("title") or f"Scene {scene.get('number', '?')}")
        beat = str(scene.get("narrative_beat") or scene.get("act") or "scene")
        scene.setdefault("entry_state", f"{title}: establishes the starting emotional state")
        scene.setdefault("turning_point", f"{title}: the {beat} shifts the relationship")
        scene.setdefault("exit_state", f"{title}: leaves the characters changed for the next scene")
        scene.setdefault("emotional_progression", ["steady", "uneasy", "changed"])
        scene_num = int(scene.get("number") or scene.get("scene_number") or scene.get("id") or 0)
        if not isinstance(scene.get("shot"), dict) or not scene["shot"]:
            speaker = "MARK" if scene_num % 2 == 1 else "SARAH"
            listener = "SARAH" if speaker == "MARK" else "MARK"
            scene["shot"] = {
                "speaker": speaker,
                "listener": listener,
                "function": "speaker coverage",
                "framing": "over-the-shoulder two-shot",
                "performance_intent": scene.get("emotional_progression", ["steady"])[0],
                "visual_intent": f"{speaker} and {listener} in a readable conversational frame",
                "lip_sync_required": True,
            }
        scenes.append(scene)

    existing_dialogues = {}
    for d in brief.get("dialogues", []) or []:
        try:
            scene_num = int(d.get("scene_number"))
        except Exception:
            continue
        existing_dialogues[scene_num] = dict(d)

    dialogues = []
    for idx, scene in enumerate(scenes, start=1):
        scene_num = int(scene.get("number") or idx)
        lead = str(scene.get("title") or f"Scene {scene_num}")
        dialogue = dict(existing_dialogues.get(scene_num) or {})
        if not dialogue:
            speaker = "MARK" if scene_num % 2 == 1 else "SARAH"
            listener = "SARAH" if speaker == "MARK" else "MARK"
            progression = scene.get("emotional_progression", ["steady", "uneasy"])
            dialogue = {
                "scene_number": scene_num,
                "conversation_intent": f"{lead}: keep the scene moving with an honest exchange",
                "subtext": f"{speaker} speaks while {listener} reacts and listens",
                "emotional_state": str(progression[0] if progression else "steady"),
                "lines": [
                    {"speaker": speaker, "text": f"{lead}: I need to tell you something important.", "emotion": str(progression[0] if progression else "steady")},
                    {"speaker": listener, "text": "I am listening.", "emotion": str(progression[1] if len(progression) > 1 else (progression[0] if progression else "uneasy"))},
                ],
                "inner_voice": [],
            }
        dialogue.setdefault("scene_number", scene_num)
        dialogue.setdefault("conversation_intent", f"{lead}: keep the scene moving with an honest exchange")
        dialogue.setdefault("subtext", "Speaker and listener stay in active conversational coverage")
        dialogue.setdefault("emotional_state", str(scene.get("emotional_progression", ["steady"])[0]))
        dialogue.setdefault("lines", [])
        if not dialogue["lines"]:
            dialogue["lines"] = [
                {"speaker": "MARK", "text": f"{lead}: I need to tell you something important.", "emotion": str(scene.get("emotional_progression", ["steady"])[0])},
                {"speaker": "SARAH", "text": "I am listening.", "emotion": str(scene.get("emotional_progression", ["steady", "uneasy"])[1 if len(scene.get("emotional_progression", [])) > 1 else 0])},
            ]
        for i, line in enumerate(dialogue["lines"]):
            if not isinstance(line, dict):
                dialogue["lines"][i] = {"speaker": "MARK" if i % 2 == 0 else "SARAH", "text": f"{lead}: I need to tell you something important.", "emotion": "neutral"}
                continue
            if not str(line.get("speaker") or "").strip():
                line["speaker"] = "MARK" if i % 2 == 0 else "SARAH"
            if not str(line.get("text") or "").strip():
                line["text"] = f"{lead}: I need to tell you something important."
            if not str(line.get("emotion") or "").strip():
                line["emotion"] = "neutral"
        dialogue.setdefault("inner_voice", [])
        dialogues.append(dialogue)

    brief = dict(brief)
    brief["scenes"] = scenes
    brief["dialogues"] = dialogues
    return brief


class ProductionService:
    """Job queue + executor for the canonical GENESIS2 → PROMETHEUS path."""

    def __init__(self, max_concurrent: int = 1):
        self._jobs: dict[str, ProductionJob] = {}
        self._tasks: dict[str, asyncio.Task] = {}
        self._max_concurrent = max_concurrent
        self._running = 0

    # ---- public API ------------------------------------------------------

    def submit(self, synopsis: str, constraints: dict[str, Any] | None = None) -> ProductionJob:
        """Queue a new production run. Returns the job immediately."""
        job = ProductionJob(str(uuid.uuid4()), synopsis, constraints or {})
        self._jobs[job.job_id] = job
        # Kick off execution in the background (single-flight per service).
        if self._running < self._max_concurrent:
            self._running += 1
            loop = asyncio.get_event_loop()
            self._tasks[job.job_id] = loop.create_task(self._execute(job))
        else:
            job.status = "queued"
        return job

    def get(self, job_id: str) -> Optional[ProductionJob]:
        return self._jobs.get(job_id)

    def list_jobs(self) -> list[dict[str, Any]]:
        return [j.to_dict() for j in self._jobs.values()]

    # ---- execution -------------------------------------------------------

    async def _execute(self, job: ProductionJob) -> None:
        job.status = "running"
        job.stage = "policy"
        job.updated_at = datetime.now(timezone.utc).isoformat()
        try:
            await self._run_production(job)
            job.status = "completed"
        except Exception as exc:
            logger.exception("Production job %s failed", job.job_id)
            job.status = "failed"
            job.error = str(exc)
        finally:
            job.stage = "done"
            job.updated_at = datetime.now(timezone.utc).isoformat()
            self._running = max(0, self._running - 1)
            self._tasks.pop(job.job_id, None)
            # Drain any queued jobs.
            for jid, j in self._jobs.items():
                if j.status == "queued" and self._running < self._max_concurrent:
                    self._running += 1
                    loop = asyncio.get_event_loop()
                    self._tasks[jid] = loop.create_task(self._execute(j))
                    break

    async def _run_production(self, job: ProductionJob) -> None:
        from movie_os.runtime_policy import load_and_resolve_canonical_policy
        from movie_os.genesis2 import Genesis2Engine
        from movie_os.genesis2.llm_client import LLMClient
        from movie_os.genesis2.llm_providers import LLMConfig
        from movie_os.runtime_paths import get_production_context

        # Step 0: Episode Contract + Effective Policy Snapshot
        job.stage = "policy"
        contract, policy_snapshot, _ = load_and_resolve_canonical_policy()
        logger.info("Production %s: contract=%s policy=%s", job.job_id, contract.episode_id, policy_snapshot.policy_snapshot_id)

        # Step 1: GENESIS2 (12 phases, real local Ollama)
        job.stage = "genesis"
        last_exc = None
        pkg = None
        for model_name in PREFERRED_MODELS:
            try:
                config = LLMConfig(provider="ollama", model=model_name, timeout=300, max_tokens=4096, num_ctx=_model_num_ctx(model_name))
                client = LLMClient(config=config)
                engine = Genesis2Engine(llm=client, on_progress=self._on_genesis_progress(job))
                logger.info("Production %s: GENESIS2 using model %s", job.job_id, model_name)
                pkg = await engine.run_async(synopsis=job.synopsis, constraints=job.constraints)
                break
            except Exception as exc:
                last_exc = exc
                logger.warning("Production %s: GENESIS2 failed with %s: %s", job.job_id, model_name, exc)
                pkg = None
        if pkg is None:
            raise RuntimeError(f"GENESIS2 failed with all local models: {last_exc}")

        production = {
            "episode_id": contract.episode_id,
            "run_id": f"RUN-{time.strftime('%Y%m%d-%H%M%S')}",
        }
        job.run_id = production["run_id"]
        prod_ctx = get_production_context({"production": production})
        production_root = Path(prod_ctx["production_root"])
        run_root = Path(prod_ctx["run_root"])
        for sub in ["contract", "policy", "genesis", "runs", "oracle", "releases"]:
            (production_root / sub).mkdir(parents=True, exist_ok=True)
        for sub in ["images", "voice", "music", "motion", "render", "manifest"]:
            (run_root / sub).mkdir(parents=True, exist_ok=True)

        # Save PKP
        output_dir = run_root / "genesis"
        output_dir.mkdir(parents=True, exist_ok=True)
        pkg_path = output_dir / "production_knowledge_package.json"
        pkg_path.write_text(json.dumps(pkg.model_dump(), indent=2, default=str), encoding="utf-8")

        # Step 2: Bridge → brief
        job.stage = "bridge"
        from movie_os.genesis2.bridge import Genesis2Bridge
        from movie_os.frozen_pkp import freeze_from_brief
        bridge = Genesis2Bridge(pkg)
        brief = _ensure_scene_state_fields(bridge.to_brief())
        brief["production"] = production
        brief["policy_snapshot_id"] = policy_snapshot.policy_snapshot_id
        brief["production_paths"] = {
            "production_root": str(production_root),
            "run_root": str(run_root),
        }
        brief_path = output_dir / "movie_os_brief.json"
        brief_path.write_text(json.dumps(brief, indent=2, default=str), encoding="utf-8")

        frozen_pkp = freeze_from_brief(
            episode_id=contract.episode_id,
            policy_snapshot_id=policy_snapshot.policy_snapshot_id,
            episode_contract_id=contract.episode_id,
            episode_contract_hash=policy_snapshot.snapshot_hash,
            policy_snapshot_hash=policy_snapshot.snapshot_hash,
            production=production,
            brief=brief,
        )
        brief["frozen_pkp"] = frozen_pkp.model_dump()
        (output_dir / "pkp").mkdir(parents=True, exist_ok=True)
        pkp_path = output_dir / "pkp" / f"{frozen_pkp.pkp_id}.yaml"
        pkp_path.write_text(json.dumps(frozen_pkp.model_dump(), indent=2, default=str), encoding="utf-8")
        (output_dir / "pkp" / "freeze_manifest.json").write_text(
            json.dumps({"pkp_id": frozen_pkp.pkp_id, "content_hash": frozen_pkp.content_hash}, indent=2), encoding="utf-8"
        )

        # Step 3: PROMETHEUS pipeline
        job.stage = "prometheus"
        from movie_os.prometheus.pipeline import PrometheusPipeline, PipelineConfig
        from movie_os.prometheus.models import ProductionCertificate, CertificationStatus, Director

        cert = ProductionCertificate(
            certificate_id="space-between-us-001",
            project_name=brief["title"],
            status=CertificationStatus.PRODUCTION_READY,
            reviewed_by=Director(name="Genesis2"),
            blueprint={"scenes": brief["scenes"]},
        )
        prom_brief = dict(brief)
        prom_brief["image_artifacts"] = [{"id": s.get("number", i + 1)} for i, s in enumerate(brief["scenes"])]

        pipeline = PrometheusPipeline(config=PipelineConfig(output_dir=str(run_root / "render")))
        result = await pipeline.execute(cert, prom_brief)

        # Record stage progress
        for s in result.stages:
            job.prometheus_stages.append({
                "name": s.name,
                "status": s.status.value if hasattr(s.status, "value") else str(s.status),
                "artifacts": len(s.artifacts),
            })

        result_path = run_root / "manifest" / "prometheus_result.json"
        result_path.write_text(json.dumps(result.model_dump(), indent=2, default=str), encoding="utf-8")

        # Locate the final MP4
        final_mp4 = None
        for s in result.stages:
            if s.name == "Film":
                for art in s.artifacts:
                    if isinstance(art, dict) and art.get("type") == "film":
                        p = Path(art.get("path", ""))
                        if p.exists() and p.stat().st_size > 10000:
                            final_mp4 = str(p)
        if final_mp4 is None:
            # Fall back to scanning the render dir
            for p in sorted((run_root / "render").glob("*_final.mp4")):
                if p.stat().st_size > 10000:
                    final_mp4 = str(p)
                    break
        job.output_path = final_mp4
        job.stage = "film"
        logger.info("Production %s: final MP4 = %s", job.job_id, final_mp4)

    def _on_genesis_progress(self, job: ProductionJob):
        def cb(phase_num: int, phase_name: str, status, detail: str = "") -> None:
            job.phases.append({
                "phase_number": phase_num,
                "phase_name": phase_name,
                "status": status.value if hasattr(status, "value") else str(status),
                "detail": detail,
            })
            job.updated_at = datetime.now(timezone.utc).isoformat()
        return cb
