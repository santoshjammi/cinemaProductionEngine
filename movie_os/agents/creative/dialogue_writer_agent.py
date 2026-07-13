"""Movie OS v1 — Dialogue Writer Agent.

Refines and enhances dialogue in screenplays using Movie OS Screenplay Specification.
Takes screenplay.md as input and produces enhanced screenplay.md output.

Usage:
    from movie_os.agents.creative.dialogue_writer_agent import DialogueWriterAgent

    agent = DialogueWriterAgent()
    result = await agent.execute(context)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from movie_os.capabilities.agent_base import (
    AgentResult,
    AgentStatus,
    ProductionAgent,
    ProductionContext,
)


logger = logging.getLogger("movie_os.agents.creative.dialogue_writer_agent")


class DialogueWriterAgent(ProductionAgent):
    """Refines and enhances dialogue in screenplays.

    This agent takes screenplay.md as input and produces enhanced screenplay.md
    with more authentic, nuanced dialogue that matches the grammar's style.

    Responsibilities:
        - Enhance dialogue authenticity and emotional depth
        - Apply grammar-specific rules for dialogue style and pacing  
        - Ensure character voices remain consistent throughout
        - Refine stage directions for better visual storytelling
        - Maintain the emotional arc and cause-and-effect chain between scenes
    """

    name = "dialogue_writer"
    version = "1.0.0"
    capability = "story"
    grammar_aware = True

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute dialogue refinement for the screenplay.

        Args:
            context: Production context with screenplay.md loaded.

        Returns:
            AgentResult with enhanced screenplay.md written to production_dir/screenplay.md
        """
        try:
            # Load input data from context
            screenplay_path = context.screenplay_path
            grammar_config = context.grammar_config
            
            if not screenplay_path or not screenplay_path.exists():
                return AgentResult(
                    status=AgentStatus.FAILED,
                    message="No screenplay file loaded in context",
                )

            # Read existing screenplay content
            screenplay_content = screenplay_path.read_text()

            # Enhance dialogue using LLM
            enhanced_content = await self._enhance_dialogue_with_llm(screenplay_content, grammar_config, context)

            # Write enhanced screenplay.md to production directory
            output_path = context.production_dir / "screenplay.md"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(enhanced_content)

            # Update context with screenplay data
            context.screenplay_path = output_path

            return AgentResult(
                status=AgentStatus.SUCCESS,
                message=f"Dialogue enhanced for '{context.title}'",
                updated_context=context,
                artifacts={"screenplay_path": str(output_path)},
            )

        except Exception as e:
            logger.exception("Dialogue enhancement failed")
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Dialogue enhancement failed: {str(e)}",
                errors=[str(e)],
            )

    async def _enhance_dialogue_with_llm(self, screenplay_content: str, grammar: dict[str, Any], context: ProductionContext) -> str:
        """Enhance screenplay dialogue using local LLM (Ollama)."""
        from movie_os.llm.client import get_llm_client

        llm = get_llm_client()
        if not llm.is_available():
            logger.warning("LLM not available, falling back to basic enhancement")
            return self._enhance_dialogue_template(screenplay_content)

        # Get the grammar name if available
        grammar_name = context.grammar if hasattr(context, 'grammar') and context.grammar else "psychological_cinema"
        
        # Get the title if available
        title = context.title or "Untitled"
        
        system_prompt = f"""You are a senior dialogue editor for the Movie OS Cinema Production Engine.
Your job is to refine and enhance screenplay dialogue while maintaining the original structure.

Grammar: {grammar_name}
Production: {title}

Rules:
- Keep all existing YAML frontmatter and structure intact
- Enhance dialogue to be more authentic, nuanced, and emotionally resonant  
- Apply grammar-specific rules for dialogue style (e.g., psychological cinema focuses on subtext, hesitation)
- Ensure character voices remain consistent throughout
- Refine stage directions for better visual storytelling
- Never change the core scenes or emotional arc structure
- Maintain cause-and-effect chain between scenes
- Keep dialogue natural and conversation-like, not exposition-heavy

Movie OS Screenplay Specification:
1. YAML frontmatter per scene with all required fields (Purpose, Location, Time, Characters, Emotion, Mood)
2. Dialogue section with character names in ALL CAPS and stage directions in parentheses
3. Action section describing visual elements and movements  
4. Beat section with timing information (e.g., "pause: 2s")
5. Narration section for internal thoughts or voiceover
6. Director Notes with specific camera and editing instructions
7. Camera Intent section describing visual language (camera movement, framing)
8. Music Intent section with musical themes and cues
9. Silence/Pauses section for moments of quiet or tension

Focus on:
- Subtle emotional beats in dialogue
- Character-specific speech patterns and rhythms  
- Natural conversation flow with pauses and hesitations
- Realistic dialogue that matches character personalities
"""

        user_prompt = f"""Enhance the following screenplay dialogue to make it more authentic and emotionally resonant:

## Screenplay Content
{screenplay_content}

## Enhancement Guidelines

1. Refine dialogue to sound more natural and conversation-like
2. Add subtle emotional beats that don't change the scene structure  
3. Ensure character voices remain consistent throughout
4. Improve stage directions for better visual storytelling
5. Maintain all existing YAML frontmatter and scene structure exactly as-is

## Example of Enhanced Dialogue:

Before:
**ETHAN**
*(pouring coffee)* "You know what I noticed?"

**CLAIRE**
*(without looking up from her sketchbook)* "What?"

After:
**ETHAN**
*(pouring coffee, pausing)* "You know what I noticed?"

**CLAIRE**
*(without looking up from her sketchbook, then glancing at him)* "What?"

**ETHAN**
"You still take your coffee with two sugars. Even after seven years."

Return the entire screenplay content exactly as-is, but with enhanced dialogue that maintains all structure and YAML frontmatter."""
        
        # Generate content using LLM
        response = llm.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.6,
            max_tokens=8192
        )

        if response.success:
            return response.content
        else:
            logger.warning(f"LLM generation failed: {response.error}")
            return self._enhance_dialogue_template(screenplay_content)

    def _enhance_dialogue_template(self, screenplay_content: str) -> str:
        """Enhance dialogue with basic template when LLM is not available."""
        # For now, just return the original content as a placeholder
        return screenplay_content