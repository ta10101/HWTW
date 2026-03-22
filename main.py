"""
Holo Edge Node — Wind Tunnel Runner GUI (HWTW)
Implements steps from: https://holo.host/files/EdgeNodeWindTunnelGuide.pdf
"""

from __future__ import annotations

import importlib
import json
import os
import shlex
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

psutil = None  # set in bootstrap_requirements()

__version__ = "1.0.1"
APP_SHORT = "HWTW"

IMAGE = "ghcr.io/holochain/wind-tunnel-runner:latest"
GUIDE_URL = "https://holo.host/files/EdgeNodeWindTunnelGuide.pdf"
GUIDE_HTML = "https://holo.host/resources/edge-node-wind-tunnel-guide/"
DOCKER_WIN_INSTALL_URL = "https://docs.docker.com/desktop/setup/install/windows-install/"
WSL_LEARN_URL = "https://learn.microsoft.com/en-us/windows/wsl/install"
MARKER = ".wind_tunnel_gui_setup_done"
CONFIG_NAME = "hwtw_config.json"

# Holo Wind Tunnel guide minimums
MIN_RAM_BYTES = 8 * 1024**3
MIN_DISK_FREE_BYTES = 10 * 1024**3
DEFAULT_LOG_TAIL = 200


def app_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def config_path() -> str:
    return os.path.join(app_dir(), CONFIG_NAME)


def load_config() -> dict:
    try:
        with open(config_path(), encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError, TypeError):
        return {}


def save_config(**kwargs) -> None:
    cfg = load_config()
    cfg.update({k: v for k, v in kwargs.items() if v is not None})
    try:
        with open(config_path(), "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except OSError:
        pass


def requirements_path() -> str:
    return os.path.join(app_dir(), "requirements.txt")


def setup_marker_path() -> str:
    return os.path.join(app_dir(), MARKER)


def run_cmd(
    args: list[str],
    *,
    timeout: int | None = 120,
    **kwargs,
) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            **kwargs,
        )
        return p.returncode, p.stdout or "", p.stderr or ""
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return -1, "", "Executable not found"
    except Exception as e:
        return -1, "", str(e)


def _which(exe: str) -> str | None:
    from shutil import which

    return which(exe)


def docker_version_line() -> str | None:
    code, out, err = run_cmd(["docker", "version", "--format", "{{.Server.Version}}"], timeout=20)
    if code == 0 and (out or "").strip():
        return (out or "").strip()
    code2, out2, err2 = run_cmd(["docker", "version"], timeout=20)
    if code2 != 0:
        return None
    for line in (out2 + err2).splitlines():
        if "Version:" in line and "Server" not in line:
            parts = line.split("Version:", 1)
            if len(parts) > 1:
                return parts[1].strip()
    return "unknown"


def docker_cli_ok() -> bool:
    code, _, _ = run_cmd(["docker", "info"], timeout=25)
    if code == 0:
        return True
    code2, _, _ = run_cmd(["docker", "version"], timeout=15)
    return code2 == 0


def _load_psutil():
    global psutil
    importlib.invalidate_caches()
    try:
        psutil = importlib.import_module("psutil")
    except ImportError:
        psutil = None  # type: ignore


def bootstrap_requirements(parent: tk.Misc | None, *, force_install: bool = False) -> bool:
    global psutil
    if not force_install:
        try:
            psutil = importlib.import_module("psutil")
            return True
        except ImportError:
            pass

    req = requirements_path()
    if not os.path.isfile(req):
        messagebox.showerror(
            "Missing requirements.txt",
            f"Could not find:\n{req}\n\nCopy requirements.txt next to the app and try again.",
            parent=parent,
        )
        _load_psutil()
        return psutil is not None

    splash = None
    if parent is not None:
        splash = tk.Toplevel(parent)
        splash.title("Setup")
        splash.resizable(False, False)
        ttk.Label(
            splash,
            text="Installing Python dependencies (first run)…\nThis may take a minute.",
            padding=20,
        ).pack()
        splash.update()

    done: list[bool] = [False]
    result: list[int] = [-1]
    pip_out: list[str] = [""]

    def work() -> None:
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    "-r",
                    req,
                ],
                capture_output=True,
                text=True,
                timeout=600,
            )
            result[0] = proc.returncode
            pip_out[0] = (proc.stdout or "") + (proc.stderr or "")
        except Exception as e:
            result[0] = -1
            pip_out[0] = str(e)
        done[0] = True

    t = threading.Thread(target=work, daemon=True)
    t.start()
    while not done[0]:
        if splash:
            try:
                splash.update()
            except tk.TclError:
                break
        time.sleep(0.05)
    t.join(timeout=1.0)

    if splash:
        try:
            splash.destroy()
        except tk.TclError:
            pass

    if result[0] != 0:
        messagebox.showerror(
            "Dependency install failed",
            "pip could not install packages from requirements.txt.\n\n"
            + (pip_out[0][:1500] if pip_out[0] else "(no output)"),
            parent=parent,
        )

    _load_psutil()
    if psutil is None:
        messagebox.showwarning(
            "psutil missing",
            "CPU/RAM/disk panel will be limited until psutil installs correctly.\n"
            "Try manually:\n"
            f'  "{sys.executable}" -m pip install -r "{req}"',
            parent=parent,
        )
        return False
    return True


