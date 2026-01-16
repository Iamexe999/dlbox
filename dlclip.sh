#!/usr/bin/env bash
set -euo pipefail

# Grab Windows clipboard via powershell.exe (works in WSL)
URL="$(powershell.exe -NoProfile -Command "Get-Clipboard" | tr -d '\r' | head -n 1)"

if [[ -z "${URL}" ]]; then
    echo "Clipboard is empty."
    exit 1
fi

# Basic sanity: require http(s)
if [[ ! "${URL}" =~ ^https?:// ]]; then
    echo "Clipboard doesn't look like an http(s) URL:"
    echo "${URL}"
    exit 1
fi

dlbox add "${URL}"