"""
StorytellerAgent: The creative engine of the Genesis Pipeline.
Takes a high-level synopsis and generates a structured, cinematic screenplay with dialogue and voice-over.
"""

import sys
sys.path.insert(0, '/Users/santosh/Desktop/projects/videoGen')

from pydantic import BaseModel
from movie_os.llm.client import OllamaClient
from movie_os.agents.genesis.schema import NarrativeDNA, ScreenplayOutput, DialogueLine, SceneBeat

class StorytellerAgent:
    """Generates the narrative structure and screenplay for a production."""
    
    def __init__(self):
        self.llm = OllamaClient(model="qwen2.5-coder:32b") # Uses local LLM
    
    def extract_dna(self, synopsis: str) -> NarrativeDNA:
        """Extracts the core narrative identity from the synopsis."""
        prompt = f"""
        Analyze the following synopsis and define its creative soul.
        
        Synopsis: {synopsis}
        
        Return valid JSON matching this schema:
        {{
          "territory": "Genre/Emotional Space",
          "archetype": "Character Arc Type",
          "theme": "Philosophical Core",
          "visual_motif": "Recurring Visual Element"
        }}
        """
        response = self.llm.generate(prompt, temperature=0.7)
        # Simple JSON extraction (in production use json_repair or similar)
        return NarrativeDNA.model_validate_json(response)

    def generate_screenplay(self, dna: NarrativeDNA, synopsis: str) -> ScreenplayOutput:
        """Generates the full screenplay with cinematic pacing and dialogue."""
        
        prompt = f"""
        You are a master film director and screenwriter. Based on the following narrative DNA, write a detailed screenplay.

        ## DIRECTOR'S NOTES (Strictly Follow):
        - Target Runtime: 15+ Minutes. Achieve this through slow, deliberate pacing, lingering shots, and meaningful silence.
        - Visual Style: Cinematic realism, shallow depth of field, muted tones.
        - Audio: Use ambient sound to build tension. Dialogue should be sparse and heavy with subtext.

        ## NARRATIVE DNA:
        Territory: {dna.territory}
        Archetype: {dna.archetype}
        Theme: {dna.theme}
        Visual Motif: {dna.visual_motif}

        ## SYNOPSIS TO EXPAND:
        "{synopsis}"

        ## OUTPUT FORMAT (JSON ONLY):
        {{
          "title": "Catchy Title",
          "logline": "One sentence summary",
          "scenes": [
            {{
              "id": 1,
              "title": "Scene Name",
              "location": "Setting",
              "time": "Time of Day",
              "duration_estimate": "X Mins",
              "visual_direction": "Cinematic instructions (Camera/Lighting)",
              "dialogue": [
                {{ "speaker": "NAME", "delivery": "Tone", "text": "...", "subtext": "Implied meaning" }}
              ],
              "voice_over": "Optional internal monologue text",
              "audio_cues": ["Sound 1", "Sound 2"]
            }}
          ]
        }}
        """
        
        response = self.llm.generate(prompt, temperature=0.8)
        
        # Parse JSON response safely
        import json
        try:
            data = json.loads(response)
            return ScreenplayOutput.model_validate(data)
        except Exception as e:
            print(f"Error parsing screenplay JSON: {e}")
            return ScreenplayOutput(title="Error", logline="Failed to generate", scenes=[])

