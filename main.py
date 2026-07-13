#!/usr/bin/env python3
"""Text Cinema Engine — Main Entry Point

Usage:
    python main.py                          # Run with default sample input
    python main.py --topic "ocean waves"    # Custom topic
    python main.py --json config.json       # Load inputs from JSON file
    python main.py --check-llm              # Check Ollama health
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import yaml
from config.ollama_client import OllamaClient
from pipeline.orchestrator import Pipeline
from pipeline.output_saver import OutputSaver


def load_config() -> dict:
    """Load LLM configuration from YAML file."""
    config_path = Path(__file__).parent / "config" / "llm_config.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


def load_sample_input() -> dict:
    """Return default sample input."""
    return {
        'topic': 'a lonely astronaut',
        'emotional_tone': 'tense',
        'story_length': 'medium',
        'platform': 'youtube'
    }


def load_json_input(path: str) -> dict:
    """Load input config from a JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def check_llm_health():
    """Check if Ollama is running and accessible, and list required models."""
    print("Checking Ollama health...")
    client = OllamaClient()
    
    if not client.check_health():
        print("❌ Ollama is NOT running or not accessible at http://localhost:11434")
        print("\nTo fix this:")
        print("  1. Install Ollama: https://ollama.com")
        print("  2. Start Ollama: ollama serve")
        print("  3. Pull required models:")
        print("     ollama pull qwen2.5:32b")
        print("     ollama pull deepseek-coder-v2:latest")
        sys.exit(1)
    
    models = client.list_models()
    print(f"✅ Ollama is running!")
    print(f"   Available models: {', '.join(models) if models else '(none)'}")
    
    required = ["qwen2.5:32b", "deepseek-coder-v2:latest"]
    missing = [m for m in required if m not in models]
    if missing:
        print(f"\n⚠️  Missing required models: {', '.join(missing)}")
        print(f"   Pull with: ollama pull {' '.join(missing)}")
    else:
        print("✅ All required models are available!")
        print("   Orchestrator:    qwen2.5:32b")
        print("   Creative Writer: deepseek-coder-v2:latest")


def main():
    parser = argparse.ArgumentParser(description='Text Cinema Engine — Generate cinematic stories for video production')
    parser.add_argument('--topic', type=str, help='Story topic (overrides default)')
    parser.add_argument('--tone', type=str, default=None, help='Emotional tone: joyful, sad, tense, wonder, fear, anger, calm')
    parser.add_argument('--length', type=str, default=None, help='Story length: short, medium, long')
    parser.add_argument('--platform', type=str, default=None, help='Platform: youtube, tiktok, instagram, other')
    parser.add_argument('--json', type=str, help='Path to JSON input file')
    parser.add_argument('--check-llm', action='store_true', help='Check Ollama health and exit')
    parser.add_argument('--no-research', action='store_true', help='Skip internet research phase')
    args = parser.parse_args()
    
    # Health check mode
    if args.check_llm:
        check_llm_health()
        return
    
    # Load config
    config = load_config()
    
    # Disable research if requested
    if args.no_research:
        config.setdefault("research", {})["enabled"] = False
    
    # Build input config
    if args.json:
        input_config = load_json_input(args.json)
    else:
        input_config = load_sample_input()
    
    # Override with CLI args if provided
    if args.topic:
        input_config['topic'] = args.topic
    if args.tone:
        input_config['emotional_tone'] = args.tone
    if args.length:
        input_config['story_length'] = args.length
    if args.platform:
        input_config['platform'] = args.platform
    
    # Check LLM health before running
    # Use orchestrator model for health check
    orchestrator_model = config.get("models", {}).get("orchestrator", {}).get("model", "qwen2.5:32b")
    client = OllamaClient(
        endpoint=config.get("llm", {}).get("endpoint", "http://localhost:11434"),
        model=orchestrator_model,
    )
    
    if not client.check_health():
        print("\n❌ Ollama is NOT running or not accessible.")
        print("   The pipeline requires a local LLM to generate content.")
        print("\nTo fix this:")
        print("  1. Install Ollama: https://ollama.com")
        print("  2. Start Ollama: ollama serve")
        print(f"  3. Pull models: ollama pull {orchestrator_model}")
        print("\n   Or run: python main.py --check-llm\n")
        sys.exit(1)
    
    # Verify both models are available
    available_models = client.list_models()
    required_models = [
        config.get("models", {}).get("orchestrator", {}).get("model", "qwen2.5:32b"),
        config.get("models", {}).get("creative_writer", {}).get("model", "deepseek-coder-v2:latest"),
    ]
    missing = [m for m in required_models if m not in available_models]
    if missing:
        print(f"\n⚠️  Missing models: {', '.join(missing)}")
        print(f"   Pull them with: ollama pull {' '.join(missing)}")
        sys.exit(1)
    
    # Run pipeline with dual-model architecture (pass None to auto-create role-specific clients)
    pipeline = Pipeline(llm_client=None, config=config)
    try:
        result = pipeline.run(input_config)
        
        # Save outputs
        saver = OutputSaver()
        paths = saver.save(
            result.story_yaml_content,
            result.scenes_yaml_content,
            result.dialogues_yaml_content,
            result.prompts_yaml_content,
            research=result.research_context,
        )
        
        print("\n" + "=" * 60)
        print("✅ PIPELINE COMPLETED")
        print("=" * 60)
        print(f"\n📖 Story: {result.story_yaml_content['title']}")
        print(f"🎬 Scenes: {len(result.scenes_yaml_content)}")
        for scene in result.scenes_yaml_content:
            print(f"   Scene {scene['id']}: {scene['narration'][:50]}...")
            print(f"      Camera: {scene['camera']} | Lighting: {scene['lighting']} | Emotion: {scene['emotion']}")
        print(f"\n🎨 Prompts: {len(result.prompts_yaml_content)}")
        for prompt in result.prompts_yaml_content:
            print(f"   [{prompt['scene_id']}] {prompt['prompt'][:60]}...")
        print(f"\n💾 Output saved to: {paths.get('manifest', 'N/A')}")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
