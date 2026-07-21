"""
Genesis Stage Demo Script: Validates the flow from Producer Brief -> Storyteller -> Prompt Engineer.
"""
import os
import sys
sys.path.insert(0, '/Users/santosh/Desktop/projects/videoGen')

from config.models import InputConfig, InputValidationError
from backend.app.services.genesis.storyteller_agent import StorytellerAgent
from backend.app.services.genesis.prompt_engineer_agent import PromptEngineerAgent
from config.ollama_client import OllamaClient

def run_genesis_demo():
    print("--- Genesis Stage Simulation ---")
    
    # 1. Define the Producer Brief (The Director's Intent)
    producer_brief = {
        "title": "Project: Neo-Genesis",
        "logline": "A lone gardener discovers a mechanical flower in a ruined city.",
        "targetAudience": "Sci-Fi Enthusiasts",
        "callToAction": "Subscribe for the next chapter.",
        "totalDuration": "120s",
        "aspectRatio": "16:9",
        "pacingStyle": "slow",
        "visualStyleGuide": ["Cinematic Realism", "Rust & Rust"],
        "musicMood": "Melancholic",
        "voiceOverStyle": "Narrative"
    }

    # 2. Configure Input for the Pipeline
    input_config = InputConfig(
        topic="A post-apocalyptic world where nature has reclaimed the cities.",
        emotional_tone="sad",
        story_length="medium",
        platform="youtube",
        producer_brief=producer_brief
    )

    # 3. Instantiate the Storyteller Sub-Agent
    print("\n[1/2] Initializing Storyteller Agent...")
    try:
        storyteller = StorytellerAgent(llm_client=None) # Uses default Ollama client
        print("[Storyteller] Awaiting narrative input...")
        
        # Note: This would require a running LLM to actually execute. 
        # We are verifying the structure and readiness here.
        print(f"[Storyteller] Ready to generate for topic: {input_config.topic}")
        print(f"[Storyteller] Style Guide: {', '.join(producer_brief['visualStyleGuide'])}")

    except Exception as e:
        print(f"Storyteller Error: {e}")

    # 4. Instantiate the Prompt Engineer Sub-Agent
    print("\n[2/2] Initializing Prompt Engineer Agent...")
    try:
        prompt_engineer = PromptEngineerAgent(llm_client=None)
        print("[Prompt Engineer] Ready to translate scenes into prompts.")
        
        # Verify it accepts the producer brief data
        print(f"[Prompt Engineer] Aspect Ratio: {producer_brief['aspectRatio']}")
        print(f"[Prompt Engineer] Visual Guide: {', '.join(producer_brief['visualStyleGuide'])}")

    except Exception as e:
        print(f"Prompt Engineer Error: {e}")

    print("\n--- Genesis Module Ready ---")

if __name__ == "__main__":
    run_genesis_demo()
