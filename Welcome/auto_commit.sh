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

SCREENSHOT_MODE=1 ./Welcome &
APP_PID=$!

sleep 2

FILENAME="build_screenshot_$COUNT.png"
echo "Please click the 'Welcome' window to capture the screenshot..."
screencapture -i "$FILENAME"

kill $APP_PID

git add "$FILENAME" "$COUNTER_FILE"
git commit -m "Auto-commit #$COUNT with screenshot"
git push -u origin HEAD || true
