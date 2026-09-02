import subprocess
import time
import os
import sys
import socket
import shutil
import urllib.request
from pathlib import Path

ROOT = Path("/Users/santosh/Desktop/projects/videoGen")
MODELS_ROOT = ROOT / "models"
COMFYUI_PATH = MODELS_ROOT / "ComfyUI" / "main.py"

print("🚀 Phase 1: Visuals - ComfyUI + FLUX Integration")
print("-" * 40)

if not COMFYUI_PATH.exists():
    print(f"❌ ComfyUI not found at {COMFYUI_PATH}")
    sys.exit(1)

has_comfy_cli = shutil.which('comfy') is not None

print(f"\n📂 Setting up model symlinks...")
unet_src = Path("/Users/santosh/Desktop/projects/videoGen/models/flux/unet/flux1-dev-bf16.safetensors")
textenc_l_src = Path("/Users/santosh/Desktop/projects/videoGen/models/flux/clip/clip_l.safetensors")
t5xxl_src = Path("/Users/santosh/Desktop/projects/videoGen/models/flux/t5xxl/t5xxl_fp8_e4m3fn.safetensors")

if not unet_src.exists():
    print(f"❌ FLUX bf16 model missing at {unet_src}")
    sys.exit(1)

comfy_unet_dir = MODELS_ROOT / "unet"
comfy_textenc_dir = MODELS_ROOT / "text_encoders"

def setup_symlink(src, target_path):
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if target_path.exists():
        print(f"ℹ️  {target_path.name} already linked.")
        return
    os.symlink(str(src), str(target_path))
    print(f"✅ Linked {src.name} -> {target_path}")

setup_symlink(unet_src, comfy_unet_dir / "flux1-dev-bf16.safetensors")
if textenc_l_src.exists():
    setup_symlink(textenc_l_src, comfy_textenc_dir / "clip_l.safetensors")
if t5xxl_src.exists():
    setup_symlink(t5xxl_src, comfy_textenc_dir / "t5xxl_fp8_e4m3fn.safetensors")

print(f"\n🚀 Starting ComfyUI...")
env = os.environ.copy()
env["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

log_path = ROOT / "comfyui_launch.log"
with open(log_path, 'w') as log_file:
    cmd = ["python3", str(COMFYUI_PATH), "--listen", "0.0.0.0", "--port", "8188"]
    proc = subprocess.Popen(cmd, stdout=log_file, stderr=log_file, env=env)

print(f"⏳ Waiting for ComfyUI on port 8188...")
for i in range(90):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8188))
    sock.close()
    if result == 0:
        print(f"✅ ComfyUI is live! (Process ID: {proc.pid})")
        break
    # Health check loop replaced hardcoded sleep
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=5)
                break
            except Exception:
                time.sleep(1)
        else:
            print("[Launcher] ComfyUI did not become ready within 30s", flush=True)
else:
    print("❌ Timeout waiting for ComfyUI. Check logs.")
    sys.exit(1)

try:
    resp = urllib.request.urlopen("http://localhost:8188/system_stats", timeout=10)
    if resp.status == 200:
        print(f"\n📊 System Stats:\n{resp.read().decode()[:800]}")
except Exception as e:
    print(f"⚠️ API check failed (might be normal during startup): {e}")

print("\n✅ Phase 1 Complete. ComfyUI is running and models are linked.")
