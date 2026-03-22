# HWTW (Holo Wind Tunnel — Windows)

Desktop GUI for setting up a **Holo Edge Node** as a [Holochain Wind Tunnel](https://holo.host/resources/edge-node-wind-tunnel-guide/) runner. It runs the same Docker commands as the official guide and shows host resources, hostname, and Docker output.

**Official PDF:** [EdgeNodeWindTunnelGuide.pdf](https://holo.host/files/EdgeNodeWindTunnelGuide.pdf)

## For non-technical users (Windows)

1. **Download `HWTW.exe`** from [Releases](https://github.com/ta10101/HWTW/releases) (no Python needed).
2. **Install Docker Desktop once** from [Docker](https://docs.docker.com/desktop/setup/install/windows-install/) — this is separate from HWTW; Microsoft licensing and drivers mean it cannot be fully hidden inside our `.exe`. The app can **start the install helper** (winget) for you.
3. **Start Docker Desktop** and wait until it is running.
4. Open **HWTW** → stay on **“Easy start”**: green boxes = good, bars show CPU/RAM/disk, then **Download Wind Tunnel image** → **Start Wind Tunnel**.
5. If something fails, click **“Why isn’t it working?”** or use **Help** in the menu.

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

### Make the GitHub repo **public** (one-time, for easy Chromebook / `wget`)

The links in this README use **`https://github.com/ta10101/HWTW`**. A **404** in the browser or from `wget` means the repo is missing, still private, or not pushed yet.

1. Sign in at [github.com/new](https://github.com/new).
2. **Repository name:** `HWTW` (matches `git clone …/HWTW.git` and the zip folder name `HWTW-main`).
3. Set visibility to **Public**.
4. **Do not** add a README, `.gitignore`, or license on GitHub (this project already has them).
5. On your PC, in this project folder, push `main` (use **HTTPS** or **SSH**; GitHub will prompt for login or a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) if needed):

   ```bash
   git remote -v
   git push -u origin main
   ```

   If `origin` is wrong, set it once:  
   `git remote set-url origin https://github.com/ta10101/HWTW.git`  
   (change `ta10101` to your GitHub username if the repo lives under another account.)

6. Confirm: open [https://github.com/ta10101/HWTW](https://github.com/ta10101/HWTW) in a **private/incognito** window — you should see the files without signing in.
7. If the repo already existed but was **private**: **Settings → General → Danger Zone → Change repository visibility → Public**.

After that, **Releases**, **Download ZIP**, and Chromebook `wget` below all work without a GitHub password for **read-only** access.

### Chromebook / Debian Linux (no Git password)

**`pip install` into system Python is blocked** on Chromebook Linux (PEP 668). **HWTW v1.1.3+** always uses a project **`.venv`** on Linux, installs dependencies there, and restarts itself — run **`python3 main.py`** from the folder that contains `main.py` (e.g. `cd ~/HWTW-main` or `cd ~/HWTW`). Install **`python3-venv`** (and **`python3-full`** if `venv` errors).

**When the repo is public**, copy-paste:

```bash
cd ~
wget -O hwtw.zip https://github.com/ta10101/HWTW/archive/refs/heads/main.zip
unzip -q -o hwtw.zip
cd HWTW-main
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-full python3-tk
python3 main.py
```

**Important:** run `python3 main.py` **inside** the project directory (`cd` into `HWTW-main` or `HWTW` first). Running it from `~` causes `can't open file '.../main.py'`.

If **`venv` fails**, run `sudo apt install python3-venv python3-full`. Manual install: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && .venv/bin/python main.py`.

If `wget` still says **404**, the project is not public at that URL yet — follow **Make the GitHub repo public** above, or temporarily use **Code → Download ZIP** in the browser once the repo is visible.

**Fork or different repo name?** Replace `ta10101/HWTW` in the `wget` URL and `cd` into the folder GitHub creates (`YourRepo-main`). **`git clone`** of a public repo does not need a GitHub login unless a school/proxy forces one — then use ZIP from the browser.

**Offline / no GitHub:** zip the project on another machine, copy into **Linux files**, `unzip`, `cd` into the folder, then the same `sudo apt install …` and `python3 main.py` as above (skip `wget`).

## What it does

- Prep: `docker stop edgenode` / `docker rm edgenode` (optional).
- `docker pull ghcr.io/holochain/wind-tunnel-runner:latest`
- `docker run` with `--hostname`, `--cgroupns=host`, `--net=host`, `--privileged`, `-d`, `--rm` as in the guide.
- Stop runner containers for that image; refresh **filtered** runner `docker ps` and full `docker ps -a`.
- **Preflight:** Docker daemon, WSL 2 (Windows), RAM/disk vs Holo guide minimums (8 GiB RAM, 10 GiB free disk).
- Saves **hostname**, optional **dark theme**, and log tail in `hwtw_config.json` (next to the app; git-ignored).
- Timestamped command log with **clear** / **save to .txt**; **copy** full `docker run` line; **docker logs** tail for the running runner.
- **View → Dark theme** ([sv-ttk](https://github.com/rdbende/Sun-Valley-ttk-theme)); window title shows **HWTW** + version.
- **Easy start** tab: large status tiles (Docker / WSL / tunnel / PC), **CPU sparkline** and **progress bars**, **hover tooltips**, first-run **welcome** dialog, plain-language **Help** entries.

## Windows release binary (CI)

Pushing a **version tag** `v*` (e.g. `v1.1.1`) builds **HWTW.exe** with PyInstaller (bundles Python, **psutil**, **sv-ttk**) and uploads **`HWTW.exe`** plus **`requirements.txt`** to a GitHub Release. **End users only need the `.exe`** for the GUI; **`requirements.txt`** is for developers running from source.

## Publishing on GitHub

First-time setup matches **Make the GitHub repo public** above (create empty **public** `HWTW` repo, then `git push -u origin main`). If you are starting from a folder without git:

```bash
git init
git add .
git commit -m "Initial commit: Holo Wind Tunnel GUI"
git branch -M main
git remote add origin https://github.com/ta10101/HWTW.git
git push -u origin main
```

In the repo **Settings → General**, optionally add a **description**, **website** (e.g. https://holo.host), and topics such as `holochain`, `holo`, `docker`, `wind-tunnel`.

## Creating a release

1. Bump **`__version__`** in `main.py` and note changes in **`CHANGELOG.md`**, then commit and push to `main`.
2. Tag and push (starts the **Release** workflow and uploads `HWTW.exe` + `requirements.txt`):

   ```bash
   git tag -a v1.1.1 -m "Release v1.1.1"
   git push origin v1.1.1
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

GitHub Actions runs on push and pull requests: install dependencies and `python -m py_compile main.py` on **ubuntu-latest** and **windows-latest** (no self-hosted runner required).

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

This project is not affiliated with Holo or the Holochain Foundation. Follow the official Holo documentation and support channels for Edge Node and Wind Tunnel participation.
