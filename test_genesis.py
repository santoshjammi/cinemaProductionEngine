import sys
import os

# Directly add the agents folder and load schema first
sys.path.insert(0, '/Users/santosh/Desktop/projects/videoGen/movie_os/agents/genesis')
schema_path = '/Users/santosh/Desktop/projects/videoGen/movie_os/agents/genesis/schema.py'
orchestrator_path = '/Users/santosh/Desktop/projects/videoGen/movie_os/agents/genesis/orchestrator.py'

# 1. Load schema directly
import importlib.util
spec_schema = importlib.util.spec_from_file_location("schema", schema_path)
schema_module = importlib.util.module_from_spec(spec_schema)
spec_schema.loader.exec_module(schema_module)
sys.modules['movie_os.agents.genesis.schema'] = schema_module

# 2. Load the orchestrator (which will now use our injected schema module)
spec_orch = importlib.util.spec_from_file_location("orchestrator", orchestrator_path)
orchestrator_module = importlib.util.module_from_spec(spec_orch)
sys.modules['movie_os.agents.genesis.orchestrator'] = orchestrator_module

# Now run the pipeline
def main():
    print("="*60)
    print("🚀 GENESIS ORCHESTRATOR START")
    # synopsis = "A man stops initiating intimacy after marriage because repeated rejection slowly convinces him he is no longer desired."
    synopsis = "A married couple's slow drift told through accumulated micro-moments. Ethan and Claire have been married seven years. They have a three-year-old daughter. He used to leave handwritten notes. She still keeps one in her drawer. This is the story of how ordinary people quietly become strangers to the people they love."
    print(f"INPUT: {synopsis}")
    print("="*60 + "\n")

    # Instantiate and run via our injected modules
    from orchestrator import GenesisOrchestrator
    output = GenesisOrchestrator().run(synopsis)

    # 1. Story DNA
    print("--- STORY DNA (The Core Decision Layer) ---")
    print(f"Territory: {output.dna.territory}")
    print(f"Archetype: {output.dna.archetype}")
    print(f"Theme: {output.dna.theme}\n")

    # 2. Audio Manifest
    print("--- AUDIO MANIFEST (For ElevenLabs / ComfyUI Audio Nodes) ---")
    for zone, track in output.audio_manifest.soundtrack_zones.items():
        print(f"  - Act Zone: {track}")
    
    print("\nVoiceover Prosody Overrides:")
    for scene_num, mod in output.audio_manifest.prosody_override.items():
        print(f"  - Scene {scene_num}: rate={mod['rate']}, vol={mod['volume']}, pitch={mod['pitch']}")

    # 3. Visual Prompts
    print("\n--- VISUAL PROMPT BUNDLE (Ready for Flux / SDXL) ---")
    print("Negative Prompts:")
    print(f"  {output.visual_prompts.negative_prompts}\n")
    
    print("Scene-by-Scene Positive Prompts:")
    for i, prompt in enumerate(output.visual_prompts.prompts):
        print(f"[Scene {i+1}] {prompt}")

    print("\n" + "="*60)
    print("✅ GENESIS PIPELINE COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
