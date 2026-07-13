"""Phase 3: ew001 Reference Implementation.

Migrates legacy ew001 timeline to new Cinema Production Engine structure,
then validates the full pipeline end-to-end.

Usage:
    python scripts/migrate_ew001.py              # Migrate only
    python scripts/migrate_ew001.py --run-pipeline  # Migrate + run pipeline
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import yaml
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

EW001_TIMELINE = _PROJECT_ROOT / "videoContentStructure" / "Psychology" / "EmotionalWithdrawal" / "fearBasedWithdrawal" / "ew001" / "master_timeline.yaml"
EW001_PRODUCTION_DIR = _PROJECT_ROOT / "productions" / "psychological" / "ew001"


def migrate_ew001():
    """Migrate ew001 legacy timeline to new production structure."""
    print("=" * 60)
    print("Phase 3: ew001 Reference Implementation")
    print("=" * 60)

    # Step 1: Run migration adapter
    print("\n📦 Step 1: Migrating ew001 to new production structure...")
    from movie_os.migration.adapter import MigrationAdapter

    adapter = MigrationAdapter()
    result = adapter.migrate_timeline_to_production(
        timeline_path=str(EW001_TIMELINE),
        production_dir=str(EW001_PRODUCTION_DIR),
    )

    if not result.success:
        print(f"❌ Migration failed: {result.message}")
        return False

    print(f"✅ Migration successful!")
    print(f"   Production dir: {result.production_dir}")
    print(f"   Files created:")
    for f in result.new_files_created:
        print(f"     - {f}")
    if result.warnings:
        print(f"\n⚠️  Warnings:")
        for w in result.warnings:
            print(f"     - {w}")

    # Step 2: Verify all new files exist
    print("\n📋 Step 2: Verifying new production files...")
    required_files = [
        "production.yaml",
        "dna.yaml",
        "creative_brief.md",
        "screenplay.md",
        "outline.md",
        "music_score.yaml",
        "scene_plan.yaml",
        "master_timeline.yaml",
    ]

    all_exist = True
    for fname in required_files:
        fpath = EW001_PRODUCTION_DIR / fname
        exists = fpath.exists()
        status = "✅" if exists else "❌"
        print(f"   {status} {fname}")
        if not exists:
            all_exist = False

    if not all_exist:
        print("\n❌ Some required files are missing!")
        return False

    print("\n✅ All required files present!")

    # Step 3: Display production summary
    print("\n📊 Step 3: Production Summary")
    print("=" * 60)

    prod_yaml = yaml.safe_load((EW001_PRODUCTION_DIR / "production.yaml").read_text())
    dna_yaml = yaml.safe_load((EW001_PRODUCTION_DIR / "dna.yaml").read_text())
    screenplay_md = (EW001_PRODUCTION_DIR / "screenplay.md").read_text()

    print(f"Title: {prod_yaml.get('title', 'N/A')}")
    print(f"Grammar: {prod_yaml.get('grammar', 'N/A')}")
    print(f"Status: {prod_yaml.get('status', 'N/A')}")
    print(f"\nDNA:")
    for key, value in dna_yaml.items():
        if key not in ('id',):
            print(f"  - {key}: {value}")

    # Count scenes in screenplay
    scene_count = screenplay_md.count("### SCENE ")
    print(f"\nScenes in screenplay: {scene_count}")

    return True


async def run_pipeline_ew001():
    """Run the Cinema Production Engine pipeline on ew001."""
    print("\n" + "=" * 60)
    print("🚀 Running Cinema Production Engine on ew001...")
    print("=" * 60)

    from movie_os.agents.orchestration.production_orchestrator_agent import ProductionOrchestratorAgent
    from movie_os.capabilities.agent_base import ProductionContext

    # Load DNA for context
    dna_path = EW001_PRODUCTION_DIR / "dna.yaml"
    with open(dna_path, 'r') as f:
        dna = yaml.safe_load(f)

    prod_yaml_path = EW001_PRODUCTION_DIR / "production.yaml"
    with open(prod_yaml_path, 'r') as f:
        prod_yaml = yaml.safe_load(f)

    # Create production context
    context = ProductionContext(
        title=prod_yaml.get("title", "EW-001"),
        dna=dna,
        production_dir=str(EW001_PRODUCTION_DIR),
        grammar=prod_yaml.get("grammar", "psychological_cinema"),
        status="in_production",
    )

    # Run orchestrator
    orchestrator = ProductionOrchestratorAgent()
    result = await orchestrator.execute(context)

    print("\n" + "=" * 60)
    print(f"Pipeline result: {result.message}")
    print("=" * 60)

    if result.status.value == "SUCCESS":
        print("✅ Pipeline completed successfully!")
        if result.artifacts.get("output_video"):
            print(f"   Output video: {result.artifacts['output_video']}")
        return True
    elif result.status.value == "REVISED":
        print("⚠️  Pipeline needs revisions:")
        for cat in result.artifacts.get("failed_evaluations", []):
            print(f"   - {cat}")
        return False
    else:
        print("❌ Pipeline failed:")
        for err in result.errors or []:
            print(f"   - {err}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Migrate ew001 to new Cinema Production Engine")
    parser.add_argument("--run-pipeline", action="store_true", help="Run the pipeline after migration")
    args = parser.parse_args()

    # Step 1: Migrate
    success = migrate_ew001()
    if not success:
        sys.exit(1)

    # Step 2: Run pipeline (optional)
    if args.run_pipeline:
        success = asyncio.run(run_pipeline_ew001())
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
