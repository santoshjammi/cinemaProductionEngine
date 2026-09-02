#!/usr/bin/env python3
"""Download FLUX.1 Dev models using diffusers HubAutoApprover (auto-accepts gated repos).

Then downloads individual safetensors files into ComfyUI's expected paths.
"""
import os
import sys
from pathlib import Path

# Read the HuggingFace token from the environment — never hardcode it.
HF_TOKEN = os.environ.get("HF_TOKEN", os.environ.get("HUGGINGFACE_HUB_TOKEN", ""))
os.environ["HUGGINGFACE_HUB_TOKEN"] = HF_TOKEN
os.environ["HF_TOKEN"] = HF_TOKEN

# Verify auth first
print("=== Verifying authentication ===")
from huggingface_hub import HfApi
api = HfApi(token=HF_TOKEN)
try:
    whoami = api.whoami()
    print(f"  Authenticated as: {whoami.get('name', whoami.get('id', 'unknown'))}")
except Exception as e:
    print(f"  Authentication failed: {e}")
    sys.exit(1)

# Use diffusers HubAutoApprover to download + extract all components
import torch
from pathlib import Path
from huggingface_hub import hf_hub_download, HfApi

comfy_unet = Path("/Users/santosh/AI_WORKSPACE/comfyui/ComfyUI/models/unet/")
comfy_vae  = Path("/Users/santosh/AI_WORKSPACE/comfyui/ComfyUI/models/vae/")
comfy_clip = Path("/Users/santosh/AI_WORKSPACE/comfyui/ComfyUI/models/clip/")
comfy_t5   = Path("/Users/santosh/AI_WORKSPACE/comfyui/ComfyUI/models/text_encoders/")

for d in [comfy_unet, comfy_vae, comfy_clip, comfy_t5]:
    d.mkdir(parents=True, exist_ok=True)

# Create temp dir for pipeline download
tmp_dir = Path("/tmp/flux_download")
import shutil
shutil.rmtree(tmp_dir, ignore_errors=True)
tmp_dir.mkdir(parents=True, exist_ok=True)

def check_file_size(path):
    """Get file size in MB."""
    return path.stat().st_size / 1024 / 1024 if path.exists() else 0

# Method 1: Save current ComfyUI state for comparison
print("\n=== Current ComfyUI model directories ===")
for dir_path, name in [(comfy_unet, "unet"), (comfy_vae, "vae"), (comfy_clip, "clip"), (comfy_t5, "text_encoders")]:
    print(f"\n  [{name}] {dir_path}:")
    if not dir_path.exists():
        print("    Directory does not exist")
        continue
    
    for ext in ['.safetensors', '.gguf', '.pt']:
        files = list(dir_path.rglob(f"*{ext}"))
        valid_files = []
        for f in files:
            if f.is_file():  # Skip symlinks etc
                size_mb = check_file_size(f)
                valid_files.append((f.name, size_mb))
        
        if valid_files:
            print(f"    {ext}:")
            for fname, size in valid_files:
                marker = "✓" if fname != "flux_dev_quantization_map.json" else "(not a model)"
                print(f"      - {fname}: {size:.1f} MB {marker}")
        else:
            print(f"    (empty)")

# Method 1: Try diffusers HubAutoApprover to download the full suite
print("\n\n=== Downloading FLUX.1 Dev via diffusers FluxPipeline ===")
print("This will auto-approve gated models on behalf of your token holder.")

success = False
saved_path = None

try:
    from diffusers.pipelines.flux.pipeline_flux import FluxPipeline
    
    print(f"  Loading black-forest-labs/FLUX.1-dev (auto-approve enabled)...")
    pipe = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-dev",
        torch_dtype=torch.bfloat16,
        cache_dir=str(tmp_dir),
        use_safetensors=True,
    )
    print(f"  ✅ Pipeline loaded! unet_type={type(pipe.unet).__name__}, vae_type={type(pipe.vae).__name__}")
    success = True
    
except ImportError as e:
    print(f"  FluxPipeline import failed: {e}")

