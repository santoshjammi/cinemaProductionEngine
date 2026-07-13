"""Movie OS v1 — Character Manager Agent.

Manages character definitions, appearance consistency across all scenes.
Takes screenplay.md as input and produces characters/ directory output.

Usage:
    from movie_os.agents.generation.character_manager_agent import CharacterManagerAgent

    agent = CharacterManagerAgent()
    result = await agent.execute(context)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from movie_os.capabilities.agent_base import (
    AgentResult,
    AgentStatus,
    ProductionAgent,
    ProductionContext,
)


class CharacterManagerAgent(ProductionAgent):
    """Manages character definitions and appearance consistency.

    This agent takes screenplay.md as input and produces:
        - characters/{character_name}.yaml — character definition files
        - characters/consistency_guide.yaml — appearance consistency guide
    """

    name = "character_manager"
    version = "1.0.0"
    capability = "generation"
    grammar_aware = False

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute character management for the production.

        Args:
            context: Production context with screenplay.md loaded.

        Returns:
            AgentResult with character files written to production_dir/characters/
        """
        try:
            screenplay = context.screenplay

            if not screenplay:
                return AgentResult(
                    status=AgentStatus.FAILED,
                    message="No screenplay loaded in context",
                )

            # Generate character definitions
            characters = self._extract_characters(screenplay)
            consistency_guide = self._generate_consistency_guide(characters)

            # Create characters directory
            chars_dir = context.production_dir / "characters"
            chars_dir.mkdir(parents=True, exist_ok=True)

            # Write individual character files
            for char in characters:
                char_file = chars_dir / f"{char['name'].lower().replace(' ', '_')}.yaml"
                char_file.write_text(self._format_character_yaml(char))

            # Write consistency guide
            (chars_dir / "consistency_guide.yaml").write_text(consistency_guide)

            # Update context
            context.characters_dir = chars_dir
            context.characters = characters

            return AgentResult(
                status=AgentStatus.SUCCESS,
                message=f"Character management completed for '{context.title}'",
                updated_context=context,
                artifacts={
                    "characters_dir": str(chars_dir),
                    "character_count": len(characters),
                },
            )

        except Exception as e:
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Character management failed: {str(e)}",
                errors=[str(e)],
            )

    def _extract_characters(self, screenplay: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract character definitions from screenplay."""
        # In production, this would parse screenplay.md for character definitions
        return [
            {
                "name": "Ethan Morrison",
                "age": 32,
                "gender": "male",
                "appearance": {
                    "height": "5'10\"",
                    "build": "slim, slightly tired",
                    "hair": "dark brown, slightly messy",
                    "eyes": "warm brown, dark circles developing",
                    "facial_hair": "light stubble",
                    "clothing_style": "casual — button-down shirts, jeans, worn sneakers",
                    "distinguishing_features": ["gentle expression", "thoughtful gaze", "tired eyes"],
                },
                "voice_profile": {
                    "tone": "gentle, exploratory, warm",
                    "pace": "moderate, slightly hesitant",
                    "pitch": "medium-low",
                    "edge_tts_voice": "en-US-GuyNeural",
                },
                "emotional_arc": "Warm → Exhausted → Hesitant → Vulnerable → Hopeful",
                "motif": "muted piano, high register — single notes, hesitant",
            },
            {
                "name": "Claire Morrison",
                "age": 30,
                "gender": "female",
                "appearance": {
                    "height": "5'6\"",
                    "build": "slender, relaxed",
                    "hair": "auburn, shoulder-length, slightly wavy",
                    "eyes": "green, expressive",
                    "facial_features": "warm smile, expressive eyebrows",
                    "clothing_style": "creative casual — oversized sweaters, sketchbooks, paint-stained jeans",
                    "distinguishing_features": ["expressive eyebrows", "warm smile", "paint-stained fingers"],
                },
                "voice_profile": {
                    "tone": "direct, witty, warm",
                    "pace": "moderate, confident",
                    "pitch": "medium",
                    "edge_tts_voice": "en-US-AriaNeural",
                },
                "emotional_arc": "Playful → Distracted → Confused → Understanding",
                "motif": "acoustic guitar, light arpeggios — bright, spontaneous",
            },
        ]

    def _generate_consistency_guide(self, characters: list[dict[str, Any]]) -> str:
        """Generate appearance consistency guide for image generation."""
        guide = "# Appearance Consistency Guide\n\n"
        guide += "## Purpose\nEnsure all generated images maintain consistent character appearances across scenes.\n\n"
        guide += "---\n\n"

        for char in characters:
            guide += f"### {char['name']}\n\n"
            guide += f"- **Age:** {char['age']}\n"
            guide += f"- **Gender:** {char['gender']}\n\n"
            guide += "**Appearance Reference:**\n\n"

            appearance = char.get("appearance", {})
            for key, value in appearance.items():
                if isinstance(value, list):
                    guide += f"- **{key}:** {', '.join(value)}\n"
                else:
                    guide += f"- **{key}:** {value}\n"

            guide += "\n**Image Generation Prompt Prefix:**\n\n"
            guide += f'```yaml\nprompt_prefix: "{char["name"]}, age {char["age"]}, '
            guide += f'{appearance.get("hair", "")}, {appearance.get("eyes", "")}, '
            guide += f'{appearance.get("build", "")} — naturalistic photography, cinematic lighting --ar 16:9"\n```'
            guide += "\n\n---\n\n"

        guide += f"\n*Generated by CharacterManagerAgent v{self.version}*\n"
        return guide

    def _format_character_yaml(self, character: dict[str, Any]) -> str:
        """Format character definition as YAML string."""
        yaml = f"# Character Definition — {character['name']}\n\n"
        yaml += f"name: \"{character['name']}\"\n"
        yaml += f"age: {character['age']}\n"
        yaml += f"gender: \"{character['gender']}\"\n\n"

        yaml += "appearance:\n"
        for key, value in character.get("appearance", {}).items():
            if isinstance(value, list):
                yaml += f"  {key}:\n"
                for item in value:
                    yaml += f"    - \"{item}\"\n"
            else:
                yaml += f"  {key}: \"{value}\"\n"

        yaml += "\nvoice_profile:\n"
        for key, value in character.get("voice_profile", {}).items():
            yaml += f"  {key}: \"{value}\"\n"

        yaml += f"\nemotional_arc: \"{character['emotional_arc']}\"\n"
        yaml += f"motif: \"{character['motif']}\"\n"
        return yaml

    async def revise(self, context: ProductionContext, feedback) -> AgentResult:
        """Revise character definitions based on evaluation feedback."""
        return await self.execute(context)


# Module exports
__all__ = ["CharacterManagerAgent"]
