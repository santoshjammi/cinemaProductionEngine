#!/bin/bash
# Start the frontend dev server
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR/frontend"

echo "Starting frontend on port 3000..."
npm run dev
