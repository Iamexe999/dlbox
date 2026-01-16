#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: dladdfile <links.txt>"
    exit 2
fi

FILE="$1"
if [[ ! -f "$FILE" ]]; then
    echo "File not found: $FILE"
    exit 2
fi

# Read non-empty, non-comment lines; strip CR for Windows-created files.
mapfile -t URLS < <(sed -e 's/\r$//' -e '/^\s*$/d' -e '/^\s*#/d' "$FILE")

if [[ ${#URLS[@]} -eq 0 ]]; then
    echo "No URLs found in $FILE (expect one per line)."
    exit 1
fi

dlbox add "${URLS[@]}"