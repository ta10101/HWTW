#!/usr/bin/env bash
# Build HWTW.dmg from dist/HWTW.app (run after PyInstaller).
# Optional: MACOS_CODESIGN_IDENTITY, then notarization env vars (see MACOS_SIGNING.md).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$ROOT/dist/HWTW.app"
STAGING="$ROOT/dist/dmg_staging"
DMG_NAME="${DMG_NAME:-HWTW-macOS-unsigned.dmg}"
DMG_PATH="$ROOT/dist/$DMG_NAME"
ENTITLEMENTS="$ROOT/packaging/macos-entitlements.plist"

if [[ ! -d "$APP" ]]; then
  echo "Missing $APP — run PyInstaller first."
  exit 1
fi

if [[ -n "${MACOS_CODESIGN_IDENTITY:-}" ]]; then
  echo "Codesigning $APP (hardened runtime)…"
  codesign --deep --force --options runtime \
    --entitlements "$ENTITLEMENTS" \
    --sign "$MACOS_CODESIGN_IDENTITY" \
    "$APP"
  codesign --verify --verbose "$APP"
else
  echo "Skipping codesign (set MACOS_CODESIGN_IDENTITY for a signed build)."
fi

rm -rf "$STAGING"
mkdir -p "$STAGING"
cp -R "$APP" "$STAGING/"
ln -sf /Applications "$STAGING/Applications"

rm -f "$DMG_PATH"
hdiutil create -volname "HWTW" -srcfolder "$STAGING" -ov -format UDZO -fs HFS+ "$DMG_PATH"

if [[ -n "${MACOS_CODESIGN_IDENTITY:-}" ]]; then
  echo "Codesigning disk image…"
  codesign --force --sign "$MACOS_CODESIGN_IDENTITY" "$DMG_PATH"
fi

if [[ -n "${MACOS_CODESIGN_IDENTITY:-}" && -n "${MACOS_NOTARIZE_APPLE_ID:-}" && -n "${MACOS_NOTARIZE_TEAM_ID:-}" && -n "${MACOS_NOTARIZE_APP_PASSWORD:-}" ]]; then
  echo "Submitting to Apple notary service…"
  xcrun notarytool submit "$DMG_PATH" \
    --apple-id "$MACOS_NOTARIZE_APPLE_ID" \
    --team-id "$MACOS_NOTARIZE_TEAM_ID" \
    --password "$MACOS_NOTARIZE_APP_PASSWORD" \
    --wait
  xcrun stapler staple "$DMG_PATH"
  xcrun stapler validate "$DMG_PATH"
  echo "Notarization complete."
else
  echo "Skipping notarization (needs signed build + MACOS_NOTARIZE_* — see MACOS_SIGNING.md)."
fi

echo "Built: $DMG_PATH"
ls -la "$DMG_PATH"
