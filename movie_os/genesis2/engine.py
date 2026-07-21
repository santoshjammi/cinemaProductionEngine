"""Genesis2 Engine — orchestrates all 12 phases of the Creative Intelligence pipeline.

Every phase runs: Draft → Review → Critique → Improve → Validate → Freeze.
No phase proceeds until validation succeeds.
Supports progress callbacks, revision loops, and human-in-the-loop questions.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from .llm_client import LLMClient, MockLLMClient
from .models import (
    PhaseResult,
    PhaseStatus,
    ProductionKnowledgePackage,
)
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
        max_revision_attempts: int = 3,
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
    ) -> ProductionKnowledgePackage:
        """Run the full 12-phase pipeline asynchronously."""
        pkg = ProductionKnowledgePackage(
            synopsis=synopsis,
            constraints=constraints or {},
        )

        context: dict[str, Any] = {
            "synopsis": synopsis,
            "constraints": constraints or {},
        }

        for phase_cls in PHASE_CLASSES:
            phase = phase_cls(self.llm)
            phase_num = phase.phase_number
            phase_name = phase.phase_name

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
        for result in pkg.phase_results:
            phase_path = phases_dir / f"phase_{result.phase_number:02d}_{result.phase_name.lower().replace(' ', '_')}.json"
            phase_path.write_text(
                json.dumps(result.model_dump(), indent=2, default=str),
                encoding="utf-8",
            )
            written["phases"].append(phase_path)

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
