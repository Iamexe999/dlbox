#!/usr/bin/env bash
set -euo pipefail

# Open the dlbox downloads folder in Windows Explorer from WSL
WIN_PATH="$(wslpath -w "$HOME/dlbox/downloads")"
explorer.exe "$WIN_PATH" >/dev/null 2>&1 &
