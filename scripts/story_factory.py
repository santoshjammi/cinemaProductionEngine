"""Story Factory CLI — turn a synopsis into a pipeline-ready manifest.

Usage:
    # Full pipeline: synopsis → DNA + context (parallel) → story → master timeline → manifest
    python scripts/story_factory.py --synopsis "..." --output-dir stories/EmotionalWithdrawal/fear/example

    # Just the DNA
    python scripts/story_factory.py --synopsis "..." --steps dna --output-dir stories/...

    # DNA + context (no story yet)
    python scripts/story_factory.py --synopsis "..." --steps dna,context --output-dir stories/...

    # Re-run just the scene structurer (after editing story.md)
    python scripts/story_factory.py --steps scenes --output-dir stories/...

The output directory will contain:
    dna.yaml              — story identity (id, territory, cluster, mechanism, ...)
    context.md            — world, characters, atmosphere (~600 words)
    story.md              — narrative prose (~1200 words, 3 acts)
    master_timeline.yaml  — structured scene-by-scene production timeline
    manifest.yaml         — pipeline-ready manifest (consumed by psychological_pipeline.py)
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

# Ensure project root is on sys.path so the package is importable
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from story_factory import (
    generate_dna,
    generate_context,
    generate_story,
    structure_scenes,
    timeline_to_manifest,
    save_manifest,
    LLMError,
)


STEPS = ["dna", "context", "story", "scenes", "manifest"]


def _read_synopsis(s: str) -> str:
    """Read synopsis from a file path or return the string directly."""
    p = Path(s)
    if p.exists() and p.is_file():
        return p.read_text().strip()
    return s.strip()


def _run_dna(synopsis: str, output_dir: Path, force: bool, lmstudio_url: str, lmstudio_key: str) -> str:
    path = output_dir / "dna.yaml"
    if path.exists() and not force:
        print(f"  [skip] dna.yaml already exists at {path}")
        import yaml
        return yaml.safe_load(path.read_text())
    print("  [1/4] Generating Story DNA...")
    t0 = time.time()
    dna = generate_dna(
        synopsis, output_path=path,
        base_url=lmstudio_url, api_key=lmstudio_key,
    )
    print(f"         done in {time.time() - t0:.1f}s — id={dna.get('id', '?')}, "
          f"territory={dna.get('territory', '?')}, ending={dna.get('ending', '?')}")
    return dna


def _run_context(synopsis: str, output_dir: Path, force: bool, lmstudio_url: str, lmstudio_key: str) -> str:
    path = output_dir / "context.md"
    if path.exists() and not force:
        print(f"  [skip] context.md already exists at {path}")
        return path.read_text()
    print("  [2/4] Generating Context...")
    t0 = time.time()
    context = generate_context(
        synopsis, output_path=path,
        base_url=lmstudio_url, api_key=lmstudio_key,
    )
    word_count = len(context.split())
    print(f"         done in {time.time() - t0:.1f}s — {word_count} words")
    return context


def _run_story(synopsis: str, dna: dict, context: str, output_dir: Path, force: bool, lmstudio_url: str, lmstudio_key: str) -> str:
    path = output_dir / "story.md"
    if path.exists() and not force:
        print(f"  [skip] story.md already exists at {path}")
        return path.read_text()
    print("  [3/4] Generating Story (the only creative writing step)...")
    t0 = time.time()
    story = generate_story(
        synopsis, dna, context, output_path=path,
        base_url=lmstudio_url, api_key=lmstudio_key,
    )
    word_count = len(story.split())
    print(f"         done in {time.time() - t0:.1f}s — {word_count} words")
    return story


def _run_scenes(dna: dict, context: str, story: str, output_dir: Path, force: bool, lmstudio_url: str, lmstudio_key: str):
    path = output_dir / "master_timeline.yaml"
    if path.exists() and not force:
        print(f"  [skip] master_timeline.yaml already exists at {path}")
        from story_factory import MasterTimeline
        return MasterTimeline.load(path)
    print("  [4/4] Structuring scenes into Master Timeline...")
    t0 = time.time()
    timeline = structure_scenes(
        dna, context, story, output_path=path,
        base_url=lmstudio_url, api_key=lmstudio_key,
    )
    print(f"         done in {time.time() - t0:.1f}s — {len(timeline.scenes)} scenes, "
          f"{timeline.total_duration_seconds:.0f}s total")
    return timeline


def _run_manifest(timeline, output_dir: Path):
    path = output_dir / "manifest.yaml"
    print("  [+] Converting Master Timeline to pipeline manifest...")
    manifest = timeline_to_manifest(
        timeline,
        playbook_file="../psychological_cinema_standard.yaml",
        context_file="context.md",
        story_file="story.md",
        dna_file="dna.yaml",
    )
    save_manifest(manifest, path)
    print(f"      wrote {path} — {len(manifest['scenes'])} scenes ready for the pipeline")


async def run_factory(args):
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    synopsis = _read_synopsis(args.synopsis)
    if not synopsis:
        print("Error: synopsis is empty (provide --synopsis as a string or path to a file)", file=sys.stderr)
        sys.exit(1)

    print(f"\n{'=' * 60}")
    print(f"STORY FACTORY")
    print(f"{'=' * 60}")
    print(f"Synopsis: {synopsis[:100]}{'...' if len(synopsis) > 100 else ''}")
    print(f"Output:   {output_dir}")
    print(f"Steps:    {', '.join(args.steps)}")
    print()

    steps = args.steps

    dna = None
    context = None
    story = None
    timeline = None

    # Phase 1: DNA + Context (run in parallel for speed)
    needs_dna = "dna" in steps or "story" in steps or "scenes" in steps or "manifest" in steps
    needs_context = "context" in steps or "story" in steps or "scenes" in steps or "manifest" in steps

    if needs_dna or needs_context:
        import concurrent.futures

        # If dna.yaml and context.md already exist, load them
        dna_path = output_dir / "dna.yaml"
        ctx_path = output_dir / "context.md"
        dna_exists = dna_path.exists() and "dna" not in steps
        ctx_exists = ctx_path.exists() and "context" not in steps

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures = {}
            if needs_dna:
                if dna_exists:
                    import yaml
                    dna = yaml.safe_load(dna_path.read_text())
                    print(f"  [skip] dna.yaml already exists — id={dna.get('id', '?')}")
                else:
                    futures["dna"] = pool.submit(
                        _run_dna, synopsis, output_dir, args.force,
                        args.lmstudio_url, args.lmstudio_key,
                    )
            if needs_context:
                if ctx_exists:
                    context = ctx_path.read_text()
                    word_count = len(context.split())
                    print(f"  [skip] context.md already exists — {word_count} words")
                else:
                    futures["context"] = pool.submit(
                        _run_context, synopsis, output_dir, args.force,
                        args.lmstudio_url, args.lmstudio_key,
                    )

            for name, fut in futures.items():
                result = fut.result()
                if name == "dna":
                    dna = result
                elif name == "context":
                    context = result

    # Phase 2: Story (depends on DNA + context)
    if "story" in steps or "scenes" in steps or "manifest" in steps:
        if dna is None or context is None:
            print("Error: story/scenes/manifest steps require DNA and context.", file=sys.stderr)
            sys.exit(1)
        story_path = output_dir / "story.md"
        if story_path.exists() and "story" not in steps:
            story = story_path.read_text()
            word_count = len(story.split())
            print(f"  [skip] story.md already exists — {word_count} words")
        else:
            story = _run_story(
                synopsis, dna, context, output_dir, args.force,
                args.lmstudio_url, args.lmstudio_key,
            )

    # Phase 3: Scene Structurer (depends on story + DNA + context)
    if "scenes" in steps or "manifest" in steps:
        if dna is None or context is None or story is None:
            print("Error: scenes/manifest steps require DNA, context, and story.", file=sys.stderr)
            sys.exit(1)
        timeline = _run_scenes(
            dna, context, story, output_dir, args.force,
            args.lmstudio_url, args.lmstudio_key,
        )

    # Phase 4: Manifest adapter
    if "manifest" in steps:
        if timeline is None:
            from story_factory import MasterTimeline
            timeline = MasterTimeline.load(output_dir / "master_timeline.yaml")
        _run_manifest(timeline, output_dir)

    print(f"\n{'=' * 60}")
    print("DONE")
    print(f"{'=' * 60}")
    print(f"Files written to: {output_dir}")
    for f in sorted(output_dir.iterdir()):
        size = f.stat().st_size
        print(f"  {f.name:<30} {size:>8} bytes")
    print()
    if "manifest" in steps:
        manifest_path = output_dir / "manifest.yaml"
        print("Next step — run the video pipeline:")
        print(f"  python scripts/psychological_pipeline.py \\")
        print(f"    --playbook videoContentStructure/Psychology/psychological_cinema_standard.yaml \\")
        print(f"    --manifest {manifest_path} \\")
        print(f"    --topic-dir {output_dir.parent.parent} \\")
        print(f"    --output-dir output/videos \\")
        print(f"    --auto-approve")


def main():
    parser = argparse.ArgumentParser(
        description="Story Factory — turn a synopsis into a pipeline-ready manifest.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--synopsis", "-s",
        required=True,
        help="Free-form story synopsis (1-5 sentences) or path to a .txt file",
    )
    parser.add_argument(
        "--output-dir", "-o",
        required=True,
        help="Directory to write dna.yaml, context.md, story.md, master_timeline.yaml, manifest.yaml",
    )
    parser.add_argument(
        "--steps",
        default=",".join(STEPS),
        help=f"Comma-separated steps to run. Options: {','.join(STEPS)}. Default: all",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files (default: skip if exists)",
    )
    # LLM connection — these have sensible defaults but can be overridden
    # for different deployments (remote LMStudio, Azure OpenAI, etc).
    parser.add_argument(
        "--lmstudio-url",
        default="http://localhost:1234",
        help="LMStudio base URL. Default: http://localhost:1234",
    )
    parser.add_argument(
        "--lmstudio-key",
        default="sk-lm-TkM3NqaZ:CQdNsDjxGRm17O3Gg59W",
        help="LMStudio API key. Default: built-in dev key",
    )
    args = parser.parse_args()
    args.steps = [s.strip() for s in args.steps.split(",") if s.strip()]
    for s in args.steps:
        if s not in STEPS:
            print(f"Error: unknown step '{s}'. Valid: {STEPS}", file=sys.stderr)
            sys.exit(1)

    try:
        asyncio.run(run_factory(args))
    except LLMError as e:
        print(f"\nLLM Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
