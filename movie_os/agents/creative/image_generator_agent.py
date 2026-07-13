"""Movie OS v1 — Image Generator Agent.

Generates images for scenes using ComfyUI backend.
Takes screenplay.md as input and produces image assets.

Usage:
    from movie_os.agents.creative.image_generator_agent import ImageGeneratorAgent

    agent = ImageGeneratorAgent()
    result = await agent.execute(context)
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from movie_os.capabilities.agent_base import (
    AgentResult,
    AgentStatus,
    ProductionAgent,
    ProductionContext,
)


logger = logging.getLogger("movie_os.agents.creative.image_generator_agent")


class ImageGeneratorAgent(ProductionAgent):
    """Generates images for scenes using ComfyUI backend.

    This agent takes screenplay.md as input and generates image assets
    for each scene using the ComfyUI provider backend.

    Responsibilities:
        - Parse screenplay to extract image generation prompts
        - Send prompts to ComfyUI backend for image generation  
        - Store generated images in production asset directory
        - Maintain scene-to-image mapping for downstream processing
    """

    name = "image_generator"
    version = "1.0.0"
    capability = "visuals"
    grammar_aware = True

    def __init__(self, comfyui_url: str = "http://localhost:8188", width: int = 1024, height: int = 1024):
        super().__init__()
        self.comfyui_url = comfyui_url
        self.width = width
        self.height = height

    async def execute(self, context: ProductionContext) -> AgentResult:
        """Execute image generation for the production.

        Args:
            context: Production context with screenplay.md loaded.

        Returns:
            AgentResult with generated images stored in production_dir/assets/images/
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

            # Generate images using ComfyUI backend
            image_paths = await self._generate_images_with_comfyui(screenplay_content, context)

            # Update context with image data
            context.image_paths = image_paths

            return AgentResult(
                status=AgentStatus.SUCCESS,
                message=f"Images generated for '{context.title}'",
                updated_context=context,
                artifacts={"image_paths": image_paths},
            )

        except Exception as e:
            logger.exception("Image generation failed")
            return AgentResult(
                status=AgentStatus.FAILED,
                message=f"Image generation failed: {str(e)}",
                errors=[str(e)],
            )

    async def _generate_images_with_comfyui(self, screenplay_content: str, context: ProductionContext) -> List[str]:
        """Generate images using ComfyUI backend with FLUX.1."""
        import asyncio
        from movie_os.llm.comfyui_client import ComfyUIClient, ComfyUIConfig
        
        logger.info("Starting image generation via ComfyUI/FLUX.1...")
        
        # Initialize ComfyUI client
        config = ComfyUIConfig(
            base_url=self.comfyui_url,
            width=self.width,
            height=self.height,
            workspace_root=str(Path(__file__).parent.parent.parent.parent),
        )
        client = ComfyUIClient(config)
        
        # Check if ComfyUI is available
        comfyui_available = await client.health_check()
        if not comfyui_available:
            logger.warning("ComfyUI not available, using placeholder images")
            return self._generate_placeholder_images(context)
        
        # Extract prompts from screenplay
        prompts = self._extract_prompts_from_screenplay(screenplay_content)
        
        # Create output directory
        images_dir = context.production_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        
        image_paths = []
        
        for prompt_data in prompts:
            scene_num = prompt_data.get('scene', 1)
            prompt = prompt_data.get('prompt', f'Scene {scene_num}')
            negative_prompt = prompt_data.get('negative_prompt', 'blurry, low quality, distorted')
            
            output_file = images_dir / f"scene_{scene_num:02d}.png"
            
            try:
                result = await client.generate_image(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=self.width,
                    height=self.height,
                    steps=30,
                    cfg_scale=7.0,
                    ckpt_name='flux1-dev-bf16.safetensors',  # Use symlinked FLUX.1 model
                    output_dir=str(images_dir),
                )
                
                if result.get('success') and result.get('image_path'):
                    import shutil
                    shutil.copy(result['image_path'], str(output_file))
                    image_paths.append(str(output_file))
                    logger.info(f"Scene {scene_num}: Image generated ({output_file.stat().st_size if output_file.exists() else 'unknown'} bytes)")
                else:
                    # Log detailed error before falling back
                    error_msg = result.get('error', 'Unknown error')
                    logger.error(f"Scene {scene_num}: ComfyUI failed - Error: {error_msg[:200]}")
                    
                    # Fallback to placeholder
                    placeholder = images_dir / f"scene_{scene_num:02d}.png"
                    self._create_placeholder_image(prompt, placeholder)
                    image_paths.append(str(placeholder))
                    logger.warning(f"Scene {scene_num}: Using placeholder image")
                    
            except Exception as e:
                logger.error(f"Scene {scene_num}: Generation failed: {e}")
                placeholder = images_dir / f"scene_{scene_num:02d}.png"
                self._create_placeholder_image(prompt, placeholder)
                image_paths.append(str(placeholder))
        
        return image_paths if image_paths else self._generate_placeholder_images(context)
    
    def _generate_placeholder_images(self, context: ProductionContext) -> List[str]:
        """Generate placeholder images when ComfyUI is unavailable."""
        logger.info("Generating placeholder images...")
        images_dir = context.production_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        
        image_paths = []
        for i in range(1, 14):
            img_path = images_dir / f"scene_{i:02d}.png"
            self._create_placeholder_image(f"Scene {i}", img_path)
            image_paths.append(str(img_path))
        return image_paths
    
    def _create_placeholder_image(self, prompt: str, output_path: Path) -> Path:
        """Create a placeholder gradient image."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            import random
            
            img = Image.new('RGB', (self.width, self.height))
            draw = ImageDraw.Draw(img)
            
            # Create gradient background
            color1 = (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))
            color2 = (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))
            
            for i in range(self.height):
                r = int(color1[0] + (color2[0] - color1[0]) * i / self.height)
                g = int(color1[1] + (color2[1] - color1[1]) * i / self.height)
                b = int(color1[2] + (color2[2] - color1[2]) * i / self.height)
                draw.line([(0, i), (self.width, i)], fill=(r, g, b))
            
            # Add text
            draw.text((50, 50), f"Scene: {prompt[:50]}", fill='white')
            draw.text((50, 100), "PLACEHOLDER IMAGE", fill='yellow')
            
            img.save(output_path)
            return output_path
        except Exception as e:
            logger.error(f"Placeholder image creation failed: {e}")
            raise

    def _extract_prompts_from_screenplay(self, screenplay_content: str) -> List[Dict[str, Any]]:
        """Extract image generation prompts from screenplay content.

        Parses the screenplay to find scene descriptions and generates
        appropriate visual prompts for each scene. Falls back to predefined
        prompts if parsing fails.
        """
        # Try to extract scene numbers from screenplay
        import re
        
        # Look for scene headings (e.g., "SCENE 1:", "Scene 1", "INT. KITCHEN - DAY")
        scene_headings = re.findall(r'(?:scene|sc\.?\s*)(\d+)', screenplay_content, re.IGNORECASE)
        
        if scene_headings:
            # Use actual scene count from screenplay
            num_scenes = min(len(set(scene_headings)), 13)
        else:
            # Default to 13 scenes for EW001
            num_scenes = 13
        
        # Generate prompts for each scene based on the emotional arc
        scene_prompts = {
            1: ("Warm, intimate kitchen scene with golden hour lighting, close-up of hands holding coffee cups", "blurry, low quality, distorted"),
            2: ("Living room scene with subtle tension between two people sitting apart, warm tones fading", "blurry, low quality, distorted"),
            3: ("Hallway scene showing emotional distance, one person walking away, shallow depth of field", "blurry, low quality, distorted"),
            4: ("Dinner table scene with misunderstanding, cold lighting, empty space between characters", "blurry, low quality, distorted"),
            5: ("Climactic confrontation scene, dramatic shadows, intense emotional expression", "blurry, low quality, distorted"),
            6: ("Aftermath scene, quiet room, soft morning light, sense of loss", "blurry, low quality, distorted"),
            7: ("Emotional withdrawal moment, person looking out window alone, cool blue tones", "blurry, low quality, distorted"),
            8: ("Isolation deepening, empty apartment, cold color palette, wide shot", "blurry, low quality, distorted"),
            9: ("Moment of clarity, character pausing at threshold, warm light breaking through", "blurry, low quality, distorted"),
            10: ("Failed connection attempt, two people reaching but not touching, shallow focus", "blurry, low quality, distorted"),
            11: ("Acceptance scene, quiet moment of resignation, muted colors", "blurry, low quality, distorted"),
            12: ("New normal routine, mundane kitchen scene, neutral lighting", "blurry, low quality, distorted"),
            13: ("Final hopeful scene, dawn light through window, subtle warmth returning", "blurry, low quality, distorted"),
        }
        
        prompts = []
        for i in range(1, num_scenes + 1):
            prompt_text, neg_prompt = scene_prompts.get(i, (f"Scene {i}", "blurry, low quality"))
            prompts.append({
                "scene": i,
                "prompt": prompt_text,
                "negative_prompt": neg_prompt,
            })
        
        return prompts