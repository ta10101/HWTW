# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.5] - 2026-03-23

### Fixed

- **Windows MSI (WiX):** **ICE69** — **`Target="[#filHWTWexe]"`** on the desktop shortcut requires **`cmpDesktopShortcut`** and **`cmpHWTWexe`** in the **same** Feature. Remove nested **`DesktopShortcutFeature`** and add **`ComponentRef Id="cmpDesktopShortcut"`** under **`MainFeature`** (public desktop shortcut is no longer a separate Custom-setup sub-feature).

## [1.3.4] - 2026-03-23

### Fixed

- **Windows MSI (WiX):** Restore **public desktop** shortcut as **`cmpDesktopShortcut`** under **`CommonDesktopFolder`** (with **`CommonDesktopFolder`** under **`TARGETDIR`**). Do not put **`DesktopFolder`** shortcuts in **`cmpHWTWexe`** — that triggers **ICE43** / **ICE57** (per-user shortcut + per-machine **File** **KeyPath**).

## [1.3.3] - 2026-03-23

### Changed

- **Windows MSI (WiX):** Put the desktop **Shortcut** inside **`cmpHWTWexe`** with **`Directory="DesktopFolder"`**; declare **`DesktopFolder`** under **`TARGETDIR`**. Removes **`CommonDesktopFolder`**, **`cmpDesktopShortcut`**, and the optional **Desktop shortcut** sub-feature (shortcut always installs with the app).

## [1.3.2] - 2026-03-23

### Fixed

- **Windows MSI (WiX 3):** Remove Unicode characters (e.g. **→**, **—**) from **`HWTW.wxs`** strings and comments so the default MSI code page **1252** is satisfied — fixes **LGHT0311**.

## [1.3.1] - 2026-03-23

### Fixed

- **Windows MSI (WiX 3):** Declare **`<Directory Id="CommonDesktopFolder" />`** under **`TARGETDIR`** so **`DirectoryRef`** for the desktop shortcut resolves — fixes **LGHT0094** (*unresolved symbol ‘Directory:CommonDesktopFolder’*).

## [1.3.0] - 2026-03-23

### Added

