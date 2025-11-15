#!/usr/bin/env bash
set -e

echo "Fixing Python module path..."
export PYTHONPATH="/opt/render/project/src"

echo "Starting bot and worker..."

# Health check
python3 -m http.server 10000 &

# Start worker in background
python3 worker/worker.py &

# Start main bot
python3 bot/main.py
