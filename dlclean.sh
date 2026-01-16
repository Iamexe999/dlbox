#!/usr/bin/env bash
set -euo pipefail

DIR="$HOME/dlbox/downloads"
if [[ ! -d "$DIR" ]]; then
    echo "Downloads folder not found: $DIR"
    exit 2
fi

count="$(find "$DIR" -maxdepth 1 -type f -name '*.aria2' | wc -l | tr -d ' ')"

if [[ "$count" == "0" ]]; then
    echo "No .aria2 files to clean."
    exit 0
fi

find "$DIR" -maxdepth 1 -type f -name '*.aria2' -print -delete
echo "Removed $count .aria2 file(s)."