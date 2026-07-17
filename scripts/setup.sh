#!/bin/bash
# Setup script for Text Cinema Engine
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== Text Cinema Engine Setup ==="
echo ""

# Check Python
echo "--- Checking Python ---"
PYTHON=$(which python3)
if [ -z "$PYTHON" ]; then
  echo "ERROR: python3 not found. Install Python 3.10+ first."
  exit 1
fi
echo "Python: $($PYTHON --version)"
echo ""

# Check Node
echo "--- Checking Node.js ---"
NODE=$(which node)
if [ -z "$NODE" ]; then
  echo "ERROR: node not found. Install Node.js 18+ first."
  exit 1
fi
echo "Node: $(node --version)"
echo ""

# Check FFmpeg
echo "--- Checking FFmpeg ---"
FFMPEG=$(which ffmpeg)
if [ -z "$FFMPEG" ]; then
  echo "WARNING: ffmpeg not found. Install it for video assembly:"
  echo "  brew install ffmpeg"
else
  echo "FFmpeg: $($FFMPEG -version 2>&1 | head -1)"
fi
echo ""

# Install backend deps
echo "--- Installing backend dependencies ---"
$PYTHON -m pip install -r backend/requirements.txt --quiet
echo "Backend dependencies installed"
echo ""

# Install frontend deps
echo "--- Installing frontend dependencies ---"
cd frontend
npm install --silent 2>/dev/null || npm install
cd "$ROOT_DIR"
echo "Frontend dependencies installed"
echo ""

# Download models (optional)
echo ""
echo "=== Setup complete ==="
echo ""
echo "To download ML models (requires ~25GB):"
echo "  bash scripts/download-models.sh"
echo ""
echo "To start the application:"
echo "  Terminal 1: bash scripts/start-backend.sh"
echo "  Terminal 2: bash scripts/start-frontend.sh"
echo "  Open:       http://localhost:3000"
