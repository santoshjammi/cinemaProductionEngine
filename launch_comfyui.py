import os
import sys
import subprocess
from pathlib import Path

# Add Homebrew PyTorch to path so ComfyUI can find torch
torch_path = "/opt/homebrew/Cellar/pytorch/2.12.1/libexec/lib/python3.14/site-packages"
if torch_path not in sys.path:
    sys.path.insert(0, torch_path)

# Verify we can see torch now
try:
    import torch
    print(f"✅ Found PyTorch: {torch.__version__} ({torch.device})")
except ImportError:
    print("❌ Still cannot find PyTorch. Launching with minimal deps.")

env = os.environ.copy()
env["PYTHONPATH"] = f"{sys.path[0]}:{env.get('PYTHONPATH', '')}"
env["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

ROOT = Path("/Users/santosh/Desktop/projects/videoGen")
cmd = ["python3", str(ROOT / "models/ComfyUI/main.py"), "--listen", "0.0.0.0", "--port", "8188"]

with open(ROOT / "comfyui_launch_v2.log", 'w') as f:
    print(f"🚀 Launching ComfyUI...")
    proc = subprocess.Popen(cmd, stdout=f, stderr=f, env=env)
    print(f"⏳ Process ID: {proc.pid}")

# Wait a bit for the port to open
import socket
import time
for _ in range(15):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8188))
    sock.close()
    if result == 0:
        print("✅ ComfyUI is live!")
        break
    time.sleep(2)
else:
    print("❌ Timed out waiting for port. Check logs.")
