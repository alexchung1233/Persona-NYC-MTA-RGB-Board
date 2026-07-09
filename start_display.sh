#!/bin/bash
# Starts run_main_display.py in the background, unless it's already running.
# Intended to be run as root (via root's crontab) since rgbmatrix needs GPIO access.
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$PROJECT_DIR/display.pid"
LOG_FILE="$PROJECT_DIR/logs/display.log"

mkdir -p "$PROJECT_DIR/logs"

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "$(date): display already running (pid $(cat "$PID_FILE"))" >> "$LOG_FILE"
    exit 0
fi

cd "$PROJECT_DIR"
echo "$(date): starting display" >> "$LOG_FILE"
nohup python3 run_main_display.py >> "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
