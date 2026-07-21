"""
Output Writer: Saves Genesis Pipeline results to the filesystem in a structured JSON format.
Intended for consumption by downstream agents (Image Gen, TTS, Video Composer).
"""

import json
from datetime import datetime
from pathlib import Path

# Forward-compatible with Pydantic v1 and v2
try:
    from pydantic import BaseModel
    HAS_PYDANTIC = True
except ImportError:
    class BaseModel: pass
    HAS_PYDANTIC = False

class OutputWriter:
    """Handles saving the complete creative state of a production to disk."""
    
    def __init__(self, base_dir="pipeline/output"):
        self.base_dir = Path(base_dir)

    def save(self, output, production_id: str = "ew001", timestamp_str: str = None):
        """
        Saves the screenplay, audio manifest, and visual bundle to a versioned directory.
        Returns the path where files were saved.
        """
        ts = timestamp_str or datetime.now().strftime("%Y%m%d_%H%M%S")
        prod_dir = self.base_dir / production_id / f"gen_{ts}"
        prod_dir.mkdir(parents=True, exist_ok=True)

        # 1. Screenplay (The canonical script with scenes/dialogue)
        screenplay_data = output.screenplay.dict() if HAS_PYDANTIC else output.screenplay
        with open(prod_dir / "screenplay.json", "w") as f:
            json.dump(screenplay_data, f, indent=2)

        # 2. Audio Manifest (For ElevenLabs/Edge TTS agents)
        audio_data = output.audio_manifest.dict() if HAS_PYDANTIC else output.audio_manifest
        with open(prod_dir / "audio_manifest.json", "w") as f:
            json.dump(audio_data, f, indent=2)

        # 3. Visual Bundle (For Flux/ComfyUI agents)
        visual_prompts = output.visual_prompts.prompts if HAS_PYDANTIC else output.visual_prompts['prompts']
        negative_prompts = output.visual_prompts.negative_prompts if HAS_PYDANTIC else output.visual_prompts['negative_prompts']
        
        visual_data = {
            "dna": output.dna.dict() if HAS_PYDANTIC else output.dna,
            "prompts": visual_prompts,
            "negative_prompts": negative_prompts
        }
        with open(prod_dir / "visual_bundle.json", "w") as f:
            json.dump(visual_data, f, indent=2)

        # 4. Master Manifest (Ties everything together for the Video Composer)
        manifest = {
            "production_id": production_id,
            "timestamp": ts,
            "dna": output.dna.dict() if HAS_PYDANTIC else output.dna,
            "files_generated": [
                "screenplay.json",
                "audio_manifest.json", 
                "visual_bundle.json"
            ]
        }
        with open(prod_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)

        return prod_dir

