"""Genesis2 CLI — command-line interface for the Creative Intelligence Engine."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Optional

from .engine import Genesis2Engine
from .llm_client import LLMClient, MockLLMClient


logger = logging.getLogger("movie_os.genesis2.cli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="genesis2",
        description="Genesis2 — Creative Intelligence Engine",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--mock", action="store_true", help="Use MockLLMClient (no real LLM calls)")
    parser.add_argument("--backend", default="ollama", choices=["ollama", "lmstudio", "mock"],
                        help="LLM backend")
    parser.add_argument("--model", default="qwen2.5:32b", help="LLM model name")

    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Run the full 12-phase Genesis pipeline")
    p_run.add_argument("--synopsis", required=True, help="Path to synopsis text file")
    p_run.add_argument("--output", "-o", default=None, help="Output directory")
    p_run.set_defaults(func=cmd_run)

    p_phases = sub.add_parser("phases", help="List all 12 phases")
    p_phases.set_defaults(func=cmd_phases)

    return parser


def _build_llm(args: argparse.Namespace) -> LLMClient | MockLLMClient:
    if args.mock or args.backend == "mock":
        return MockLLMClient()
    return LLMClient(model=args.model)


def cmd_run(args: argparse.Namespace) -> int:
    synopsis_path = Path(args.synopsis)
    if not synopsis_path.exists():
        print(f"❌ Synopsis file not found: {args.synopsis}", file=sys.stderr)
        return 1

    synopsis = synopsis_path.read_text(encoding="utf-8")
    output_dir = args.output or f"./output/genesis2_{synopsis_path.stem}"

    llm = _build_llm(args)

    print(f"\n🧠 Genesis2 — Creative Intelligence Engine", file=sys.stderr)
    print(f"   Synopsis: {args.synopsis}", file=sys.stderr)
    print(f"   Output:   {output_dir}", file=sys.stderr)
    print(f"   Backend:  {args.backend}", file=sys.stderr)
    print(file=sys.stderr)

    engine = Genesis2Engine(llm=llm)
    pkg = engine.run(synopsis=synopsis)

    written = engine.save_package(pkg, output_dir)

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"  Production Knowledge Package")
    print(f"{'=' * 60}")
    print(f"  Version:    {pkg.version}")
    print(f"  Synopsis:   {pkg.synopsis[:80]}...")
    print(f"  Phases:     {len(pkg.phase_results)}")
    completed = sum(1 for r in pkg.phase_results if r.status.value == "completed")
    failed = sum(1 for r in pkg.phase_results if r.status.value == "failed")
    print(f"  Completed:  {completed}")
    print(f"  Failed:     {failed}")
    print()

    for r in pkg.phase_results:
        icon = "✅" if r.status.value == "completed" else "❌"
        print(f"  {icon} Phase {r.phase_number:02d} {r.phase_name}: {r.status.value} ({r.draft_count} drafts)")
        if r.validation_issues:
            for issue in r.validation_issues:
                print(f"      ⚠ {issue.category}: {issue.description}")
        if r.critique_findings:
            for f in r.critique_findings:
                if f.severity in ("critical", "major"):
                    print(f"      🔍 {f.question}: {f.answer}")

    print()
    total_files = sum(len(v) for v in written.values())
    print(f"  Files written: {total_files}")
    for cat, files in written.items():
        print(f"    {cat}: {len(files)}")
    print(f"{'=' * 60}")
    print()

    return 0 if failed == 0 else 1


def cmd_phases(args: argparse.Namespace) -> int:
    from .phases import PHASE_CLASSES

    print(f"\n{'=' * 60}")
    print(f"  Genesis2 — 12 Creative Intelligence Phases")
    print(f"{'=' * 60}")
    print()

    for cls in PHASE_CLASSES:
        p = cls.__new__(cls)
        print(f"  Phase {p.phase_number:02d}: {p.phase_name}")
        print(f"    Model tier: {p.model_tier}")
        print()

    print(f"  Total: {len(PHASE_CLASSES)} phases")
    print(f"{'=' * 60}")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if getattr(args, "verbose", False) else logging.WARNING,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 2
    return func(args)


if __name__ == "__main__":
    sys.exit(main())
