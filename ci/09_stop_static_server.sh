#!/usr/bin/env bash
set +e

echo "=== Stop static server ==="

PID_FILE="logs/http_server.pid"

if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  echo "Killing PID: $PID"

  if ps -p "$PID" >/dev/null 2>&1; then
    kill "$PID" || true
    sleep 1
    if ps -p "$PID" >/dev/null 2>&1; then
      echo "Process still alive, force kill"
      kill -9 "$PID" || true
    fi
  else
    echo "Process $PID not running"
  fi
else
  echo "No PID file found, nothing to stop."
fi
