"""End-to-end integration test: ComfyUI + FLUX.1 Dev.

This script:
  1. Connects to a running ComfyUI server
  2. Submits a real FLUX txt2img workflow
  3. Waits for the image to render
  4. Downloads and saves the result
  5. Verifies the file exists and has reasonable size

Run:
    /Users/santosh/Desktop/projects/videoGen/venv/bin/python \\
        movie_os/tests/integration/test_comfyui_flux_e2e.py

Requires:
    - ComfyUI running on http://127.0.0.1:8188 with --cpu
    - FLUX.1 Dev fp8 model + CLIP-L + T5-XXL + VAE in
      models/ComfyUI/models/{diffusion_models,clip,text_encoders,vae}
"""

from __future__ import annotations

import sys
import time
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo_root))

    from movie_os.providers import registry
    from movie_os.capabilities.base import ImageIntent

    print("=" * 60)
    print("ComfyUI + FLUX.1 End-to-End Test")
    print("=" * 60)

    provider = registry.make(
        "image", "flux_comfyui",
        {
            "comfyui_url": "http://127.0.0.1:8188",
            "model": "flux1-dev-fp8.safetensors",
            "timeout": 600.0,
        },
        0.0,
    )
    print(f"\nProvider: {provider.name}")
    print(f"  comfyui_url: {provider.comfyui_url}")
    print(f"  model: {provider.model}")

    output_dir = Path("/tmp/comfyui_e2e_output")
    output_dir.mkdir(exist_ok=True)

    intent = ImageIntent(
        prompt="A lonely man sitting in a dark room, dimly lit, cinematic",
        width=256,
        height=256,
        seed=42,
        metadata={
            "quality": "draft",
            "output_dir": str(output_dir),
            "pipeline_id": "e2e_test",
            "scene_number": 1,
        },
    )
    print(f"\nIntent:")
    print(f"  prompt: {intent.prompt[:80]}...")
    print(f"  size: {intent.width}x{intent.height}")
    print(f"  quality: {intent.metadata['quality']}")
    print(f"  seed: {intent.seed}")

    workflow_name = provider._select_workflow(intent)
    print(f"  selected workflow: {workflow_name}")

    print("\nRendering (this may take 30-300 seconds on CPU)...")
    t0 = time.time()
    try:
        import asyncio
        asset = asyncio.run(provider.render(intent))
        elapsed = time.time() - t0
    except Exception as e:
        print(f"\nFAILED: {type(e).__name__}: {e}")
        return 1

    print(f"\nRender completed in {elapsed:.1f}s")
    print(f"  Asset path: {asset.path}")
    print(f"  Asset exists: {asset.path.exists()}")
    if asset.path.exists():
        size_kb = asset.path.stat().st_size / 1024
        print(f"  File size: {size_kb:.1f} KB")
    print(f"  Backend: {asset.backend}")
    print(f"  Metadata: {asset.metadata}")

    if not asset.path.exists():
        print("\nFAIL: Output file does not exist")
        return 1
    if asset.path.stat().st_size < 1000:
        print(f"\nFAIL: Output file is too small ({asset.path.stat().st_size} bytes)")
        return 1

    print(f"\nPASS: Image saved to {asset.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
