#!/usr/bin/env bash
# After packaging/build-macos-dmg.sh: zip the .app and build a flat .pkg into /Applications.
# Uses dist/HWTW.app as built/signed by the DMG step. Env: DMG_NAME, PKG_VERSION (e.g. 1.2.8).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/dist"

APP="HWTW.app"
DMG_NAME="${DMG_NAME:-HWTW-macOS-unsigned.dmg}"
PKG_VERSION="${PKG_VERSION:-1.0.0}"

if [[ ! -d "$APP" ]]; then
  echo "Missing $APP — run PyInstaller and build-macos-dmg.sh first."
  exit 1
fi

echo "Zipping $APP → HWTW-macOS.app.zip …"
rm -f HWTW-macOS.app.zip
ditto -c -k --sequesterRsrc --keepParent "$APP" HWTW-macOS.app.zip

echo "Building HWTW-macOS.pkg (installs to /Applications) …"
rm -rf pkgroot HWTW-macOS.pkg
mkdir -p pkgroot/Applications
cp -R "$APP" pkgroot/Applications/
pkgbuild \
  --root pkgroot \
  --identifier io.github.ta10101.hwtw.pkg \
  --version "$PKG_VERSION" \
  --install-location / \
  HWTW-macOS.pkg

echo "SHA256SUMS-macos.txt …"
rm -f SHA256SUMS-macos.txt
for f in "$DMG_NAME" HWTW-macOS.app.zip HWTW-macOS.pkg; do
  if [[ ! -f "$f" ]]; then
    echo "Missing $f"
    exit 1
  fi
  shasum -a 256 "$f" | awk -v b="$(basename "$f")" '{print $1 "  " b}'
done > SHA256SUMS-macos.txt
cat SHA256SUMS-macos.txt

ls -la HWTW-macOS.app.zip HWTW-macOS.pkg
