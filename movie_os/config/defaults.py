"""Built-in defaults for Movie OS configuration.

These are the values used when a config file doesn't specify something.
They reflect the current state of the system (July 2026):

  - Local-first inference (LMStudio, edge-tts, SDXL local)
  - M1 Max target hardware
  - Apple Silicon MPS for image generation
  - 16:9 cinematic aspect ratio (YouTube primary)
  - h264 + AAC for compatibility
  - FLUX coming soon as the image default (Phase 5)
"""

from __future__ import annotations

from typing import Any


DEFAULT_CONFIG_DICT: dict[str, Any] = {
    "version": "1.0",
    "project": {
        "name": "movie_os",
        "output_dir": "output/videos",
        "log_level": "INFO",
        "cache_dir": ".movie_os_cache",
    },
    "providers": {
        "image": {
            "default": "sdxl_local",
            "options": {
                "sdxl_local": {
                    "label": "SDXL Local (M1 Max)",
                    "enabled": True,
                    "cost_per_call_usd": 0.0,
                    "settings": {
                        "model": "stabilityai/stable-diffusion-xl-base-1.0",
                        "device": "mps",
                        "dtype": "float16",
                        "resolution_width": 1024,
                        "resolution_height": 576,
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5,
                        "num_candidates": 4,
                        "min_clip_score": 0.30,
                    },
                },
                "flux_comfyui": {
                    "label": "FLUX.1 Dev via ComfyUI",
                    "enabled": False,                # Phase 5 — coming soon
                    "cost_per_call_usd": 0.0,
                    "settings": {
                        "model": "flux1-dev-fp8.safetensors",
                        "comfyui_url": "http://localhost:8188",
                        "workflow": "flux_txt2img",
                    },
                },
            },
        },
        "video": {
            "default": "svd_local",
            "options": {
                "svd_local": {
                    "label": "Stable Video Diffusion Local",
                    "enabled": False,                # Phase 4
                    "cost_per_call_usd": 0.0,
                    "settings": {
                        "model": "stabilityai/stable-video-diffusion-img2vid-xt",
                        "device": "mps",
                        "dtype": "float16",
                    },
                },
            },
        },
        "voice": {
            "default": "edge_tts",
            "options": {
                "edge_tts": {
                    "label": "Microsoft Edge TTS",
                    "enabled": True,
                    "cost_per_call_usd": 0.0,
                    "settings": {
                        "default_voice": "en-US-GuyNeural",
                        "default_language": "en-US",
                        "default_rate": "+0%",
                    },
                },
            },
        },
        "music": {
            "default": "procedural",
            "options": {
                "procedural": {
                    "label": "Procedural music synthesis (numpy)",
                    "enabled": True,
                    "cost_per_call_usd": 0.0,
                    "settings": {
                        "sample_rate": 44100,
                        "default_volume": 0.3,
                    },
                },
            },
        },
        "story": {
            "default": "lmstudio",
            "options": {
                "lmstudio": {
                    "label": "LMStudio (local)",
                    "enabled": True,
                    "cost_per_call_usd": 0.0,
                    "settings": {
                        "base_url": "http://localhost:1234",
                        "api_key": "sk-lm-TkM3NqaZ:CQdNsDjxGRm17O3Gg59W",
                        "narrative_model": "qwen3-coder-30b-a3b-instruct-mlx",
                        "narrative_temperature": 0.7,
                        "narrative_max_tokens": 4000,
                        "refiner_model": "supergemma4-26b-uncensored-mlx-v2",
                        "refiner_temperature": 0.6,
                        "refiner_max_tokens": 2000,
                    },
                },
            },
        },
        "translation": {
            "default": "",
            "options": {},
        },
        "research": {
            "default": "",
            "options": {},
        },
    },
    "capabilities": {
        "image": {"enabled": True, "budget_usd": 0.0, "timeout_seconds": 600, "max_retries": 3},
        "video": {"enabled": True, "budget_usd": 0.0, "timeout_seconds": 600, "max_retries": 3},
        "voice": {"enabled": True, "budget_usd": 0.0, "timeout_seconds": 300, "max_retries": 3},
        "music": {"enabled": True, "budget_usd": 0.0, "timeout_seconds": 300, "max_retries": 3},
        "story": {"enabled": True, "budget_usd": 0.0, "timeout_seconds": 600, "max_retries": 3},
        "translation": {"enabled": True, "budget_usd": 0.0, "timeout_seconds": 300, "max_retries": 3},
        "research": {"enabled": True, "budget_usd": 0.0, "timeout_seconds": 300, "max_retries": 3},
    },
    "rendering": {
        "aspect_ratio": "16:9",
        "resolution": "1280x720",
        "quality": "production",
        "output_format": "mp4",
        "video_codec": "libx264",
        "audio_codec": "aac",
        "video_bitrate": "5M",
        "audio_bitrate": "192k",
        "fps": 24,
    },
    "pipeline": {
        "steps": ["narrative", "images", "audio", "music", "sfx", "mix", "video"],
        "skip": [],
        "auto_approve": False,
        "dry_run": False,
        "parallel": True,
    },
}
