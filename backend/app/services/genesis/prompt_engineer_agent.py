"""
Prompt Engineer Sub-Agent: Translates narrative DNA into technical prompts.
"""
import json
import logging
from typing import Dict, Any, Optional

from config.models import InputConfig
from config.ollama_client import OllamaClient
from backend.app.services.genesis.prompt_config import PROMPT_ENGINEER_SYSTEM_PROMPT, PROMPT_ENGINEER_USER_TEMPLATE
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator
from backend.app.services.genesis.styles.style_loader import VisualStyleGuideLoader
from backend.app.services.genesis.manifest_generator import SynchronizationManifestGenerator

logger = logging.getLogger("genesis_prompt_engineer")

class PromptEngineerAgent:
    """Translates story DNA into visual and technical prompts for Flux/ComfyUI."""

    def __init__(self, llm_client: Optional[OllamaClient] = None):
        self.llm = llm_client or OllamaClient()
        logger.info("PromptEngineerAgent initialized.")

    def generate(self, narrative_dna: Dict[str, Any], input_config: InputConfig) -> Dict[str, Any]:
        """Generate cinematic and technical prompts for every scene."""
        logger.info(f"[PromptEngineering] Converting {len(narrative_dna.get('scenes', []))} scenes into prompts.")

        # 1. Load Active Styles (The DNA of the Visuals)
        style_loader = VisualStyleGuideLoader()
        style_guide_list = []
        
        if input_config.producer_brief and 'visualStyleGuide' in input_config.producer_brief:
            for style_name in input_config.producer_brief['visualStyleGuide']:
                rules = style_loader.load_style(style_name)
                style_guide_list.append(rules)
        
        visual_styles_applied = [s['name'] for s in style_guide_list] if style_guide_list else ['Cinematic Realism']

        # 2. Construct the prompt
        try:
            scenes_json = json.dumps(narrative_dna.get("scenes", []))
            
            user_prompt = PROMPT_ENGINEER_USER_TEMPLATE.format(
                scenes=scenes_json,
                visual_style=visual_style_guides,
                platform=input_config.platform.value,
                aspect_ratio=input_config.producer_brief.get('aspectRatio', '16:9') if input_config.producer_brief else '16:9',
                camera_settings="Standard cinematic lens"
            )
        except KeyError as e:
            raise ValueError(f"Template formatting error: Missing {e}")

        messages = [
            {"role": "system", "content": PROMPT_ENGINEER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        # 3. Execute LLM call
        try:
            response_text = self.llm.chat(
                messages,
                temperature=0.6, # Lower temp for technical consistency
                max_tokens=4000,
                top_p=0.9
            )
            return self._parse_json_response(response_text)
        except Exception as e:
            logger.error(f"Prompt Engineer failed to generate: {e}")
            raise e

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Extract the list of prompts."""
        cleaned = text.strip()
        if "```" in cleaned:
            for part in cleaned.split("```"):
                if "json" in part.lower():
                    cleaned = part.replace("json", "").strip()
                    break
        return json.loads(cleaned)
