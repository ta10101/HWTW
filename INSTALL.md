# Installing HWTW (Holo Wind Tunnel GUI)

## Get the latest build first

Use **[Latest](https://github.com/ta10101/HWTW/releases/latest)** (newest published release). **[All releases](https://github.com/ta10101/HWTW/releases)** lists older versions (**newest at the top**).

**Windows (direct links):** [`HWTW.exe`](https://github.com/ta10101/HWTW/releases/latest/download/HWTW.exe) · [`HWTW.msi`](https://github.com/ta10101/HWTW/releases/latest/download/HWTW.msi) · [`SHA256SUMS.txt`](https://github.com/ta10101/HWTW/releases/latest/download/SHA256SUMS.txt) · [`requirements.txt`](https://github.com/ta10101/HWTW/releases/latest/download/requirements.txt)

**macOS:** **[Latest → Assets](https://github.com/ta10101/HWTW/releases/latest)** — **`.dmg`**, **`.app.zip`**, **`.pkg`**, **`SHA256SUMS-macos.txt`**.

---

HWTW helps you run the **Holochain Wind Tunnel** runner with Docker.  
**Official guide (PDF):** [EdgeNodeWindTunnelGuide.pdf](https://holo.host/files/EdgeNodeWindTunnelGuide.pdf)

**Important:** Wind Tunnel needs **Docker** running. HWTW only runs Docker commands for you — install Docker separately.

**Official downloads:** Use **`ta10101/HWTW`** only — preferably **[Latest](https://github.com/ta10101/HWTW/releases/latest)**.

### Not covered by this guide

- **Linux without `apt`** (Fedora, Arch, …) — install Python 3.10+, venv, Tk, Docker yourself; then `python3 main.py`.  
- **Chromebook without Linux (Crostini)** — enable **Linux** in Settings first.  
- **Windows before 10** — unsupported.  
- **Apple notarization without a paid Developer account** — unsigned **`HWTW-macOS-unsigned.dmg`** may need **Right-click → Open**; see [MACOS_SIGNING.md](MACOS_SIGNING.md) for signed builds.  
- **Docker / WSL** — never bundled; install separately.  
- **Strict school/work PCs** — may block Docker or Linux.  
- **Chromebook / macOS + Docker + Wind Tunnel** — privileged / host-network containers may **not** match bare Linux; see **Holo’s official guide**.  
- **Holo endorsement** — third-party tool; see [README disclaimer](README.md#disclaimer).

---

## Windows 10 / 11

### Recommended (prebuilt app)

| Step | What to do |
| ---- | ---------- |
| 1 | Download **`HWTW.exe`** (portable) or **`HWTW.msi`** (64-bit installer) from **[Latest](https://github.com/ta10101/HWTW/releases/latest)** (see top of this page). You do **not** need Python for either build. **MSI (**v1.2.12+**):** wizard with license → pick **Custom** to opt out of the **Desktop shortcut** → finish (**v1.2.13+** app icon; **v1.2.14+** adds **Start → HWTW → Uninstall HWTW**). Setup does not auto-launch — open **HWTW** from Start menu, desktop, or **`C:\Program Files\HWTW\HWTW.exe`**. |
| 2 | Install **[Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)** (one time). Use **WSL 2** if Docker asks for it. |
| 3 | **Start Docker Desktop** and wait until it is fully running. |
| 4 | Run **`HWTW.exe`** (or the shortcut from **`HWTW.msi`** under Program Files). If SmartScreen warns, use **More info → Run anyway** if you trust the release. |
| 5 | In the app, open **Easy start** → fix any red status → **Download Wind Tunnel image** → set **hostname** (e.g. `nomad-client-you-01`) → **Start Wind Tunnel**. |

**MSI blocked by administrator / policy:** If Windows says the **system administrator** has set rules that **prevent this installation** (often on work or school PCs), that is **Group Policy / AppLocker** — not something HWTW can override. Our MSI is **not** signed with a corporate-style certificate. Use the portable **[`HWTW.exe`](https://github.com/ta10101/HWTW/releases/latest/download/HWTW.exe)** from the same release instead, or use a **personal** PC, or ask **IT** for an exception.

**Stuck?** Use **Why isn’t it working?** or **Help** in the app menu.

**Checklist**

- [ ] `HWTW.exe` or `HWTW.msi` from **[Latest](https://github.com/ta10101/HWTW/releases/latest)**  
- [ ] Docker Desktop installed and **running**  
- [ ] WSL 2 OK if Docker needed it  

### Optional: run from source (developers)

```bash
git clone https://github.com/ta10101/HWTW.git
cd HWTW
python -m pip install -r requirements.txt
python main.py
```

Use **Python 3.10+**.

---

## macOS (Intel or Apple Silicon)

### Recommended (prebuilt app)

| Step | What to do |
| ---- | ---------- |
| 1 | Download from **[Latest → Assets](https://github.com/ta10101/HWTW/releases/latest)** — **`.dmg`**, **`HWTW-macOS.app.zip`**, or **`HWTW-macOS.pkg`**. |
| 2 | **DMG:** drag **HWTW** to **Applications**. **Zip:** unzip, drag **HWTW.app** to **Applications**. **Pkg:** run the installer (installs to **/Applications**). |
| 3 | If macOS blocks an unsigned build: **Right-click → Open**, or **System Settings → Privacy & Security**. |
| 4 | Install **[Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/)** and keep it running for Wind Tunnel. |

### Optional: Terminal + Python (developers)

**Before you start:** **Python 3.10+** with **tkinter** ([python.org macOS](https://www.python.org/downloads/macos/) or `brew install python@3.12`); test `python3 -c "import tkinter"`. **Docker Desktop** as above.

```bash
git clone https://github.com/ta10101/HWTW.git
cd HWTW
bash install-macos.sh
./run-hwtw-macos.sh
```

**Next launches:** `cd` to the same folder, then `./run-hwtw-macos.sh`.

**Or:** `python3 main.py` (the app will manage **`.venv`** on macOS when needed).

**Checklist**

- [ ] DMG / pkg / zip from **[Latest](https://github.com/ta10101/HWTW/releases/latest)** **or** `import tkinter` works for script/source path  
- [ ] **`install-macos.sh`** done if not using the DMG (or you use **`python3 main.py`**)  
- [ ] Docker Desktop **running** for Wind Tunnel  

**Install / fix Docker** in the app can run **`brew install --cask docker`** if Homebrew is installed.

---

## Linux (Chromebook Linux, Ubuntu, Debian, …)

Uses **`apt`**. Turn **Linux** on first (Chromebook: **Settings → Developers → Linux**). You may be asked for your **Linux password** during install (normal).

Install **Docker** yourself if you want Wind Tunnel **containers**; the steps below only install the **HWTW** app.

### Path A — One command (easiest)

Paste **one** line in a terminal:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/ta10101/HWTW/main/fetch-hwtw-linux.sh)
```

No `curl`? Use:

```bash
wget -qO- https://raw.githubusercontent.com/ta10101/HWTW/main/fetch-hwtw-linux.sh | bash
```

This creates **`~/HWTW-main`** and starts HWTW once. **Later:**

```bash
cd ~/HWTW-main && ./run-hwtw-linux.sh
```

(or launch **HWTW (Wind Tunnel)** from the Linux app list).

### Path B — You already have the folder (`git clone` or zip)

```bash
cd ~/HWTW-main    # or the folder that contains main.py
bash install-linux.sh
./run-hwtw-linux.sh
```

### Path C — Download zip yourself, then install

```bash
cd ~
wget -O hwtw.zip https://github.com/ta10101/HWTW/archive/refs/heads/main.zip
unzip -q -o hwtw.zip
cd HWTW-main
bash install-linux.sh
./run-hwtw-linux.sh
```

If **`wget`** shows **404**, the GitHub repo may be private — use **Code → Download ZIP** in the browser instead, move the folder into **Linux files**, then use **Path B**.

### Path D — Offline

Copy the project folder into Linux, then:

```bash
cd /path/to/HWTW-main
bash install-linux.sh
./run-hwtw-linux.sh
```

**Checklist**

- [ ] Linux terminal works; **`install-linux.sh`** finished without errors  
- [ ] Start with **`./run-hwtw-linux.sh`** (or **`python3 main.py`** from the project folder)  
- [ ] Docker running if you use Wind Tunnel in Docker  

---

## Uninstall

### Windows — MSI install

Use any of these (they all run the same **Windows Installer** removal):

- **Start** → **All apps** → **HWTW** → **Uninstall HWTW** (shortcut added by the MSI from **v1.2.14**).
- **Settings** → **Apps** → **Installed apps** → **HWTW (Holo Wind Tunnel GUI)** → **⋯** → **Uninstall**.
- **Control Panel** → **Programs and Features** → **HWTW (Holo Wind Tunnel GUI)** → **Uninstall**.

You may need **administrator** approval (per-machine install). This removes **`C:\Program Files\HWTW\`**, Start Menu entries, and the public **desktop** shortcut if you installed it. It does **not** remove **Docker Desktop**.

### Windows — portable `HWTW.exe`

1. Quit **HWTW** (check the system tray / Task Manager if needed).
2. Delete **`HWTW.exe`** and, if present beside it, **`requirements.txt`**.
3. Optional: delete **`hwtw_config.json`** and **`.wind_tunnel_gui_setup_done`** in the **same folder** if you want to remove saved hostname / theme (the app stores them next to the `.exe` when you run portable).

### macOS — `.app` (from **DMG**, **`.app.zip`**, or **`.pkg`**)

1. Quit **HWTW**.
2. Open **Finder** → **Applications** → drag **`HWTW.app`** to **Trash** (then **Empty Trash** if you want it gone from disk).

**Optional** (only if you installed with **`HWTW-macOS.pkg`** and want to clear the installer receipt after deleting the app):

```bash
sudo pkgutil --forget io.github.ta10101.hwtw.pkg
```

That does **not** delete the `.app` by itself — remove **`HWTW.app`** first.

### Linux — **`install-linux.sh`** / **`fetch-hwtw-linux.sh`**

1. Quit **HWTW**.
2. Remove the launcher entry (if you ran **`install-linux.sh`**):

   ```bash
   rm -f "${XDG_DATA_HOME:-$HOME/.local/share}/applications/hwtw.desktop"
   ```

   Log out and back in (or restart the session) if the app still appears in the menu.
3. Delete the project folder (e.g. **`~/HWTW-main`** or wherever **`main.py`** lives). That removes **`.venv`** and all app files.

**Docker** is separate — uninstall only HWTW above; remove Docker via your distro or Docker’s docs if you want that gone too.

---

## Requirements (short)

| | Windows | macOS | Linux (scripts) |
| -- | -- | -- | -- |
| App | `HWTW.exe` or Python + deps | **`run-hwtw-macos.sh`** or **`python3 main.py`** | **`run-hwtw-linux.sh`** |
| Python | 3.10+ only for source | 3.10+ with **Tk** | Via **`install-linux.sh`** |
| Docker | Docker Desktop + WSL 2 (typical) | Docker Desktop for Mac | Your distro |

Holo suggests about **8 GiB RAM** and **10 GiB** free disk for Wind Tunnel workloads.

---

## More help

- Full detail, features, and maintainer notes: **[README.md](README.md)**  
- Security reporting: **[SECURITY.md](SECURITY.md)**  
- Repo URL in this file assumes **`github.com/ta10101/HWTW`** — change it if you use a fork.
