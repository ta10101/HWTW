#!/usr/bin/env bash
# Easy setup for macOS (Intel or Apple Silicon). Requires Python 3.10+ with Tcl/Tk (tkinter).
# Run from inside the HWTW folder (same place as main.py).

set -e

LAUNCH_AFTER=0
if [[ "${1:-}" == "--launch" ]]; then
  LAUNCH_AFTER=1
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "=== HWTW — macOS install ==="
echo ""

if [[ ! -f "$ROOT/main.py" ]] || [[ ! -f "$ROOT/requirements.txt" ]]; then
  echo "Run this from the HWTW folder (where main.py is)."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 not found. Install one of:"
  echo "  • https://www.python.org/downloads/macos/  (official installer includes Tk)"
  echo "  • brew install python@3.12"
  exit 1
fi

if ! python3 -c "import tkinter" 2>/dev/null; then
  echo "This python3 has no tkinter (GUI). Fix with one of:"
  echo "  • Install Python from https://www.python.org/downloads/macos/"
  echo "  • brew install python@3.12"
  echo "Then ensure \`python3\` points to that install (which python3)."
  exit 1
fi

echo "Step 1/2: Virtual environment (.venv) in this folder."
if [[ -d "$ROOT/.venv" ]]; then
  echo "         Removing old .venv…"
  rm -rf "$ROOT/.venv"
fi
python3 -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/pip" install --upgrade pip -q
"$ROOT/.venv/bin/pip" install -r "$ROOT/requirements.txt"
echo "         Done."
echo ""

chmod +x "$ROOT/run-hwtw-macos.sh" 2>/dev/null || true

echo "Step 2/2: Done."
echo ""
echo "Docker: install **Docker Desktop for Mac** separately if you use Wind Tunnel containers."
echo "         https://docs.docker.com/desktop/setup/install/mac-install/"
echo ""
echo "Start HWTW:"
echo "  cd $(printf '%q' "$ROOT")"
echo "  ./run-hwtw-macos.sh"
echo ""

if [[ "$LAUNCH_AFTER" == 1 ]]; then
  exec "$ROOT/run-hwtw-macos.sh"
fi
