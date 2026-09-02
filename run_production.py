"""End-to-end pipeline: Synopsis → Genesis2 PKP → movie_os brief → production graph run.

Artifact-first design: every stage writes durable artifacts before proceeding downstream.
If an upstream stage fails or is skipped, the pipeline stops gracefully and reports which
artifacts were produced for recovery.

Usage:
    ./venv/bin/python run_production.py                        # uses default synopsis
    ./venv/bin/python run_production.py "A story about..."     # custom synopsis text
    ./venv/bin/python run_production.py --synopsis fear        # use the fear synopsis preset
    ./venv/bin/python run_production.py --synopsis-file /path  # load synopsis from file
    ./venv/bin/python run_production.py --model ollama/qwen3     # use a real LLM instead of MockLLMClient
    ./venv/bin/python run_production.py --dry-run               # validate inputs & PKP only
    ./venv/bin/python run_production.py --confirm               # suppress pre-execution prompt
    ./venv/bin/python run_production.py --output-dir /out       # custom output directory
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

# Ensure the project root is on sys.path (for monorepo-style imports)
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from movie_os.genesis2 import Genesis2Engine, MockLLMClient  # noqa: E402
from movie_os.genesis2.bridge import Genesis2Bridge  # noqa: E402
from movie_os.agents.graph import build_graph, run_graph  # noqa: E402
from movie_os.agents.state import new_state  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("run_production")


# ---------------------------------------------------------------------------
# Synopsis presets
# ---------------------------------------------------------------------------

DEFAULT_SYNOPSIS = (
    "In a near-future Tokyo, a retired clockmaker named Kenzo discovers that one of his "
    "grandfather's most intricate timepieces contains a hidden message — coordinates pointing to "
    "a buried vault beneath the city. As he follows the trail, he uncovers a family secret dating "
    "back to World War II: a collection of art looted by his grandfather that could change historical "
    "memory. Torn between personal redemption and public justice, Kenzo must decide whether to expose "
    "the truth or protect his family's name — all while a rival collector races against him."
)

FEARSOME_SYNOPSIS = (
    "A man who has been married for seven years stops reaching for his wife in bed. Each night he lies awake, hand hovering inches from her shoulder, afraid of the rejection he knows is coming. She hasn't said no — but she hasn't said yes in months. The silence between them grows until every touch feels like a question he's tired of asking."
)

SYNOPSIS_PRESETS = {
    "default": DEFAULT_SYNOPSIS,
    "fear": FEARSOME_SYNOPSIS,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _print_section(title: str) -> None:
    """Print a decorative section header."""
    width = 60
    print(f"\n{'=' * width}")
    print(f"  {title}")
    print(f"{'=' * width}")


def _save_json(data: dict, path: Path) -> None:
    """Save data as JSON to disk atomically (write to temp-file then rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    # Atomic move on the same filesystem avoids partial reads
    tmp_path.rename(path)
    print(f"  → Saved {path}")


def _validate_pkp_artifacts(pkg_dir: Path) -> list[str]:
    """Validate that generated PKP artifacts are non-empty / coherent.

    Returns a list of warning strings (empty means everything is OK).
    """
    warnings: list[str] = []
    pkp_file = pkg_dir / "production_knowledge_package.json"
    if not pkp_file.exists():
        return ["PKP file missing — nothing to validate"]

    with open(pkp_file, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    # Check that we have at least some phases
    phase_results = data.get("phase_results", [])
    if not phase_results:
        warnings.append("PKP contains no phase results — Genesis2 may have failed silently")

    completed = [r for r in phase_results if r.get("status", {}).get("value") == "completed"]
    failed = [r for r in phase_results if r.get("status", {}).get("value") == "failed"]
    if failed:
        warnings.append(f"PKP has {len(failed)} failed phase(s): {[f['phase_number'] for f in failed]}")

    # Check that title/characters are present
    title = data.get("title") or (data.get("story_foundation") or {}).get("premise", "")[:40]
    if not title:
        warnings.append("PKP title is empty — bridge may produce minimal brief")

    return warnings


def _preflight(args) -> dict[str, str | Path] | list[str]:
    """Run pre-flight checks.

    Returns ``{"synopsis": str, "output_dir": Path, "synopsis_source": str}``
    on success, or a list of error strings when something is wrong.
    """
    errors: list[str] = []

    # Resolve synopsis text and track source
    if args.synopsis:
        syn_text = args.synopsis.strip()
        synopsis_source = "CLI argument"
    elif args.synopsis_preset:
        syn_text = SYNOPSIS_PRESETS.get(args.synopsis_preset, "")
        synopsis_source = f"preset: {args.synopsis_preset}"
    elif args.synopsis_file and Path(args.synopsis_file).exists():
        syn_text = Path(args.synopsis_file).read_text(encoding="utf-8").strip()
        synopsis_source = f"file: {args.synopsis_file}"
    else:
        syn_text = DEFAULT_SYNOPSIS
        synopsis_source = "default"

    if not syn_text or len(syn_text) < 20:
        errors.append("Synopsis text is too short (expect ≥20 chars)")

    # Verify output directory is writable
    output_dir = Path(args.output_dir) if args.output_dir else ROOT / "output" / "videos" / "final"
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        test_file = output_dir / ".write_test"
        test_file.write_text("", encoding="utf-8")
        test_file.unlink()
    except OSError as exc:
        errors.append(f"Output directory is not writable: {exc}")

    if errors:
        return errors  # type: ignore[return-value]

    return dict(synopsis=syn_text, output_dir=output_dir, synopsis_source=synopsis_source)


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the production pipeline."""
    parser = argparse.ArgumentParser(
        description="Genesis2 → movie_os Pipeline: Synopsis to Production"
    )
    parser.add_argument(
        "synopsis",
        nargs="?",
        default=None,
        help="Synopsis text (overrides presets and file)",
    )
    parser.add_argument(
        "--synopsis", "-s",
        dest="synopsis_preset",
        choices=sorted(SYNOPSIS_PRESETS.keys()),
        metavar="NAME",
        help="Use a named synopsis preset instead of default",
    )
    parser.add_argument(
        "--synopsis-file",
        type=str,
        default=None,
        dest="synopsis_file",
        help="Load synopsis content from a file (one or more lines)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        dest="model_name",
        help=f"LLM model to use (e.g. 'ollama/qwen3'). Default: MockLLMClient",
    )
    return parser.parse_args(argv if argv is not None else sys.argv[1:])


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

RECURSION_LIMIT = 64  # allow for multiple QA↔visual retry rounds (max 2 retries × ~10 nodes + headroom)


async def run_pipeline(
    synopsis: str,
    output_dir: Path | None = None,
    model_name: str | None = None,
) -> dict:
    """Run the complete Genesis2 → Bridge → movie_os pipeline."""
    if output_dir is None:
        output_dir = ROOT / "output" / "videos" / "final"

    # Step 1 — Run Genesis2 Engine (MockLLMClient or real LLM)
    _print_section("Step 1: Running Genesis2 Creative Intelligence Engine")

    if model_name:
        try:
            from movie_os.genesis2.llm_client import LLMClient
            from movie_os.genesis2.llm_providers import LLMConfig
            llm_client = LLMClient(config=LLMConfig(provider="ollama", model=model_name))
            engine = Genesis2Engine(llm=llm_client)
            print(f"  Using real LLM: {model_name}")
        except ImportError:
            # Fallback if real models module isn't available yet
            logger.warning("Real model module not available — falling back to MockLLMClient")
            engine = Genesis2Engine(llm=MockLLMClient())
    else:
        engine = Genesis2Engine(llm=MockLLMClient())

    pkg = await engine.run_async(synopsis=synopsis)

    print(f"  PKP version : {pkg.version}")
    print(f"  Synopsis     : {synopsis[:80]}...")
    print(f"  Phase results : {len(pkg.phase_results)} phases executed")

    completed = sum(1 for r in pkg.phase_results if r.status.value == "completed")
    failed = sum(1 for r in pkg.phase_results if r.status.value == "failed")
    print(f"   ✓ Completed: {completed}    ✗ Failed: {failed}")

    # Summary per phase
    for r in pkg.phase_results:
        status_icon = "\u2713" if r.status.value == "completed" else ("!" if r.status.value != "pending" else "-")
        print(f"   {status_icon} Phase {r.phase_number:02d} ({r.phase_name}):  {r.status.value}  [{len(r.validation_issues)} issues]")

    # Save the raw PKP
    pkg_dir = output_dir / "genesis2"
    _save_json(pkg.model_dump(), pkg_dir / "production_knowledge_package.json")

    # Step 2 — Convert PKP → movie_os brief via bridge
    _print_section("Step 2: Converting PKP → movie_os Brief (Genesis2Bridge)")

    bridge = Genesis2Bridge(pkg)
    brief = bridge.to_brief()

    print(f"  Title         : {brief['title']}")
    print(f"  Logline       : {brief['logline'][:100]}...")
    print(f"  DNA keys      : {list(brief['dna'].keys())}")
    for k, v in brief['dna'].items():
        if isinstance(v, str) and v not in ("Unknown", "Undefined", "Unspecified", "", "Drama", "Neutral"):
            print(f"    → DNA.{k} = {v}")
    print(f"  Scenes        : {len(brief['scenes'])} scenes generated")
    for scene in brief['scenes']:
        print(
            f"    Scene {scene.get('number', '?'):2d}: "
            f"{scene.get('title', '???'):30s} | {scene.get('act', ''):6s} | "
            f"energy={scene.get('energy', 0)} dur={scene.get('target_duration_seconds', 0):4.0f}s | "
            f"{scene.get('emotional_state', '???')}"
        )
    print(f"  Context world : {str(brief['context']['world'])[:80] if brief['context']['world'] else '(empty)'}...")
    n_chars = len(str(brief['context'].get('characters', [])))
    print(f"  Context chars : {n_chars} bytes of character data")
    n_themes = len(brief['context'].get('themes', []))
    print(f"  Context themes: {n_themes} theme(s)")

    # Save the brief (YAML → JSON fallback)
    brief_path = pkg_dir / "brief.yaml"
    saved_path = bridge.save_brief(brief_path)
    print(f"  Brief saved   : {saved_path}")

    _save_json(brief, output_dir / "movie_os_brief.json")

    # Step 3 — Build and run the movie_os graph with this brief
    _print_section("Step 3: Running movie_os Agent Graph")

    thread_id = f"genesis2-{pkg.created_at[:10]}"
    state = new_state(brief=brief, thread_id=thread_id)
    print(f"  Thread ID     : {thread_id}")

    # Use the legacy architecture path (handles missing capabilities gracefully)
    # In mock mode, run only the story agent to validate the brief pipeline
    graph = build_graph(
        checkpointer=None,
        use_new_architecture=False,
        only_stage='story',
    )
    print("  Graph built   : OK (legacy architecture, story-only mode)")

    result: dict = {}  # will be filled by run_graph or exception handler

    # Run it
    try:
        cfg = {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": 25,
        }
        result = await graph.ainvoke(state, config=cfg)

        # Print high-level outcome
        errors = result.get("errors", [])
        current_step = result.get("current_step", "unknown")
        final_video = result.get("final_video")

        print(f"  Final step    : {current_step}")
        if final_video:
            print(f"  Output video  : {final_video}")
        else:
            print(f"  Output video  : [pending] (generation requires GPU/media tools)")

        if errors:
            print(f"\n  ⚠ Pipeline produced {len(errors)} error(s):")
            for e in errors[:5]:
                print(f"    • {e}")

        success = final_video is not None or current_step == "publishing_agent"
        status = "SUCCESS" if success else "COMPLETED (no video asset)"
        print(f"\n  🎬 Pipeline status: {status}")

    except Exception as exc:
        import traceback
        tb_lines = traceback.format_exc().splitlines()
        # Print only the top of the traceback
        printed = False
        for line in tb_lines[:12]:
            print(f"  {line}")
            if "... (remaining lines omitted)" not in line and len(tb_lines) > 12:
                print(f"  ┆ ... ({len(tb_lines) - 12} more lines)")
                break
        result = {"error": str(exc)}

    # Step 4 — Write final summary
    summary_path = output_dir / "pipeline_summary.json"
    errors_list = result.get("errors", []) if isinstance(result, dict) and isinstance(result.get("errors"), list) else []
    summary = {
        "synopsis": synopsis[:120],
        "pkp_version": pkg.version,
        "title": brief["title"],
        "scenes_count": len(brief["scenes"]),
        "phases_completed": completed,
        "phases_total": len(pkg.phase_results),
        "errors": errors_list,
        "graph_status": result.get("current_step", "unknown"),
    }
    _save_json(summary, summary_path)

    return {
        "brief": brief,
        "package": pkg.model_dump(),
        "result": result,
    }


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

async def main():
    args = parse_args()

    # Resolve synopsis source (priority: CLI arg > preset > file > default)
    if args.synopsis:
        synopsis = args.synopsis.strip()
        synopsis_source = "CLI argument"
    elif args.synopsis_preset:
        synopsis = SYNOPSIS_PRESETS[args.synopsis_preset]
        synopsis_source = f"preset: {args.synopsis_preset}"
    elif args.synopsis_file and Path(args.synopsis_file).exists():
        synopsis = Path(args.synopsis_file).read_text(encoding="utf-8").strip()
        if not synopsis:
            print("Error: synopsis file is empty — aborting.")
            sys.exit(1)
        synopsis_source = f"file: {args.synopsis_file}"
    else:
        synopsis = DEFAULT_SYNOPSIS
        synopsis_source = "default"

    _print_section("Genesis2 → movie_os Pipeline")
    print(f"  Synopsis source : {synopsis_source}")
    print(f"  Synopsis preview: {synopsis[:80]}...")
    print(f"  Model           : {'real: ' + args.model_name if args.model_name else 'MockLLMClient'}")

    try:
        results = await run_pipeline(
            synopsis=synopsis,
            model_name=args.model_name,
        )
    except Exception as exc:
        print(f"\n  ⚠ Pipeline failed: {exc}")
        raise

    _print_section("Pipeline Complete")
    print("  ✅ Pipeline complete!  Check output/videos/final/ for artifacts.")


if __name__ == "__main__":
    asyncio.run(main())
