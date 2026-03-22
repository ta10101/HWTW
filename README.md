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

On the **first run**, the app installs dependencies from `requirements.txt`, may offer **Docker** and **WSL** setup on Windows, and creates a local marker file `.wind_tunnel_gui_setup_done` (ignored by git).

## What it does

- Prep: `docker stop edgenode` / `docker rm edgenode` (optional).
- `docker pull ghcr.io/holochain/wind-tunnel-runner:latest`
- `docker run` with `--hostname`, `--cgroupns=host`, `--net=host`, `--privileged`, `-d`, `--rm` as in the guide.
- Stop runner containers for that image; refresh `docker ps`.
- Status: PC hostname, CPU/RAM/disk (`psutil`), Docker availability, scrollable logs.

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

1. Update **version references** if you add them (e.g. in `CHANGELOG.md`).
2. Commit and push:

   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin main --tags
   ```

3. On GitHub: **Releases → Create a new release**, choose tag `v1.0.0`, title `v1.0.0`, paste notes from `CHANGELOG.md`.
4. **Source archives** (zip/tar.gz) are generated automatically. Optionally attach a **Windows executable** (see below).

### Optional: one-file executable (Windows)

Requires [PyInstaller](https://pyinstaller.org/) and a full Python environment on the build machine:

```bash
python -m pip install pyinstaller
pyinstaller --onefile --windowed --name holo-wind-tunnel-gui main.py
```

Copy `requirements.txt` next to the built `.exe` if you rely on first-run `pip install` from the frozen app layout. Test the binary on a clean machine before attaching it to a release.

## CI

GitHub Actions runs on push and pull requests: install dependencies and `python -m py_compile main.py` on Ubuntu and Windows.

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

This project is not affiliated with Holo or the Holochain Foundation. Follow the official Holo documentation and support channels for Edge Node and Wind Tunnel participation.
