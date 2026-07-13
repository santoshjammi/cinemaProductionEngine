"""ComfyUI Backend Client for FLUX.1 image and video generation.

Connects to a running ComfyUI instance on localhost:8188 and provides
methods for generating images via FLUX.1 models.

Usage:
    from movie_os.llm.comfyui_client import ComfyUIClient

    client = ComfyUIClient(base_url="http://localhost:8188")
    result = await client.generate_image(prompt="a cat", negative_prompt="blurry")
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ComfyUIConfig:
    """Configuration for ComfyUI connection."""
    base_url: str = "http://localhost:8188"
    timeout: int = 300  # seconds
    poll_interval: float = 2.0  # seconds between status checks
    width: int = 1024
    height: int = 1024
    seed: int = -1
    cfg_scale: float = 7.0
    steps: int = 30
    
    # Local FLUX.1 model paths (auto-detected from workspace)
    workspace_root: str = ""
    
    def __post_init__(self):
        """Auto-detect local ComfyUI and FLUX.1 model paths."""
        if not self.workspace_root:
            import os
            # Try to find workspace root by looking for models/ComfyUI
            self.workspace_root = self._find_workspace_root()
        
        if self.workspace_root:
            comfy_path = Path(self.workspace_root) / "models" / "ComfyUI"
            if comfy_path.exists():
                self.comfyui_path = str(comfy_path)
                self.checkpoints_dir = str(comfy_path / "models" / "checkpoints")
                self.diffusion_models_dir = str(comfy_path / "models" / "diffusion_models")
                self.vae_dir = str(comfy_path / "models" / "vae")
                self.clip_dir = str(comfy_path / "models" / "clip")
                self.text_encoders_dir = str(comfy_path / "models" / "text_encoders")
            else:
                self.comfyui_path = ""
                self.checkpoints_dir = ""
                self.diffusion_models_dir = ""
                self.vae_dir = ""
                self.clip_dir = ""
                self.text_encoders_dir = ""
        else:
            self.comfyui_path = ""
            self.checkpoints_dir = ""
            self.diffusion_models_dir = ""
            self.vae_dir = ""
            self.clip_dir = ""
            self.text_encoders_dir = ""
    
    def _find_workspace_root(self) -> str:
        """Find the workspace root by searching for models/ComfyUI."""
        # Start from common locations
        candidates = [
            Path(__file__).parent.parent.parent,  # movie_os parent
            Path.cwd(),  # current working directory
            Path.home() / "Desktop" / "projects",  # default projects location
        ]
        
        for candidate in candidates:
            comfy_path = Path(candidate) / "models" / "ComfyUI"
            if comfy_path.exists():
                return str(candidate)
        
        # Search parent directories
        current = Path(__file__).resolve().parent
        while current.parent != current:
            comfy_path = current / "models" / "ComfyUI"
            if comfy_path.exists():
                return str(current)
            current = current.parent
        
        return ""
    
    def _find_comfyui_output_dir(self) -> Path:
        """Find ComfyUI's actual output directory where generated images are saved."""
        candidates = [
            Path.home() / "ComfyUI" / "output",  # Default ComfyUI install
            Path.cwd() / "models" / "ComfyUI" / "output",  # Workspace-relative
            Path(self.comfyui_path) / "output" if self.comfyui_path else None,  # Detected comfyui path
        ]
        
        for candidate in candidates:
            if candidate and candidate.exists():
                return candidate
        
        return Path.home() / "ComfyUI" / "output"  # Default fallback
    
    def get_flux_model_path(self, variant: str = "bf16") -> str:
        """Get the path to a FLUX.1 model variant.
        
        Args:
            variant: 'bf16', 'fp8', 'fp16', or 'auto' (defaults to bf16)
        
        Returns:
            Path to the model file, or empty string if not found
        """
        if not self.diffusion_models_dir:
            return ""
        
        variant_map = {
            "bf16": "flux1-dev-bf16.safetensors",
            "fp8": "flux1-dev-fp8.safetensors",
            "fp16": "flux1-dev-fp16.safetensors",
        }
        
        model_name = variant_map.get(variant, variant)
        model_path = Path(self.diffusion_models_dir) / model_name
        
        if model_path.exists():
            return str(model_path)
        
        # Try any flux1-dev file as fallback
        for f in Path(self.diffusion_models_dir).glob("flux1-dev*.safetensors"):
            return str(f)
        
        return ""
    
    def get_vae_path(self) -> str:
        """Get the path to the FLUX VAE model."""
        if not self.vae_dir:
            return ""
        vae_path = Path(self.vae_dir) / "flux-vae.safetensors"
        return str(vae_path) if vae_path.exists() else ""
    
    def get_clip_paths(self) -> dict[str, str]:
        """Get paths to CLIP and text encoder models."""
        paths = {}
        if self.clip_dir:
            clip_l = Path(self.clip_dir) / "clip_l.safetensors"
            if clip_l.exists():
                paths["clip_l"] = str(clip_l)
        
        if self.text_encoders_dir:
            t5xxl = Path(self.text_encoders_dir) / "t5xxl_fp8_e4m3fn.safetensors"
            if t5xxl.exists():
                paths["t5xxl"] = str(t5xxl)
        
        return paths
    
    def prompt(self, prompt: str, negative_prompt: str = "", **kwargs) -> dict[str, Any]:
        """Generate a ComfyUI prompt for FLUX.1 image generation using local models.
        
        Uses CheckpointLoaderSimple with symlinked models in ComfyUI's registered directories.
        """
        # Get the checkpoint name (just filename, not full path)
        ckpt_name = kwargs.get("ckpt_name", "flux1-dev-bf16.safetensors")
        
        return {
            # Node 4: Load checkpoint (includes UNET + CLIP + VAE for FLUX.1)
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": ckpt_name,  # Just filename - must be in ComfyUI's checkpoints dir
                }
            },
            
            # Node 5: Empty latent image
            "5": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "batch_size": 1,
                    "height": kwargs.get("height", self.height),
                    "width": kwargs.get("width", self.width),
                }
            },
            
            # Node 6: Positive prompt encoding (uses CLIP from checkpoint node 4)
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["4", 1],  # Use CLIP output from CheckpointLoaderSimple
                    "text": prompt,
                }
            },
            
            # Node 7: Negative prompt encoding (uses CLIP from checkpoint node 4)
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["4", 1],  # Use CLIP output from CheckpointLoaderSimple
                    "text": negative_prompt or "blurry, low quality, distorted, deformed",
                }
            },
            
            # Node 3: KSampler with correct parameters for FLUX.1
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["4", 0],  # UNET from checkpoint node 4
                    "positive": ["6", 0],  # Positive prompt from node 6
                    "negative": ["7", 0],  # Negative prompt from node 7
                    "latent_image": ["5", 0],  # Latent from EmptyLatentImage node 5
                    "sampler_name": "euler",  # Required parameter for KSampler
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "seed": max(0, kwargs.get("seed", self.seed if self.seed > 0 else int(time.time()))),  # Ensure seed >= 0
                    "steps": kwargs.get("steps", self.steps),
                    "cfg": kwargs.get("cfg_scale", self.cfg_scale),
                    "random_noise": True,
                }
            },
            
            # Node 8: VAE Decode (latent to image) - uses VAE from checkpoint node 4
            "8": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["3", 0],  # Latent from KSampler
                    "vae": ["4", 2],  # VAE from CheckpointLoaderSimple
                }
            },
            
            # Node 9: Save Image
            "9": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": kwargs.get("filename_prefix", "ComfyUI"),
                    "images": ["8", 0],  # Image from VAEDecode
                }
            },
        }