def _open_url(url: str) -> None:
    import webbrowser

    webbrowser.open(url)


def _windows_new_console_flags() -> int:
    if sys.platform == "win32" and hasattr(subprocess, "CREATE_NEW_CONSOLE"):
        return subprocess.CREATE_NEW_CONSOLE  # type: ignore[attr-defined]
    return 0


def wsl2_environment_ready() -> bool:
    if sys.platform != "win32":
        return True
    if _which("wsl") is None:
        return False
    code, out, err = run_cmd(["wsl", "--status"], timeout=25)
    blob = out + err
    if code == 0 and "Default Version: 2" in blob:
        return True
    code2, out2, err2 = run_cmd(["wsl", "-l", "-v"], timeout=30)
    full = out2 + err2
    if code2 != 0:
        return False
    low = full.lower()
    if "no installed distributions" in low or "there are no installed distributions" in low:
        return False
    saw_header = False
    for line in full.splitlines():
        raw = line.strip().strip("\x00").strip()
        if not raw:
            continue
        ul = raw.upper()
        if "VERSION" in ul and "STATE" in ul:
            saw_header = True
            continue
        if not saw_header:
            continue
        toks = raw.replace("*", " ").split()
        if toks and toks[-1] == "2":
            return True
    return False


def _docker_info_text() -> str:
    _, o, e = run_cmd(["docker", "info"], timeout=25)
    return (o + e).lower()


def windows_docker_needs_wsl2_setup() -> bool:
    if sys.platform != "win32":
        return False
    if wsl2_environment_ready():
        return False
    if _which("docker") is None:
        return True
    if docker_cli_ok():
        return False
    return "wsl" in _docker_info_text()


def ensure_wsl_before_docker_desktop_windows(parent: tk.Misc | None) -> str:
    if sys.platform != "win32":
        return "proceed"
    if not windows_docker_needs_wsl2_setup():
        return "proceed"
    choice = messagebox.askyesnocancel(
        "WSL 2 needed for Docker Desktop",
        "On Windows, Docker Desktop’s Linux engine needs WSL 2 with a Linux distribution.\n"
        "This PC does not have WSL 2 ready yet, or Docker reported a WSL-related error.\n\n"
        "Yes — open a console to run: wsl --install\n"
        "   (Administrator / reboot may be required; when WSL is done, use “Install / fix Docker”.)\n\n"
        "No — skip WSL and continue with Docker Desktop install anyway.\n\n"
        "Cancel — stop (no Docker install now).",
        parent=parent,
    )
    if choice is None:
        return "abort"
    if choice:
        creationflags = _windows_new_console_flags()
        try:
            subprocess.Popen(["wsl", "--install"], creationflags=creationflags)
        except Exception as ex:
            messagebox.showerror("WSL", f"Could not start wsl --install:\n{ex}", parent=parent)
            _open_url(WSL_LEARN_URL)
            return "proceed"
        messagebox.showinfo(
            "WSL install started",
            "Complete the steps in the console window.\n"
            "Restart Windows if asked, then return here and use “Install / fix Docker”.",
            parent=parent,
        )
        return "wsl_started"
    return "proceed"


