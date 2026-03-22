# macOS `.app` / `.dmg` signing and notarization

GitHub Actions builds **`HWTW.app`** with PyInstaller, then **`HWTW-macOS.dmg`** (or **`HWTW-macOS-unsigned.dmg`**), **`HWTW-macOS.app.zip`** (same bundle as a zip), and **`HWTW-macOS.pkg`** (installs **`HWTW.app`** into **`/Applications`**). Signing applies to the **`.app`** before those artifacts are produced when secrets are set. **`SHA256SUMS-macos.txt`** lists hashes for **`.dmg`**, **`.zip`**, and **`.pkg`**.

## What you need (for a **signed & notarized** DMG)

1. **Apple Developer Program** membership (paid).
2. **Developer ID Application** certificate (Xcode → Settings → Accounts, or developer.apple.com).
3. Export the cert as **`.p12`** with a password you know.
4. An **app-specific password** for your Apple ID (Apple ID account → App-Specific Passwords) — used only for `notarytool`, not your main password.

## Repository secrets (Settings → Secrets and variables → Actions)

| Secret | Purpose |
| ------ | -------- |
| `MACOS_CERTIFICATE_P12` | Base64-encoded **`.p12`** file (see below). |
| `MACOS_CERTIFICATE_PASSWORD` | Password for that `.p12`. |
| `MACOS_CODESIGN_IDENTITY` | Full identity string, e.g. `Developer ID Application: Your Name (XXXXXXXXXX)`. Run `security find-identity -v -p codesigning` after importing the cert locally to copy it exactly. |
| `MACOS_NOTARIZE_APPLE_ID` | Your Apple ID email. |
| `MACOS_NOTARIZE_TEAM_ID` | 10-character **Team ID** (Membership details on developer.apple.com). |
| `MACOS_NOTARIZE_APP_PASSWORD` | App-specific password (not your Apple ID login password). |

### Encode `.p12` for `MACOS_CERTIFICATE_P12`

On a Mac (or with OpenSSL elsewhere):

```bash
base64 -i YourCert.p12 | pbcopy   # macOS: copies to clipboard; paste into secret value
# or: base64 -w0 YourCert.p12   # Linux, paste entire line into GitHub secret
```

## Behavior in CI

| Secrets present | Output file | Gatekeeper |
| ---------------- | ----------- | ---------- |
| All signing + notarization secrets | `HWTW-macOS.dmg` | Should open normally after download (stapled ticket). |
| Missing `MACOS_CERTIFICATE_P12` (or identity) | `HWTW-macOS-unsigned.dmg` | Users may need **Right-click → Open** the first time, or **System Settings → Privacy & Security**. |

The **Windows** release job uploads **`requirements.txt`** once per release; the macOS job only adds the **`.dmg`** so the asset list is not duplicated.

## Local test (optional)

```bash
python3 -m pip install pyinstaller psutil "sv-ttk>=2.6.0"
pyinstaller --windowed --name HWTW \
  --osx-bundle-identifier io.github.ta10101.HWTW \
  --collect-all sv_ttk main.py
export MACOS_CODESIGN_IDENTITY="Developer ID Application: …"
export MACOS_NOTARIZE_APPLE_ID="…"
export MACOS_NOTARIZE_TEAM_ID="…"
export MACOS_NOTARIZE_APP_PASSWORD="…"
export DMG_NAME="HWTW-local.dmg"
bash packaging/build-macos-dmg.sh
```

## Entitlements

`packaging/macos-entitlements.plist` is tuned for **PyInstaller** + **hardened runtime**. If notarization rejects the build, Apple’s email explains the missing entitlement — adjust the plist in small steps and re-tag.

## Bundle ID

The release build uses **`io.github.ta10101.HWTW`**. If you fork under another GitHub user, consider changing **`--osx-bundle-identifier`** in `.github/workflows/release.yml` and your signing **provisioning** expectations to match your team.