- **Workflow [Set release as Latest](https://github.com/ta10101/HWTW/actions/workflows/set-latest-release.yml):** manual **`workflow_dispatch`** to set **GitHub Latest** when it lags a green **Release** run.

### Changed

- **Windows MSI (WiX):** **`MajorUpgrade`** sets **`AllowSameVersionUpgrades="yes"`** so reinstalling an MSI with the **same** product version is allowed; clearer **downgrade** message references **Settings → Apps** / **Uninstall HWTW**.
- **GitHub Release pipeline:** **`publish-release`** uses REST **PATCH** (**`draft=false`**, **`make_latest=true`**); **immutable** / re-run handling (**`overwrite_files: false`**, prune **draft** for tag); **macOS** job installs **Pillow**, uses absolute **`--icon`**, **`--collect-submodules psutil`**, **`psutil._psosx`**; **Windows** job fetches **HWTW.ico** / **License.rtf** from **`main`** when missing on old tags.
- **Release draft notes:** Download table uses **tag-pinned** `releases/download/<tag>/...` URLs for **Windows + macOS** assets; explains **`/releases/latest/download/...`** after publish.
- **README / INSTALL:** **macOS** direct **`/releases/latest/download/...`** links; troubleshooting for **Latest** vs **Set release as Latest**.

### Fixed

- **Windows (frozen app):** Docker / WSL / runner status polling avoids flashing consoles (**`CREATE_NO_WINDOW`**) and moves heavy probes off the Tk thread (see **1.2.15**).
- **Windows MSI (WiX 3):** **`CommonDesktopFolder`**, **`light -dWixUILicenseRtf`**, **`WixVariable` / `Package`** ordering (see **1.2.16–1.2.19**).

## [1.2.19] - 2026-03-22

### Fixed

- **Windows MSI (WiX 3):** **`DirectoryRef Id="PublicDesktopFolder"`** caused **LGHT0094** (unresolved symbol). Replaced with **`CommonDesktopFolder`**, the standard **all-users desktop** directory (same intent as “public” desktop shortcut).

## [1.2.18] - 2026-03-22

### Fixed

- **Windows MSI (CI):** Drop inline **`WixUILicenseRtf`** from **`.wxs`**; **`light`** now receives **`-dWixUILicenseRtf=<resolved path>`** and **`-b` $PWD** so the license file binds correctly on **GitHub Actions** (avoids link-time **LGHT** / missing-file failures).

## [1.2.17] - 2026-03-22

### Fixed

- **Windows MSI (WiX 3):** **`WixUILicenseRtf`** moved into a **`Fragment`** so **`Package`** is again the **first** child of **`Product`** (WiX requires **`Package`** first; **`WixVariable`** before **`Package`** broke **candle**).

## [1.2.16] - 2026-03-22

### Fixed

- **Windows MSI (CI / WiX 3):** **`WixVariable`** for **`WixUILicenseRtf`** moved under **`Product`** — **candle** no longer fails with **CNDL0005** (*unexpected child element ‘WixVariable’ under ‘Wix’*).

## [1.2.15] - 2026-03-22

### Fixed

- **Windows (windowed / frozen app):** **Docker**, **WSL**, and **Wind Tunnel** status polling no longer opens flashing **CMD** windows (**`subprocess.CREATE_NO_WINDOW`** on helper subprocesses; **`CREATE_NEW_CONSOLE`** flows unchanged for **winget** / **WSL install**).
- **UI responsiveness:** Easy-start dashboard, preflight, and header **Docker** line updates run **`docker` / `wsl` checks off the Tk thread** so the window stays interactive while probes run. Easy dashboard poll interval **2.5s** (was **1.5s**).

## [1.2.14] - 2026-03-22

### Added

- **Uninstall:** **Windows MSI** includes a **Start Menu** shortcut **Uninstall HWTW** (**`msiexec /x [ProductCode]`**). **README** and **[INSTALL.md](INSTALL.md#uninstall)** document removal for **MSI**, portable **`.exe`**, **macOS** (**.app** + optional **`pkgutil --forget`**), and **Linux** (**.desktop** + delete project folder).

## [1.2.13] - 2026-03-22

### Added

- **App icon:** **`packaging/icons/HWTW.ico`** (multi-size from project artwork) for **PyInstaller** (**`--icon`**) on Windows and macOS; **WiX** shortcuts and **ARPPRODUCTICON** (Add/Remove Programs). Source PNG: **`packaging/icons/hwtw_icon_source.png`**.

## [1.2.12] - 2026-03-22

### Added

- **Windows MSI:** **WixUI_FeatureTree** wizard (license + setup type). Nested **Desktop shortcut** feature (public desktop); use **Custom** to disable. **`License.rtf`** in **`packaging/wix/`**.

### Fixed

- **Frozen Windows build:** **`--collect-submodules psutil`** and extra **`psutil._pswindows` / `psutil._psutil_windows`** hidden imports to improve bundling.
- **Frozen app startup:** If **psutil** fails to load (e.g. **Defender** quarantine), show a **warning** and **continue** — Wind Tunnel / Docker still work; resource labels stay “unknown” until fixed.

## [1.2.11] - 2026-03-22

### Added

- **Windows MSI (WiX):** **Start Menu** shortcut (**All users** → **HWTW** → **HWTW**) so installs are easier to find; **`HWTW.exe`** remains at **`C:\Program Files\HWTW\HWTW.exe`**.

## [1.2.10] - 2026-03-22

### Fixed

- **Single instance:** **Windows** (named mutex) and **Linux/macOS** (non-blocking file lock) so only one HWTW process runs. Avoids many windows when SmartScreen or first-run setup is slow and **`HWTW.exe`** is double-clicked repeatedly.

## [1.2.9] - 2026-03-22

### Fixed

- **Release CI:** GitHub’s workflow parser rejects **`secrets` in `if:`** and in **`${{ }}` inside `run:`** (only direct **`env:` / `with:`** assignments like **`${{ secrets.NAME }}`** are valid). Earlier we also hit **`secrets` inside `env:` for a boolean**. macOS signing steps now branch in the shell on **`[ -n "$P12_BASE64" ]`** with **`P12_BASE64: ${{ secrets.MACOS_CERTIFICATE_P12 }}`** on the step. **`workflow_dispatch`** can rebuild an existing tag after pushing this fix.
- **Immutable releases:** If the repo uses **immutable releases**, uploading macOS assets **after** Windows had already **published** the release fails. The workflow now creates a **draft** with Windows files, attaches macOS files to the same **draft**, then a **`publish-release`** job runs **`gh release edit --draft=false --latest`** (still runs if macOS fails, so Windows-only releases publish).

### Changed

- **Releases:** Windows draft step prepends a **download table** to release notes; README / INSTALL document **`/releases/latest/download/...`** links for **`HWTW.exe`**, **`HWTW.msi`**, **`SHA256SUMS.txt`**, and **`requirements.txt`**.

## [1.2.8] - 2026-03-22

### Added

- **macOS release artifacts:** **`HWTW-macOS.app.zip`** ( **`ditto`** zip of **`HWTW.app`** after DMG/sign step) and **`HWTW-macOS.pkg`** (**`pkgbuild`**, installs **`HWTW.app`** under **`/Applications`**).
- **`packaging/build-macos-zip-pkg.sh`**; **`SHA256SUMS-macos.txt`** lists **`.dmg`**, **`.zip`**, and **`.pkg`** (replaces **`SHA256SUMS-macos-dmg.txt`**).

## [1.2.7] - 2026-03-22

### Added

- **Windows MSI:** **`HWTW.msi`** built in Release CI with **WiX Toolset v3** (`packaging/wix/HWTW.wxs`) — x64, per-machine install to Program Files with **`HWTW.exe`** + **`requirements.txt`**. **`SHA256SUMS.txt`** lists **`HWTW.msi`** alongside the exe.

## [1.2.6] - 2026-03-22

### Fixed

- **Release workflow:** **Windows** job creates the **GitHub Release** and uploads **`HWTW.exe`**, **`requirements.txt`**, and **`SHA256SUMS.txt`** immediately; **macOS** runs **after** and **attaches** the **`.dmg`** plus **`SHA256SUMS-macos-dmg.txt`**. If macOS fails, Windows assets are still published (fixes “tag exists but no **HWTW.exe** / not Latest”).
- **macOS PyInstaller:** **`--collect-all psutil`** / **`--hidden-import=psutil`** for parity with Windows.

## [1.2.5] - 2026-03-22

### Fixed

- **Windows release binary:** PyInstaller build now uses **`--collect-all psutil`** and **`--hidden-import=psutil`** so **`psutil`** native modules ship inside **`HWTW.exe`** (fixes “Missing built-in libraries / psutil failed to load” on fresh downloads).
- **`_load_psutil`:** treat **`OSError`** from broken/native load like a missing dependency.
- **Frozen error dialog:** points to current **Releases** URL, warns about old builds and Windows Security blocks.

## [1.2.4] - 2026-03-22

### Added

- **Easy start:** prominent **Wind Tunnel runner** status line (running / not running / need Docker).
- **In-app “What’s new”** once per version after upgrade or first run; text keyed by version (`WHATS_NEW_BY_VERSION` in `main.py`). **`last_seen_version`** stored in `hwtw_config.json`.
- **Optional default dark theme:** if **`dark_theme`** is not in config, **`HWTW_DEFAULT_DARK=1`** (or `true` / `yes`) selects dark UI on launch; **View → Dark theme** still persists preference.
- **Help → HWTW downloads (GitHub Releases)…**
- **Release workflow:** single **publish** job builds **`SHA256SUMS.txt`** (SHA-256 of **`HWTW.exe`**, **`requirements.txt`**, DMG) and uploads one Release with all assets.
- **`tests/test_hostname.py`** + **CI** runs **`pytest`** for hostname validation.

### Changed

- **README / INSTALL / SECURITY:** official downloads only from **GitHub Releases**; verify with **`SHA256SUMS.txt`**.

## [1.2.3] - 2026-03-22

### Security

- **Hostname validation** (DNS-like ASCII) before **Start** / **Copy docker run**; invalid values are removed from **`hwtw_config.json`** on load and not re-saved on exit.
- **`_open_url`:** only opens **`http`/`https`** URLs with a host.
- **`docker stop` / `docker logs`:** only pass container IDs that match expected **hex** id shape from `docker ps` output.
- **[SECURITY.md](SECURITY.md):** application threat model and maintainer note on **macOS signing** secrets.

## [1.2.2] - 2026-03-22

### Changed

- **Runner status URL:** Easy and Expert tabs show a **full example link** to [wind-tunnel-runner-status.holochain.org](https://wind-tunnel-runner-status.holochain.org/) using placeholder **`nomad-client-yourname-01`** so users see the exact URL shape; copy clarifies replacing **yourname** with their own. The live URL field still tracks the hostname they enter.

## [1.2.1] - 2026-03-22

### Added

- **macOS release artifacts:** GitHub Actions **`macos-dmg`** job builds **`HWTW.app`** with PyInstaller and wraps **`HWTW-macOS.dmg`** (signed + notarized when repo **secrets** are set) or **`HWTW-macOS-unsigned.dmg`** otherwise; **`packaging/build-macos-dmg.sh`**, **`packaging/macos-entitlements.plist`**, and **[MACOS_SIGNING.md](MACOS_SIGNING.md)** for maintainers.

### Changed

- **README / INSTALL:** Releases now include a macOS **`.dmg`**; scripts / **`python3 main.py`** remain documented as alternatives.

## [1.2.0] - 2026-03-22

### Added

- **macOS support:** **`install-macos.sh`**, **`run-hwtw-macos.sh`**; bootstrap uses **`.venv`** on **darwin** (PEP 668 / Homebrew); **Docker Desktop** helper via **Homebrew** (`brew install --cask docker`); platform-specific **welcome**, **footer**, **diagnosis**, and **Easy** / **preflight** copy; **`primary_disk_usage()`** for APFS / home volume free space.
- **CI:** **`macos-latest`** matrix job; **`bash -n`** on macOS install scripts.
- **Linux easy install:** `install-linux.sh`, `run-hwtw-linux.sh`, `fetch-hwtw-linux.sh`; README curl/wget one-liners.
- **`INSTALL.md`** — one-page **Windows, macOS, Linux** install.
- **README:** **Install guide — macOS**; install hub table; **“What we do not cover”** updates (no macOS app in Releases; Docker-on-Mac limits).

### Changed

- **README / INSTALL:** install guides, requirements table, **Release binaries** and **CI** sections for three OSes.

### Security

- GitHub Actions: default **`permissions: contents: read`**, **concurrency** to cancel stale CI, **`persist-credentials: false`** on checkout; release job alone gets **`contents: write`**.
- **Dependabot:** grouped **github-actions** updates; pip **open-pull-requests-limit**.
- **`.gitignore`:** `.env`, keys, certs.
- **`SECURITY.md`** (reporting + maintainer checklist); **`.github/CODEOWNERS`**.
- README: link to **Security** policy.

## [1.1.4] - 2026-03-22

### Added

- **Holochain runner status:** readonly field with **full URL** `https://wind-tunnel-runner-status.holochain.org/status?hostname=…` (updates with your node name), plus **Copy URL**, **Open**, and **Help → Holochain runner status page…**.

### Changed

- **Linux `.venv`:** before recreating a broken/missing-deps environment, **remove the existing `.venv` folder** so pip does not layer on a stale tree. A working `.venv` is still reused (fast restart).

## [1.1.3] - 2026-03-22

### Fixed

- **Linux / Chromebook:** always bootstrap via **`.venv`** when running from source (not only when `EXTERNALLY-MANAGED` is detected), so Crostini and similar setups never hit system **`pip`**. If system **`pip` still fails** with PEP 668, **retry** via `.venv`. Clearer **psutil** / **`cd`** hints.

### Changed

- README: Chromebook **`python3-full`**, and **run `main.py` from the project folder** (not `~`).

## [1.1.2] - 2026-03-22

### Added

- **PEP 668 / Chromebook:** on Debian-style “externally managed” Python, the app creates **`.venv`**, runs **`pip install -r requirements.txt`** inside it, then **restarts** with the venv interpreter (no more `externally-managed-environment` on first run).

### Changed

- README: **Chromebook** — simplified to `python3 main.py` after installing **`python3-venv`**; note auto-`.venv` from v1.1.2.

## [1.1.1] - 2025-03-22

### Added

- **Welcome** dialog on first open (skippable with “Don’t show again”); **Help → Welcome tips…** to reopen.
- **Tooltips** on Easy tab status tiles, labels, and CPU chart (hover hints).

## [1.1.0] - 2025-03-22

### Added

- **Easy start** tab for non-technical users: color status tiles (Docker, WSL, Wind Tunnel container, PC RAM/disk), CPU **sparkline**, **progress bars** for CPU/RAM/disk.
- **Help** menu and **“Why isn’t it working?”** with plain-language diagnosis.
- **Frozen `HWTW.exe`**: skips `pip` on first run; bundled deps only; friendly Docker setup message.

## [1.0.2] - 2025-03-22

### Changed

- CI and release workflows use **GitHub-hosted `windows-latest`** again so builds complete without a self-hosted runner.

## [1.0.1] - 2025-03-22

### Added

- Saved hostname / dark theme / log tail in `hwtw_config.json`; version in window title (`HWTW v1.0.1`).
- Preflight row (Docker, WSL 2 on Windows, RAM/disk vs Holo guide minimums).
- Command log timestamps, clear/save log, filtered runner `docker ps`, all-container `docker ps -a`.
- Runner `docker logs` (configurable tail), copy full `docker run` line, privilege/network warning before start.
- Optional dark theme via **View → Dark theme** ([sv-ttk](https://github.com/rdbende/Sun-Valley-ttk-theme)).
- GitHub Actions workflow to build `HWTW.exe` + attach `requirements.txt` on `v*` tags.

## [1.0.0] - 2025-03-22

### Added

- GUI for Holo Edge Node Wind Tunnel runner (`docker pull` / `docker run` per official guide).
- First-run `pip install -r requirements.txt` and optional Docker / WSL setup prompts on Windows.
- Host and resource monitoring via `psutil`, Docker status, and command log.