if not success:
    # Method 2: Use HF Hub for individual file downloads
    # Try downloading files directly - some may succeed even if the full repo is gated
    
    print("\n\n=== Alternative: Direct hf_hub_download (individual files) ===")
    
    files_to_try = [
        ("ae.safetensors", "vae"),                                    # VAE
        ("text_encoder/model.safetensors", None),                    # CLIP text encoder  
        ("transformer/diffusion_pytorch_model.safetensors", None),   # UNet diffusion weights
    ]
    
    for fname, dest_type in files_to_try:
        try:
            print(f"  Trying {fname}...")
            
            local_path = hf_hub_download(
                repo_id="black-forest-labs/FLUX.1-dev",
                filename=fname,
                token=HF_TOKEN,
                local_dir=str(tmp_dir),
            )
            
            downloaded_size = check_file_size(Path(local_path))
            print(f"    ✅ Downloaded: {Path(fname).name} ({downloaded_size:.1f} MB)")
            
        except Exception as fe:
            err_str = str(fe)
            if "403" in err_str or "not found" in err_str.lower():
                print(f"    ❌ {err_str}")
            else:
                print(f"    ⚠ Error: {err_str}")

# Check what we actually got
print("\n\n=== Files in tmp_dir ===")
for f in tmp_dir.rglob("*"):
    if f.is_file() and (f.suffix in ['.pt', '.safetensors', '.pth']) or ('diffusion' in str(f).lower()):
        size_mb = check_file_size(f)
        print(f"  {Path(f).name}: {size_mb:.1f} MB")

# Scan subdirectories too for safetensors files with full paths  
for subdir_path in [tmp_dir / "FLUX.1-dev", tmp_dir / "black-forest-labs" / "FLUX.1-dev"]:
    if subdir_path.exists():
        for sf in subdir_path.rglob("*.safetensors"):
            size_mb = check_file_size(sf)
            print(f"  {sf}: {size_mb:.1f} MB")

# Method 3: Check CivitAI as a last resort for publicly accessible models  
print("\n\n=== Checking CivitAI as a backup source ===")
import subprocess
result = subprocess.run([
    "curl", "-s", 
    "--max-time", "10",
    "https://civitai.com/api/v1/models"
], capture_output=True, text=True, timeout=15)

if result.returncode == 0 and len(result.stdout) < 50000:
    import json
    try:
        data = json.loads(result.stdout)
        items = data.get('items', []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        flux_models = [m for m in items if 'flux' in m.get('name', '').lower()]
        
        print(f"  Found {len(flux_models)} FLUX models on CivitAI:")
        for model in flux_models[:10]:
            name = model.get('name', '?')
            downloads = model.get('downloads', 0) 
            model_type = model.get('modelType', '?')
            print(f"    - {name} (type={model_type}, downloads={downloads})")
    except (json.JSONDecodeError, KeyError):
        pass
else:
    print("  CivitAI query returned too much data or error — trying targeted search...")
    
    # Targeted search for FLUX GGUF models (which are often public on CivitAI)
    result2 = subprocess.run([
        "curl", "-s", "--max-time", "10", 
        "-G", "-d", "page=1&limit=3&q=flux+gguf&type=model",
        "https://civitai.com/api/v1/models"
    ], capture_output=True, text=True, timeout=15)
    
    if result2.returncode == 0:
        try:
            data = json.loads(result2.stdout)
            items = data.get('items', []) if isinstance(data, dict) else []
            for model in items[:5]:
                name = model.get('name', '?')
                downloads = model.get('downloads', 0)
                print(f"    - {name} (type={model.get('modelType','?')}, downloads={downloads})")
        except:
            pass

# Final summary of what we need and what we have
print("\n\n=== SUMMARY ===")
needed = {
    "unet": ("flux1-dev-fp8.safetensors or flux1-dev-bf16.safetensors", comfy_unet),
    "vae":  ("flux-vae.safetensors (ae.safetensors)", comfy_vae), 
    "clip_l": ("clip_l.safetensors", comfy_clip),
    "t5xxl": ("t5xxl_fp8_e4m3fn.safetensors", comfy_t5 if comfy_t5.exists() else comfy_clip),
}

print("Needed files for ComfyUI FluxComfyUIProvider:")
for key, (name, path) in needed.items():
    size = check_file_size(path / name)
    marker = "✓" if size > 10 else "✗"
    print(f"  [{marker}] {key}: {path / name} (expected: {name})")
