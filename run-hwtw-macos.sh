#!/usr/bin/env bash
# Start HWTW using the project virtual environment (after install-macos.sh).

set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PY="$ROOT/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "HWTW is not installed yet."
  echo ""
  echo "Open Terminal in this folder and run:"
  echo "  bash install-macos.sh"
  echo ""
  exit 1
fi

exec "$PY" "$ROOT/main.py" "$@"
