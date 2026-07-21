import sys
sys.path.insert(0, '/Users/santosh/Desktop/projects/videoGen')

# Stub Pydantic to allow imports in environments where it's missing
class StubModel:
    @classmethod
    def model_rebuild(cls): pass
    class Config: pass

class PydanticStub:
    BaseModel = StubModel
    ConfigDict = lambda **kw: {}
    Field = lambda *a, **kw: None

sys.modules['pydantic'] = PydanticStub()

from movie_os.agents.genesis.orchestrator import GenesisOrchestrator

synopsis = "A man stops initiating intimacy after marriage because repeated rejection slowly convinces him he is no longer desired."

print("="*60)
print("🚀 GENESIS ORCHESTRATOR START")
print(f"INPUT: {synopsis}")
print("="*60 + "\n")

output = GenesisOrchestrator().run(synopsis)

# Output: Narrative DNA
print("--- STORY DNA (The Core Decision Layer) ---")
print(f"Territory: {output.dna.territory}")
print(f"Archetype: {output.dna.archetype}")
print(f"Theme: {output.dna.theme}\n")

# Output: Audio Manifest
print("--- AUDIO MANIFEST (For ElevenLabs / ComfyUI Audio Nodes) ---")
for zone, track in output.audio_manifest.soundtrack_zones.items():
    print(f"  - Act Zone: {track}")

print("\nVoiceover Prosody Overrides:")
for scene_num, mod in output.audio_manifest.prosody_override.items():
    print(f"  - Scene {scene_num}: {mod}")

# Output: Visual Prompts
print("\n--- VISUAL PROMPT BUNDLE (Ready for Flux / SDXL) ---")
print("Negative Prompts:")
print(f"  {output.visual_prompts.negative_prompts}\n")

print("Scene-by-Scene Positive Prompts:")
for i, prompt in enumerate(output.visual_prompts.prompts):
    print(f"[Scene {i+1}] {prompt}")

print("\n" + "="*60)
print("✅ GENESIS PIPELINE COMPLETE")
print("="*60)
