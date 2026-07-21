"""
Storyteller Sub-Agent: Generates narrative DNA, scripts, and character arcs.
"""
import json
import logging
from typing import Dict, Any, Optional

from config.models import InputConfig, InputValidationError
from config.ollama_client import OllamaClient
from backend.app.services.genesis.prompt_config import STORYTELLER_SYSTEM_PROMPT, STORYTELLER_USER_TEMPLATE

logger = logging.getLogger("genesis_storyteller")

class StorytellerAgent:
    """Generates the core narrative structure: story, scenes, and dialogues."""

    def __init__(self, llm_client: Optional[OllamaClient] = None):
        self.llm = llm_client or OllamaClient()
        logger.info("StorytellerAgent initialized.")

    def generate(self, input_config: InputConfig) -> Dict[str, Any]:
        """Generate the complete story DNA."""
        logger.info(f"[Storytelling] Generating for: '{input_config.topic}' with tone '{input_config.emotional_tone.value}'")
        
        # 1. Prepare Context based on Producer Brief and Platform
        producer_context = "N/A"
        if input_config.producer_brief:
            pb = input_config.producer_brief
            producer_context = f"""
            Director's Brief:
            - Target Audience: {pb.get('targetAudience', 'General')}
            - Visual Style: {', '.join(pb.get('visualStyleGuide', []))}
            - Audio Mood: {pb.get('musicMood', 'Neutral')}
            - Voiceover Style: {pb.get('voiceOverStyle', 'Narrative')}
            """

        # 2. Build the user prompt using the template
        try:
            user_prompt = STORYTELLER_USER_TEMPLATE.format(
                topic=input_config.topic,
                tone=input_config.emotional_tone.value,
                platform=input_config.platform.value,
                length=input_config.story_length,
                producer_context=producer_context,
                character_constraints="" # Add specific constraints from UI later if needed
            )
        except KeyError as e:
            raise ValueError(f"Template formatting error: Missing {e}")

        # 3. Execute LLM call
        messages = [
            {"role": "system", "content": STORYTELLER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        try:
            response_text = self.llm.chat(
                messages,
                temperature=0.85,
                max_tokens=4000,
                top_p=0.95
            )
            
            # 4. Parse and Validate Output
            result = self._parse_json_response(response_text)
            logger.info(f"[Storytelling] Successfully generated story: {result.get('story', {}).get('title', 'Untitled')}")
            return result

        except InputValidationError as e:
            logger.error(f"Validation failed for generated DNA: {e}")
            raise e

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Extract structured JSON from the LLM response."""
        cleaned_text = text.strip()
        
        # Attempt to extract JSON from markdown blocks
        if "```" in cleaned_text:
            for part in cleaned_text.split("```"):
                if "json" in part.lower():
                    cleaned_text = part.replace("json", "").strip()
                    break
        
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            logger.warning("Could not parse JSON from Storyteller response. Falling back to a generic structure.")
            return {
                "story": {"title": input_config.topic, "synopsis": text[:200]},
                "scenes": [{"sceneNumber": 1, "description": "Default scene"}],
                "dialogues": []
            }
