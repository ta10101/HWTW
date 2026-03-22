# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
