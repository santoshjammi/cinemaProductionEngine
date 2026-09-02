import os, sys, socket, time
from pathlib import Path

torch_path = "/opt/homebrew/Cellar/pytorch/2.12.1/libexec/lib/python3.14/site-packages"
sys.path.insert(0, torch_path)
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

ROOT = Path("/Users/santosh/Desktop/projects/videoGen")
cmd = ["python3", str(ROOT / "models/ComfyUI/main.py"), "--listen", "0.0.0.0", "--port", "8188"]

import subprocess
with open(ROOT / "comfyui_v4.log", 'w') as f:
    p = subprocess.Popen(cmd, stdout=f, stderr=f)
    print(f"🚀 PID {p.pid}")

for _ in range(200):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r = sock.connect_ex(('localhost', 8188))
    sock.close()
    if r == 0:
        print("✅ Live!")
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
    print("❌ Timeout.")
