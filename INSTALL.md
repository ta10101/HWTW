# Installing HWTW (Holo Wind Tunnel GUI)

HWTW helps you run the **Holochain Wind Tunnel** runner with Docker.  
**Official guide (PDF):** [EdgeNodeWindTunnelGuide.pdf](https://holo.host/files/EdgeNodeWindTunnelGuide.pdf)

**Important:** Wind Tunnel needs **Docker** running. HWTW only runs Docker commands for you — install Docker separately.

---

## Windows 10 / 11

### Recommended (prebuilt app)

| Step | What to do |
| ---- | ---------- |
| 1 | Download **`HWTW.exe`** from **[GitHub Releases](https://github.com/ta10101/HWTW/releases)**. You do **not** need Python for this build. |
| 2 | Install **[Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)** (one time). Use **WSL 2** if Docker asks for it. |
| 3 | **Start Docker Desktop** and wait until it is fully running. |
| 4 | Run **`HWTW.exe`**. If SmartScreen warns, use **More info → Run anyway** if you trust the release. |
| 5 | In the app, open **Easy start** → fix any red status → **Download Wind Tunnel image** → set **hostname** (e.g. `nomad-client-you-01`) → **Start Wind Tunnel**. |

**Stuck?** Use **Why isn’t it working?** or **Help** in the app menu.

**Checklist**

- [ ] `HWTW.exe` from Releases  
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

## Requirements (short)

| | Windows | Linux (scripts) |
| -- | -- | -- |
| App | `HWTW.exe` or Python + deps | `.venv` + **`run-hwtw-linux.sh`** |
| Python | 3.10+ only for source runs | Installed via **`install-linux.sh`** |
| Docker | Docker Desktop (+ WSL 2 typical) | Your distro’s Docker |

Holo suggests about **8 GiB RAM** and **10 GiB** free disk for Wind Tunnel workloads.

---

## More help

- Full detail, features, and maintainer notes: **[README.md](README.md)**  
- Security reporting: **[SECURITY.md](SECURITY.md)**  
- Repo URL in this file assumes **`github.com/ta10101/HWTW`** — change it if you use a fork.
