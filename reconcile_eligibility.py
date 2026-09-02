#!/usr/bin/env python3
"""Evaluate a GENESIS run's freeze eligibility and emit a reconciliation report.

Usage:
    ./venv/bin/python scripts/run_freeze_eligibility.py productions/EP-0001/runs/RUN-XXX

Reads the run's production_knowledge_package.json + movie_os_brief.json, runs the
deterministic freeze-eligibility gate (P0-01/P0-03) and writes
``manifest/freeze_eligibility.json`` plus a human summary to stdout.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from movie_os.genesis2.freeze_gate import evaluate_genesis_freeze_eligibility


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: reconcile_eligibility.py <run_root>", file=sys.stderr)
        return 2
    run_root = Path(argv[1])
    genesis_dir = run_root / "genesis"
    pkg_path = genesis_dir / "production_knowledge_package.json"
    brief_path = genesis_dir / "movie_os_brief.json"
    if not pkg_path.exists() or not brief_path.exists():
        print(f"missing genesis artifacts under {genesis_dir}", file=sys.stderr)
        return 1
    pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    brief = json.loads(brief_path.read_text(encoding="utf-8"))
    narrative_contract = brief.get("narrative_contract") or {}
    res = evaluate_genesis_freeze_eligibility(
        pkg,
        brief,
        resolution_requirement=narrative_contract.get("resolution_requirement", "REQUIRED"),
        narrative_structure=narrative_contract.get("narrative_structure", "LINEAR"),
    )
    report = {
        "run_root": str(run_root),
        "freeze_allowed": res.freeze_allowed,
        "blocking_reasons": res.blocking_reasons,
        "warnings": res.warnings,
        "summary": res.summary,
    }
    out = run_root / "genesis" / "freeze_eligibility.json"
    out.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"freeze_allowed: {res.freeze_allowed}")
    print(f"report: {out}")
    for b in res.blocking_reasons:
        print(f"  BLOCK  {b.get('code','?')} @ {b.get('phase','?')}: {b.get('detail','')[:90]}")
    rec = res.summary.get("cross_phase_reconciliation") or {}
    cov = rec.get("required_coverage") or {}
    print(f"coverage: {cov.get('preserved',0)}/{cov.get('total',0)} = {cov.get('percentage','?')}%")
    return 0 if res.freeze_allowed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
