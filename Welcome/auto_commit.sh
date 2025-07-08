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
mkdir -p images


SCREENSHOT_MODE=1 ./Welcome.app/Contents/MacOS/Welcome &
APP_PID=$!

sleep 2
TIMESTAMPUNIX=$(date +%s)
TIMESTAMP=$(date -r "$TIMESTAMPUNIX" '+%Y-%m-%d %H:%M:%S')
FILENAME="welcome_screenshot_$COUNT.png"
IMAGE_PATH="images/$FILENAME"

echo "Please click the 'Welcome' window to capture the screenshot..." # this message can be changed
screencapture -i "$IMAGE_PATH"

if [ ! -f "$IMAGE_PATH" ]; then
  echo "Screenshot not captured. Aborting commit."
  kill $APP_PID 2>/dev/null
  exit 1
fi
kill $APP_PID 2>/dev/null
COMMIT_SOURCE=$(basename "$PWD")
git add . "$IMAGE_PATH" "$COUNTER_FILE"  "$0"
git commit -m "Auto-commit #$COUNT from $COMMIT_SOURCE at $TIMESTAMP"
git push -u origin HEAD || true
