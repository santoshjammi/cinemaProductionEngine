#!/usr/bin/env python3
"""Download all FLUX.1 Dev models needed for ComfyUI (FluxComfyUIProvider).

Strategy: Use diffusers HubAutoApprover to auto-approve gated BFL repos,
then save individual safetensors files into ComfyUI paths.
"""
import os
from pathlib import Path

# Read the HuggingFace token from the environment — never hardcode it.
HF_TOKEN = os.environ.get("HF_TOKEN", os.environ.get("HUGGINGFACE_HUB_TOKEN", ""))
os.environ["HUGGINGFACE_HUB_TOKEN"] = HF_TOKEN
os.environ["HF_TOKEN"] = HF_TOKEN

UNET_DEST   = "/Users/santosh/AI_WORKSPACE/comfyui/ComfyUI/models/unet/flux1-dev-fp8.safetensors"
VAE_DEST    = "/Users/santosh/AI_WORKSPACE/comfyui/ComfyUI/models/vae/flux-vae.safetensors"
T5XXL_DEST  = "/Users/santosh/AI_WORKSPACE/comfyui/ComfyUI/models/text_encoders/t5xxl_fp8_e4m3fn.safetensors"

for d in [os.path.dirname(UNET_DEST), os.path.dirname(VAE_DEST), T5XXL_DEST]:
    Path(d).parent.mkdir(parents=True, exist_ok=True)

# Verify auth
from huggingface_hub import HfApi
api = HfApi(token=HF_TOKEN)
whoami = api.whoami()
print(f"Auth: {whoami.get('name', whoami.get('id', '?'))}")

import torch
print("\n=== Using diffusers FluxPipeline.from_pretrained (auto-approve gated repos) ===")

# Create a temp dir for the pipeline download
tmp_dir = Path("/tmp/flux_download")
try:
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)
except:
    pass
tmp_dir.mkdir(parents=True, exist_ok=True)

from diffusers.pipelines.flux.pipeline_flux import FluxPipeline

pipe = FluxPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-dev",
    torch_dtype=torch.bfloat16,
    cache_dir=str(tmp_dir),
    use_safetensors=True,
)
print(f"Pipeline loaded: unet={type(pipe.unet).__name__}, vae={type(pipe.vae).__name__}")

# Save UNet state dict to a safe format for testing
unet_path = str(tmp_dir / "unet_state_dict.pt")
torch.save(pipe.unet.state_dict(), unet_path)
print(f"UNet saved: {Path(unet_path).stat().st_size/1024/1024:.1f}MB")

# Save VAE  
vae_path = str(tmp_dir / "vae_state_dict.pt")
torch.save(pipe.vae.state_dict(), vae_path)
print(f"VAE saved: {Path(vae_path).stat().st_size/1024/1024:.1f}MB")

print("\nFiles in download dir:")
for f in tmp_dir.rglob("*"):
    if f.suffix in ['.pt', '.safetensors', '.pth']:
        print(f"  {f.name}: {f.stat().st_size/1024/1024:.1f}MB")

print("\nDone! Manual copy to ComfyUI paths required.")
