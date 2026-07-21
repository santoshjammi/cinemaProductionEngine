import asyncio
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.app.models.schemas import (
    PipelineStartRequest, RetryStageRequest, PipelineResponse,
    GenerationProgressResponse
)
from backend.app.services.pipeline_service import PipelineService
from backend.app.services.video_service import (
    VideoGenerationService, get_generation_state, remove_generation_state,
)
from backend.app.services.image_service import (
    ImageGenerationService, get_image_state, remove_image_state,
)
from backend.app.services.tts_service import TTSService
from backend.app.core.config import settings

logger = logging.getLogger("pipeline_router")

router = APIRouter(prefix="/api/v1/pipeline", tags=["pipeline"])

pipeline_service = PipelineService()
video_service = VideoGenerationService(settings.video_output_dir)
image_service = ImageGenerationService(settings.video_output_dir)
tts_service = TTSService(settings.video_output_dir)
_generation_tasks: dict[str, asyncio.Task] = {}


@router.post("/start", response_model=PipelineResponse)
async def start_pipeline(req: PipelineStartRequest):
    pb = req.producer_brief
    result = await pipeline_service.start_pipeline(
        topic=req.topic,
        tone=req.tone,
        length=req.length,
        platform=req.platform,
        enable_research=req.enable_research,
        project_id=req.project_id,
        producer_brief=pb.model_dump() if pb else None,
        profile_id=req.profile_id,
    )
    return result


@router.post("/import", response_model=PipelineResponse)
async def import_script(req: dict):
    """Import a pre-written script (story, scenes, dialogues, prompts)
    directly as a completed pipeline, bypassing LLM text generation."""
    if not req.get("scenes"):
        raise HTTPException(status_code=422, detail="scenes are required")
    result = pipeline_service.import_script(req, project_id=req.get("project_id"))
    return result


