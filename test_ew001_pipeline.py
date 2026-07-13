#!/usr/bin/env python3
"""Test script to run the ew001 pipeline with our new agents."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
_PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_PROJECT_ROOT))

from movie_os.agents.orchestration.production_orchestrator_agent import ProductionOrchestratorAgent
from movie_os.capabilities.agent_base import ProductionContext

async def test_ew001_pipeline():
    """Test running the ew001 pipeline with our new agents."""
    
    print("🚀 Testing ew001 pipeline with new Movie OS agents...")
    
    # Create context for the ew001 production
    production_dir = Path("productions/psychological/ew001")
    
    # Create a basic context (this would normally be populated from the production data)
    context = ProductionContext(
        title="Story EW-001",
        dna={
            "territory": "emotional_withdrawal",
            "cluster": "fear_based_withdrawal", 
            "mechanism": "anticipated_rejection",
            "archetype": "married_husband",
            "theme": "love_becomes_dangerous"
        },
        production_dir=str(production_dir),
        grammar="psychological_cinema",
    )
    
    # Create orchestrator and run pipeline
    orchestrator = ProductionOrchestratorAgent()
    
    print(f"Starting pipeline for production: {context.title}")
    print(f"Production directory: {production_dir}")
    
    try:
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
                
    except Exception as e:
        print(f"❌ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ew001_pipeline())