#!/usr/bin/env python3
"""Genesis-to-PROMETHEUS handoff script.

Chains: Genesis engine → GenesisPrometheusAdapter → PROMETHEUS pipeline.

Usage:
    ./venv/bin/python run_genesis_to_prometheus.py --synopsis ./synopsis/001.md
    ./venv/bin/python run_genesis_to_prometheus.py --synopsis ./synopsis/001.md --mock
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

logger = logging.getLogger("run_genesis_to_prometheus")


def main():
    parser = argparse.ArgumentParser(
        description="Genesis → PROMETHEUS handoff pipeline"
    )
    parser.add_argument("--synopsis", required=True, help="Path to synopsis file")
    parser.add_argument("--mock", action="store_true", help="Use mock LLM (no real calls)")
    parser.add_argument("--output", "-o", default="./output/genesis_to_prometheus",
                        help="Output directory")
    args = parser.parse_args()

    # Read synopsis
    synopsis_path = Path(args.synopsis)
    if not synopsis_path.exists():
        print(f"❌ Synopsis not found: {synopsis_path}")
        sys.exit(1)
    synopsis = synopsis_path.read_text().strip()

    # Run Genesis
    print(f"\n🎬 Genesis → PROMETHEUS Handoff")
    print(f"   Synopsis: {args.synopsis}")
    print(f"   Mock: {args.mock}")

    from movie_os.genesis.engine import GenesisEngine
    from movie_os.genesis.llm_factory import create_client, create_tiered_clients

    if args.mock:
        llm = create_client(mock=True)
    else:
        llm = create_client()

    engine = GenesisEngine(llm=llm)
    print("\n📋 Running Genesis pre-production pipeline...")
    result = asyncio.run(engine.run_async(synopsis))
    gate_passed = result["gate_result"]["passed"]
    completeness = result["overall_completeness"]
    print(f"   Gate: {'✅ PASSED' if gate_passed else '❌ FAILED'}")
    print(f"   Completeness: {completeness:.0%}")
    print(f"   Session: {result['session_id'][:20]}")

    # Convert to ProductionCertificate
    print("\n📦 Converting to PROMETHEUS certificate...")
    from movie_os.genesis2.genesis_to_prometheus import GenesisPrometheusAdapter
    adapter = GenesisPrometheusAdapter(project_name=synopsis[:50])
    certificate = adapter.convert(result)
    print(f"   Status: {certificate.status.value}")
    print(f"   Blueprint scenes: {len(certificate.blueprint.get('scenes', []))}")
    print(f"   Production ready: {certificate.production_ready}")

    # Save certificate
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    cert_path = output_dir / "certificate.json"
    cert_path.write_text(certificate.model_dump_json(indent=2))
    print(f"   Certificate saved: {cert_path}")

    # Handoff to PROMETHEUS if production-ready
    if certificate.production_ready:
        print("\n🎥 Handing off to PROMETHEUS pipeline...")
        from movie_os.prometheus.engine import PrometheusEngine
        prometheus = PrometheusEngine()
        prom_result = asyncio.run(prometheus.produce(certificate))
        stage_summary = prom_result.get("stage_summary", [])
        artifacts = prom_result.get("artifact_dicts", [])
        prom_result_model = prom_result.get("result")
        print(f"   Stages: {len(stage_summary)}")
        print(f"   Artifacts: {len(artifacts)}")
        if prom_result_model:
            print(f"   Status: {prom_result_model.overall_status.value}")
        result_path = output_dir / "prometheus_result.json"
        result_path.write_text(json.dumps(prom_result, indent=2, default=str))
        print(f"   Result saved: {result_path}")
    else:
        print(f"\n⏸️  Certificate not production-ready ({certificate.status.value}).")
        print(f"   Gate blockers: {result['gate_result'].get('blockers', [])}")
        print(f"   Run with --mock for a full test, or improve the pipeline.")

    print(f"\n✅ Handoff complete. Output: {output_dir}")


if __name__ == "__main__":
    main()