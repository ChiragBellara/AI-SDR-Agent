#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

open_terminal() {
    local title="$1"
    local cmd="$2"
    osascript \
        -e "tell application \"Terminal\"" \
        -e "  activate" \
        -e "  set t to do script \"echo -e '\\\\033]0;${title}\\\\007'; cd '${ROOT}'; ${cmd}\"" \
        -e "end tell"
}

open_terminal "AI-SDR · Backend" "uv run python main.py"
open_terminal "AI-SDR · Frontend" "nvm use 20 && cd ui && npm run dev"
