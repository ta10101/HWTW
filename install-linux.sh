#!/usr/bin/env bash
# Easy setup for Chromebook Linux, Ubuntu, Debian, and similar (uses apt).
# Run from inside the HWTW folder (same place as main.py).

set -e

LAUNCH_AFTER=0
if [[ "${1:-}" == "--launch" ]]; then
  LAUNCH_AFTER=1
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

echo "=== HWTW — Linux easy install ==="
echo ""

if [[ ! -f "$ROOT/main.py" ]] || [[ ! -f "$ROOT/requirements.txt" ]]; then
  echo "This script must run from the HWTW project folder (where main.py is)."
  echo "Tip: cd into HWTW-main or HWTW, then run:  bash install-linux.sh"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found. On Debian/Ubuntu/Chromebook install it with apt first."
  exit 1
fi

if command -v apt-get >/dev/null 2>&1; then
  echo "Step 1/3: Installing system packages (apt)."
  echo "         You may be asked for your Linux password — that is normal."
  sudo apt-get update -qq
  sudo apt-get install -y python3 python3-venv python3-full python3-tk python3-pip wget unzip
  echo "         Done."
  echo ""
else
  echo "This easy installer uses apt (Debian, Ubuntu, Chromebook Linux)."
  echo "On Fedora or Arch, install Python 3.10+, venv, tkinter, then run:"
  echo "  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && ./run-hwtw-linux.sh"
  exit 1
fi

echo "Step 2/3: Creating a private Python environment (.venv) in this folder."
if [[ -d "$ROOT/.venv" ]]; then
  echo "         Removing old .venv for a clean install…"
  rm -rf "$ROOT/.venv"
fi
python3 -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/pip" install --upgrade pip -q
"$ROOT/.venv/bin/pip" install -r "$ROOT/requirements.txt"
echo "         Done."
echo ""

echo "Step 3/3: Desktop shortcut (optional)."
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
DESKTOP_FILE="$DESKTOP_DIR/hwtw.desktop"
mkdir -p "$DESKTOP_DIR"
cat >"$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=HWTW (Wind Tunnel)
Comment=Holo Wind Tunnel runner GUI
Exec=$ROOT/run-hwtw-linux.sh
Path=$ROOT
Terminal=true
Type=Application
Categories=Utility;
EOF
chmod 644 "$DESKTOP_FILE" 2>/dev/null || true
echo "         Added: $DESKTOP_FILE"
echo "         (You may find “HWTW” in your app launcher after a refresh.)"
echo ""

chmod +x "$ROOT/run-hwtw-linux.sh" 2>/dev/null || true

echo "=== Install finished ==="
echo ""
echo "Start HWTW:"
echo "  cd $(printf '%q' "$ROOT")"
echo "  ./run-hwtw-linux.sh"
echo ""
echo "Wind Tunnel still needs Docker installed and running on this machine."
echo ""

if [[ "$LAUNCH_AFTER" == 1 ]]; then
  exec "$ROOT/run-hwtw-linux.sh"
fi
