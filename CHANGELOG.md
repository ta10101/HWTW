# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
