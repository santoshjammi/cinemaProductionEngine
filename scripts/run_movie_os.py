#!/usr/bin/env python3
"""Run the modular Movie OS pipeline using the LangGraph state machine.

Supports two architectures:
1. Legacy (backward compatible): MovieAgent → Story → Visual → Voice → Music → QA → Publishing
2. New (Cinema Production Engine): ProductionOrchestratorAgent → all 26 agents → Evaluation → Revision

Auto-detection: If production_dir/screenplay.md exists, uses new architecture.
Otherwise uses legacy for backward compatibility with existing productions.

Usage:
    # Full pipeline (auto-detects architecture)
    python scripts/run_movie_os.py --timeline <path>

    # Force new architecture
    python scripts/run_movie_os.py --timeline <path> --new-architecture

    # Force legacy architecture
    python scripts/run_movie_os.py --timeline <path> --legacy

    # Skip specific stages (legacy only)
    python scripts/run_movie_os.py --timeline <path> --skip-visual  # No image generation
    python scripts/run_movie_os.py --timeline <path> --skip-music   # No music generation
    python scripts/run_movie_os.py --timeline <path> --skip-voice   # No TTS voiceover

    # Run only specific stages (legacy only)
    python scripts/run_movie_os.py --timeline <path> --only-visual  # Only generate images

    # Dry run (validate timeline without executing)
    python scripts/run_movie_os.py --timeline <path> --dry-run

    # Migrate legacy timeline to new production structure
    python scripts/run_movie_os.py --timeline <path> --migrate

Flags:
    --skip-music      Skip music generation stage (legacy only)
    --skip-voice      Skip TTS voiceover stage (legacy only)
    --skip-visual     Skip image/video generation stage (legacy only)
    --skip-publishing Skip final video assembly stage (legacy only)
    --only-music      Run only music generation (implies skip others, legacy only)
    --only-voice      Run only voice generation (implies skip others, legacy only)
    --only-visual     Run only visual generation (implies skip others, legacy only)
    --only-publishing Run only publishing (requires existing assets, legacy only)
    --dry-run         Validate timeline and exit without running pipeline
    --new-architecture Force use of new Cinema Production Engine architecture
    --legacy          Force use of legacy architecture
    --migrate         Migrate legacy timeline to new production structure
"""
import argparse
import asyncio
import sys
import yaml
from pathlib import Path

# Add project root to path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

# Force importing from backend/ package for internal dependencies
sys.path.insert(0, str(_PROJECT_ROOT / "backend"))

from movie_os.agents import build_graph, new_state
from movie_os.config import load_config
from movie_os.capabilities import CapabilityRegistry, set_default_registry
from movie_os.providers import default_provider_factory


async def run_pipeline(timeline_path: str, config_path: str | None = None, skip_stages: list[str] | None = None, only_stage: str | None = None, use_new_architecture: bool | None = None, production_dir: Path | None = None):
    """Run the pipeline with architecture auto-detection."""
    
    # Auto-detect architecture if not forced
    if use_new_architecture is None:
        prod_dir = production_dir or Path(timeline_path).parent
        screenplay_exists = (prod_dir / "screenplay.md").exists()
        use_new_architecture = screenplay_exists
        print(f"\n🔍 Auto-detected architecture: {'new' if use_new_architecture else 'legacy'}")
    
    arch = "new" if use_new_architecture else "legacy"
    print(f"\n🎬 Using architecture: {arch}")
    
    # Load config and populate registry with providers
    print(f"Loading Movie OS config: {config_path or 'config/movie_os.yaml'}")
    config = load_config(config_path)
    
    # Initialize the default registry from config using the default provider factory
    registry = CapabilityRegistry.from_config(config, provider_factory=default_provider_factory)
    set_default_registry(registry)

    # Load master timeline/brief
    print(f"Loading timeline from {timeline_path}")
    with open(timeline_path, 'r') as f:
        timeline_data = yaml.safe_load(f)

    # Resolve top-level key if nested
    if "master_timeline" in timeline_data:
        timeline_data = timeline_data["master_timeline"]

    if arch == "new":
        # New architecture: ProductionOrchestratorAgent handles everything
        print("\n🚀 Starting Cinema Production Engine...")
        from movie_os.agents.orchestration.production_orchestrator_agent import ProductionOrchestratorAgent
        from movie_os.capabilities.agent_base import ProductionContext
        
        prod_dir = production_dir or Path(timeline_path).parent / "production_new"
        context = ProductionContext(
            title=timeline_data.get("title", "Untitled"),
            dna=timeline_data.get("dna", {}),
            production_dir=str(prod_dir),
            grammar=config.get("grammar", "psychological_cinema") if config else "psychological_cinema",
        )
        
        orchestrator = ProductionOrchestratorAgent()
        result = await orchestrator.execute(context)
        
        print("=" * 60)
        print(f"Pipeline finished: {result.message}")
        if result.status.value == "SUCCESS":
            print("✅ Pipeline completed successfully!")
            if result.artifacts.get("output_video"):
                print(f"Final Video: {result.artifacts['output_video']}")
        elif result.status.value == "REVISED":
            print("⚠️  Pipeline needs revisions:")
            for cat in result.artifacts.get("failed_evaluations", []):
                print(f"  - {cat}")
        else:
            print("❌ Errors occurred:")
            for err in result.errors or []:
                print(f"  - {err}")
            sys.exit(1)
    else:
        # Legacy architecture (backward compatible)
        if only_stage:
            skip_stages = [s for s in ['music', 'voice', 'visual', 'qa', 'publishing'] if s != only_stage]
            print(f"\n🎯 Running ONLY stage: {only_stage}")
        
        if skip_stages:
            skipped_str = ", ".join(skip_stages)
            running = [s for s in ['music', 'voice', 'visual', 'qa', 'publishing'] if s not in skip_stages]
            print(f"\n⏭️  Skipping stages: {skipped_str}")
            print(f"▶️  Running stages: {running}")

        # Reconstruct brief for story agent to consume
        brief = {
            "title": timeline_data.get("title", "Untitled"),
            "synopsis": timeline_data.get("synopsis", ""),
            "dna": timeline_data.get("dna", {}),
            "scenes": timeline_data.get("scenes", []),
        }

        # Setup graph state
        thread_id = f"run_{Path(timeline_path).stem}"
        state = new_state(brief, thread_id=thread_id)

        print("\nStarting Movie OS LangGraph Pipeline (legacy)...")
        print(f"Thread ID: {thread_id}")
        print("=" * 60)

        # Build and execute the graph
        graph = build_graph(
            config=config,
            skip_stages=skip_stages,
        only_stage=only_stage,
    )
    result = await graph.ainvoke(
        state,
        config={"configurable": {"thread_id": thread_id}},
    )

    print("=" * 60)
    print(f"Pipeline finished with step: {result.get('current_step')}")
    if result.get("errors"):
        print("❌ Errors occurred:")
        for err in result["errors"]:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ Pipeline completed successfully!")
        print(f"Saved manifest: {result.get('publishing_manifest')}")
        print(f"Final Video: {result.get('final_video')}")


