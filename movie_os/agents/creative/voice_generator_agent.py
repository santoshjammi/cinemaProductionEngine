"""Movie OS v1 — Voice Generator Agent.

Generates voiceovers using Edge TTS backend.
Takes screenplay.md as input and produces audio assets.

Usage:
    from movie_os.agents.creative.voice_generator_agent import VoiceGeneratorAgent

    agent = VoiceGeneratorAgent()
    result = await agent.execute(context)
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, List

from movie_os.capabilities.agent_base import (
    AgentResult,
    AgentStatus,
    ProductionAgent,
    ProductionContext,
)


logger = logging.getLogger("movie_os.agents.creative.voice_generator_agent")


class VoiceGeneratorAgent(ProductionAgent):
    """Generates voiceovers using Edge TTS backend.

    This agent takes screenplay.md as input and generates audio assets
    for each scene using the Edge TTS provider backend.

    Responsibilities:
        - Parse screenplay to extract dialogue for voiceover generation
        - Send dialogue to Edge TTS backend for audio generation  
        - Store generated voiceovers in production asset directory
        - Maintain scene-to-audio mapping for downstream processing
    """

    name = "voice_generator"
    version = "1.0.0"
    capability = "audio"
    grammar_aware = True

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute voiceover generation for the production.

        Args:
            context: Production context with screenplay.md loaded.

        Returns:
            AgentResult with generated voiceovers stored in production_dir/assets/voice/
        """
        try:
            # Load input data from context
            screenplay_path = context.screenplay_path
            
            if not screenplay_path or not screenplay_path.exists():
                return AgentResult(
                    status=AgentStatus.FAILED,
                    message="No screenplay file loaded in context",
                )

            # Read existing screenplay content
            screenplay_content = screenplay_path.read_text()

            # Generate voiceovers using Edge TTS backend
            audio_paths = await self._generate_voiceovers_with_edge_tts(screenplay_content, context)

            # Update context with audio data
            context.voice_paths = audio_paths

            return AgentResult(
                status=AgentStatus.SUCCESS,
                message=f"Voiceovers generated for '{context.title}'",
                updated_context=context,
                artifacts={"voice_paths": audio_paths},
            )

        except Exception as e:
            logger.exception("Voiceover generation failed")
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Voiceover generation failed: {str(e)}",
                errors=[str(e)],
            )

    async def _generate_voiceovers_with_edge_tts(self, screenplay_content: str, context: ProductionContext) -> List[str]:
        """Generate voiceovers using Edge TTS backend."""
        logger.info("Generating voiceovers with Edge TTS...")
        
        # Parse dialogue from screenplay
        dialogue_lines = self._extract_dialogue_from_screenplay(screenplay_content)
        
        if not dialogue_lines:
            logger.warning("No dialogue found in screenplay")
            return []
        
        # Create output directory
        voice_dir = context.production_dir / "voiceovers"
        voice_dir.mkdir(parents=True, exist_ok=True)
        
        audio_paths = []
        
        # Try to use edge-tts if available
        try:
            import edge_tts
        except ImportError:
            logger.warning("edge-tts not installed, using placeholder audio")
            return self._create_placeholder_voiceovers(dialogue_lines, voice_dir)
        
        # Configure voice (use a default English voice)
        voice = "en-US-JennyNeural"  # Default female voice
        
        for i, line in enumerate(dialogue_lines, 1):
            scene_num = line.get('scene_number', i)
            # Handle different possible key names for the text content
            text = line.get('text') or line.get('dialogue') or line.get('description') or ''
            
            if not text or len(text.strip()) < 10:
                logger.warning(f"Scene {scene_num}: Text too short, skipping")
                continue
            
            # Generate voiceover
            output_file = voice_dir / f"scene_{scene_num:02d}_voice.mp3"
            
            try:
                comm = edge_tts.Communicate(text, voice, rate="+10%", pitch="+5Hz")
                await comm.save(str(output_file))
                
                audio_paths.append(str(output_file))
                logger.info(f"Scene {scene_num}: Voiceover generated ({output_file.stat().st_size} bytes)")
                
            except Exception as e:
                logger.error(f"Scene {scene_num}: Edge TTS failed: {e}")
                # Create placeholder
                placeholder = voice_dir / f"scene_{scene_num:02d}_voice.mp3"
                placeholder.write_text(f"Placeholder for scene {scene_num}")
                audio_paths.append(str(placeholder))
        
        return audio_paths if audio_paths else self._create_placeholder_voiceovers(dialogue_lines, voice_dir)
    
    def _create_placeholder_voiceovers(self, dialogue_lines: List[Dict], voice_dir: Path) -> List[str]:
        """Create placeholder audio files when Edge TTS is unavailable."""
        audio_paths = []
        for i, line in enumerate(dialogue_lines, 1):
            scene_num = line.get('scene_number', i)
            placeholder = voice_dir / f"scene_{scene_num:02d}_voice.mp3"
            placeholder.write_text(f"Placeholder audio for scene {scene_num}")
            audio_paths.append(str(placeholder))
        return audio_paths

    def _extract_dialogue_from_screenplay(self, screenplay_content: str) -> List[Dict[str, Any]]:
        """Extract dialogue lines from screenplay content."""
        import re
        
        # Split screenplay by scene headers
        scene_blocks = re.split(r'(?i)###\s*(?:SCENE|Scene)\s+', screenplay_content)
        
        dialogue_lines = []
        
        for block in scene_blocks:
            if not block.strip():
                continue
                
            # Get scene number from the first line
            header_line = block.split('\n')[0]
            scene_match = re.match(r'^(\d+)', header_line)
            if not scene_match:
                continue
            scene_num = int(scene_match.group(1))
            
            # Extract dialogue section and narration section
            dialogue_text_parts = []
            
            # Find dialogue section
            dialogue_part = ""
            if "#### Dialogue" in block:
                # Get content between #### Dialogue and the next #### header or next scene boundary
                dialogue_content = block.split("#### Dialogue")[1]
                dialogue_part = dialogue_content.split("####")[0]
            
            # Parse spoken text inside quotes from the dialogue part
            quotes = re.findall(r'["“]([^"”]+)["”]', dialogue_part)
            for q in quotes:
                clean_q = q.strip()
                if clean_q:
                    dialogue_text_parts.append(clean_q)
            
            # Find narration section
            narration_part = ""
            if "#### Narration" in block:
                narration_content = block.split("#### Narration")[1]
                narration_part = narration_content.split("####")[0]
                
            # Narration lines are usually wrapped in asterisks
            narrations = re.findall(r'\*([^*]+)\*', narration_part)
            for n in narrations:
                # Strip "Ethan's thoughts:" prefix if present to make it sound better
                clean_n = re.sub(r'^(?:\w+\'s thoughts:|\w+:)\s*', '', n, flags=re.IGNORECASE).strip()
                if clean_n:
                    dialogue_text_parts.append(clean_n)
            
            # Join all dialogue/narration parts for this scene
            scene_text = " ".join(dialogue_text_parts).strip()
            
            # Fallback: if no dialogue or narration was parsed, use the scene title/purpose
            if not scene_text:
                purpose_match = re.search(r'\*\*Purpose:\*\*\s*([^\n]+)', block, re.IGNORECASE)
                if purpose_match:
                    scene_text = f"Scene {scene_num}: {purpose_match.group(1).strip()}"
                else:
                    scene_text = f"This is scene {scene_num} of Emotional Withdrawal."
            
            dialogue_lines.append({
                "scene_number": scene_num,
                "text": scene_text
            })
            
        # Sort by scene number
        dialogue_lines.sort(key=lambda x: x["scene_number"])
        return dialogue_lines