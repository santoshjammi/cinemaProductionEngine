#!/usr/bin/env python3
"""Re-run PROMETHEUS on the existing verified brief with the fixed (fp8 high-quality)
image pipeline. Reuses the already-rendered fp8 scene images, regenerates voice/music,
and assembles a new high-quality film. Skips the flaky GENESIS story stage."""

import asyncio, json, logging, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_prometheus_hq")

BRIEF_PATH = ROOT / "output" / "space_between_us" / "movie_os_brief.json"
OUT_DIR = ROOT / "output" / "space_between_us" / "prometheus_hq"


async def main():
    from movie_os.prometheus.pipeline import PrometheusPipeline, PipelineConfig
    from movie_os.prometheus.models import ProductionCertificate, CertificationStatus, Director

    print("=" * 60)
    print("  PROMETHEUS HQ — high-quality (fp8 production) re-render")
    print("=" * 60)

    brief = json.loads(BRIEF_PATH.read_text(encoding="utf-8"))
    print(f"  Title   : {brief['title']}")
    print(f"  Scenes  : {len(brief['scenes'])}")
    print(f"  Output  : {OUT_DIR}")

    cert = ProductionCertificate(
        certificate_id="space-between-us-hq-001",
        project_name=brief["title"],
        status=CertificationStatus.PRODUCTION_READY,
        reviewed_by=Director(name="Prometheus-HQ"),
        blueprint={"scenes": brief["scenes"]},
    )

    prom_brief = dict(brief)
    prom_brief["image_artifacts"] = [{"id": s.get("number", i + 1)} for i, s in enumerate(brief["scenes"])]

    pipeline = PrometheusPipeline(config=PipelineConfig(output_dir=str(OUT_DIR)))

    t0 = time.time()
    result = await pipeline.execute(cert, prom_brief)
    elapsed = time.time() - t0

    print(f"\n  Overall status : {result.overall_status.value}")
    for s in result.stages:
        status_val = s.status.value if hasattr(s.status, "value") else str(s.status)
        print(f"    {s.name:20s}: {status_val}  [{len(s.artifacts)} artifacts]")

    result_path = OUT_DIR / "prometheus_result.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result.model_dump(), indent=2, default=str), encoding="utf-8")
    print(f"\n  → Saved result to {result_path}")
    print(f"  → Output path: {result.output_path}")
    print(f"  → Elapsed: {elapsed:.0f}s")
    return {"overall": result.overall_status.value, "output": result.output_path}


if __name__ == "__main__":
    asyncio.run(main())
