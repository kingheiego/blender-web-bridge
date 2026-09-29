#!/bin/bash
# Author / 作者水印: @kinghei.ego/@ai.alter (GitHub: kingheiego)
# Pick an interpreter with Tk for the controller, preferring a current 3.11+, and
# hand it to install.py, which re-runs the shared prerequisite check. Never installs.
set -eu
cd "$(dirname "$0")"

CONTROLLER_MIN_TRY="3, 11"   # preferred: current supported releases
CONTROLLER_FLOOR="3, 10"     # fallback: minimum the controller code runs on

pick() {
  # $1 = version floor expression tested inside the candidate interpreter
  for candidate in \
    /Library/Frameworks/Python.framework/Versions/Current/bin/python3 \
    /opt/homebrew/bin/python3 \
    /usr/local/bin/python3 \
    "${HOME}/miniconda3/bin/python3" \
    "${HOME}/miniforge3/bin/python3" \
    "$(command -v python3 2>/dev/null || true)"; do
    [ -n "$candidate" ] && [ -x "$candidate" ] || continue
    if "$candidate" -c "import sys, tkinter; sys.exit(0 if sys.version_info[:2] >= ($1) else 1)" >/dev/null 2>&1; then
      printf '%s' "$candidate"; return 0
    fi
  done
  return 1
}

PY="$(pick "$CONTROLLER_MIN_TRY" || true)"
if [ -z "$PY" ]; then PY="$(pick "$CONTROLLER_FLOOR" || true)"; fi

if [ -z "$PY" ]; then
  printf '%s\n' \
    'Python 3.10+ with Tk is required; 3.11+ is recommended (current supported releases). / 需要 Python 3.10 或以上及 Tk；建議 3.11+（現行支援版本）。' \
    'Install the official macOS package / 請安裝官方 macOS 版本：' \
    'https://www.python.org/downloads/macos/' \
    'Then double-click Install.command again / 安裝後再雙擊此檔。'
  read -r -p 'Press Return to close / 按 Return 關閉。' _
  exit 1
fi

# Non-writing path: --check only reports the prerequisite and installs nothing.
if [ "${1:-}" = "--check" ]; then
  exec "$PY" install.py --check
fi
exec "$PY" install.py "$@"
