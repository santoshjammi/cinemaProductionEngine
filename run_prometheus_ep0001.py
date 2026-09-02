#!/usr/bin/env python3
"""PROMETHEUS vertical slice for EP-0001 from the frozen PKP.

Loads the frozen PKP (RUN-20260828-161752), reconstructs the brief the
PROMETHEUS pipeline expects, and runs the real 6-stage pipeline to produce
the first watchable MP4.

Stages: Storyboard -> ImageGeneration (FLUX/ComfyUI) -> Voice (edge-tts)
        -> Music (CC0) -> Editing -> Film (ffmpeg assembly).
"""
from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_prometheus_ep0001")

PKP_PATH = ROOT / "productions/EP-0001/runs/RUN-20260828-161752/genesis/pkp/PKP-EP-0001-v1.yaml"
RUN_ROOT = ROOT / "productions/EP-0001/runs/RUN-20260828-161752"


def _build_brief(pkp: dict) -> dict:
    """Reconstruct the PROMETHEUS brief from the frozen PKP."""
    sp = pkp.get("screenplay", {})
    scenes = []
    for sc in sp.get("scenes", []):
        scenes.append({
            "number": sc.get("scene_id"),
            "scene_number": sc.get("scene_id"),
            "title": sc.get("narrative_function", f"Scene {sc.get('scene_id')}"),
            "narrative_beat": sc.get("narrative_function"),
            "scene_description": sc.get("entry_state", ""),
            "emotional_state": (sc.get("emotional_progression") or ["neutral"])[0],
            "characters_present": ["Mark", "Sarah"],
        })
    dialogues = []
    for sc in sp.get("scenes", []):
        lines = []
        for ln in sc.get("dialogue", []):
            lines.append({
                "line_id": ln.get("line_id"),
                "speaker": ln.get("speaker"),
                "text": ln.get("text"),
                "emotion": ln.get("emotional_state", "neutral"),
                "delivery_intent": ln.get("delivery_intent", ""),
                "subtext": ln.get("subtext", ""),
                "character_voice_id": ln.get("character_voice_id", ""),
                "presentation_mode": ln.get("presentation_mode", "EXTERNAL"),
            })
        dialogues.append({"scene_number": sc.get("scene_id"), "lines": lines, "inner_voice": []})

    shots = pkp.get("shots", {}).get("shots", [])

    brief = {
        "title": "The Email Mark Wouldn't Open",
        "logline": pkp.get("story", {}).get("logline", ""),
        "synopsis": pkp.get("story", {}).get("synopsis", ""),
        "scenes": scenes,
        "dialogues": dialogues,
        "shots": shots,
        "production": pkp.get("production", {}),
        "policy_snapshot_id": pkp.get("policy_snapshot_id", ""),
        "frozen_pkp": pkp,
        "resolution": 1024,
        "aspect_ratio": "16:9",
        "bpm": 90,
    }
    return brief


async def main():
    print("=" * 60)
    print("  PROMETHEUS — EP-0001 vertical slice (first watchable MP4)")
    print("=" * 60)

    pkp = json.loads(PKP_PATH.read_text(encoding="utf-8"))
    print(f"  PKP      : {pkp.get('pkp_id')} (status={pkp.get('status')})")
    print(f"  Scenes   : {len(pkp.get('screenplay', {}).get('scenes', []))}")
    print(f"  Shots    : {len(pkp.get('shots', {}).get('shots', []))}")

    brief = _build_brief(pkp)

    from movie_os.prometheus.pipeline import PrometheusPipeline, PipelineConfig
    from movie_os.prometheus.models import ProductionCertificate, CertificationStatus, Director

    cert = ProductionCertificate(
        certificate_id="ep0001-prometheus-001",
        project_name=brief["title"],
        status=CertificationStatus.PRODUCTION_READY,
        reviewed_by=Director(name="Prometheus"),
        blueprint={"scenes": brief["scenes"]},
    )

    prom_brief = dict(brief)
    prom_brief["image_artifacts"] = [{"id": s.get("number", i + 1)} for i, s in enumerate(brief["scenes"])]

    pipeline = PrometheusPipeline(config=PipelineConfig(output_dir=str(RUN_ROOT / "render")))

    t0 = time.time()
    result = await pipeline.execute(cert, prom_brief)
    elapsed = time.time() - t0

    print(f"\n  Overall status : {result.overall_status.value}")
    for s in result.stages:
        status_val = s.status.value if hasattr(s.status, "value") else str(s.status)
        print(f"    {s.name:20s}: {status_val}  [{len(s.artifacts)} artifacts]")

    result_path = RUN_ROOT / "manifest" / "prometheus_result.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result.model_dump(), indent=2, default=str), encoding="utf-8")
    print(f"\n  → Saved result to {result_path}")
    print(f"  → Output path: {result.output_path}")
    print(f"  → Elapsed: {elapsed:.0f}s")
    return {"overall": result.overall_status.value, "output": result.output_path}


if __name__ == "__main__":
    asyncio.run(main())
