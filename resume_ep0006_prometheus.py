#!/usr/bin/env python3
"""Resume EP-0006 from the frozen PKP boundary into PROMETHEUS.

Reuses the existing frozen PKP (RUN-20260901-114335) and runs the canonical
PrometheusPipeline (Storyboard -> Image -> Voice -> Music -> Editing -> Film)
which generates real voice clips, FLUX images, and assembles the final MP4.

This is the blocker-repair resume path: it does NOT rerun GENESIS. It feeds
the already-frozen EP-0006 package into PROMETHEUS.
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

RUN_ROOT = ROOT / "productions/EP-0006/runs/RUN-20260901-114335"
PKP_PATH = RUN_ROOT / "genesis/pkp/PKP-EP-0006-v1.yaml"
BRIEF_PATH = RUN_ROOT / "genesis/movie_os_brief.json"


async def main():
    from movie_os.frozen_pkp import validate_frozen_pkp
    from movie_os.prometheus.pipeline import PrometheusPipeline, PipelineConfig
    from movie_os.prometheus.models import ProductionCertificate, CertificationStatus, Director

    print("=" * 60)
    print("  EP-0006 RESUME — frozen PKP -> PROMETHEUS")
    print("=" * 60)

    # Load the frozen PKP and validate it.
    pkp_data = json.loads(PKP_PATH.read_text(encoding="utf-8"))
    pkp = validate_frozen_pkp(
        pkp_data,
        expected_episode_id="EP-0006",
        expected_policy_snapshot_id="POLICY-EP-0006-13e83544f37a",
    )
    print(f"  Frozen PKP : {pkp.pkp_id}  hash={pkp.content_hash[:16]}...")
    print(f"  Shots      : {len(pkp.shots.get('shots', []))}")

    # Load the brief and attach the frozen PKP (the pipeline requires it).
    brief = json.loads(BRIEF_PATH.read_text(encoding="utf-8"))
    brief["frozen_pkp"] = pkp_data
    brief["production"] = {"episode_id": "EP-0006", "run_id": "RUN-20260901-114335"}
    brief["policy_snapshot_id"] = "POLICY-EP-0006-13e83544f37a"
    brief["production_paths"] = {
        "production_root": str(RUN_ROOT.parent),
        "run_root": str(RUN_ROOT),
    }
    # Character preparation — ensure the brief carries the character_consistency
    # block (idempotent; re-injects if the brief predates the GENESIS step).
    from movie_os.genesis2.character_prep import prepare_characters
    prepare_characters(brief)
    # The pipeline's image stage reads storyboard_artifacts; seed it from scenes
    # so all 5 scenes render (or reuse existing consistent images).
    brief.setdefault("storyboard_artifacts", [
        {
            "id": s.get("number", i + 1),
            "scene_number": s.get("number", i + 1),
            "description": s.get("description", ""),
            "metadata": {
                "camera_angle": (s.get("shot", {}) or {}).get("camera_angle", "medium")
                if isinstance(s.get("shot", {}), dict) else "medium",
                "lighting": s.get("lighting", "natural"),
            },
        }
        for i, s in enumerate(brief.get("scenes", []))
    ])

    # Build a production-ready certificate.
    cert = ProductionCertificate(
        certificate_id="ep0006-resume-001",
        project_name=brief.get("title", "EP-0006"),
        status=CertificationStatus.PRODUCTION_READY,
        reviewed_by=Director(name="Genesis2"),
        blueprint={"scenes": brief.get("scenes", [])},
    )

    pipeline = PrometheusPipeline(config=PipelineConfig(output_dir=str(RUN_ROOT / "render")))
    result = await pipeline.execute(cert, brief)

    print(f"\n  Overall status : {result.overall_status.value}")
    for s in result.stages:
        status_val = s.status.value if hasattr(s.status, "value") else str(s.status)
        print(f"    {s.name:20s}: {status_val}  [{len(s.artifacts)} artifacts]")

    result_path = RUN_ROOT / "manifest" / "prometheus_result.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result.model_dump(), indent=2, default=str), encoding="utf-8")
    print(f"  -> Saved result to {result_path}")
    print(f"  -> Output path: {result.output_path}")
    return result


if __name__ == "__main__":
    asyncio.run(main())
