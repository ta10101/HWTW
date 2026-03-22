# HWTW (Holo Wind Tunnel — Windows)

Desktop GUI for setting up a **Holo Edge Node** as a [Holochain Wind Tunnel](https://holo.host/resources/edge-node-wind-tunnel-guide/) runner. It runs the same Docker commands as the official guide and shows host resources, hostname, and Docker output.

**Official PDF:** [EdgeNodeWindTunnelGuide.pdf](https://holo.host/files/EdgeNodeWindTunnelGuide.pdf)

## Requirements

- **Python** 3.10 or newer (includes Tkinter on most installers).
- **Docker** — the Wind Tunnel runner image is pulled and run with Docker.
- **Windows:** Docker Desktop normally needs **WSL 2**; the app can prompt to run `wsl --install` when that applies.

The upstream guide targets **HolOS/Linux**; on Windows, use Docker Desktop (and WSL 2) or run the stack in a Linux VM.

## Quick start

```bash
git clone https://github.com/ta10101/HWTW.git
cd HWTW
python -m pip install -r requirements.txt
python main.py
```

On the **first run**, the app installs dependencies from `requirements.txt`, may offer **Docker** and **WSL** setup on Windows, and creates a local marker file `.wind_tunnel_gui_setup_done` (ignored by git). If you already ran an older version, run `python -m pip install -r requirements.txt` once to pick up **sv-ttk** (dark theme).

## What it does

- Prep: `docker stop edgenode` / `docker rm edgenode` (optional).
- `docker pull ghcr.io/holochain/wind-tunnel-runner:latest`
- `docker run` with `--hostname`, `--cgroupns=host`, `--net=host`, `--privileged`, `-d`, `--rm` as in the guide.
- Stop runner containers for that image; refresh **filtered** runner `docker ps` and full `docker ps -a`.
- **Preflight:** Docker daemon, WSL 2 (Windows), RAM/disk vs Holo guide minimums (8 GiB RAM, 10 GiB free disk).
- Saves **hostname**, optional **dark theme**, and log tail in `hwtw_config.json` (next to the app; git-ignored).
- Timestamped command log with **clear** / **save to .txt**; **copy** full `docker run` line; **docker logs** tail for the running runner.
- **View → Dark theme** ([sv-ttk](https://github.com/rdbende/Sun-Valley-ttk-theme)); window title shows **HWTW** + version.

## Windows release binary (CI)

Pushing a **version tag** `v*` (e.g. `v1.0.1`) builds **HWTW.exe** with PyInstaller and uploads **`HWTW.exe`** plus **`requirements.txt`** to a GitHub Release (workflow: `.github/workflows/release.yml`). Keep **`requirements.txt`** beside the `.exe` so first-run `pip install` can find it.

## Publishing on GitHub

1. Create a new repository on GitHub (empty, no README if you already have one locally).
2. From this folder:

   ```bash
   git init
   git add .
   git commit -m "Initial commit: Holo Wind Tunnel GUI"
   git branch -M main
   git remote add origin https://github.com/ta10101/HWTW.git
   git push -u origin main
   ```

3. In the repo **Settings → General**, optionally add a **description**, **website** (e.g. https://holo.host), and topics such as `holochain`, `holo`, `docker`, `wind-tunnel`.

## Creating a release

1. Bump **`__version__`** in `main.py` and note changes in **`CHANGELOG.md`**, then commit and push to `main`.
2. Tag and push (starts the **Release** workflow and uploads `HWTW.exe` + `requirements.txt`):

   ```bash
   git tag -a v1.0.1 -m "Release v1.0.1"
   git push origin v1.0.1
   ```

3. On GitHub, open **Releases** — the workflow creates the release and attaches the binaries. Edit the release notes if you want.

### Local PyInstaller build (optional)

```bash
python -m pip install pyinstaller "sv-ttk>=2.6.0"
pyinstaller --onefile --windowed --name HWTW --collect-all sv_ttk main.py
copy requirements.txt dist\
```

Ship **`dist/HWTW.exe`** and **`dist/requirements.txt`** together.

## CI

GitHub Actions runs on push and pull requests: install dependencies and `python -m py_compile main.py` on Ubuntu and Windows.

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

This project is not affiliated with Holo or the Holochain Foundation. Follow the official Holo documentation and support channels for Edge Node and Wind Tunnel participation.
