#!/bin/bash

cd "$(dirname "$0")" || exit 1
if git diff --quiet HEAD welcome.cpp; then # here we can modify the file for those students edit
  echo " welcome.cpp unchanged, skipping screenshot + commit."
  exit 0
fi

COUNTER_FILE=".autocommit_counter.txt"
if [ -f "$COUNTER_FILE" ]; then
  COUNT=$(cat "$COUNTER_FILE")
else
  COUNT=0
fi
COUNT=$((COUNT + 1))
echo "$COUNT" > "$COUNTER_FILE"

SCREENSHOT_MODE=1 ./Welcome.app/Contents/MacOS/Welcome &
APP_PID=$!

sleep 2
TIMESTAMPUNIX=$(date +%s)
TIMESTAMP=$(date -r "$TIMESTAMPUNIX" '+%Y-%m-%d %H:%M:%S')
FILENAME="welcome_screenshot_$COUNT.png"
echo "Please click the 'Welcome' window to capture the screenshot..." # this message can be changed
screencapture -i "$FILENAME"

if [ ! -f "$FILENAME" ]; then
  echo "Screenshot not captured. Aborting commit."
  kill $APP_PID 2>/dev/null
  exit 1
fi
COMMIT_SOURCE=$(basename "$PWD")
kill $APP_PID 2>/dev/null
git add . "$FILENAME" "$COUNTER_FILE"  "$0"
git commit -m "Auto-commit #$COUNT from $COMMIT_SOURCE at $TIMESTAMP"
git push -u origin HEAD || true
