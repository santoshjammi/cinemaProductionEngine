#!/bin/bash
# Start the backend server
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "Starting backend on port 8000..."
python3 -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info
