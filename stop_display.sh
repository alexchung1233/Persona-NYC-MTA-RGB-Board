#!/bin/bash
# Stops run_main_display.py gracefully (SIGINT triggers its own matrix.Clear()),
# then clears the matrix again as a safety net in case the process was already
# dead or didn't clean up on its own.
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$PROJECT_DIR/display.pid"
LOG_FILE="$PROJECT_DIR/logs/display.log"

mkdir -p "$PROJECT_DIR/logs"

if [ -f "$PID_FILE" ]; then
    PID="$(cat "$PID_FILE")"
    if kill -0 "$PID" 2>/dev/null; then
        echo "$(date): stopping display (pid $PID)" >> "$LOG_FILE"
        kill -INT "$PID"
        for i in $(seq 1 10); do
            kill -0 "$PID" 2>/dev/null || break
            sleep 1
        done
        kill -9 "$PID" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
fi

python3 "$PROJECT_DIR/clear_matrix.py"
echo "$(date): matrix cleared" >> "$LOG_FILE"
