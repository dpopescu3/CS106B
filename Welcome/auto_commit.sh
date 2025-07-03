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

git add . "$COUNTER_FILE"
git commit -m "Auto-commit #$COUNT from Welcome at $(date '+%Y-%m-%d %H:%M:%S')"
git push -u origin HEAD || true

