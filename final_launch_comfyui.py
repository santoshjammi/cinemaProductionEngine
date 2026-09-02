import os
import sys
import subprocess
import socket
import time
from pathlib import Path

# 1. Environment Setup
ROOT = Path("/Users/santosh/Desktop/projects/videoGen")
torch_path = "/opt/homebrew/Cellar/pytorch/2.12.1/libexec/lib/python3.14/site-packages"
dummy_path = "/tmp"

if torch_path not in sys.path: sys.path.insert(0, torch_path)
if dummy_path not in sys.path: sys.path.insert(0, dummy_path)

# 2. Verify Torch
import torch
print(f"✅ PyTorch found: {torch.__version__}")
try: import numpy as np; print("✅ NumPy found")
except ImportError: print("⚠️ NumPy missing (will add fake stub)")

# Create fake numpy to silence warnings during load
class FakeNumpy:
    @staticmethod
    def array(*args, **kwargs): return None
sys.modules['numpy'] = FakeNumpy()

# 3. Launch ComfyUI
env = os.environ.copy()
env["PYTHONPATH"] = f"{torch_path}:{dummy_path}"
env["PYTORCH_ENABLE_MPS_FALLBACK"] = "1" # Force fallback if MPS fails
env["HF_HOME"] = str(ROOT / ".hf_cache")

log_path = ROOT / "comfyui_launch_final.log"
cmd = ["python3", str(ROOT / "models/ComfyUI/main.py"), "--listen", "0.0.0.0", "--port", "8188", "--disable-auto-launch"]

print("🚀 Launching ComfyUI (FLUX bf16 load may take several minutes)...")
with open(log_path, 'w') as f:
    proc = subprocess.Popen(cmd, stdout=f, stderr=f, env=env)

# 4. Wait for Port (up to 5 mins)
print(f"⏳ Waiting for port 8188 (PID: {proc.pid})...")
for i in range(150): # 150 * 2s = 300s = 5 mins
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8188))
    sock.close()
    if result == 0:
        print("✅ ComfyUI is live!")
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
    if i % 30 == 0: print(f"   ...waiting... {i}s")

if result != 0:
    print("❌ Timeout. Check logs for model loading progress.")
