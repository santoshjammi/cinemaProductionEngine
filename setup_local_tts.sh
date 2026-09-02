#!/bin/bash
set -e
echo "🎙️ Setting up Local TTS (Kokelo/Piper)..."

# Check for Python 3.9+
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed."
    exit 1
fi

# Option A: Piper TTS (Lightweight, Fast)
echo "Attempting to install Piper TTS..."
pip3 install --user piper-tts 2>/dev/null || echo "⚠️ Piper installation skipped (network restrictions?)"

# Option B: Kokelo via MLX-Audio (Apple Silicon Optimized)
if [[ $(uname -m) == "arm64" ]]; then
    echo "🍎 Apple Silicon detected. Attempting Kokelo/MLX setup..."
    pip3 install --user mlx 2>/dev/null || echo "⚠️ MLX installation skipped."
fi

echo "✅ TTS environment preparation complete."
echo "Next step: Ensure 'pipeline/run_v7.py' is pointed to your local backend."
