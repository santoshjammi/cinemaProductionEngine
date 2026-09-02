#!/usr/bin/env python3
"""Download FLUX models for ComfyUI from HuggingFace."""

import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from huggingface_hub import hf_hub_download

# Base directories
UNET_DIR = "/Users/santosh/AI_WORKSPACE/comfyui/ComfyUI/models/unet"
VAE_DIR = "/Users/santosh/AI_WORKSPACE/comfyui/ComfyUI/models/vae"
CLIP_DIR = "/Users/santosh/AI_WORKSPACE/comfyui/ComfyUI/models/clip"

DOWNLOADS = [
    # (repo_id, filename, target_dir, description)
    ("comfyanonymous/flux1-dev", "flux1-dev-fp8.safetensors", UNET_DIR, "FLUX UNet fp8"),
    ("black-forest-labs/FLUX.1-dev", "ae.safetensors", VAE_DIR, "FLUX VAE"),
    ("comfyanonymous/flux-text-encoders", "clip_l.safetensors", CLIP_DIR, "CLIP-L text encoder"),
    ("comfyanonymous/flux-text-encoders", "t5xxl_fp8_e4m3fn.safetensors", CLIP_DIR, "T5XXL fp8 text encoder"),
]

def download_one(repo_id, filename, target_dir, desc):
    """Download a single file from HuggingFace Hub."""
    print(f"\n{'='*60}")
    print(f"Downloading: {desc}")
    print(f"  Repo: {repo_id}")
    print(f"  File: {filename}")
    print(f"  Dest: {target_dir}/")
    print(f"{'='*60}")
    
    path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=target_dir,
        resume_download=True,
    )
    
    import os
    size_mb = os.path.getsize(path) / (1024 * 1024)
    print(f"✓ Downloaded to: {path}")
    print(f"  Size: {size_mb:.1f} MB")
    return path

def main():
    # Ensure directories exist
    for d in [UNET_DIR, VAE_DIR, CLIP_DIR]:
        os.makedirs(d, exist_ok=True)
    
    results = {}
    errors = []
    
    print(f"Starting {len(DOWNLOADS)} parallel downloads...")
    print(f"Available disk: {os.statvfs('/Users/santosh').f_bavail * 512 / (1024**3):.1f} GB free")
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(download_one, repo, fname, ddir, desc): f"{desc}_{repo}"
            for repo, fname, ddir, desc in DOWNLOADS
        }
        
        for future in as_completed(futures):
            key = futures[future]
            try:
                path = future.result()
                results[key] = path
            except Exception as e:
                errors.append(key)
                print(f"\n✗ FAILED: {key}")
                print(f"  Error: {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("DOWNLOAD SUMMARY")
    print(f"{'='*60}")
    print(f"Successes ({len(results)}):")
    for k, v in results.items():
        print(f"  ✓ {k} -> {v}")
    
    if errors:
        print(f"\nFailures ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    
    # List final contents
    import subprocess
    for d in [UNET_DIR, VAE_DIR, CLIP_DIR]:
        result = subprocess.run(["ls", "-lh", d], capture_output=True, text=True, timeout=5)
        print(f"\nContents of {d}:")
        print(result.stdout)
    
    print("\nAll models downloaded successfully!")

if __name__ == "__main__":
    main()
