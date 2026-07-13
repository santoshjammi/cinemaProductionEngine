import sys
import os
import subprocess
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1.pipeline import router as pipeline_router
from backend.app.api.v1.projects import router as projects_router
from backend.app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("main")

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pipeline_router)
app.include_router(projects_router)

os.makedirs(settings.output_dir, exist_ok=True)
os.makedirs(settings.video_output_dir, exist_ok=True)


def _check_ffmpeg():
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
        )
        version = result.stdout.split("\n")[0] if result.stdout else "unknown"
        return {"available": True, "version": version}
    except Exception:
        return {"available": False, "version": None}


@app.get("/api/health")
async def health_check():
    import torch
    return {
        "status": "ok",
        "app": settings.app_name,
        "gpu": {
            "mps_available": torch.backends.mps.is_available(),
            "cuda_available": torch.cuda.is_available(),
            "device": _get_device(),
        },
        "ffmpeg": _check_ffmpeg(),
    }


@app.post("/api/download-models")
async def download_models():
    import asyncio

    async def _download_all():
        from backend.app.services.video_service import VideoGenerationService
        from backend.app.services.tts_service import TTSService

        try:
            logger.info("Starting model pre-download...")
            vs = VideoGenerationService(settings.video_output_dir)
            vs._load_models()
            logger.info("Video models downloaded")

            ts = TTSService(settings.video_output_dir)
            ts._load_model()
            logger.info("TTS models downloaded")
        except Exception as e:
            logger.error("Model download failed: %s", e)

    asyncio.create_task(_download_all())
    return {"status": "started", "message": "Model downloads initiated"}


def _get_device():
    import torch
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"
