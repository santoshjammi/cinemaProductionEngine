from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="TCE_")

    app_name: str = "Text Cinema Engine API"
    debug: bool = True

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]

    # Pipeline
    project_root: str = str(Path(__file__).parent.parent.parent.parent)
    output_dir: str = os.path.join(project_root, "output")
    config_path: str = os.path.join(project_root, "config", "llm_config.yaml")

    # LLM
    ollama_endpoint: str = "http://localhost:11434"
    orchestrator_model: str = "qwen2.5:32b"
    creative_writer_model: str = "deepseek-coder-v2:latest"

    # Video
    video_output_dir: str = os.path.join(output_dir, "videos")
    video_model: str = "stabilityai/stable-video-diffusion-img2vid-xt"
    tts_model: str = "tts_models/en/ljspeech/tacotron2-DDC"

    # Generation
    max_scenes: int = 12
    default_story_length: str = "medium"


settings = Settings()
