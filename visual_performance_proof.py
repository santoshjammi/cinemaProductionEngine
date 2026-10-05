#!/usr/bin/env python3
"""PROMETHEUS-STATIC-PERFORMANCE-STANDARD-001 — first proof.

Generates 4 images from real EP-0006 shots using the visual-performance
prompt builder:
  1. one Mark speaking shot
  2. one Sarah speaking shot
  3. one listener reaction
  4. one reconnection two-shot

Compares against the current neutral character images.
"""
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

RUN = ROOT / "productions/EP-0006/runs/RUN-20260901-114335"
BRIEF_PATH = RUN / "genesis/movie_os_brief.json"
PKP_PATH = RUN / "genesis/pkp/PKP-EP-0006-v1.yaml"
OUT_DIR = RUN / "render" / "visual_performance_proof"


def pick_proof_shots(shots: list[dict]) -> dict[str, dict]:
    """Select the 4 proof shots per the standard."""
    mark_speaking = next((s for s in shots if s["purpose"] == "SPEAKER_COVERAGE" and s.get("performance_context", {}).get("speaker") == "MARK"), None)
    sarah_speaking = next((s for s in shots if s["purpose"] == "SPEAKER_COVERAGE" and s.get("performance_context", {}).get("speaker") == "SARAH"), None)
    listener = next((s for s in shots if s["purpose"] == "LISTENER_REACTION"), None)
    two_shot = next((s for s in shots if s["purpose"] == "TWO_SHOT"), None)
    return {
        "mark_speaking": mark_speaking,
        "sarah_speaking": sarah_speaking,
        "listener_reaction": listener,
        "reconnection_two_shot": two_shot,
    }


async def main():
    from movie_os.providers.image.flux_comfyui import FluxComfyUIProvider
    from movie_os.capabilities.base import ImageIntent
    from movie_os.prometheus.stages.image_stage import ImageGenerationStage
    from movie_os.character_consistency import ensure_character_consistency

    brief = json.loads(BRIEF_PATH.read_text(encoding="utf-8"))
    pkp = json.loads(PKP_PATH.read_text(encoding="utf-8"))
    brief["frozen_pkp"] = pkp
    brief["production"] = {"episode_id": "EP-0006", "run_id": "RUN-20260901-114335"}
    brief["production_paths"] = {"run_root": str(RUN)}

    shots = (pkp.get("shots", {}) or {}).get("shots", [])
    proof = pick_proof_shots(shots)
    for name, s in proof.items():
        print(f"  {name:24s}: {s['shot_id'] if s else 'MISSING'} [{s['purpose'] if s else '?'}]")

    stage = ImageGenerationStage(brief=brief)
    provider = FluxComfyUIProvider(comfyui_url="http://127.0.0.1:8190", model="flux1-dev-fp8.safetensors")
    char_ref = ensure_character_consistency(brief).get("reference_filename")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, shot in proof.items():
        if not shot:
            print(f"  SKIP {name} (no shot)")
            continue
        scene_id = shot.get("scene_id")
        scene = next((s for s in brief.get("scenes", []) if s.get("number") == scene_id), {})
        # Build the visual-performance prompt via the stage, passing the EXACT
        # shot so listener-reaction / two-shot get their own performance (not
        # the scene's default speaker shot).
        prompt = stage._build_prompt(scene, scene.get("scene_description", ""), "medium", "natural", shot)
        out = OUT_DIR / f"{name}.png"
        intent = ImageIntent(
            prompt=prompt,
            negative_prompt=stage._build_negative_prompt(),
            width=1024, height=576,
            quality="production",
            seed=3000 + scene_id,
            reference_image_paths=[char_ref] if char_ref else None,
            ipadapter_strength=0.6,
            metadata={
                "scene_number": scene_id,
                "output_dir": str(OUT_DIR),
                "pipeline_id": "visual-performance-proof",
                "use_img2img": True,
                "use_ipadapter": False,
                "denoise": 0.4,
            },
        )
        print(f"\n  [{name}] rendering scene {scene_id}...", flush=True)
        asset = await provider.render(intent)
        p = Path(asset.path)
        if p != out:
            import shutil
            shutil.copy2(p, out)
        print(f"  [{name}] OK -> {out}", flush=True)

    print("\nPROOF DONE")


if __name__ == "__main__":
    asyncio.run(main())
