#!/bin/bash
# Script to view attendance API logs

LOG_FILE="attendance_api.log"

if [ -f "$LOG_FILE" ]; then
    echo "=== Viewing last 50 lines of $LOG_FILE ==="
    echo ""
    tail -50 "$LOG_FILE"
    echo ""
    echo "=== To watch logs in real-time, run: tail -f $LOG_FILE ==="
else
    echo "Log file '$LOG_FILE' doesn't exist yet."
    echo "It will be created when the server processes face recognition requests."
    echo ""
    echo "To watch for new logs, run:"
    echo "  watch -n 1 'tail -20 $LOG_FILE 2>/dev/null || echo \"Waiting for logs...\"'"
fi
