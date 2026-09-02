#!/usr/bin/env python3
"""Render all 5 EP-0006 scene images via img2img with the new Mark/Sarah
two-shot reference (denoise=0.4). Writes to the canonical run image dir."""
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

RUN = ROOT / "productions/EP-0006/runs/RUN-20260901-114335"
BRIEF_PATH = RUN / "genesis/movie_os_brief.json"
IMG_DIR = RUN / "images/RUN-20260901-114335/scene_images"


async def main():
    from movie_os.providers.image.flux_comfyui import FluxComfyUIProvider
    from movie_os.capabilities.base import ImageIntent
    from movie_os.prometheus.stages.image_stage import ImageGenerationStage

    brief = json.loads(BRIEF_PATH.read_text(encoding="utf-8"))
    brief["production"] = {"episode_id": "EP-0006", "run_id": "RUN-20260901-114335"}
    brief["production_paths"] = {"run_root": str(RUN)}

    stage = ImageGenerationStage(brief=brief)
    provider = FluxComfyUIProvider(
        comfyui_url="http://127.0.0.1:8190", model="flux1-dev-fp8.safetensors"
    )

    scenes = {s.get("number"): s for s in brief.get("scenes", [])}
    for scene_id in [3, 4, 5]:  # remaining scenes
        scene = scenes.get(scene_id, {})
        prompt = stage._build_prompt(
            scene,
            scene.get("description", ""),
            "two-shot medium close-up",
            "natural",
            scene.get("shot", {}) if isinstance(scene.get("shot", {}), dict) else {},
        )
        out = IMG_DIR / f"scene_{scene_id:03d}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        intent = ImageIntent(
            prompt=prompt,
            negative_prompt=stage._build_negative_prompt(),
            width=1024,
            height=576,
            quality="production",
            seed=1000 + scene_id,
            reference_image_paths=["character_ref_twoshot.png"],
            ipadapter_strength=0.6,
            metadata={
                "scene_number": scene_id,
                "output_dir": str(IMG_DIR.parent),
                "pipeline_id": "RUN-20260901-114335",
                "use_img2img": True,
                "use_ipadapter": False,
            },
        )
        print(f"[scene {scene_id}] rendering...", flush=True)
        asset = await provider.render(intent)
        print(f"[scene {scene_id}] OK -> {asset.path}", flush=True)

    print("ALL SCENES DONE", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
