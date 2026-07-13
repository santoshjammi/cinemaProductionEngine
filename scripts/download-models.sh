#!/bin/bash
# Download required ML models for video generation
set -e

echo "=== Text Cinema Engine - Model Downloader ==="
echo "This script downloads all required ML models."
echo "Total size: ~25GB (SVD-XT: 15GB, SD v1.5: 5GB, XTTS-v2: 2GB, others: 3GB)"
echo ""

# Check Python
PYTHON=$(which python3)
if [ -z "$PYTHON" ]; then
  echo "ERROR: python3 not found"
  exit 1
fi

# Check available disk space
AVAILABLE_GB=$(df -k / | tail -1 | awk '{printf "%.0f", $4/1024/1024}')
echo "Available disk space: ${AVAILABLE_GB}GB"
if [ "$AVAILABLE_GB" -lt 30 ]; then
  echo "WARNING: Low disk space. At least 30GB free recommended."
fi

download_progress() {
  local model=$1
  local name=$2
  echo "--- Downloading $name ---"
  python3 -c "
import os
from huggingface_hub import snapshot_download, HfApi

api = HfApi()
try:
    model_info = api.model_info('$model')
    size_bytes = sum(f.size for f in model_info.siblings if f.size) if hasattr(model_info, 'siblings') else 0
    if size_bytes > 0:
        print(f'Model size: {size_bytes / 1024**3:.1f}GB')
except Exception:
    pass

print(f'Downloading $model...')
snapshot_download(
    repo_id='$model',
    local_files_only=False,
    resume_download=True,
)
print(f'✓ $name downloaded successfully')
"
  echo ""
}

# Download models
download_progress "runwayml/stable-diffusion-v1-5" "Stable Diffusion v1.5"
download_progress "stabilityai/stable-video-diffusion-img2vid-xt" "Stable Video Diffusion XT"

echo "=== Downloading XTTS-v2 ==="
python3 -c "
from TTS.api import TTS
print('Downloading XTTS-v2...')
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2', gpu=False)
print('✓ XTTS-v2 downloaded')
"

echo ""
echo "=== All models downloaded ==="
echo "You can now run: python3 -m uvicorn backend.app.main:app --reload"
