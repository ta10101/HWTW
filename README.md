# HWTW — Holo Wind Tunnel runner (GUI)

Desktop app for setting up a **Holo Edge Node** as a [Holochain Wind Tunnel](https://holo.host/resources/edge-node-wind-tunnel-guide/) runner. It runs the same Docker steps as the official guide and shows host resources, hostname, and Docker output.

**Official PDF:** [EdgeNodeWindTunnelGuide.pdf](https://holo.host/files/EdgeNodeWindTunnelGuide.pdf)

---

## Install guides — pick your system

| I use… | Go to |
| ------ | ----- |
| **Windows 10/11** | [Install guide — Windows](#install-guide--windows) |
| **macOS** (Intel or Apple Silicon) | [Install guide — macOS](#install-guide--macos) |
| **Linux** (Chromebook Linux, Ubuntu, Debian, …) | [Install guide — Linux](#install-guide--linux) |

**Everyone:** Wind Tunnel needs **Docker** running. HWTW only drives Docker — it does not replace Docker.

### Download latest (stable URLs)

These links follow GitHub’s **Latest** release ([open release page](https://github.com/ta10101/HWTW/releases/latest)):

| Asset | Direct download |
| ----- | ---------------- |
| **Windows portable** | [`HWTW.exe`](https://github.com/ta10101/HWTW/releases/latest/download/HWTW.exe) |
| **Windows installer (x64)** | [`HWTW.msi`](https://github.com/ta10101/HWTW/releases/latest/download/HWTW.msi) |
| **SHA-256 checksums (Windows assets)** | [`SHA256SUMS.txt`](https://github.com/ta10101/HWTW/releases/latest/download/SHA256SUMS.txt) |
| **Bundled `requirements.txt`** | [`requirements.txt`](https://github.com/ta10101/HWTW/releases/latest/download/requirements.txt) |

**macOS** filenames vary (**`HWTW-macOS.dmg`** vs **`HWTW-macOS-unsigned.dmg`**, plus **`.app.zip`**, **`.pkg`**, **`SHA256SUMS-macos.txt`**) — use **[Latest → Assets](https://github.com/ta10101/HWTW/releases/latest)** on the release page.

If **Latest** still points at an old version while newer **tags** exist on the repo, the **Release** workflow likely failed — open **[Actions → Release](https://github.com/ta10101/HWTW/actions/workflows/release.yml)**; after fixing CI, use **Run workflow** (pick tag **e.g. `v1.2.8`**) or push a new **`v*`** tag.

**Official downloads:** Use **`ta10101/HWTW`** only. Verify Windows files with **`SHA256SUMS.txt`** and macOS with **`SHA256SUMS-macos.txt`**.

**One-page install only:** **[INSTALL.md](INSTALL.md)** (Windows, macOS, Linux — easy to print or share).

### What we do **not** cover

| Not covered | Notes |
| ----------- | ----- |
| **Apple notarization without a Developer account** | A **signed, stapled** **`HWTW-macOS.dmg`** needs **Apple Developer** credentials as [repository secrets](MACOS_SIGNING.md). Without them, Releases still ship **`HWTW-macOS-unsigned.dmg`** (you may need **Right-click → Open** the first time). |
| **Linux without `apt`** (Fedora, Arch, openSUSE, NixOS, …) | **`install-linux.sh`** / **`fetch-hwtw-linux.sh`** are only for **Debian/Ubuntu-style** systems. On other distros, install **Python 3.10+**, **venv**, **Tk**, **pip**, and Docker yourself, then run **`python3 main.py`**. |
| **Chromebook without Linux** | There is **no** Chrome OS or Android build. **Linux (Crostini)** must be turned on in Settings. |
| **Windows older than 10** | Not a supported target; use Windows **10/11**, another PC, or a VM. |
| **Docker / WSL inside the app** | **Docker** is always a **separate** install. On Windows, **WSL 2** is separate too — HWTW only **starts** or **guides** you; it does not bundle the engine. |
| **Managed / locked-down devices** | Schools and employers often block Docker, Linux, or admin installs — we can’t bypass policy. **MSI** installs are often blocked by **Group Policy / AppLocker** (message like *administrator has set policies that prevent this installation*); use **`HWTW.exe`** on a personal PC or ask IT. |
| **Chromebook + Docker + Wind Tunnel** | Even with Linux enabled, **Docker in Crostini** is often **limited**; the runner uses **privileged** / **host networking** flags that **may not work** on every device. Check Holo’s official guidance for **supported** setups. |
| **macOS + Docker + Wind Tunnel** | Containers run in **Docker Desktop’s Linux VM**. **`--privileged` / `--net=host`** apply inside that VM, not on the Mac host — behavior can differ from bare Linux. Confirm with **Holo’s guide** whether your use case is supported. |
| **Official Holo support** | This repo is **not** from Holo/Holochain. Participation rules, eligibility, and infrastructure are per **official Holo docs**. |

---

## Install guide — Windows

### Who this is for

You use a normal **Windows PC** and want the simplest path: a downloaded **`.exe`**, no Python to install for the GUI itself.

### Steps (do in order)

1. **Download `HWTW.exe` or `HWTW.msi`**  
   Open **[Releases](https://github.com/ta10101/HWTW/releases)** → download **`HWTW.exe`** (portable) **or** **`HWTW.msi`** (64-bit installer: installs under Program Files). You do **not** need Python on Windows for either build.

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

### If the MSI says an administrator blocked installation

That dialog (e.g. Danish: *Systemadministratoren har angivet systemregler, der forhindrer denne installation*) means **Windows policy** on a **managed** PC — often **Group Policy**, **Software Restriction Policies**, or **AppLocker**. The **`HWTW.msi`** from GitHub is **not** signed with a commercial **Authenticode** certificate, which many organizations require for MSI installs. This is **not** a bug in the installer that we can fix from the repo alone.

**What you can try:**

- Prefer the **portable [`HWTW.exe`](https://github.com/ta10101/HWTW/releases/latest/download/HWTW.exe)** — it does **not** use Windows Installer. Put it in a folder you control (e.g. **Desktop** or **Documents**) and run it from there. Some workplaces still block unknown **`.exe`** files; then you need a **personal** machine or an **IT exception**.
- On a PC you fully control, install while signed in as a user with **local administrator** rights and without those restrictions.
- Ask **IT** to allowlist the MSI or install HWTW for you.

**SmartScreen** (“Windows protected your PC”) is separate from policy: use **More info → Run anyway** only if you trust the file from **[official Releases](https://github.com/ta10101/HWTW/releases/latest)**.

**Many windows / PC overwhelmed:** The first launch can take a while (SmartScreen, one-time Docker message). **Click `HWTW.exe` once** and wait — opening it again and again starts **one process per click**. **v1.2.10+** allows only **one** running instance; older builds need a single click and patience.

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

## Install guide — macOS

### Who this is for

**Mac** with **macOS** (Intel or Apple Silicon). Prefer a **`.dmg`** from **[Releases](https://github.com/ta10101/HWTW/releases)** if you do not want to install Python yourself; otherwise use the **install script** or **`python3 main.py`**.

### Steps (recommended — prebuilt app)

1. Download from **[Releases](https://github.com/ta10101/HWTW/releases)** — **`HWTW-macOS*.dmg`** (open and drag **HWTW** to **Applications**), **`HWTW-macOS.app.zip`** (unzip, drag **HWTW.app** to **Applications**), or **`HWTW-macOS.pkg`** (double-click to install into **/Applications**).  
2. If Gatekeeper blocks an **unsigned** build: **Right-click → Open** on the app, or allow it under **System Settings → Privacy & Security**.  
3. Install and **start Docker Desktop** for Wind Tunnel **containers**: **[Docker Mac install](https://docs.docker.com/desktop/setup/install/mac-install/)**. HWTW can run **`brew install --cask docker`** from **Install / fix Docker (Mac)** if [Homebrew](https://brew.sh) is installed.

### Before you start (script / source path)

1. **Python 3.10+** with **Tkinter** (`import tkinter` must work). Easiest fixes if `python3` is missing or has no Tk:  
   - **[python.org macOS installer](https://www.python.org/downloads/macos/)**, or  
   - **Homebrew:** `brew install python@3.12`  
2. **Docker Desktop for Mac** — same as above.

### Steps (script / source)

1. Get the project: **`git clone https://github.com/ta10101/HWTW.git`** or **Code → Download ZIP** and unzip.  
2. In **Terminal**, go to the folder that contains **`main.py`** (e.g. `cd ~/HWTW` or `cd ~/Downloads/HWTW-main`).  
3. Run:

   ```bash
   bash install-macos.sh
   ./run-hwtw-macos.sh
   ```

   This creates **`.venv`**, installs **`requirements.txt`**, and starts the GUI via **`run-hwtw-macos.sh`** next time.

4. Install and **start Docker Desktop**, then use **Easy start** in HWTW like on other platforms.

### Optional: `python3 main.py` only

From the project folder, **`python3 main.py`** also works: the app will use **`.venv`** automatically on macOS when needed (PEP 668 / Homebrew).

### Quick checklist (macOS)

- [ ] **`python3 -c "import tkinter"`** succeeds  
- [ ] **`install-macos.sh`** completed (or you use **`python3 main.py`**)  
- [ ] **Docker Desktop for Mac** running when using Wind Tunnel  

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

| | Windows | macOS | Linux (easy path) |
| -- | -- | -- | -- |
| **App** | **`HWTW.exe`** from Releases, or Python + deps | **`install-macos.sh`** + **`run-hwtw-macos.sh`**, or **`python3 main.py`** | **`run-hwtw-linux.sh`** (after **`install-linux.sh`**) |
| **Python** | Only for source runs (3.10+) | **3.10+** with **Tk** (python.org or Homebrew) | Via **`install-linux.sh`** / `apt` |
| **Docker** | Docker Desktop + WSL 2 (typical) | **Docker Desktop for Mac** | Distro Docker package / engine |
| **RAM / disk** | Holo guide: **≥ 8 GiB RAM**, **≥ 10 GiB** free | Same | Same |

---

## Quick start (developers, any OS)

```bash
git clone https://github.com/ta10101/HWTW.git
cd HWTW
python -m pip install -r requirements.txt
python main.py
```

On **Linux**, prefer **`install-linux.sh`**. On **macOS**, prefer **`install-macos.sh`** (or let **`python3 main.py`** create **`.venv`**). On the **first run**, the app may create local files (e.g. **`.wind_tunnel_gui_setup_done`** — git-ignored).

**Optional — default dark theme before any config exists:** set environment variable **`HWTW_DEFAULT_DARK=1`** (or `true` / `yes`) when launching HWTW. After you use **View → Dark theme**, the choice is stored in **`hwtw_config.json`** and overrides the env default.

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
- **Preflight:** Docker daemon, **WSL 2** (Windows only), RAM/disk vs Holo guide minimums (8 GiB RAM, 10 GiB free disk); disk free space uses home / data volume on **macOS**.
- Saves **hostname**, optional **dark theme**, and log tail in `hwtw_config.json` (next to the app; git-ignored).
- Timestamped command log with **clear** / **save to .txt**; **copy** full `docker run` line; **docker logs** tail for the running runner.
- **Holochain runner status** URL (copy/open) for [wind-tunnel-runner-status.holochain.org](https://wind-tunnel-runner-status.holochain.org/).
- **View → Dark theme** ([sv-ttk](https://github.com/rdbende/Sun-Valley-ttk-theme)); window title shows **HWTW** + version.
- **Easy start** tab: status tiles (Docker / WSL / tunnel / PC), CPU **sparkline**, **progress bars**, **tooltips**, **welcome** dialog, **Help**.

## Release binaries (CI)

Pushing a **version tag** `v*` builds **Windows** (**`HWTW.exe`**, **`HWTW.msi`**, **`requirements.txt`**, **`SHA256SUMS.txt`**) into a **GitHub Release** first, then **macOS** attaches **`.dmg`**, **`.app.zip`**, **`.pkg`**, and **`SHA256SUMS-macos.txt`** (see [MACOS_SIGNING.md](MACOS_SIGNING.md)). **Linux** still uses the install scripts or **`python3 main.py`** from this repo.

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
3. Check **Releases** for **`HWTW.exe`**, **`HWTW.msi`**, **`requirements.txt`**, and macOS **`.dmg`** / **`.app.zip`** / **`.pkg`**.  
4. **Optional (maintainers):** configure **[MACOS_SIGNING.md](MACOS_SIGNING.md)** secrets so the macOS artifact is **signed and notarized** instead of **`HWTW-macOS-unsigned.dmg`**.

### Local PyInstaller build (optional)

```bash
python -m pip install pyinstaller psutil "sv-ttk>=2.6.0"
pyinstaller --onefile --windowed --name HWTW --collect-all sv_ttk --collect-all psutil --hidden-import=psutil main.py
copy requirements.txt dist\
```

## CI

GitHub Actions: `python -m py_compile main.py` and **`pytest`** on **ubuntu-latest**, **windows-latest**, and **macos-latest**; **`bash -n`** on Linux and macOS install scripts, **`packaging/build-macos-dmg.sh`**, and **`packaging/build-macos-zip-pkg.sh`**.

## Security

See [SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

This project is not affiliated with Holo or the Holochain Foundation. Follow the official Holo documentation and support channels for Edge Node and Wind Tunnel participation.
