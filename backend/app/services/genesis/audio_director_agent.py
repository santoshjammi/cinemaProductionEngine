"""
Audio Director Sub-Agent: Generates music cues, SFX lists, and voiceover scripts.
"""
import json
import logging
from typing import Dict, Any, Optional

from config.models import InputConfig
from config.ollama_client import OllamaClient
from backend.app.services.genesis.prompt_config import AUDIO_DIRECTOR_SYSTEM_PROMPT, AUDIO_DIRECTOR_USER_TEMPLATE

logger = logging.getLogger("genesis_audio_director")

class AudioDirectorAgent:
    """Generates the 'Sound Design' layer of the production."""

    def __init__(self, llm_client: Optional[OllamaClient] = None):
        self.llm = llm_client or OllamaClient()
        logger.info("AudioDirectorAgent initialized.")

    def generate(self, narrative_dna: Dict[str, Any], input_config: InputConfig) -> Dict[str, Any]:
        """Generate audio cues and voiceover instructions for the entire story."""
        logger.info(f"[AudioDirector] Generating sound design for: '{input_config.topic}'")

        # 1. Build context from Producer Brief and Story DNA
        scenes_json = json.dumps(narrative_dna.get("scenes", []))
        
        producer_context = "N/A"
        if input_config.producer_brief:
            pb = input_config.producer_brief
            producer_context = f"""
            Director's Audio Brief:
            - Music Mood: {pb.get('musicMood', 'Neutral')}
            - Voiceover Style: {pb.get('voiceOverStyle', 'Narrative')}
            """

        # 2. Construct the prompt
        try:
            user_prompt = AUDIO_DIRECTOR_USER_TEMPLATE.format(
                scenes=scenes_json,
                music_mood=producer_context.split("Music Mood:")[1].split("\n")[0].strip() if "Music Mood:" in producer_context else "Neutral",
                voice_style=producer_context.split("Voiceover Style:")[1].split("\n")[0].strip() if "Voiceover Style:" in producer_context else "Narrative"
            )
        except KeyError as e:
            raise ValueError(f"Template formatting error: Missing {e}")

        messages = [
            {"role": "system", "content": AUDIO_DIRECTOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        # 3. Execute LLM call
        try:
            response_text = self.llm.chat(
                messages,
                temperature=0.75, # Slightly more creative for audio design
                max_tokens=4000,
                top_p=0.9
            )
            return self._parse_json_response(response_text)
        except Exception as e:
            logger.error(f"Audio Director failed to generate: {e}")
            raise e

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Extract the list of audio cues."""
        cleaned = text.strip()
        if "```" in cleaned:
            for part in cleaned.split("```"):
                if "json" in part.lower():
                    cleaned = part.replace("json", "").strip()
                    break
        return json.loads(cleaned)
