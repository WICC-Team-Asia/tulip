#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INTERVAL=30

echo "Polling for pcaps every ${INTERVAL}s. Press Ctrl+C to stop."
while true; do
  python3 "$SCRIPT_DIR/fetch_pcaps.py"
  sleep "$INTERVAL"
done
