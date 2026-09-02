"""Genesis2 Engine — orchestrates all 12 phases of the Creative Intelligence pipeline.

Every phase runs: Draft → Review → Critique → Improve → Validate → Freeze.
No phase proceeds until validation succeeds.
Supports progress callbacks, revision loops, and human-in-the-loop questions.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import Any, Callable, Optional

from .llm_client import LLMClient, MockLLMClient
from .models import (
    PhaseResult,
    PhaseStatus,
    ProductionKnowledgePackage,
)
from .phase_context import RunContext
from .phases import PHASE_CLASSES

logger = logging.getLogger("movie_os.genesis2.engine")

ProgressCallback = Callable[[int, str, PhaseStatus, str], None]
"""Callback(phase_number, phase_name, status, detail)"""


class Genesis2Engine:
    """Creative Intelligence Engine — 12-phase pipeline.

    Usage:
        engine = Genesis2Engine(llm=LLMClient())
        pkg = engine.run(synopsis="A man withdraws from his wife...")

    For progress reporting:
        def on_progress(phase_num, phase_name, status, detail):
            print(f"Phase {phase_num}: {status.value} - {detail}")
        engine = Genesis2Engine(llm=llm, on_progress=on_progress)
    """

    def __init__(
        self,
        llm: LLMClient | MockLLMClient | None = None,
        on_progress: ProgressCallback | None = None,
        max_revision_attempts: int = 0,
    ):
        self.llm = llm or MockLLMClient()
        self.on_progress = on_progress
        self.max_revision_attempts = max_revision_attempts

    def _progress(self, phase_num: int, phase_name: str, status: PhaseStatus, detail: str = "") -> None:
        if self.on_progress:
            self.on_progress(phase_num, phase_name, status, detail)

    def run(
        self,
        synopsis: str,
        constraints: dict[str, Any] | None = None,
    ) -> ProductionKnowledgePackage:
        """Run the full 12-phase Genesis pipeline."""
        return asyncio.run(self.run_async(synopsis, constraints))

    async def run_async(
        self,
        synopsis: str,
        constraints: dict[str, Any] | None = None,
        checkpoint_dir: str | Path | None = None,
    ) -> ProductionKnowledgePackage:
        """Run the full 12-phase pipeline asynchronously."""
        constraints = constraints or {}
        episode_id = constraints.get("episode_id", "")
        run_id = constraints.get("run_id", "")
        policy_id = constraints.get("policy_snapshot_id", constraints.get("policy_id", ""))
        policy_hash = constraints.get("policy_hash", "")
        requirement_manifest_hash = constraints.get("requirement_manifest_hash", "")
        pkg = ProductionKnowledgePackage(
            episode_id=episode_id,
            run_id=run_id,
            policy_snapshot_id=policy_id,
            synopsis=synopsis,
            constraints=constraints,
        )

        run_context = RunContext(
            production_id=episode_id,
            run_id=run_id,
            policy_id=policy_id,
            policy_hash=policy_hash,
            requirement_manifest_hash=requirement_manifest_hash,
            mode=str(constraints.get("mode", "RUNTIME")),
            source_run_id=str(constraints.get("source_run_id", run_id)),
            source_episode_id=str(constraints.get("source_episode_id", episode_id)),
        )

        context: dict[str, Any] = {
            "synopsis": synopsis,
            "constraints": constraints,
            "run_context": run_context.model_dump(),
            "run_id": run_id,
            "episode_id": episode_id,
            "policy_snapshot_id": policy_id,
        }

        prev_hash: str | None = None
        for phase_cls in PHASE_CLASSES:
            phase = phase_cls(self.llm)
            phase_num = phase.phase_number
            phase_name = phase.phase_name

            loaded: PhaseResult | None = None
            if checkpoint_dir is not None and phase_num <= 7:
                loaded = self._load_checkpoint_if_valid(checkpoint_dir, pkg, phase_num, prev_hash)
            if loaded is not None:
                prev_hash = self._apply_loaded_result(pkg, phase_num, loaded, context)
                continue

            self._progress(phase_num, phase_name, PhaseStatus.DRAFTING, "Starting")

            result = await phase.run(context)

            # Revision loop: if validation failed, re-run with accumulated context
            for attempt in range(self.max_revision_attempts):
                if result.status != PhaseStatus.FAILED:
                    break
                self._progress(
                    phase_num, phase_name, PhaseStatus.IMPROVING,
                    f"Revision attempt {attempt + 1}/{self.max_revision_attempts}"
                )
                # Re-run the phase — it will see its own previous output in context
                result = await phase.run(context)

            # Store result
            pkg.phase_results.append(result)

            # Store knowledge in context for downstream phases
            phase_key = f"phase_{phase.phase_number:02d}"
            if result.knowledge:
                context[phase_key] = result.knowledge.model_dump()

            # Map to PKG fields
            self._map_to_pkg(pkg, phase.phase_number, result)

            status = result.status
            self._progress(
                phase_num, phase_name, status,
                f"{result.draft_count} drafts, {len(result.validation_issues)} issues"
            )

            if status == PhaseStatus.FAILED:
                logger.warning(
                    f"[Genesis2] Phase {phase_num} failed after "
                    f"{result.draft_count} drafts and {self.max_revision_attempts} revisions."
                )
                break

        return pkg

    def _map_to_pkg(self, pkg: ProductionKnowledgePackage, phase_number: int, result: PhaseResult) -> None:
        """Map phase result to the appropriate PKG field."""
        if not result.knowledge:
            return
        mapping = {
            1: ("creative_understanding", "CreativeUnderstanding"),
            2: ("story_foundation", "StoryFoundation"),
            3: ("character_psychology", "CharacterPsychology"),
            4: ("world_development", "WorldDevelopment"),
            5: ("narrative_expansion", "NarrativeExpansion"),
            6: ("scene_planning", "ScenePlanning"),
            7: ("dialogue_planning", "DialoguePlanning"),
            8: ("visual_language", "VisualLanguage"),
            9: ("production_specifications", "ProductionSpecifications"),
            10: ("validation", "Validation"),
            11: ("creative_critique", "CreativeCritique"),
            12: ("knowledge_integration", "KnowledgeIntegration"),
        }
        if phase_number in mapping:
            attr_name, _ = mapping[phase_number]
            setattr(pkg, attr_name, result.knowledge)

    def _checkpoint_payload(self, pkg: ProductionKnowledgePackage, result: PhaseResult, dependencies: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        phase_data = result.model_dump()
        content_hash = hashlib.sha256(
            json.dumps(phase_data, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()
        return {
            "checkpoint": {
                "phase": result.phase_number,
                "phase_name": result.phase_name,
                "phase_schema_version": 1,
                "episode_id": pkg.episode_id,
                "run_id": pkg.run_id,
                "policy_snapshot_id": pkg.policy_snapshot_id,
                "status": "VALID" if result.status == PhaseStatus.COMPLETED else result.status.value.upper(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "content_hash": content_hash,
                "dependencies": dependencies or [],
            },
            "result": phase_data,
        }

    @staticmethod
    def _checkpoint_file_name(result: Any) -> str:
        phase_number = getattr(result, "phase_number", 0)
        phase_name = getattr(result, "phase_name", "phase")
        return f"phase_{phase_number:02d}_{phase_name.lower().replace(' ', '_')}.json"

    @classmethod
    def write_phase_checkpoint(cls, output_dir: str | Path, pkg: Any, result: Any, dependencies: list[dict[str, Any]] | None = None) -> Path:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        path = out / cls._checkpoint_file_name(result)
        tmp = path.with_suffix(path.suffix + ".tmp")
        phase_data = result.model_dump() if hasattr(result, "model_dump") else dict(result)
        pkg_obj = pkg if hasattr(pkg, "episode_id") else None
        deps: list[dict[str, Any]] = list(dependencies or [])
        checkpoint = {
            "phase": getattr(result, "phase_number", 0),
            "phase_name": getattr(result, "phase_name", ""),
            "phase_schema_version": 1,
            "episode_id": getattr(pkg_obj, "episode_id", ""),
            "run_id": getattr(pkg_obj, "run_id", ""),
            "policy_snapshot_id": getattr(pkg_obj, "policy_snapshot_id", ""),
            "status": getattr(getattr(result, "status", None), "value", "VALID"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "content_hash": hashlib.sha256(json.dumps(phase_data, sort_keys=True, default=str).encode("utf-8")).hexdigest(),
            "dependencies": deps,
        }
        tmp.write_text(json.dumps({"checkpoint": checkpoint, "result": phase_data}, indent=2, default=str), encoding="utf-8")
        tmp.replace(path)
        return path

    @classmethod
    def read_phase_checkpoint(cls, path: str | Path) -> dict[str, Any]:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if "checkpoint" not in data or "result" not in data:
            raise ValueError("invalid checkpoint format")
        checkpoint = data["checkpoint"]
        phase_data = data["result"]
        expected = hashlib.sha256(
            json.dumps(phase_data, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()
        if checkpoint.get("content_hash") != expected:
            raise ValueError("checkpoint content hash mismatch")
        return data

    def _load_checkpoint_if_valid(
        self,
        checkpoint_dir: str | Path,
        pkg: ProductionKnowledgePackage,
        phase_number: int,
        expected_dependency_hash: str | None,
    ) -> PhaseResult | None:
        path = Path(checkpoint_dir) / f"phase_{phase_number:02d}_"
        matches = sorted(path.parent.glob(f"phase_{phase_number:02d}_*.json"))
        if not matches:
            return None
        cp_path = matches[0]
        data = self.read_phase_checkpoint(cp_path)
        meta = data["checkpoint"]
        if meta.get("episode_id") != pkg.episode_id or meta.get("run_id") != pkg.run_id or meta.get("policy_snapshot_id") != pkg.policy_snapshot_id:
            raise ValueError("checkpoint provenance mismatch")
        if meta.get("phase") != phase_number or meta.get("phase_schema_version") != 1:
            raise ValueError("checkpoint schema mismatch")
        deps = meta.get("dependencies", []) or []
        if expected_dependency_hash is not None:
            if not deps or deps[-1].get("phase") != phase_number - 1:
                raise ValueError("checkpoint dependency mismatch")
        phase_cls = PHASE_CLASSES[phase_number - 1]
        phase = phase_cls(self.llm)
        result = PhaseResult.model_validate(data["result"])
        result.status = PhaseStatus.COMPLETED
        phase.result = result
        return result

    def _apply_loaded_result(self, pkg: ProductionKnowledgePackage, phase_number: int, result: PhaseResult, context: dict[str, Any]) -> str:
        pkg.phase_results.append(result)
        phase_key = f"phase_{phase_number:02d}"
        if result.knowledge:
            context[phase_key] = result.knowledge.model_dump()
        self._map_to_pkg(pkg, phase_number, result)
        self._progress(phase_number, result.phase_name, PhaseStatus.COMPLETED, "loaded from checkpoint")
        return hashlib.sha256(json.dumps(result.model_dump(), sort_keys=True, default=str).encode("utf-8")).hexdigest()

    def save_package(self, pkg: ProductionKnowledgePackage, output_dir: str | Path) -> dict[str, list[Path]]:
        """Save the Production Knowledge Package to disk."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        written: dict[str, list[Path]] = {
            "package": [],
            "phases": [],
            "summary": [],
        }

        pkg_path = out / "production_knowledge_package.json"
        pkg_path.write_text(
            json.dumps(pkg.model_dump(), indent=2, default=str),
            encoding="utf-8",
        )
        written["package"].append(pkg_path)

        phases_dir = out / "phases"
        phases_dir.mkdir(exist_ok=True)
        prev_hash: str | None = None
        for idx, result in enumerate(pkg.phase_results):
            dependencies = []
            if prev_hash is not None:
                dependencies.append({"phase": pkg.phase_results[idx - 1].phase_number, "content_hash": prev_hash})
            phase_path = self.write_phase_checkpoint(phases_dir, pkg, result, dependencies=dependencies)
            written["phases"].append(phase_path)
            prev_hash = hashlib.sha256(json.dumps(result.model_dump(), sort_keys=True, default=str).encode("utf-8")).hexdigest()

        summary_path = out / "summary.json"
        summary = {
            "synopsis": pkg.synopsis[:200],
            "version": pkg.version,
            "created_at": pkg.created_at,
            "phases": [
                {
                    "number": r.phase_number,
                    "name": r.phase_name,
                    "status": r.status.value,
                    "draft_count": r.draft_count,
                    "validation_issues": len(r.validation_issues),
                    "critique_findings": len(r.critique_findings),
                }
                for r in pkg.phase_results
            ],
            "total_phases": len(pkg.phase_results),
            "completed_phases": sum(1 for r in pkg.phase_results if r.status == PhaseStatus.COMPLETED),
            "failed_phases": sum(1 for r in pkg.phase_results if r.status == PhaseStatus.FAILED),
        }
        summary_path.write_text(
            json.dumps(summary, indent=2, default=str),
            encoding="utf-8",
        )
        written["summary"].append(summary_path)

        return written

    @classmethod
    def run_with_ollama(
        cls,
        synopsis: str,
        model: str = "ornith:9b",
        constraints: dict[str, Any] | None = None,
        on_progress: ProgressCallback | None = None,
    ) -> ProductionKnowledgePackage:
        """Run the Genesis2 pipeline using real Ollama inference.

        Args:
            synopsis: Story synopsis to analyze.
            model: Ollama model name (default: ornith:9b).
            constraints: Optional constraints dict.
            on_progress: Optional progress callback.

        Returns:
            ProductionKnowledgePackage with all 12 phase results.
        """
        from .llm_providers import LLMConfig

        config = LLMConfig(provider="ollama", model=model)
        client = LLMClient(config=config)
        return cls(llm=client, on_progress=on_progress).run(synopsis, constraints)
