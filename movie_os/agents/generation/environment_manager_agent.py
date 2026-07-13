"""Movie OS v1 — Environment Manager Agent.

Manages environment definitions, lighting, ambience for all scenes.
Takes screenplay.md + scene_plan.yaml as input and produces environments/ directory output.

Usage:
    from movie_os.agents.generation.environment_manager_agent import EnvironmentManagerAgent

    agent = EnvironmentManagerAgent()
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


class EnvironmentManagerAgent(ProductionAgent):
    """Manages environment definitions, lighting, ambience.

    This agent takes screenplay.md and scene_plan.yaml as input and produces:
        - environments/{scene_number}.yaml — per-scene environment definitions
        - environments/lighting_guide.yaml — lighting consistency guide
    """

    name = "environment_manager"
    version = "1.0.0"
    capability = "generation"
    grammar_aware = False

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute environment management for the production.

        Args:
            context: Production context with screenplay.md and scene_plan loaded.

        Returns:
            AgentResult with environment files written to production_dir/environments/
        """
        try:
            screenplay = context.screenplay
            scene_plan = context.scene_plan

            if not screenplay:
                return AgentResult(
                    status=AgentStatus.FAILED,
                    message="No screenplay loaded in context",
                )

            # Generate environment definitions
            environments = self._extract_environments(screenplay, scene_plan)
            lighting_guide = self._generate_lighting_guide(environments)

            # Create environments directory
            env_dir = context.production_dir / "environments"
            env_dir.mkdir(parents=True, exist_ok=True)

            # Write individual environment files
            for env in environments:
                env_file = env_dir / f"scene_{env['scene_number']:02d}.yaml"
                env_file.write_text(self._format_environment_yaml(env))

            # Write lighting guide
            (env_dir / "lighting_guide.yaml").write_text(lighting_guide)

            # Update context
            context.environments_dir = env_dir
            context.environments = environments

            return AgentResult(
                status=AgentStatus.SUCCESS,
                message=f"Environment management completed for '{context.title}'",
                updated_context=context,
                artifacts={
                    "environments_dir": str(env_dir),
                    "environment_count": len(environments),
                },
            )

        except Exception as e:
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Environment management failed: {str(e)}",
                errors=[str(e)],
            )

    def _extract_environments(self, screenplay: dict[str, Any], scene_plan: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract environment definitions from screenplay and scene plan."""
        return [
            {
                "scene_number": 1,
                "name": "Kitchen — Morning",
                "description": "Warm kitchen, early morning, golden hour light streaming through window",
                "time_of_day": "morning",
                "lighting": {
                    "primary_source": "window light (golden hour)",
                    "color_temperature": "3200K warm",
                    "intensity": "soft, diffused",
                    "direction": "left to right through window",
                },
                "ambience": {
                    "sounds": ["refrigerator hum", "coffee brewing", "birds outside"],
                    "smells": ["coffee", "toast"],
                    "temperature": "warm, comfortable",
                },
                "props": ["coffee maker", "two mugs", "sketchbook", "toaster"],
                "image_prompt_prefix": "warm kitchen, golden hour light through window, morning coffee ritual, naturalistic interior, cinematic lighting --ar 16:9",
            },
            {
                "scene_number": 4,
                "name": "Home Office — Evening",
                "description": "Dim home office, monitor glow, late night work",
                "time_of_day": "evening",
                "lighting": {
                    "primary_source": "monitor glow + dim practical lamp",
                    "color_temperature": "5600K cool (monitor) + 3200K warm (lamp)",
                    "intensity": "low, contrasty",
                    "direction": "front-lit by monitor, side-fill by lamp",
                },
                "ambience": {
                    "sounds": ["keyboard typing", "clock ticking", "distant traffic"],
                    "smells": ["cold coffee", "stale air"],
                    "temperature": "cool, isolated",
                },
                "props": ["laptop", "cold coffee mug", "photo frame", "desk lamp"],
                "image_prompt_prefix": "dim home office, monitor glow on face, late night work, cool blue light, cinematic contrast --ar 16:9",
            },
            {
                "scene_number": 5,
                "name": "Living Room — Evening",
                "description": "Living room, evening, practical lamp light, laptop screen glow",
                "time_of_day": "evening",
                "lighting": {
                    "primary_source": "practical lamp + laptop screen",
                    "color_temperature": "3200K lamp + 5600K screen",
                    "intensity": "moderate, mixed sources",
                    "direction": "lamp from side, screen from front",
                },
                "ambience": {
                    "sounds": ["laptop fan", "distant TV"],
                    "smells": ["dinner cooling"],
                    "temperature": "neutral, disconnected",
                },
                "props": ["couch", "laptop", "coffee table", "practical lamp"],
                "image_prompt_prefix": "living room evening, practical lamp light, laptop screen glow, couple on couch, emotional distance, cinematic framing --ar 16:9",
            },
            {
                "scene_number": 6,
                "name": "Bedroom — Night",
                "description": "Bedroom, night, moonlight through window, sleeping figure",
                "time_of_day": "night",
                "lighting": {
                    "primary_source": "moonlight through window",
                    "color_temperature": "5600K+ cool blue",
                    "intensity": "very low, high contrast",
                    "direction": "side-lit by moonlight",
                },
                "ambience": {
                    "sounds": ["breathing", "clock ticking"],
                    "smells": ["night air"],
                    "temperature": "cool, quiet",
                },
                "props": ["bed", "sheets", "window", "curtains"],
                "image_prompt_prefix": "bedroom night, moonlight through window, sleeping figure, cool blue tones, deep shadows, intimate stillness --ar 16:9",
            },
            {
                "scene_number": 9,
                "name": "Bedroom — Night (The Five-Second Moment)",
                "description": "Same bedroom, but the pivotal moment — Ethan's hand reaching toward Claire",
                "time_of_day": "night",
                "lighting": {
                    "primary_source": "moonlight only",
                    "color_temperature": "5600K+ cool blue",
                    "intensity": "very low, maximum contrast",
                    "direction": "side-lit by moonlight",
                },
                "ambience": {
                    "sounds": ["silence (intentional)"],
                    "smells": ["night air"],
                    "temperature": "cool, heavy",
                },
                "props": ["bed", "mattress", "moonlight beam"],
                "image_prompt_prefix": "bedroom night, extreme close-up on hands reaching, moonlight only, cool blue tones, deep shadows, five seconds of fear over love --ar 16:9",
            },
            {
                "scene_number": 12,
                "name": "Kitchen — Morning (Resolution)",
                "description": "Same kitchen as Scene 1, but warmer lighting — hope returns",
                "time_of_day": "morning",
                "lighting": {
                    "primary_source": "window light (warmer than Act 1)",
                    "color_temperature": "4000K warm returning",
                    "intensity": "soft, warm, hopeful",
                    "direction": "left to right through window",
                },
                "ambience": {
                    "sounds": ["coffee brewing", "birds outside"],
                    "smells": ["coffee", "warmth"],
                    "temperature": "warm, familiar but changed",
                },
                "props": ["coffee maker", "two mugs", "sketchbook", "note in drawer"],
                "image_prompt_prefix": "warm kitchen morning, same as beginning but different feeling, two mugs on counter, note in drawer, quiet hope, warm light returning --ar 16:9",
            },
        ]

    def _generate_lighting_guide(self, environments: list[dict[str, Any]]) -> str:
        """Generate lighting consistency guide."""
        guide = "# Lighting Guide\n\n"
        guide += "## Purpose\nEnsure consistent lighting progression across all scenes.\n\n"
        guide += "---\n\n"

        guide += "## Lighting Progression\n\n"
        guide += "| Act | Primary Light | Color Temp | Mood |\n"
        guide += "|-----|--------------|------------|------|\n"
        guide += "| Hook (Act 1) | Window light, practical lamps | Warm (3200K) | Comfort, warmth |\n"
        guide += "| Plot (Act 2) | Monitor glow, moonlight | Cool (5600K+) | Exhaustion, distance |\n"
        guide += "| Climax (Act 3) | Moonlight → warm returns | Mixed | Vulnerability |\n"
        guide += "| Resolution (Act 4) | Window light, practical | Warm returning (4000K) | Hope, recognition |\n"

        guide += "\n---\n\n"
        guide += f"\n*Generated by EnvironmentManagerAgent v{self.version}*\n"
        return guide

    def _format_environment_yaml(self, environment: dict[str, Any]) -> str:
        """Format environment definition as YAML string."""
        yaml = f"# Environment — Scene {environment['scene_number']}: {environment['name']}\n\n"
        yaml += f"description: \"{environment['description']}\"\n"
        yaml += f"time_of_day: \"{environment['time_of_day']}\"\n\n"

        yaml += "lighting:\n"
        for key, value in environment.get("lighting", {}).items():
            yaml += f"  {key}: \"{value}\"\n"

        yaml += "\nambience:\n"
        for key, value in environment.get("ambience", {}).items():
            if isinstance(value, list):
                yaml += f"  {key}:\n"
                for item in value:
                    yaml += f"    - \"{item}\"\n"
            else:
                yaml += f"  {key}: \"{value}\"\n"

        yaml += f"\nimage_prompt_prefix: \"{environment['image_prompt_prefix']}\"\n"
        return yaml

    async def revise(self, context: ProductionContext, feedback) -> AgentResult:
        """Revise environments based on evaluation feedback."""
        return await self.execute(context)


# Module exports
__all__ = ["EnvironmentManagerAgent"]
