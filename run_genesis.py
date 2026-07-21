"""
Genesis Pipeline Driver: Programmatic Scene Generation.
Takes a synopsis and outputs the full movie-style storyboard.
"""
import sys
sys.path.insert(0, '/Users/santosh/Desktop/projects/videoGen')

from movie_os.agents.genesis.orchestrator import GenesisOrchestrator

def run_genesis(synopsis: str):
    orchestrator = GenesisOrchestrator()
    print(f"--- INITIATING GENESIS PIPELINE ---")
    print(f"INPUT SYNOPSIS: {synopsis}")
    
    # Run the full pipeline: DNA -> Screenplay -> Audio/Visual Prompts
    output = orchestrator.run(synopsis)
    
    # Present the screenplay section in a readable "Movie Style" format
    print("\n" + "="*60)
    print(f"🎬 TITLE: {output.screenplay.title}")
    print("="*60)
    
    for scene in output.screenplay.scenes:
        print(f"\n### SCENE {scene.id}: {scene.title}")
        print(f"[{scene.location}] - {scene.time} (Est. {scene.duration_estimate})")
        print("-" * 40)
        
        # Visuals
        print(f"DIRECTION: {scene.visual_direction}")
        if scene.audio_cues:
            print(f"AUDIO CUES: {' | '.join(scene.audio_cues)}")
            
        # Dialogue
        for line in scene.dialogue:
            print(f"> {line.speaker} ({line.delivery}): \"{line.text}\"")
            
        # Voice Over
        if scene.voice_over:
            print(f"(V.O.): {scene.voice_over}")

    print("\n" + "="*60)
    print("✅ GENESIS PIPELINE COMPLETE - READY FOR RENDERING")
    print("="*60)

if __name__ == "__main__":
    # Example 1: The "Quiet Room" (Withdrawal)
    syn_1 = "A man stops initiating intimacy after marriage because repeated rejection slowly convinces him he is no longer desired."
    
    # Example 2: A generic "Hero's Journey" for testing
    # syn_2 = "An old mechanic finds a vintage car in his barn that can travel back in time. He decides to fix his past mistake with his daughter."
    
    run_genesis(syn_1)