class ComfyUIClient:
    """Client for interacting with ComfyUI API."""

    def __init__(self, config: Optional[ComfyUIConfig] = None):
        self.config = config or ComfyUIConfig()
        self._ws = None
        import uuid
        self._client_id: str = uuid.uuid4().hex[:16]
    
    def _find_comfyui_output_dir(self) -> Path:
        """Find ComfyUI's actual output directory where generated images are saved."""
        candidates = [
            Path.home() / "ComfyUI" / "output",  # Default ComfyUI install
            Path.cwd() / "models" / "ComfyUI" / "output",  # Workspace-relative
            Path(self.config.comfyui_path) / "output" if hasattr(self.config, 'comfyui_path') and self.config.comfyui_path else None,  # Detected comfyui path
        ]
        
        for candidate in candidates:
            if candidate and candidate.exists():
                return candidate
        
        return Path.home() / "ComfyUI" / "output"  # Default fallback

    async def _get_http(self, path: str) -> Any:
        """Make an HTTP GET request."""
        import aiohttp
        url = f"{self.config.base_url}{path}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()

    async def _post_http(self, path: str, data: dict | None = None) -> Any:
        """Make an HTTP POST request."""
        import aiohttp
        url = f"{self.config.base_url}{path}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as resp:
                return await resp.json()

    async def health_check(self) -> bool:
        """Check if ComfyUI is running."""
        try:
            stats = await self._get_http("/system_stats")
            return stats is not None and len(str(stats)) > 0
        except Exception as e:
            logger.debug(f"ComfyUI health check failed: {e}")
            return False

    async def get_models(self) -> list[dict]:
        """Get available checkpoint models."""
        try:
            return await self._get_http("/models/checkpoints")
        except Exception:
            return []

    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = 30,
        cfg_scale: float = 7.0,
        seed: int = -1,
        ckpt_name: str = "flux1-dev.safetensors",
        output_dir: Optional[str] = None,
    ) -> dict[str, Any]:
        """Generate an image using FLUX.1 via ComfyUI.

        Returns:
            dict with keys: success (bool), image_path (str | None), prompt_id (str)
        """
        try:
            # Build the prompt graph for FLUX.1
            prompt_data = self.config.prompt(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                steps=steps,
                cfg_scale=cfg_scale,
                seed=seed,
                ckpt_name=ckpt_name,
                filename_prefix=output_dir or "ComfyUI",
            )

            # Queue the prompt
            resp = await self._post_http("/prompt", {"prompt": prompt_data, "client_id": self._client_id})
            prompt_id = resp.get("prompt_id") or resp.get("job_id")
            if not prompt_id:
                return {"success": False, "image_path": None, "error": f"No prompt_id returned: {resp}"}

            logger.debug(f"Prompt queued with ID: {prompt_id}")

            # Wait for completion - poll more frequently
            start_time = time.time()
            
            # Record existing files BEFORE generation starts
            comfyui_output_dir = self._find_comfyui_output_dir()
            before_files: set[str] = set()
            if comfyui_output_dir and comfyui_output_dir.exists():
                before_files = {str(f) for f in comfyui_output_dir.rglob('*.png')}
            
            while time.time() - start_time < self.config.timeout:
                await asyncio.sleep(1.0)  # Poll every 1 second instead of 2
                history = await self._get_http(f"/history/{prompt_id}")
                
                if not history or prompt_id not in history:
                    continue
                    
                node_results = history.get(prompt_id, {}).get("outputs", {})
                
                # Check for saved images in outputs
                for node_id, node_output in node_results.items():
                    images = node_output.get("images", [])
                    if images:
                        img_info = images[0]
                        filename = img_info.get("filename", "")
                        subfolder = img_info.get("subfolder", "")
                        
                        # ComfyUI saves to its own output directory structure
                        # Try multiple possible locations
                        possible_paths = []
                        if subfolder:
                            possible_paths.extend([
                                Path(subfolder) / filename,  # Absolute path from ComfyUI
                                Path(output_dir or "/tmp") / subfolder / filename if not subfolder.startswith('/') else None,
                            ])
                        else:
                            # Check ComfyUI's default output directories
                            comfyui_outputs = [
                                Path.home() / "ComfyUI" / "output" / filename,
                                Path.home() / "ComfyUI" / "temp" / filename,
                                Path.cwd() / "ComfyUI" / "output" / filename,
                                Path("/tmp") / "ComfyUI" / "output" / filename,
                            ]
                            possible_paths.extend([p for p in comfyui_outputs if p])
                        
                        # Also try the specified output_dir
                        if output_dir:
                            possible_paths.extend([
                                Path(output_dir) / filename,
                                Path(output_dir) / "output" / filename,
                                Path(output_dir) / "input" / filename,
                                Path(output_dir) / "temp" / filename,
                            ])
                        
                        # Find the first existing path
                        for img_path in possible_paths:
                            if img_path and img_path.exists():
                                logger.info(f"Image generated: {img_path}")
                                return {
                                    "success": True,
                                    "image_path": str(img_path),
                                    "prompt_id": prompt_id,
                                    "seed": seed if seed > 0 else int(time.time()),
                                }
                        
                        # If file info exists but path doesn't, return the expected path anyway
                        logger.warning(f"Image info found but file not at expected paths: {filename}, subfolder={subfolder}")
                        expected_path = Path(output_dir or "/tmp") / (subfolder or "output") / filename
                        return {
                            "success": True,
                            "image_path": str(expected_path),
                            "prompt_id": prompt_id,
                            "seed": seed if seed > 0 else int(time.time()),
                        }

                # Check if generation completed (no more outputs but history exists)
                if prompt_id in history and not node_results:
                    logger.debug(f"Generation completed for prompt {prompt_id}")
                    
                    # Find NEW files created during this generation
                    new_files: list[Path] = []
                    if comfyui_output_dir and comfyui_output_dir.exists():
                        after_files = {str(f) for f in comfyui_output_dir.rglob('*.png')}
                        new_files = [Path(f) for f in (after_files - before_files)]
                    
                    if new_files:
                        # Sort by modification time, newest first
                        new_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                        image_path = new_files[0]
                        logger.info(f"Found new image from prompt {prompt_id}: {image_path}")
                        return {
                            "success": True,
                            "image_path": str(image_path),
                            "prompt_id": prompt_id,
                            "seed": seed if seed > 0 else int(time.time()),
                        }
                    else:
                        logger.debug(f"Generation completed for prompt {prompt_id} but no new files found")
                    
                    # ComfyUI saves images to its output directory - check all possible locations
                    import tempfile
                    comfyui_output_dirs = [
                        # Standard ComfyUI output locations (in order of priority)
                        Path(output_dir or "/tmp") if output_dir else None,  # User-specified output dir
                        Path.home() / "ComfyUI" / "output",
                        Path.cwd() / "ComfyUI" / "output",
                        Path(tempfile.gettempdir()) / "ComfyUI" / "output",
                        # Also check ComfyUI installation directory
                        Path(self.config.comfyui_path) / "output" if self.config.comfyui_path else None,
                        Path(self.config.comfyui_path) / "temp" if self.config.comfyui_path else None,
                    ]
                    
                    # Search for recently created PNG files (last 120 seconds)
                    now = time.time()
                    for output_dir_path in comfyui_output_dirs:
                        if not output_dir_path or not output_dir_path.exists():
                            continue
                        
                        # Find PNG files created in the last 120 seconds
                        for png_file in output_dir_path.rglob("*.png"):
                            file_mtime = png_file.stat().st_mtime
                            if now - file_mtime < 120:  # Created in last 120 seconds
                                logger.info(f"Found generated image: {png_file}")
                                return {
                                    "success": True,
                                    "image_path": str(png_file),
                                    "prompt_id": prompt_id,
                                    "seed": seed if seed > 0 else int(time.time()),
                                }
                    
                    # If no files found by time, search for any PNG files in ComfyUI output
                    for output_dir_path in comfyui_output_dirs:
                        if not output_dir_path or not output_dir_path.exists():
                            continue
                        
                        # Look for any PNG files (most recent)
                        png_files = list(output_dir_path.rglob("*.png"))
                        if png_files:
                            # Sort by modification time, get most recent
                            most_recent = max(png_files, key=lambda f: f.stat().st_mtime)
                            logger.info(f"Found image in ComfyUI output: {most_recent}")
                            return {
                                "success": True,
                                "image_path": str(most_recent),
                                "prompt_id": prompt_id,
                                "seed": seed if seed > 0 else int(time.time()),
                            }
                    
                    return {"success": False, "image_path": None, "error": "Generation completed but no images found in ComfyUI output directories"}

            return {"success": False, "image_path": None, "error": f"Timeout after {self.config.timeout}s"}

        except Exception as e:
            logger.error(f"ComfyUI image generation failed: {e}", exc_info=True)
            return {"success": False, "image_path": None, "error": str(e)}

    async def generate_video(
        # Video generation via ComfyUI (AnimateDiff/Video nodes)
        self,
        prompt: str,
        negative_prompt: str = "",
        frames: int = 64,
        fps: int = 25,
        **kwargs,
    ) -> dict[str, Any]:
        """Generate a short video clip using ComfyUI video nodes (AnimateDiff/FramePack)."""
        try:
            # Video generation uses similar prompt structure but with video-specific nodes
            prompt_data = {
                "3": {
                    "class_type": "KSamplerVideo",
                    "inputs": {
                        "cfg": kwargs.get("cfg_scale", self.cfg_scale),
                        "denoise": 1.0,
                        "latent_image": ["5", 0],
                        "model": ["4", 0],
                        "negative": ["7", 0],
                        "positive": ["6", 0],
                        "steps": kwargs.get("steps", self.steps),
                        "seed": kwargs.get("seed", int(time.time())),
                    }
                },
                "5": {
                    "class_type": "EmptyLatentImageLarge",
                    "inputs": {
                        "batch_size": 1,
                        "height": kwargs.get("height", self.height),
                        "width": kwargs.get("width", self.width),
                        "frame_count": frames,
                    }
                },
                "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": prompt}},
                "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["4", 1], "text": negative_prompt or "blurry, low quality"}},
                "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
                "9": {
                    "class_type": "SaveVideo",
                    "inputs": {
                        "filename_prefix": kwargs.get("filename_prefix", "ComfyUI_video"),
                        "fps": fps,
                        "frames": ["8", 0],
                    }
                },
            }

            prompt_id = await self._post_http("/prompt", {"prompt": prompt_data, "client_id": self._client_id})
            prompt_id = prompt_id.get("prompt_id") or prompt_id.get("job_id")

            # Wait for completion (video takes longer)
            start_time = time.time()
            while time.time() - start_time < self.config.timeout * 3:
                await asyncio.sleep(self.config.poll_interval * 2)
                history = await self._get_http(f"/history/{prompt_id}")
                if not history:
                    continue
                for node_output in history.get(prompt_id, {}).get("outputs", {}).values():
                    frames_out = node_output.get("videos", [])
                    if frames_out:
                        return {"success": True, "video_path": str(frames_out[0].get("filename")), "prompt_id": prompt_id}

            return {"success": False, "video_path": None, "error": "Video generation timeout"}

        except Exception as e:
            logger.error(f"ComfyUI video generation failed: {e}")
            return {"success": False, "video_path": None, "error": str(e)}


__all__ = ["ComfyUIClient", "ComfyUIConfig"]
