import sys, json
from pathlib import Path

# Update paths
sys.path.insert(0, str(Path(__file__).parent / "pipeline"))
sys.path.insert(0, str(Path(__file__).parent / "builder"))

from architect.context_manager import ContextManager
from guardian.guardian import Guardian
from builder.admission import Builder as RenderBuilder
from builder.generate_assets import AssetGenerator

def main():
    print("=== INITIALIZING VIDEO GENESIS SYSTEM ===")
    
    contract_path = "pipeline/contracts/narrative_contract.json"
    
    # 1. Run Context Manager
    ctx_mgr = ContextManager(contract_path)
    capsule = ctx_mgr.get_capsule("generate_prompts", {"scene_id": 1})
    print(f"[Context] Built capsule with {len(capsule)} constraints.")

    # 2. Verify Guardian Status on canon
    guardian = Guardian(contract_path)
    
    # Check Canon (scenes.json)
    scene_report = guardian.validate_artifact("pipeline/architect/scenes.json")
    print(f"[Guardian] Canon Validation: {scene_report['status']}")

    # Check Negative Fixture (if exists)
    neg_path = "quarantine/rejected_artifacts/ew001/screenplay.md"
    if Path(neg_path).exists():
        neg_report = guardian.validate_artifact(neg_path)
        print(f"[Guardian] Negative Fixture Validation: {neg_report['status']}")

    # 3. Run Builder
    package_dir = "packages/ew001"
    builder = RenderBuilder(package_dir)
    
    if builder.is_sealed():
        print("[Builder] Admission: PASSED. Starting rendering...")
        generator = AssetGenerator(builder)
        generator.generate_all()
    else:
        print("[Builder] Admission: DENIED.")

if __name__ == "__main__":
    main()
