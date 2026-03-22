# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Linux easy install:** `install-linux.sh`, `run-hwtw-linux.sh`, `fetch-hwtw-linux.sh`; README curl/wget one-liners.
- **`INSTALL.md`** — one-page Windows + Linux install; linked from README.

### Changed

- **README:** install hub (table), full **Windows** / **Linux** guides (steps, paths A–D, checklists); cross-platform title.
- **README** + **INSTALL.md:** **“What we do not cover”** (macOS, non-apt Linux, Chromebook without Linux, old Windows, Docker/WSL scope, managed devices, Chromebook Docker limits, third-party disclaimer).

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