def try_install_docker_windows(parent: tk.Misc | None, *, confirm_winget: bool = True) -> None:
    outcome = ensure_wsl_before_docker_desktop_windows(parent)
    if outcome == "abort":
        return
    if outcome == "wsl_started":
        return
    winget = _which("winget")
    if not winget:
        messagebox.showinfo(
            "winget not found",
            "Install Docker Desktop from the website (button in the app), or install App Installer / winget from the Microsoft Store.",
            parent=parent,
        )
        _open_url(DOCKER_WIN_INSTALL_URL)
        return
    if confirm_winget and not messagebox.askyesno(
        "Install Docker Desktop",
        "This will run winget to install Docker.DockerDesktop.\n"
        "A separate window may open; approve UAC if asked.\n"
        "After install, sign in or skip, then restart this app.\n\n"
        "Continue?",
        parent=parent,
    ):
        return
    creationflags = _windows_new_console_flags()
    args = [
        winget,
        "install",
        "-e",
        "--id",
        "Docker.DockerDesktop",
        "--accept-package-agreements",
        "--accept-source-agreements",
    ]
    try:
        subprocess.Popen(args, creationflags=creationflags)
    except Exception as e:
        messagebox.showerror("winget failed", str(e), parent=parent)
        _open_url(DOCKER_WIN_INSTALL_URL)


def try_install_docker_macos(parent: tk.Misc | None, *, confirm_brew: bool = True) -> None:
    brew = _which("brew")
    if brew:
        if confirm_brew and not messagebox.askyesno(
            "Install Docker Desktop",
            "Run: brew install --cask docker\n\nContinue?",
            parent=parent,
        ):
            _open_url("https://docs.docker.com/desktop/setup/install/mac-install/")
            return
        creationflags = 0
        if hasattr(subprocess, "CREATE_NEW_CONSOLE"):
            creationflags = subprocess.CREATE_NEW_CONSOLE  # type: ignore[attr-defined]
        try:
            subprocess.Popen([brew, "install", "--cask", "docker"], creationflags=creationflags)
        except Exception as e:
            messagebox.showerror("brew failed", str(e), parent=parent)
    else:
        _open_url("https://docs.docker.com/desktop/setup/install/mac-install/")


def docker_setup_hint_linux() -> str:
    return (
        "Docker not found. On Debian/Ubuntu (HolOS/Linux), typical setup:\n\n"
        "  sudo apt update && sudo apt install -y docker.io\n"
        "  sudo usermod -aG docker $USER\n"
        "  (log out and back in)\n\n"
        "Then start Docker and run this app again."
    )


def _install_docker_for_platform(parent: tk.Misc | None, *, confirm_inner: bool) -> None:
    plat = sys.platform
    if plat == "win32":
        try_install_docker_windows(parent, confirm_winget=confirm_inner)
    elif plat == "darwin":
        try_install_docker_macos(parent, confirm_brew=confirm_inner)
    else:
        messagebox.showinfo("Docker", docker_setup_hint_linux(), parent=parent)


def offer_docker_on_first_launch(parent: tk.Misc | None) -> None:
    if docker_cli_ok():
        return
    msg = (
        "Docker is not available on this system (or the engine is not running).\n\n"
        "Wind Tunnel steps need the docker command.\n"
        "Would you like to try installing Docker Desktop now?\n"
        "(You can choose No and install later.)"
    )
    if not messagebox.askyesno("Docker", msg, parent=parent):
        messagebox.showinfo(
            "Docker",
            "You can install Docker later and use the “Install / fix Docker” button in the app.",
            parent=parent,
        )
        return
    _install_docker_for_platform(parent, confirm_inner=False)


def run_docker_install_wizard(parent: tk.Misc | None) -> None:
    if docker_cli_ok():
        messagebox.showinfo("Docker", "Docker is already available.", parent=parent)
        return
    if not messagebox.askyesno(
        "Install Docker",
        "Install or repair Docker for Wind Tunnel?\n\n"
        "Windows: launches winget for Docker Desktop (new console; UAC may appear).\n"
        "macOS: Homebrew cask or download page.\n"
        "Linux: shows terminal commands.\n\n"
        "Continue?",
        parent=parent,
    ):
        return
    _install_docker_for_platform(parent, confirm_inner=False)


def run_first_run_setup() -> None:
    root = tk.Tk()
    root.withdraw()
    try:
        first = not os.path.isfile(setup_marker_path())
        bootstrap_requirements(root, force_install=first)
        if first:
            offer_docker_on_first_launch(root)
        try:
            with open(setup_marker_path(), "w", encoding="utf-8") as f:
                f.write("ok\n")
        except OSError:
            pass
    finally:
        try:
            root.destroy()
        except tk.TclError:
            pass


