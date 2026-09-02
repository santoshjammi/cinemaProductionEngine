import os, sys, socket, time
from pathlib import Path

torch_path = "/opt/homebrew/Cellar/pytorch/2.12.1/libexec/lib/python3.14/site-packages"
stub_path = "/tmp"
sys.path.insert(0, torch_path)
sys.path.insert(0, stub_path) # For yaml and dummy seeder

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

ROOT = Path("/Users/santosh/Desktop/projects/videoGen")
cmd = ["python3", str(ROOT / "models/ComfyUI/main.py"), "--listen", "0.0.0.0", "--port", "8188"]

import subprocess
with open(ROOT / "comfyui_v5.log", 'w') as f:
    p = subprocess.Popen(cmd, stdout=f, stderr=f)
    print(f"🚀 PID {p.pid}")

for _ in range(300): # 10 mins wait for FLUX bf16 load
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r = sock.connect_ex(('localhost', 8188))
    sock.close()
    if r == 0:
        print("✅ Live!")
        break
    time.sleep(2)
else:
    print("❌ Timeout.")
