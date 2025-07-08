#!/bin/bash

cd "$(dirname "$0")" || exit 1

COUNTER_FILE=".autocommit_counter.txt"

if [ -f "$COUNTER_FILE" ]; then
  COUNT=$(cat "$COUNTER_FILE")
else
  COUNT=0
fi

COUNT=$((COUNT + 1))
echo "$COUNT" > "$COUNTER_FILE"

SCREENSHOT_MODE=1 ./Welcome &  # Replace with your actual binary
APP_PID=$!
sleep 3  

screencapture -x "$FILENAME"
kill $APP_PID


git add . "$FILENAME" "$COUNTER_FILE"
git commit -m "Auto-commit #$COUNT from Welcome at $(date '+%Y-%m-%d %H:%M:%S')"
git push -u origin HEAD || true

