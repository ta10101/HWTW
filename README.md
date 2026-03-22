# HWTW — Holo Wind Tunnel runner (GUI)

Desktop app for setting up a **Holo Edge Node** as a [Holochain Wind Tunnel](https://holo.host/resources/edge-node-wind-tunnel-guide/) runner. It runs the same Docker steps as the official guide and shows host resources, hostname, and Docker output.

**Official PDF:** [EdgeNodeWindTunnelGuide.pdf](https://holo.host/files/EdgeNodeWindTunnelGuide.pdf)

---

## Install guides — pick your system

| I use… | Go to |
| ------ | ----- |
| **Windows 10/11** | [Install guide — Windows](#install-guide--windows) |
| **Linux** (Chromebook Linux, Ubuntu, Debian, …) | [Install guide — Linux](#install-guide--linux) |

**Everyone:** Wind Tunnel needs **Docker** running. HWTW only drives Docker — it does not replace Docker.

**One-page install only:** **[INSTALL.md](INSTALL.md)** (same Windows / Linux steps, easy to print or share).

---

## Install guide — Windows

### Who this is for

You use a normal **Windows PC** and want the simplest path: a downloaded **`.exe`**, no Python to install for the GUI itself.

### Steps (do in order)

1. **Download `HWTW.exe`**  
   Open **[Releases](https://github.com/ta10101/HWTW/releases)** → download the latest **`HWTW.exe`**. The release build bundles what the GUI needs; you do **not** need Python on Windows for that file.

2. **Install Docker Desktop** (one time, separate from HWTW)  
   Install from Docker’s site: **[Windows install guide](https://docs.docker.com/desktop/setup/install/windows-install/)**.  
   HWTW cannot bundle Docker (licensing / drivers). The app can open a **winget** helper for you if you use **Install / fix Docker** inside the app.

3. **Install / enable WSL 2** if Docker asks for it  
   Docker Desktop on Windows usually needs **WSL 2**. HWTW can suggest **`wsl --install`** when that applies.

4. **Start Docker Desktop** and wait until it is **fully running** (whale icon steady, no “starting…”).

5. **Run `HWTW.exe`**  
   If Windows shows “Unknown publisher”, choose **More info → Run anyway** (or unblock in file properties) if you trust this release.

6. **In HWTW — “Easy start” tab**  
   - Wait for **green** (or OK) status for **Docker** (and **WSL** if shown).  
   - **Download Wind Tunnel image** (first time can take a while).  
   - Set your **hostname** (see Holo guide, e.g. `nomad-client-you-01`).  
   - **Start Wind Tunnel**.

**If something fails:** use **“Why isn’t it working?”** or **Help** in the menu.

### Quick checklist (Windows)

- [ ] `HWTW.exe` from **Releases**
- [ ] **Docker Desktop** installed
- [ ] **WSL 2** OK if Docker required it
- [ ] Docker **running** before starting Wind Tunnel steps in HWTW

### Optional: Windows — run from Python source (developers)

If you develop or prefer `git clone`:

```text
git clone https://github.com/ta10101/HWTW.git
cd HWTW
python -m pip install -r requirements.txt
python main.py
```

Use **Python 3.10+**. First run may install extra UI pieces (e.g. **sv-ttk**). To refresh deps: `python -m pip install -r requirements.txt`.

---

## Install guide — Linux

### Who this is for

**Chromebook** (Linux enabled), **Ubuntu**, **Debian**, and similar systems that use **`apt`**. Other distros can run from source with their own package manager (Python 3.10+, venv, Tk).

### Before you start

1. **Chromebook:** turn on Linux — **Settings → Advanced → Developers → Linux development environment** (wording may vary). Open the **Linux terminal** when done.  
2. You will need your **Linux password** when the installer runs `sudo apt-get` (normal).  
3. **Docker:** install and start Docker on Linux separately if you want Wind Tunnel **containers**; the scripts below only set up **HWTW** (Python GUI).

---

### Path A — Easiest: download + install in one go (recommended)

1. Open a **terminal**.  
2. Paste **one** of these lines and press Enter:

   **If you have `curl`:**

   ```bash
   bash <(curl -fsSL https://raw.githubusercontent.com/ta10101/HWTW/main/fetch-hwtw-linux.sh)
   ```

   **If you only have `wget`:**

   ```bash
   wget -qO- https://raw.githubusercontent.com/ta10101/HWTW/main/fetch-hwtw-linux.sh | bash
   ```

3. Wait until it finishes. The app is installed under **`~/HWTW-main`** and should **start once** at the end.

**Next time you want HWTW:**

```bash
cd ~/HWTW-main && ./run-hwtw-linux.sh
```

Or look for **HWTW (Wind Tunnel)** in your **Linux apps** list (a `.desktop` file is created during install).

---

### Path B — You already have the project folder (zip or `git clone`)

1. Open a terminal.  
2. Go to the folder that contains **`main.py`** (often **`HWTW-main`** or **`HWTW`**):

   ```bash
   cd ~/HWTW-main
   ```

3. Run the installer, then start the app:

   ```bash
   bash install-linux.sh
   ./run-hwtw-linux.sh
   ```

**What this does:** `install-linux.sh` installs packages with **apt**, creates a **`.venv`**, runs **`pip install -r requirements.txt`**, and adds a launcher entry. **`run-hwtw-linux.sh`** starts HWTW without using system-wide `pip` (avoids **PEP 668** errors on Chromebook/Debian).

---

### Path C — Manual zip (no fetch script)

Use this if you prefer not to run a download script, but still want the easy installer **inside** the folder:

```bash
cd ~
wget -O hwtw.zip https://github.com/ta10101/HWTW/archive/refs/heads/main.zip
unzip -q -o hwtw.zip
cd HWTW-main
bash install-linux.sh
./run-hwtw-linux.sh
```

If **`wget`** returns **404**, the repo is not public at that URL — see [Make the GitHub repo public](#make-the-github-repo-public-maintainers) (or use **Code → Download ZIP** in the browser and move the folder into **Linux files**).

---

### Path D — Offline copy

1. Copy the project folder into **Linux files** (USB, Drive, zip, etc.).  
2. In a terminal:

   ```bash
   cd /path/to/HWTW-main
   bash install-linux.sh
   ./run-hwtw-linux.sh
   ```

---

### Linux notes

- **`git clone`** of a **public** repo usually needs **no** GitHub password. If a network forces login, use **Download ZIP** in the browser instead.  
- **Fork / different URL:** replace **`ta10101/HWTW`** in links with your fork; after unzip, **`cd`** into the folder GitHub created (e.g. **`YourRepo-main`**).  
- You can run **`python3 main.py`** from the project folder: recent HWTW will create **`.venv`** and restart when needed, but **`install-linux.sh` + `run-hwtw-linux.sh`** is the clearest path for beginners.

### Quick checklist (Linux)

- [ ] Linux (Crostini) or apt-based distro available  
- [ ] **Path A, B, C, or D** completed  
- [ ] Start with **`./run-hwtw-linux.sh`** (or **`python3 main.py`** from project folder)  
- [ ] **Docker** installed/running if you use Wind Tunnel containers  

---

## Requirements (summary)

| | Windows | Linux (easy path) |
| -- | -- | -- |
| **App** | `HWTW.exe` from Releases, or Python + `requirements.txt` | Scripts create **`.venv`**; use **`run-hwtw-linux.sh`** |
| **Python** | Only for source runs (3.10+) | Installed via **`install-linux.sh`** / `apt` |
| **Docker** | Docker Desktop + WSL 2 (typical) | Your distro’s Docker package / engine |
| **RAM / disk** | Holo guide suggests **≥ 8 GiB RAM**, **≥ 10 GiB** free disk | Same |

---

## Quick start (developers, any OS)

```bash
git clone https://github.com/ta10101/HWTW.git
cd HWTW
python -m pip install -r requirements.txt
python main.py
```

On **Linux**, prefer **`install-linux.sh`** unless you know your environment. On the **first run**, the app may create local files (e.g. **`.wind_tunnel_gui_setup_done`** — git-ignored).

---

## Make the GitHub repo public (maintainers)

The links in this README use **`https://github.com/ta10101/HWTW`**. A **404** from **`wget`** or the browser means the repo is missing, private, or not pushed.

1. [Create a repository](https://github.com/new) named **`HWTW`**, **Public**, without adding README/license on GitHub (this repo already has them).  
2. Push **`main`**: `git push -u origin main`  
3. Confirm in an **incognito** window: [https://github.com/ta10101/HWTW](https://github.com/ta10101/HWTW)  
4. If it was private: **Settings → General → Danger zone → Change visibility → Public**  
5. Set remote if needed: `git remote set-url origin https://github.com/ta10101/HWTW.git` (change **`ta10101`** if the owner differs).

---

## What it does

- Prep: `docker stop edgenode` / `docker rm edgenode` (optional).
- `docker pull ghcr.io/holochain/wind-tunnel-runner:latest`
- `docker run` with `--hostname`, `--cgroupns=host`, `--net=host`, `--privileged`, `-d`, `--rm` as in the guide.
- Stop runner containers for that image; refresh **filtered** runner `docker ps` and full `docker ps -a`.
- **Preflight:** Docker daemon, WSL 2 (Windows), RAM/disk vs Holo guide minimums (8 GiB RAM, 10 GiB free disk).
- Saves **hostname**, optional **dark theme**, and log tail in `hwtw_config.json` (next to the app; git-ignored).
- Timestamped command log with **clear** / **save to .txt**; **copy** full `docker run` line; **docker logs** tail for the running runner.
- **Holochain runner status** URL (copy/open) for [wind-tunnel-runner-status.holochain.org](https://wind-tunnel-runner-status.holochain.org/).
- **View → Dark theme** ([sv-ttk](https://github.com/rdbende/Sun-Valley-ttk-theme)); window title shows **HWTW** + version.
- **Easy start** tab: status tiles (Docker / WSL / tunnel / PC), CPU **sparkline**, **progress bars**, **tooltips**, **welcome** dialog, **Help**.

## Windows release binary (CI)

Pushing a **version tag** `v*` builds **`HWTW.exe`** with PyInstaller and uploads **`HWTW.exe`** + **`requirements.txt`** to a GitHub Release.

## Publishing on GitHub

First-time setup: create empty **public** **`HWTW`** repo, then:

```bash
git init
git add .
git commit -m "Initial commit: Holo Wind Tunnel GUI"
git branch -M main
git remote add origin https://github.com/ta10101/HWTW.git
git push -u origin main
```

## Creating a release

1. Bump **`__version__`** in `main.py` and **`CHANGELOG.md`**, commit and push.  
2. `git tag -a v1.1.1 -m "Release v1.1.1"` && `git push origin v1.1.1`  
3. Check **Releases** for the workflow artifacts.

### Local PyInstaller build (optional)

```bash
python -m pip install pyinstaller "sv-ttk>=2.6.0"
pyinstaller --onefile --windowed --name HWTW --collect-all sv_ttk main.py
copy requirements.txt dist\
```

## CI

GitHub Actions: `python -m py_compile main.py` on **ubuntu-latest** and **windows-latest**; Linux install scripts checked with **`bash -n`**.

## Security

See [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

This project is not affiliated with Holo or the Holochain Foundation. Follow the official Holo documentation and support channels for Edge Node and Wind Tunnel participation.