def docker_run_args(hostname: str) -> list[str]:
    return [
        "docker",
        "run",
        "--hostname",
        hostname,
        "--cgroupns=host",
        "--net=host",
        "--privileged",
        "-d",
        "--rm",
        IMAGE,
    ]


def format_docker_run_command(hostname: str) -> str:
    return shlex.join(docker_run_args(hostname))


def _import_sv_ttk():
    try:
        import sv_ttk

        return sv_ttk
    except ImportError:
        return None


class WindTunnelApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_SHORT} v{__version__} — Holo Wind Tunnel Runner")
        self.minsize(760, 640)
        self.geometry("920x720")

        self._docker_busy = threading.Lock()
        self._poll_after_id: str | None = None
        self._preflight_after_id: str | None = None

        cfg = load_config()
        self._sv_ttk = _import_sv_ttk()
        dark = bool(cfg.get("dark_theme", False))
        self._var_dark = tk.BooleanVar(value=dark)
        if self._sv_ttk:
            self._sv_ttk.set_theme("dark" if dark else "light")

        hn = cfg.get("hostname")
        self.var_hostname = tk.StringVar(value=hn if isinstance(hn, str) and hn.strip() else "nomad-client-")
        self.var_log_tail = tk.IntVar(value=int(cfg.get("log_tail", DEFAULT_LOG_TAIL)))

        self._build_menubar()
        self._build_ui()
        self._start_resource_poll()
        self._start_docker_status_poll()
        self._start_preflight_poll()

    def _build_menubar(self) -> None:
        menubar = tk.Menu(self)
        view = tk.Menu(menubar, tearoff=0)
        if self._sv_ttk:
            view.add_checkbutton(
                label="Dark theme",
                variable=self._var_dark,
                command=self._toggle_dark_theme,
            )
        else:
            view.add_command(label="Dark theme (install sv-ttk)", state=tk.DISABLED)
        menubar.add_cascade(label="View", menu=view)
        self.config(menu=menubar)

    def _toggle_dark_theme(self) -> None:
        if not self._sv_ttk:
            return
        dark = self._var_dark.get()
        self._sv_ttk.set_theme("dark" if dark else "light")
        save_config(dark_theme=dark)

    def _build_ui(self) -> None:
        main = ttk.Frame(self, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        top_bar = ttk.Frame(main)
        top_bar.pack(fill=tk.X, pady=(0, 8))
        self.lbl_docker = ttk.Label(top_bar, text="Docker: checking…")
        self.lbl_docker.pack(side=tk.LEFT)
        ttk.Button(top_bar, text="Install / fix Docker", command=self.on_install_docker).pack(side=tk.RIGHT)

        pf = ttk.LabelFrame(main, text="Preflight (Holo guide: ≥8 GiB RAM, ≥10 GiB free disk)", padding=8)
        pf.pack(fill=tk.X, pady=(0, 8))
        pgrid = ttk.Frame(pf)
        pgrid.pack(fill=tk.X)
        self.lbl_pf_docker = ttk.Label(pgrid, text="Docker daemon: …")
        self.lbl_pf_docker.grid(row=0, column=0, sticky=tk.W, padx=(0, 16))
        self.lbl_pf_wsl = ttk.Label(pgrid, text="WSL 2: …")
        self.lbl_pf_wsl.grid(row=0, column=1, sticky=tk.W, padx=(0, 16))
        self.lbl_pf_ram = ttk.Label(pgrid, text="RAM: …")
        self.lbl_pf_ram.grid(row=1, column=0, sticky=tk.W, padx=(0, 16), pady=(4, 0))
        self.lbl_pf_disk = ttk.Label(pgrid, text="Disk free: …")
        self.lbl_pf_disk.grid(row=1, column=1, sticky=tk.W, padx=(0, 16), pady=(4, 0))

        hn_frame = ttk.LabelFrame(main, text="Wind Tunnel hostname (guide: nomad-client-<you>-<nn>)", padding=8)
        hn_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(
            hn_frame,
            text="Example: nomad-client-rob-01 — must be unique in the cluster. Saved automatically when you close the app.",
        ).pack(anchor=tk.W)
        row = ttk.Frame(hn_frame)
        row.pack(fill=tk.X, pady=(6, 0))
        self.entry_hostname = ttk.Entry(row, textvariable=self.var_hostname, width=50)
        self.entry_hostname.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row, text="Copy docker run …", command=self.on_copy_run_command).pack(side=tk.LEFT, padx=(8, 0))

        act = ttk.LabelFrame(main, text="Docker actions (official guide steps)", padding=8)
        act.pack(fill=tk.X, pady=(0, 8))
        btn_row1 = ttk.Frame(act)
        btn_row1.pack(fill=tk.X)
        ttk.Button(btn_row1, text="1. Stop & remove edgenode (prep)", command=self.on_prep_edgenode).pack(
            side=tk.LEFT, padx=(0, 6), pady=2
        )
        ttk.Button(btn_row1, text="2. Pull wind-tunnel-runner image", command=self.on_pull).pack(
            side=tk.LEFT, padx=6, pady=2
        )
        ttk.Button(btn_row1, text="3. Start runner container", command=self.on_start_runner).pack(
            side=tk.LEFT, padx=6, pady=2
        )
        ttk.Button(btn_row1, text="Stop runner", command=self.on_stop_runner).pack(side=tk.LEFT, padx=6, pady=2)

        btn_row2 = ttk.Frame(act)
        btn_row2.pack(fill=tk.X, pady=(4, 0))
        ttk.Button(btn_row2, text="Refresh docker ps", command=self.on_refresh_ps).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_row2, text="Open PDF guide", command=self.open_guide_pdf).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_row2, text="Wind Tunnel guide (web)", command=self.open_guide_web).pack(side=tk.LEFT, padx=6)

        log_row = ttk.Frame(act)
        log_row.pack(fill=tk.X, pady=(8, 0))
        ttk.Label(log_row, text="Runner logs tail lines:").pack(side=tk.LEFT)
        ttk.Spinbox(log_row, from_=50, to=2000, width=6, textvariable=self.var_log_tail).pack(side=tk.LEFT, padx=(4, 12))
        ttk.Button(log_row, text="Fetch runner container logs", command=self.on_fetch_runner_logs).pack(side=tk.LEFT)

        status = ttk.LabelFrame(main, text="Behind the scenes", padding=8)
        status.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        res_row = ttk.Frame(status)
        res_row.pack(fill=tk.X)
        self.lbl_host = ttk.Label(res_row, text="This PC hostname: …")
        self.lbl_host.pack(anchor=tk.W)
        self.lbl_resources = ttk.Label(res_row, text="Resources: …")
        self.lbl_resources.pack(anchor=tk.W)
        if psutil is None:
            ttk.Label(
                res_row,
                text="Resources need psutil — restart the app after first-run setup, or run pip install -r requirements.txt",
                foreground="#a60",
            ).pack(anchor=tk.W)

        ttk.Label(status, text="Wind Tunnel runner containers (docker ps, filtered by image):").pack(
            anchor=tk.W, pady=(8, 4)
        )
        self.txt_runner_ps = scrolledtext.ScrolledText(status, height=5, wrap=tk.NONE, font=("Consolas", 10))
        self.txt_runner_ps.pack(fill=tk.BOTH, expand=False)

        ttk.Label(status, text="All containers (docker ps -a):").pack(anchor=tk.W, pady=(8, 4))
        self.txt_ps = scrolledtext.ScrolledText(status, height=6, wrap=tk.NONE, font=("Consolas", 10))
        self.txt_ps.pack(fill=tk.BOTH, expand=True)

        ttk.Label(status, text="Command log:").pack(anchor=tk.W, pady=(8, 4))
        log_btn_row = ttk.Frame(status)
        log_btn_row.pack(fill=tk.X)
        ttk.Button(log_btn_row, text="Clear log", command=self.on_clear_log).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(log_btn_row, text="Save log to file…", command=self.on_save_log).pack(side=tk.LEFT)

        self.log = scrolledtext.ScrolledText(status, height=10, wrap=tk.WORD, font=("Consolas", 9))
        self.log.pack(fill=tk.BOTH, expand=True)

        foot = ttk.Frame(main)
        foot.pack(fill=tk.X)
        ttk.Label(
            foot,
            text="Guide expects HolOS/Linux with Docker. On Windows use Docker Desktop + WSL2 backend; "
            "some flags (--privileged, --net=host) apply inside Docker’s Linux engine.",
            font=("Segoe UI", 8),
            foreground="#555",
        ).pack(anchor=tk.W)

        self._update_hostname_label()
        self.after(500, self._update_hostname_label_loop)
        self.on_refresh_ps()
        self._refresh_docker_status()

    def _preflight_ok_color(self, ok: bool | None) -> str:
        if ok is None:
            return "#666"
        return "#0a7a0a" if ok else "#b00020"

    def _refresh_preflight(self) -> None:
        ok_d = docker_cli_ok()
        self.lbl_pf_docker.configure(
            text=f"Docker daemon: {'OK' if ok_d else 'not reachable'}",
            foreground=self._preflight_ok_color(ok_d),
        )
        if sys.platform == "win32":
            ok_w = wsl2_environment_ready()
            self.lbl_pf_wsl.configure(
                text=f"WSL 2: {'OK' if ok_w else 'not ready'}",
                foreground=self._preflight_ok_color(ok_w),
            )
        else:
            self.lbl_pf_wsl.configure(text="WSL 2: n/a (not Windows)", foreground="#666")

        if psutil is None:
            self.lbl_pf_ram.configure(text="RAM: unknown (psutil)", foreground="#666")
            self.lbl_pf_disk.configure(text="Disk free: unknown (psutil)", foreground="#666")
            return

        try:
            vm = psutil.virtual_memory()
            ok_ram = vm.total >= MIN_RAM_BYTES
            self.lbl_pf_ram.configure(
                text=f"RAM: {vm.total // (1024**3)} GiB total — {'meets ≥8 GiB' if ok_ram else 'below 8 GiB guide minimum'}",
                foreground=self._preflight_ok_color(ok_ram),
            )
            du = None
            for p in ("C:\\", "/"):
                try:
                    du = psutil.disk_usage(p)
                    break
                except OSError:
                    continue
            if du:
                ok_disk = du.free >= MIN_DISK_FREE_BYTES
                self.lbl_pf_disk.configure(
                    text=f"Disk free: {du.free // (1024**3)} GiB — {'meets ≥10 GiB' if ok_disk else 'below 10 GiB guide minimum'}",
                    foreground=self._preflight_ok_color(ok_disk),
                )
            else:
                self.lbl_pf_disk.configure(text="Disk free: unknown", foreground="#666")
        except Exception:
            self.lbl_pf_ram.configure(text="RAM: error", foreground="#b00020")
            self.lbl_pf_disk.configure(text="Disk: error", foreground="#b00020")

    def _start_preflight_poll(self) -> None:
        def tick() -> None:
            self._refresh_preflight()
            self._preflight_after_id = self.after(5000, tick)

        self._refresh_preflight()
        self._preflight_after_id = self.after(3000, tick)

    def _refresh_docker_status(self) -> None:
        if docker_cli_ok():
            ver = docker_version_line()
            self.lbl_docker.configure(text=f"Docker: OK{f' (engine {ver})' if ver else ''}")
        else:
            self.lbl_docker.configure(text="Docker: not available — use “Install / fix Docker”")

    def _start_docker_status_poll(self) -> None:
        def tick() -> None:
            self._refresh_docker_status()
            self.after(8000, tick)

        self.after(4000, tick)

    def on_install_docker(self) -> None:
        run_docker_install_wizard(self)

    def _update_hostname_label_loop(self) -> None:
        self._update_hostname_label()
        self.after(3000, self._update_hostname_label_loop)

    def _update_hostname_label(self) -> None:
        import socket

        try:
            h = socket.gethostname()
            self.lbl_host.configure(text=f"This PC hostname: {h}")
        except OSError:
            self.lbl_host.configure(text="This PC hostname: (unavailable)")

    def _resource_text(self) -> str:
        if psutil is None:
            return "Resources: (psutil not loaded — reinstall deps)"
        try:
            cpu = psutil.cpu_percent(interval=None)
            vm = psutil.virtual_memory()
            du = None
            for p in ("C:\\", "/"):
                try:
                    du = psutil.disk_usage(p)
                    break
                except OSError:
                    continue
            disk_s = ""
            if du:
                free_gb = du.free / (1024**3)
                total_gb = du.total / (1024**3)
                disk_s = f" | Disk free {free_gb:.1f} / {total_gb:.1f} GB"
            return (
                f"Resources: CPU {cpu:.0f}% | RAM {vm.percent:.0f}% used "
                f"({vm.used // (1024**3)} / {vm.total // (1024**3)} GiB){disk_s}"
            )
        except Exception as e:
            return f"Resources: (error: {e})"

    def _start_resource_poll(self) -> None:
        def tick() -> None:
            self.lbl_resources.configure(text=self._resource_text())
            self._poll_after_id = self.after(2000, tick)

        tick()

    def destroy(self) -> None:
        try:
            save_config(
                hostname=self.var_hostname.get().strip(),
                dark_theme=self._var_dark.get(),
                log_tail=int(self.var_log_tail.get()),
            )
        except (tk.TclError, ValueError):
            pass
        if self._poll_after_id:
            self.after_cancel(self._poll_after_id)
            self._poll_after_id = None
        if self._preflight_after_id:
            self.after_cancel(self._preflight_after_id)
            self._preflight_after_id = None
        super().destroy()

    def log_line(self, msg: str) -> None:
        ts = time.strftime("%H:%M:%S")
        self.log.insert(tk.END, f"[{ts}] {msg}\n")
        self.log.see(tk.END)

    def on_clear_log(self) -> None:
        self.log.delete("1.0", tk.END)

    def on_save_log(self) -> None:
        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("All", "*.*")],
            title="Save command log",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log.get("1.0", tk.END))
            messagebox.showinfo("Saved", f"Log saved to:\n{path}", parent=self)
        except OSError as e:
            messagebox.showerror("Save failed", str(e), parent=self)

    def _async_cmd(self, label: str, args: list[str], timeout: int | None = 300) -> None:
        if not self._docker_busy.acquire(blocking=False):
            self.log_line("(skipped: another Docker command is running)")
            return

        def work() -> None:
            try:
                self.after(0, lambda: self.log_line(f"$ {' '.join(args)}"))
                code, out, err = run_cmd(args, timeout=timeout)
                combined = (out + err).strip() or "(no output)"
                self.after(0, lambda c=code, t=combined: self._cmd_done(label, c, t))
            finally:
                self._docker_busy.release()

        threading.Thread(target=work, daemon=True).start()

    def _cmd_done(self, label: str, code: int, text: str) -> None:
        self.log_line(f"— {label} — exit {code}")
        for line in text.splitlines()[:200]:
            self.log_line(line)
        if len(text.splitlines()) > 200:
            self.log_line("… (truncated)")
        self.on_refresh_ps()
        self._refresh_docker_status()

    def on_prep_edgenode(self) -> None:
        def chain() -> None:
            if not self._docker_busy.acquire(blocking=False):
                return
            try:

                def run_seq() -> None:
                    try:
                        self.after(0, lambda: self.log_line("$ docker stop edgenode"))
                        c1, o1, e1 = run_cmd(["docker", "stop", "edgenode"], timeout=60)
                        self.after(
                            0,
                            lambda: self.log_line(f"stop edgenode → {c1} {(o1 + e1).strip() or '(no output)'}"),
                        )
                        self.after(0, lambda: self.log_line("$ docker rm edgenode"))
                        c2, o2, e2 = run_cmd(["docker", "rm", "edgenode"], timeout=60)
                        self.after(
                            0,
                            lambda: self.log_line(f"rm edgenode → {c2} {(o2 + e2).strip() or '(no output)'}"),
                        )
                        self.after(0, self.on_refresh_ps)
                        self.after(0, self._refresh_docker_status)
                    finally:
                        self._docker_busy.release()

                threading.Thread(target=run_seq, daemon=True).start()
            except Exception:
                self._docker_busy.release()

        chain()

    def on_pull(self) -> None:
        self._async_cmd("docker pull", ["docker", "pull", IMAGE], timeout=600)

    def on_copy_run_command(self) -> None:
        hn = self.var_hostname.get().strip()
        if not hn or hn == "nomad-client-":
            messagebox.showwarning("Hostname", "Set a full hostname first, e.g. nomad-client-yourname-01", parent=self)
            return
        cmd = format_docker_run_command(hn)
        self.clipboard_clear()
        self.clipboard_append(cmd)
        self.update_idletasks()
        messagebox.showinfo("Copied", "Full docker run command copied to the clipboard.", parent=self)

    def on_start_runner(self) -> None:
        hn = self.var_hostname.get().strip()
        if not hn or hn == "nomad-client-":
            messagebox.showwarning("Hostname", "Set a full hostname, e.g. nomad-client-yourname-01")
            return
        if not hn.startswith("nomad-client-"):
            if not messagebox.askyesno(
                "Hostname",
                "Guide recommends names like nomad-client-you-01.\nUse this hostname anyway?",
            ):
                return
        if not messagebox.askyesno(
            "Wind Tunnel container — security notice",
            "Per the official Holo Edge Node Wind Tunnel guide, this container runs with:\n\n"
            "• --privileged — broad capabilities inside the container (for stress testing)\n"
            "• --net=host — host networking inside Docker’s Linux environment\n\n"
            "These are intentional for Wind Tunnel participation, not for routine desktop use.\n\n"
            "Start the runner now?",
            parent=self,
        ):
            return
        save_config(hostname=hn)
        args = docker_run_args(hn)
        self._async_cmd("docker run (wind tunnel)", args, timeout=120)

    def on_stop_runner(self) -> None:
        def work() -> None:
            if not self._docker_busy.acquire(blocking=False):
                self.after(0, lambda: self.log_line("(skipped: busy)"))
                return
            try:
                self.after(0, lambda: self.log_line("$ docker ps --filter ancestor=" + IMAGE + " -q"))
                code, out, err = run_cmd(
                    ["docker", "ps", "--filter", f"ancestor={IMAGE}", "-q"],
                    timeout=30,
                )
                ids = [x.strip() for x in (out or "").splitlines() if x.strip()]
                if not ids:
                    self.after(0, lambda: self.log_line("No running wind-tunnel-runner container found."))
                    return
                for cid in ids:
                    self.after(0, lambda c=cid: self.log_line(f"$ docker stop {c}"))
                    c2, o2, e2 = run_cmd(["docker", "stop", cid], timeout=120)
                    self.after(
                        0,
                        lambda c=c2, t=(o2 + e2).strip() or "(no output)": self.log_line(f"stop → {c} {t}"),
                    )
                self.after(0, self.on_refresh_ps)
                self.after(0, self._refresh_docker_status)
            finally:
                self._docker_busy.release()

        threading.Thread(target=work, daemon=True).start()

    def on_fetch_runner_logs(self) -> None:
        if not self._docker_busy.acquire(blocking=False):
            self.log_line("(skipped: busy)")
            return

        def work() -> None:
            try:
                try:
                    n = max(10, min(5000, int(self.var_log_tail.get())))
                except (tk.TclError, ValueError):
                    n = DEFAULT_LOG_TAIL
                code, out, err = run_cmd(
                    ["docker", "ps", "-q", "--filter", f"ancestor={IMAGE}", "--filter", "status=running"],
                    timeout=30,
                )
                cids = [x.strip() for x in (out or "").splitlines() if x.strip()]
                if not cids:
                    self.after(
                        0,
                        lambda: self.log_line("No running wind-tunnel-runner container for docker logs."),
                    )
                    return
                cid = cids[0]
                self.after(0, lambda: self.log_line(f"$ docker logs --tail {n} {cid}"))
                c2, o2, e2 = run_cmd(["docker", "logs", "--tail", str(n), cid], timeout=60)
                combined = (o2 + e2).strip() or "(no output)"
                self.after(0, lambda: self.log_line(f"— runner logs — exit {c2}"))
                for line in combined.splitlines()[:300]:
                    self.after(0, lambda ln=line: self.log_line(ln))
                if len(combined.splitlines()) > 300:
                    self.after(0, lambda: self.log_line("… (truncated)"))
            finally:
                self._docker_busy.release()

        threading.Thread(target=work, daemon=True).start()

    def on_refresh_ps(self) -> None:
        def work() -> None:
            c1, o1, e1 = run_cmd(
                ["docker", "ps", "-a", "--filter", f"ancestor={IMAGE}"],
                timeout=30,
            )
            text_runner = (o1 + e1).strip() or f"(filtered docker ps failed, exit {c1})"
            c2, o2, e2 = run_cmd(["docker", "ps", "-a"], timeout=30)
            text_all = (o2 + e2).strip() or f"(docker ps -a failed, exit {c2})"

            def apply() -> None:
                self.txt_runner_ps.delete("1.0", tk.END)
                self.txt_runner_ps.insert(tk.END, text_runner)
                self.txt_ps.delete("1.0", tk.END)
                self.txt_ps.insert(tk.END, text_all)

            self.after(0, apply)

        threading.Thread(target=work, daemon=True).start()

    def open_guide_pdf(self) -> None:
        _open_url(GUIDE_URL)

    def open_guide_web(self) -> None:
        _open_url(GUIDE_HTML)


def main() -> None:
    run_first_run_setup()
    app = WindTunnelApp()
    app.mainloop()


if __name__ == "__main__":
    main()