@router.get("/history", response_model=list[PipelineResponse])
async def get_history():
    return pipeline_service.get_history()


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(pipeline_id: str):
    result = pipeline_service.get_pipeline(pipeline_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return result


@router.post("/{pipeline_id}/retry", response_model=PipelineResponse)
async def retry_stage(pipeline_id: str, req: RetryStageRequest):
    result = pipeline_service.retry_stage(pipeline_id, req.stage)
    if result is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return result


# --- Image Generation ---

@router.post("/{pipeline_id}/generate-images")
async def generate_scene_images(pipeline_id: str):
    pipeline = pipeline_service.get_pipeline(pipeline_id)
    if pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    prompts = pipeline.get("prompts", [])
    if not prompts:
        raise HTTPException(status_code=400, detail="No cinematic prompts available")

    remove_image_state(pipeline_id)
    get_image_state(pipeline_id, total_scenes=len(prompts))

    async def generate_all():
        try:
            for p in prompts:
                scene_num = p["scene_number"]
                cinematic_prompt = p.get("cinematic_prompt", "")
                await image_service.generate_scene_image(
                    pipeline_id, scene_num, cinematic_prompt
                )
        except Exception as e:
            logger.exception("Image generation task failed for %s", pipeline_id)

    asyncio.create_task(generate_all())
    return {"status": "started", "total_scenes": len(prompts)}


@router.get("/{pipeline_id}/images")
async def get_scene_images(pipeline_id: str):
    pipeline = pipeline_service.get_pipeline(pipeline_id)
    if pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    state = get_image_state(pipeline_id)
    images = state.get_all_images()
    scenes = pipeline.get("scenes", [])
    # If state is empty but images exist on disk, reconstruct from filesystem
    if not images and scenes:
        from pathlib import Path as PPath
        img_dir = PPath(settings.output_dir) / "videos" / pipeline_id / "scene_images"
        if img_dir.exists():
            for sc in scenes:
                scene_num = sc.get("scene_number", 0)
                img_path = img_dir / f"scene_{scene_num:03d}.png"
                if img_path.exists():
                    images.append({
                        "scene_number": scene_num,
                        "status": "completed",
                        "image_url": f"/api/v1/pipeline/{pipeline_id}/image/{scene_num}",
                        "progress": 1.0,
                        "error": None,
                    })
            images.sort(key=lambda x: x["scene_number"])
            state.total_scenes = len(scenes)
            for img in images:
                state.set_image(img["scene_number"], img)
    return {
        "pipeline_id": pipeline_id,
        "images": images,
        "total_scenes": len(scenes),
    }


@router.get("/{pipeline_id}/image/{scene_number}")
async def get_scene_image(pipeline_id: str, scene_number: int):
    image_path = image_service.get_image_path(pipeline_id, scene_number)
    if image_path is None:
        raise HTTPException(status_code=404, detail="Scene image not found")
    return FileResponse(str(image_path), media_type="image/png")


# --- SVD-XT Video Generation ---

@router.post("/{pipeline_id}/generate-video")
async def generate_video(pipeline_id: str):
    pipeline = pipeline_service.get_pipeline(pipeline_id)
    if pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    if pipeline["status"] != "completed":
        raise HTTPException(status_code=400, detail="Pipeline must be completed first")
    scenes = pipeline.get("scenes", [])
    if not scenes:
        raise HTTPException(status_code=400, detail="No scenes to generate")

    if pipeline_id in _generation_tasks and not _generation_tasks[pipeline_id].done():
        return {"clips": []}

    prompts_map = {}
    for p in pipeline.get("prompts", []):
        prompts_map[p["scene_number"]] = p.get("cinematic_prompt", "")

    dialogues_map = {}
    for d in pipeline.get("dialogues", []):
        sn = d["scene_number"]
        dialogues_map[sn] = " ".join(
            line["dialogue"] for line in d.get("dialogues", [])
        )

    state = get_generation_state(pipeline_id)
    state.current_stage = "video-generation"

    async def run_all():
        try:
            for scene in scenes:
                scene_num = scene["scene_number"]
                prompt = prompts_map.get(scene_num, "")
                await video_service.generate_clip(pipeline_id, scene_num, prompt)

                dialogue_text = dialogues_map.get(scene_num, "")
                if dialogue_text.strip():
                    await tts_service.generate_speech(
                        pipeline_id, scene_num, dialogue_text
                    )

            video_service.assemble_final_video(pipeline_id, len(scenes))
        except Exception as e:
            logger.exception("Video generation task failed for %s", pipeline_id)
        finally:
            _generation_tasks.pop(pipeline_id, None)
            remove_generation_state(pipeline_id)

    _generation_tasks[pipeline_id] = asyncio.create_task(run_all())
    return {"clips": []}


# --- Ken Burns Image-Based Video ---

@router.post("/{pipeline_id}/generate-ken-burns-video")
async def generate_ken_burns_video(pipeline_id: str):
    pipeline = pipeline_service.get_pipeline(pipeline_id)
    if pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    scenes = pipeline.get("scenes", [])
    if not scenes:
        raise HTTPException(status_code=400, detail="No scenes to generate")

    if pipeline_id in _generation_tasks and not _generation_tasks[pipeline_id].done():
        return {"status": "already_running"}

    dialogues_map = {}
    for d in pipeline.get("dialogues", []):
        sn = d["scene_number"]
        dialogues_map[sn] = " ".join(
            line["dialogue"] for line in d.get("dialogues", [])
        )

    effects = ["ken-burns", "zoom-in", "zoom-out", "pan-right", "pan-left"]

    state = get_generation_state(pipeline_id)
    state.current_stage = "ken-burns"

    async def run_ken_burns():
        try:
            for i, scene in enumerate(scenes):
                scene_num = scene["scene_number"]
                effect = effects[i % len(effects)]

                state.set_clip(scene_num, {
                    "scene_number": scene_num,
                    "status": "generating",
                    "progress": 0.1,
                })

                image_path = image_service.get_image_path(pipeline_id, scene_num)
                if image_path is None:
                    state.set_clip(scene_num, {
                        "scene_number": scene_num,
                        "status": "failed",
                        "error": "No image generated for this scene",
                        "progress": 0,
                    })
                    continue

                # 1. Generate TTS audio FIRST so we know the real duration
                dialogue_text = dialogues_map.get(scene_num, "")
                audio_duration = None
                if dialogue_text.strip():
                    state.set_clip(scene_num, {
                        "scene_number": scene_num,
                        "status": "generating",
                        "progress": 0.3,
                    })
                    await tts_service.generate_speech(
                        pipeline_id, scene_num, dialogue_text
                    )
                    audio_duration = tts_service.get_audio_duration(pipeline_id, scene_num)

                # 2. Use audio duration for clip, or fall back to scene duration
                if audio_duration and audio_duration > 2.0:
                    clip_duration = audio_duration
                else:
                    clip_duration = _parse_duration(scene.get("duration", "8s"))

                state.set_clip(scene_num, {
                    "scene_number": scene_num,
                    "status": "generating",
                    "progress": 0.5,
                })

                clip_path = video_service.generate_ken_burns_clip(
                    pipeline_id, scene_num, image_path, clip_duration, effect
                )

                if clip_path:
                    if dialogue_text.strip():
                        tts_service.merge_audio_with_video(
                            pipeline_id, scene_num
                        )

                    state.set_clip(scene_num, {
                        "scene_number": scene_num,
                        "status": "completed",
                        "video_url": f"/api/v1/pipeline/{pipeline_id}/video/{scene_num}",
                        "progress": 1.0,
                    })
                else:
                    state.set_clip(scene_num, {
                        "scene_number": scene_num,
                        "status": "failed",
                        "error": "Ken Burns generation failed",
                        "progress": 0,
                    })

            video_service.assemble_final_video(pipeline_id, len(scenes))
        except Exception as e:
            logger.exception("Ken Burns video task failed for %s", pipeline_id)
        finally:
            _generation_tasks.pop(pipeline_id, None)
            remove_generation_state(pipeline_id)

    _generation_tasks[pipeline_id] = asyncio.create_task(run_ken_burns())
    return {"status": "started"}


@router.get("/{pipeline_id}/generation", response_model=GenerationProgressResponse)
async def get_generation_progress(pipeline_id: str):
    pipeline = pipeline_service.get_pipeline(pipeline_id)
    if pipeline is None:
        raise HTTPException(status_code=404, detail="Pipeline not found")

    state = get_generation_state(pipeline_id)
    clips = state.get_all_clips()
    final_video = state.get_final_video()

    return {
        "pipeline": pipeline,
        "clips": clips,
        "final_video": final_video or {
            "status": "pending",
            "progress": 0,
        },
        "overall_progress": state.overall_progress(),
        "current_stage": state.current_stage,
    }


@router.get("/{pipeline_id}/video/{scene_number}")
async def get_video_clip(pipeline_id: str, scene_number: int):
    clip_path = video_service.get_clip_path(pipeline_id, scene_number)
    if clip_path is None:
        raise HTTPException(status_code=404, detail="Video clip not found")
    return FileResponse(str(clip_path), media_type="video/mp4")


@router.get("/{pipeline_id}/audio/{scene_number}")
async def get_audio_clip(pipeline_id: str, scene_number: int):
    audio_path = tts_service.get_audio_path(pipeline_id, scene_number)
    if audio_path is None:
        raise HTTPException(status_code=404, detail="Audio clip not found")
    return FileResponse(str(audio_path), media_type="audio/wav")


@router.get("/{pipeline_id}/final-video")
async def get_final_video(pipeline_id: str):
    parent = Path(settings.video_output_dir) / pipeline_id
    final_video = parent / "final.mp4"
    if not final_video.exists():
        raise HTTPException(status_code=404, detail="Final video not found")
    return FileResponse(str(final_video), media_type="video/mp4")


def _parse_duration(duration_str: str) -> float:
    duration_str = duration_str.strip().lower()
    if duration_str.endswith("s"):
        try:
            return float(duration_str.rstrip("s"))
        except ValueError:
            pass
    if duration_str.endswith("min"):
        try:
            return float(duration_str.replace("min", "").strip()) * 60
        except ValueError:
            pass
    if duration_str.endswith("m"):
        try:
            return float(duration_str.rstrip("m")) * 60
        except ValueError:
            pass
    try:
        return float(duration_str)
    except ValueError:
        return 8.0
