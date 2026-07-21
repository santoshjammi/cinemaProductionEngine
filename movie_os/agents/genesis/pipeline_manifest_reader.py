"""
PipelineManifestReader: Reads and validates Genesis output files for downstream agents.
Ensures the "next phase" (Video Composer, TTS, Image Gen) gets a clean, verified input state.
"""

import json
from pathlib import Path
from typing import Optional

class PipelineManifestReader:
    def __init__(self, base_dir="pipeline/output"):
        self.base_dir = Path(base_dir)

    def get_latest_gen(self, production_id: str):
        """Finds the most recent generation directory for a specific production ID."""
        prod_path = self.base_dir / production_id
        if not prod_path.exists():
            return None
        
        gen_dirs = sorted([d for d in prod_path.iterdir() if d.is_dir()], reverse=True)
        return gen_dirs[0] if gen_dirs else None

    def read_manifest(self, production_id: str):
        """Reads manifest.json and returns its contents."""
        latest_gen = self.get_latest_gen(production_id)
        if not latest_gen:
            raise FileNotFoundError(f"No generations found for {production_id} in {self.base_dir}")
        
        manifest_path = latest_gen / "manifest.json"
        with open(manifest_path, "r") as f:
            return json.load(f), latest_gen

    def read_screenplay(self, production_id: str):
        """Reads screenplay.json from the latest generation."""
        _, gen_dir = self.read_manifest(production_id)
        with open(gen_dir / "screenplay.json", "r") as f:
            return json.load(f)

    def get_scene_list(self, production_id: str):
        """Returns a list of scene dictionaries ready for processing."""
        screenplay_data = self.read_screenplay(production_id)
        return screenplay_data.get("scenes", [])

