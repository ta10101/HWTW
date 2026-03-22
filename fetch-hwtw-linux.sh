#!/usr/bin/env bash
# Download the latest HWTW from GitHub into ~/HWTW-main and run the easy installer.
# For beginners: open Linux terminal, paste one line from the README, or run:
#   bash fetch-hwtw-linux.sh

set -e

ZIP_URL="${HWTW_ZIP_URL:-https://github.com/ta10101/HWTW/archive/refs/heads/main.zip}"
TARGET_DIR="${HWTW_HOME:-$HOME/HWTW-main}"

cd "$HOME"

echo "=== HWTW — download and install ==="
echo "This will download the app into: $TARGET_DIR"
echo ""

if ! command -v wget >/dev/null 2>&1 && ! command -v curl >/dev/null 2>&1; then
  echo "Need wget or curl. Try: sudo apt-get install -y wget"
  exit 1
fi

if ! command -v unzip >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    echo "Installing unzip (one time)…"
    sudo apt-get update -qq
    sudo apt-get install -y unzip
  else
    echo "Please install unzip, then run this script again."
    exit 1
  fi
fi

TMP_ZIP="$HOME/.hwtw-download-$$.zip"
cleanup() { rm -f "$TMP_ZIP" 2>/dev/null || true; }
trap cleanup EXIT

echo "Downloading…"
if command -v wget >/dev/null 2>&1; then
  wget -q -O "$TMP_ZIP" "$ZIP_URL"
else
  curl -fsSL -o "$TMP_ZIP" "$ZIP_URL"
fi

if [[ -d "$TARGET_DIR" ]]; then
  echo "Replacing existing folder: $TARGET_DIR"
  rm -rf "$TARGET_DIR"
fi

unzip -q -o "$TMP_ZIP" -d "$HOME"
# GitHub zip extracts to HWTW-main when repo is HWTW and branch main
if [[ ! -d "$HOME/HWTW-main" ]]; then
  echo "Unexpected zip layout. Look for a folder like HWTW-main or HWTW-* and cd into it,"
  echo "then run:  bash install-linux.sh"
  exit 1
fi

if [[ "$TARGET_DIR" != "$HOME/HWTW-main" ]]; then
  mv "$HOME/HWTW-main" "$TARGET_DIR"
fi

cd "$TARGET_DIR"
echo ""
exec bash install-linux.sh --launch
