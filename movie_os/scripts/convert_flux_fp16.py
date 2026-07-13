"""Convert FLUX fp8 model to fp16 for MPS compatibility.

FLUX.1 Dev fp8 stores weights as torch.float8_e4m3fn. The M1 Max
GPU (MPS backend) doesn't support fp8. This script converts the
weights to fp16 — same numerical range, larger file size (~24GB
vs ~12GB), but works on MPS.

Run once:
    python -m movie_os.scripts.convert_flux_fp16

Output: models/flux/unet/flux1-dev-fp16.safetensors
"""

import sys
import time
from pathlib import Path

import torch
from safetensors import safe_open
from safetensors.torch import save_file


def convert(src: Path, dst: Path) -> None:
    if dst.exists():
        print(f"Already exists: {dst}")
        return
    if not src.exists():
        raise FileNotFoundError(f"Source not found: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)

    print(f"Converting {src} → {dst}")
    print(f"  Loading source...")
    t0 = time.time()
    new_tensors = {}
    with safe_open(str(src), framework="pt") as f:
        keys = list(f.keys())
        n = len(keys)
        for i, k in enumerate(keys):
            t = f.get_tensor(k)
            new_tensors[k] = t.to(torch.float16)
            if (i + 1) % 50 == 0 or i + 1 == n:
                pct = (i + 1) / n * 100
                print(f"  {i + 1}/{n} ({pct:.1f}%) — {time.time() - t0:.1f}s")
    print(f"  Loaded in {time.time() - t0:.1f}s")
    print(f"  Saving fp16 model...")
    t0 = time.time()
    save_file(new_tensors, str(dst), metadata={"format": "pt"})
    print(f"  Saved in {time.time() - t0:.1f}s")
    print(f"  Output: {dst} ({dst.stat().st_size / 1024**3:.1f} GB)")


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[2]
    src = repo_root / "models" / "flux" / "unet" / "flux1-dev-fp8.safetensors"
    dst = repo_root / "models" / "flux" / "unet" / "flux1-dev-fp16.safetensors"
    if len(sys.argv) > 1:
        src = Path(sys.argv[1])
    if len(sys.argv) > 2:
        dst = Path(sys.argv[2])
    convert(src, dst)
