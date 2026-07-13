"""Movie OS v1 — Image Generator Agent.

Generates FLUX.1 images via ComfyUI per scene.
Takes screenplay/prompts as input and produces output/images/ directory output.

Usage:
    from movie_os.agents.generation.image_generator_agent import ImageGeneratorAgent

    agent = ImageGeneratorAgent()
    result = await agent.execute(context)
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

from movie_os.capabilities.agent_base import (
    AgentResult,
    AgentStatus,
    ProductionAgent,
    ProductionContext,
)
from movie_os.llm.comfyui_client import ComfyUIClient, ComfyUIConfig

logger = logging.getLogger(__name__)


class ImageGeneratorAgent(ProductionAgent):
    """Generates FLUX.1 images via ComfyUI per scene."""

    name = "image_generator"
    version = "1.0.0"
    capability = "generation"
    grammar_aware = False

    def __init__(self, comfyui_url: Optional[str] = None, width: int = 1024, height: int = 1024):
        super().__init__()
        self.comfyui_url = comfyui_url or "http://localhost:8188"
        self.width = width
        self.height = height

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute image generation for the production using ComfyUI/FLUX.1."""
        try:
            # Initialize ComfyUI client with local FLUX.1 models
            config = ComfyUIConfig(
                base_url=self.comfyui_url,
                width=self.width,
                height=self.height,
                workspace_root=str(Path(__file__).parent.parent.parent.parent),
            )
            client = ComfyUIClient(config)

            # Check if ComfyUI is running
            comfyui_available = await client.health_check()
            
            # Get production data from context
            scenes = getattr(context, 'scenes', []) or []
            screenplay_path = getattr(context, 'screenplay_path', None)
            
            images_dir = context.production_dir / "images"
            images_dir.mkdir(parents=True, exist_ok=True)

            if not scenes:
                # Try to load scenes from screenplay if available
                if screenplay_path and Path(screenplay_path).exists():
                    scenes = self._extract_scenes_from_screenplay(screenplay_path)
                
                if not scenes:
                    # Generate default scenes for the production
                    scenes = self._generate_default_scenes(context.title)

            generated_images = []
            failed_count = 0
            
            logger.info(f"Generating {len(scenes)} images via ComfyUI/FLUX.1...")

            for scene in scenes:
                scene_num = scene.get('scene_number', 1)
                prompt = scene.get('visual_prompt', scene.get('description', ''))
                negative_prompt = scene.get('negative_prompt', 'blurry, low quality, distorted, deformed, ugly')
                
                # Generate image using ComfyUI/FLUX.1
                result = await client.generate_image(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=self.width,
                    height=self.height,
                    steps=30,
                    cfg_scale=7.0,
                    output_dir=str(images_dir),
                )

                image_path = result.get('image_path')
                if result.get('success') and image_path:
                    generated_images.append({
                        "scene_number": scene_num,
                        "path": str(image_path),
                        "status": "generated",
                        "seed": result.get('seed'),
                    })
                    logger.info(f"Scene {scene_num}: Image generated successfully")
                else:
                    # Fallback: generate placeholder image if ComfyUI unavailable
                    fallback_path = images_dir / f"scene_{scene_num:02d}.png"
                    await self._generate_placeholder_image(prompt, fallback_path)
                    generated_images.append({
                        "scene_number": scene_num,
                        "path": str(fallback_path),
                        "status": "placeholder",
                        "error": result.get('error', 'ComfyUI unavailable'),
                    })
                    failed_count += 1
                    logger.warning(f"Scene {scene_num}: ComfyUI generation failed, using placeholder")

            # Generate manifest
            manifest = self._generate_manifest(context.title, generated_images)
            (images_dir / "MANIFEST.md").write_text(manifest)

            context.images_dir = images_dir
            context.generated_images = generated_images

            status = AgentStatus.SUCCESS if failed_count == 0 else AgentStatus.PARTIAL
            return AgentResult(
                status=status,
                message=f"Image generation completed: {len(generated_images)} images ({len(generated_images) - failed_count} real, {failed_count} placeholders)",
                updated_context=context,
                artifacts={
                    "images_dir": str(images_dir),
                    "image_count": len(generated_images),
                    "real_images": len(generated_images) - failed_count,
                    "placeholder_images": failed_count,
                    "comfyui_available": comfyui_available,
                },
            )

        except Exception as e:
            logger.error(f"Image generation failed: {e}", exc_info=True)
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Image generation failed: {str(e)}",
                errors=[str(e)],
            )

    def _extract_scenes_from_screenplay(self, screenplay_path: str) -> list[dict]:
        """Extract scene descriptions from screenplay markdown."""
        scenes = []
        content = Path(screenplay_path).read_text()
        
        # Parse scenes from screenplay (assuming standard format)
        current_scene = {}
        for line in content.split('\n'):
            if line.startswith('## Scene '):
                if current_scene:
                    scenes.append(current_scene)
                scene_num = int(line.replace('## Scene ', '').replace('.', '').strip())
                current_scene = {'scene_number': scene_num, 'visual_prompt': '', 'description': ''}
            elif current_scene and line.strip().startswith('**Visual:**'):
                current_scene['visual_prompt'] = line.split('**Visual:**')[1].strip()
            elif current_scene and line.strip().startswith('**Description:**'):
                current_scene['description'] = line.split('**Description:**')[1].strip()
        
        if current_scene:
            scenes.append(current_scene)
        
        return scenes if scenes else self._generate_default_scenes("Unknown Production")

    def _generate_default_scenes(self, title: str) -> list[dict]:
        """Generate default scenes for a production."""
        return [
            {"scene_number": i, "visual_prompt": f"Scene {i}", "description": f"Default scene {i} for {title}"}
            for i in range(1, 14)
        ]

    async def _generate_placeholder_image(self, prompt: str, output_path: Path) -> Path:
        """Generate a placeholder image using PIL if ComfyUI unavailable."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import random
            
            # Generate a gradient background
            img = Image.new('RGB', (self.width, self.height))
            draw = ImageDraw.Draw(img)
            
            # Create gradient
            color1 = (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))
            color2 = (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))
            
            for i in range(self.height):
                r = int(color1[0] + (color2[0] - color1[0]) * i / self.height)
                g = int(color1[1] + (color2[1] - color1[1]) * i / self.height)
                b = int(color1[2] + (color2[2] - color1[2]) * i / self.height)
                draw.line([(0, i), (self.width, i)], fill=(r, g, b))
            
            # Add text
            draw.text((50, 50), f"Scene: {prompt[:50]}", fill='white')
            draw.text((50, 100), "COMFYUI UNAVAILABLE - PLACEHOLDER", fill='yellow')
            
            img.save(output_path)
            return output_path
        except Exception as e:
            logger.error(f"Placeholder generation failed: {e}")
            raise

    def _generate_manifest(self, title: str, images: list[dict]) -> str:
        """Generate a manifest file for generated images."""
        manifest = f"""# Image Generation Manifest — {title}

## Version: v1.0
## Generated by: ImageGeneratorAgent v{self.version}
## Model: FLUX.1-dev (local)
## Backend: ComfyUI
## Total Scenes: {len(images)}

---

| Scene | Status | Path | Seed |
|-------|--------|------|------|
"""
        for img in images:
            manifest += f"| {img['scene_number']} | {img['status']} | {img['path']} | {img.get('seed', 'N/A')} |\n"
        
        manifest += f"\n*Generated by ImageGeneratorAgent v{self.version}*\n"
        return manifest

    async def revise(self, context: ProductionContext, feedback) -> AgentResult:
        """Revise image generation based on evaluation feedback."""
        # Update prompts based on feedback and regenerate
        if hasattr(feedback, 'get') and feedback.get('prompts'):
            context.updated_prompts = feedback['prompts']
        return await self.execute(context)


__all__ = ["ImageGeneratorAgent"]
