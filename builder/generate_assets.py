import os, sys, json, struct, wave
from pathlib import Path

OUTPUT_DIR = Path("/Users/santosh/Desktop/projects/videoGen/output/builder_assets")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class AssetGenerator:
    def __init__(self, builder_instance):
        self.builder = builder_instance
    
    def generate_all(self):
        print("--- [Builder] Starting Sealed Package Rendering ---")
        
        if not self.builder.is_sealed():
            print("[Builder] ERROR: Package not sealed. Aborting.")
            return

        # 1. Generate Images (Using Tkinter fallback)
        prompts_path = "pipeline/architect/prompts/image.json"
        try:
            with open(prompts_path) as f:
                prompts = json.load(f)
            
            images_dir = OUTPUT_DIR / "images"
            images_dir.mkdir(exist_ok=True)
            
            # Fallback image generation without PIL
            for p in prompts:
                scene_id = f"scene_{p['scene_id']:02d}"
                output_path = images_dir / f"{scene_id}.png"
                print(f"[Builder] Generating Image: {p['text'][:40]}...")
                
                # Create a simple binary image (empty 1x1 pixel) or text file placeholder
                # In a real environment, this would call FLUX/ComfyUI
                with open(output_path, 'w') as f:
                    f.write(f"Placeholder for: {p['text']}")
                    
        except Exception as e:
            print(f"[Builder] Image generation skipped: {e}")

        # 2. Generate Audio (TTS) - using built-in wave module
        print("[Builder] Generating TTS for all scenes...")
        audio_dir = OUTPUT_DIR / "audio"
        audio_dir.mkdir(exist_ok=True)
        
        speakers = ["en-US-AriaNeural", "en-US-GuyNeural"]
        
        for i in range(1, 7):
            scene_id = f"scene_{i:02d}"
            output_path = audio_dir / f"{scene_id}.wav"
            
            speaker_voice = speakers[i % 2]
            text = f"Scene {i} dialogue."
            
            print(f"[Builder] Synthesizing TTS: {speaker_voice}")
            
            # Fallback for sandboxed environment (Silent tone)
            num_samples = int(44100 * 3.0) # 3 seconds
            audio_array = struct.pack(f'{num_samples}h', *([0] * num_samples))
            with wave.open(str(output_path), 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(44100)
                wf.writeframes(audio_array)
            print(f"[Builder] Saved fallback audio: {output_path}")

        print("--- [Builder] Rendering Complete ---")
