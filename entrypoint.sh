#!/usr/bin/env bash
set -e

echo "Starting bot and worker..."

# Start health check server (Render required)
python3 -m http.server 10000 &

# Start the main bot
python3 bot/main.py
