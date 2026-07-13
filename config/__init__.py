# config/__init__.py

# Configuration for Text Cinema Engine
import os

class Config:
    # Model configurations
    CREATIVE_WRITER_MODEL = "gpt2"
    VISUAL_PROMPT_MODEL = "stabilityai/stable-diffusion-2"
    
    # Pipeline settings
    DEFAULT_DURATION = "30 seconds"
    MAX_SCENE_COUNT = 10
    
    # Device settings
    DEVICE = "cuda" if os.environ.get("CUDA_AVAILABLE", "false").lower() == "true" else "cpu"
    
    # Output settings
    OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
    
    @classmethod
    def get_config(cls):
        return {
            'creative_writer_model': cls.CREATIVE_WRITER_MODEL,
            'visual_prompt_model': cls.VISUAL_PROMPT_MODEL,
            'default_duration': cls.DEFAULT_DURATION,
            'device': cls.DEVICE
        }