def main():
    parser = argparse.ArgumentParser(
        description="Run Movie OS Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline (all stages)
  python scripts/run_movie_os.py --timeline <path>

  # Skip specific stages
  python scripts/run_movie_os.py --timeline <path> --skip-visual
  python scripts/run_movie_os.py --timeline <path> --skip-music --skip-voice

  # Run only specific stage
  python scripts/run_movie_os.py --timeline <path> --only-visual
  python scripts/run_movie_os.py --timeline <path> --only-publishing

  # Dry run (validate timeline without executing)
  python scripts/run_movie_os.py --timeline <path> --dry-run
        """
    )
    parser.add_argument("--timeline", "-t", required=True, help="Path to master_timeline.yaml")
    parser.add_argument("--config", "-c", default=None, help="Path to config/movie_os.yaml")
    
    # Skip flags
    skip_group = parser.add_argument_group('skip options')
    skip_group.add_argument("--skip-music", action="store_true", help="Skip music generation")
    skip_group.add_argument("--skip-voice", action="store_true", help="Skip TTS voiceover")
    skip_group.add_argument("--skip-visual", action="store_true", help="Skip image/video generation")
    skip_group.add_argument("--skip-publishing", action="store_true", help="Skip final video assembly")
    
    # Only flags (run only this stage)
    only_group = parser.add_argument_group('only options')
    only_group.add_argument("--only-music", action="store_true", help="Run only music generation")
    only_group.add_argument("--only-voice", action="store_true", help="Run only voice generation")
    only_group.add_argument("--only-visual", action="store_true", help="Run only visual generation")
    only_group.add_argument("--only-publishing", action="store_true", help="Run only publishing")
    
    # Other options
    parser.add_argument("--dry-run", action="store_true", help="Validate timeline and exit without running pipeline")
    
    args = parser.parse_args()

    # Handle dry run
    if args.dry_run:
        print(f"📋 Dry run: validating timeline at {args.timeline}...")
        with open(args.timeline, 'r') as f:
            timeline_data = yaml.safe_load(f)
        if "master_timeline" in timeline_data:
            timeline_data = timeline_data["master_timeline"]
        scenes = timeline_data.get("scenes", [])
        print(f"✅ Timeline valid: {len(scenes)} scenes loaded")
        print(f"   Title: {timeline_data.get('title', 'N/A')}")
        print(f"   Total duration: {timeline_data.get('metadata', {}).get('total_duration_seconds', 'N/A')}s")
        sys.exit(0)

    # Determine which stages to skip/run
    skip_stages = []
    if args.skip_music: skip_stages.append('music')
    if args.skip_voice: skip_stages.append('voice')
    if args.skip_visual: skip_stages.append('visual')
    if args.skip_publishing: skip_stages.append('publishing')
    
    only_stage = None
    if args.only_music: only_stage = 'music'
    elif args.only_voice: only_stage = 'voice'
    elif args.only_visual: only_stage = 'visual'
    elif args.only_publishing: only_stage = 'publishing'
    
    asyncio.run(run_pipeline(args.timeline, args.config, skip_stages=skip_stages, only_stage=only_stage))


if __name__ == "__main__":
    main()
