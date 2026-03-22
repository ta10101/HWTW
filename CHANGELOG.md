# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- README: **Chromebook / no Git credentials** — ZIP or `wget` archive + note that public `git clone` needs no GitHub login.

### Changed

- README: Chromebook / Debian — **`venv`** for `pip` (PEP 668); explain **404** on `wget` zip (wrong/missing GitHub URL); **copy folder** / Drive zip path.
- README: **Make the GitHub repo public** (step-by-step); Chromebook block uses canonical URL once public; **Publishing on GitHub** defers to that section.

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
