"""
Genesis Pipeline Runner (Standalone): Generates scenes from a synopsis and saves them to structured files.
Designed to work even without the full `movie_os` dependencies in this environment.
"""

import json
import os
from datetime import datetime
from pathlib import Path

def save_genesis_files(synopsis: str):
    """Simulates the pipeline generation and writes to pipeline/output/ew001."""
    
    # 1. Define the Output Structure (The "Manifest")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("pipeline/output/ew001") / f"gen_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 2. Mock the LLM Output (What StorytellerAgent would return)
    screenplay_data = {
        "title": "The Quiet Room",
        "logline": "A man slowly withdraws from his marriage after repeated small rejections.",
        "scenes": [
            {
                "id": 1,
                "title": "Morning Routine",
                "location": "Kitchen",
                "time": "Dawn",
                "duration_estimate": "2 Mins",
                "visual_direction": "Wide shot of Aryan pouring coffee. Cold blue lighting.",
                "dialogue": [
                    {"speaker": "ARYAN", "delivery": "Quietly", "text": "Did you sleep?"},
                    {"speaker": "SIA", "delivery": "Distracted", "text": "Mhm."}
                ],
                "voice_over": "It used to be she'd lean into my touch. Now a touch feels like a demand.",
                "audio_cues": ["Clock ticking", "Fridge hum"]
            },
            {
                "id": 2,
                "title": "The Mirror",
                "location": "Bathroom",
                "time": "Midnight",
                "duration_estimate": "3 Mins",
                "visual_direction": "Close up on Aryan's face. He looks tired.",
                "dialogue": [],
                "voice_over": "I think I've stopped wanting to be wanted because trying hurts less when you stop.",
                "audio_cues": ["Distant city sounds", "Water dripping"]
            }
        ]
    }

    audio_manifest_data = {
        "global_mood": "Melancholic / Sparse Piano",
        "soundtrack_zones": {"act_1": "Slow ambient pads", "act_2": "Silence"},
        "prosody_override": {1: "monotone", 2: "whisper"}
    }

    visual_bundle_data = {
        "dna": {"territory": "Melancholic Drama", "archetype": "The Silent Withdrawal", "theme": "Erosion of intimacy"},
        "prompts": [
            "Cinematic shot, Aryan pouring coffee, shallow depth of field, muted tones --v 2",
            "Close up of Aryan in mirror, dim yellow light, cold atmosphere --v 2"
        ],
        "negative_prompts": ["cartoon, bright colors, happy expression"]
    }

    manifest_data = {
        "production_id": "ew001",
        "timestamp": timestamp,
        "synopsis_source": synopsis,
        "files_generated": ["screenplay.json", "audio_manifest.json", "visual_bundle.json"]
    }

    # 3. Write the files
    with open(output_dir / "screenplay.json", "w") as f:
        json.dump(screenplay_data, f, indent=2)
    
    with open(output_dir / "audio_manifest.json", "w") as f:
        json.dump(audio_manifest_data, f, indent=2)

    with open(output_dir / "visual_bundle.json", "w") as f:
        json.dump(visual_bundle_data, f, indent=2)

    with open(output_dir / "manifest.json", "w") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"✅ Genesis files generated and saved to:\n   {output_dir}\n\n--- Preview of screenplay.json ---")
    print(json.dumps(screenplay_data['scenes'][0], indent=4))

if __name__ == "__main__":
    synopsis = "A man stops initiating intimacy after marriage because repeated rejection slowly convinces him he is no longer desired."
    save_genesis_files(synopsis)
