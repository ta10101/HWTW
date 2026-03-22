"""
Holo Edge Node — Wind Tunnel Runner GUI (HWTW)
Implements steps from: https://holo.host/files/EdgeNodeWindTunnelGuide.pdf
"""

from __future__ import annotations

import importlib
import json
import os
import shlex
import shutil
import sysconfig
from urllib.parse import urlencode
from collections import deque
from pathlib import Path
import subprocess
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

psutil = None  # set in bootstrap_requirements()

__version__ = "1.1.4"
APP_SHORT = "HWTW"

IMAGE = "ghcr.io/holochain/wind-tunnel-runner:latest"
RUNNER_STATUS_ORIGIN = "https://wind-tunnel-runner-status.holochain.org"
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


def runner_status_check_url(hostname: str) -> str:
    """Full URL for the Holochain Wind Tunnel runner status page (matches /status?hostname=… on the dashboard)."""
    h = (hostname or "").strip()
    if not h:
        return f"{RUNNER_STATUS_ORIGIN}/"
    return f"{RUNNER_STATUS_ORIGIN}/status?{urlencode({'hostname': h})}"


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def app_dir() -> str:
    if is_frozen():
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


def is_externally_managed() -> bool:
    """True on Chromebook Linux, Debian 12+, etc. (PEP 668); system pip install is blocked."""
    try:
        stdlib = Path(sysconfig.get_path("stdlib"))
        return (stdlib / "EXTERNALLY-MANAGED").is_file()
    except Exception:
        return False


def _use_project_venv_for_bootstrap() -> bool:
    """Linux source runs always use .venv — PEP 668 is universal on Chromebook/Debian; marker path can differ."""
    if is_frozen():
        return False
    return sys.platform.startswith("linux")


def _venv_python(venv_dir: str) -> str | None:
    if sys.platform == "win32":
        for name in ("python.exe", "python3.exe"):
            p = os.path.join(venv_dir, "Scripts", name)
            if os.path.isfile(p):
                return p
    else:
        for name in ("python3", "python"):
            p = os.path.join(venv_dir, "bin", name)
            if os.path.isfile(p):
                return p
    return None


def _venv_can_import(py_exe: str, module: str = "psutil") -> bool:
    code, _, _ = run_cmd([py_exe, "-c", f"import {module}"], timeout=60)
    return code == 0


def _bootstrap_via_project_venv(parent: tk.Misc | None, req: str) -> bool:
    """Create .venv, pip install there, re-exec this app with the venv interpreter (PEP 668)."""
    app_root = app_dir()
    venv_dir = os.path.join(app_root, ".venv")
    main_py = os.path.join(app_root, "main.py")
    venv_py = _venv_python(venv_dir)

    if venv_py and _venv_can_import(venv_py):
        try:
            os.execv(venv_py, [venv_py, main_py, *sys.argv[1:]])
        except OSError as e:
            messagebox.showerror(
                "Could not start virtual environment",
                f"{e}\n\nIn a terminal:\n  cd {shlex.quote(app_root)}\n"
                f'  {shlex.quote(venv_py)} {shlex.quote("main.py")}',
                parent=parent,
            )
        return False

    # Drop stale/partial .venv before recreating (avoids mixed pip / broken imports).
    if os.path.isdir(venv_dir):
        try:
            shutil.rmtree(venv_dir)
        except OSError as e:
            messagebox.showerror(
                "Could not remove old .venv",
                f"{e}\n\nClose terminals or apps using this folder, then try again.\n"
                f"Or delete manually:\n{venv_dir}",
                parent=parent,
            )
            return False
    venv_py = None

    splash = None
    if parent is not None:
        splash = tk.Toplevel(parent)
        splash.title("Setup")
        splash.resizable(False, False)

    def splash_msg(text: str) -> None:
        if not splash:
            return
        for w in splash.winfo_children():
            w.destroy()
        ttk.Label(splash, text=text, padding=20).pack()
        splash.update()

    if splash:
        splash_msg(
            "Linux uses a protected system Python.\n"
            "Creating a project virtual environment (.venv)…"
        )

    if not venv_py:
        try:
            cr = subprocess.run(
                [sys.executable, "-m", "venv", venv_dir],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except Exception as e:
            if splash:
                try:
                    splash.destroy()
                except tk.TclError:
                    pass
            messagebox.showerror(
                "Could not create .venv",
                f"{e}\n\nIn the project folder, run:\n"
                f"  sudo apt install python3-venv python3-full\n"
                f"  python3 -m venv .venv\n"
                f"  .venv/bin/pip install -r requirements.txt\n"
                f"  .venv/bin/python main.py",
                parent=parent,
            )
            return False
        if cr.returncode != 0:
            if splash:
                try:
                    splash.destroy()
                except tk.TclError:
                    pass
            blob = ((cr.stdout or "") + (cr.stderr or ""))[:1500]
            messagebox.showerror(
                "Could not create .venv",
                f"python -m venv failed:\n\n{blob}",
                parent=parent,
            )
            return False
        venv_py = _venv_python(venv_dir)
        if not venv_py:
            if splash:
                try:
                    splash.destroy()
                except tk.TclError:
                    pass
            messagebox.showerror(
                "Virtual environment incomplete",
                f"Expected Python under:\n{venv_dir}",
                parent=parent,
            )
            return False

    if _venv_can_import(venv_py):
        if splash:
            try:
                splash.destroy()
            except tk.TclError:
                pass
        try:
            os.execv(venv_py, [venv_py, main_py, *sys.argv[1:]])
        except OSError as e:
            messagebox.showerror(
                "Could not start virtual environment",
                str(e),
                parent=parent,
            )
        return False

    if splash:
        splash_msg("Installing packages into .venv (first run)…\nThis may take a minute.")

    try:
        pr = subprocess.run(
            [
                venv_py,
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
    except Exception as e:
        if splash:
            try:
                splash.destroy()
            except tk.TclError:
                pass
        messagebox.showerror("pip failed", str(e), parent=parent)
        return False

    if splash:
        try:
            splash.destroy()
        except tk.TclError:
            pass

    if pr.returncode != 0:
        blob = ((pr.stdout or "") + (pr.stderr or ""))[:1500]
        messagebox.showerror(
            "Dependency install failed",
            "pip could not install packages into .venv.\n\n" + blob,
            parent=parent,
        )
        return False

    try:
        os.execv(venv_py, [venv_py, main_py, *sys.argv[1:]])
    except OSError as e:
        messagebox.showinfo(
            "Dependencies installed",
            f"Installed into .venv. Start the app with:\n\n"
            f'  cd {app_root}\n'
            f'  "{venv_py}" main.py\n\n'
            f"Error was: {e}",
            parent=parent,
        )
    return False


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
    _ = force_install  # callers pass first-run flag; satisfied imports skip redundant pip
    try:
        psutil = importlib.import_module("psutil")
        return True
    except ImportError:
        pass

    if is_frozen():
        _load_psutil()
        if psutil is None:
            messagebox.showerror(
                "Missing built-in libraries",
                "This build should include psutil but it failed to load.\n"
                "Re-download HWTW.exe from the project releases page.",
                parent=parent,
            )
        return psutil is not None

    req = requirements_path()
    if not os.path.isfile(req):
        messagebox.showerror(
            "Missing requirements.txt",
            f"Could not find:\n{req}\n\nCopy requirements.txt next to the app and try again.",
            parent=parent,
        )
        _load_psutil()
        return psutil is not None

    if _use_project_venv_for_bootstrap() or is_externally_managed():
        return _bootstrap_via_project_venv(parent, req)

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
        blob = pip_out[0][:1500] if pip_out[0] else "(no output)"
        if "externally-managed-environment" in blob and not is_frozen():
            return _bootstrap_via_project_venv(parent, req)
        messagebox.showerror(
            "Dependency install failed",
            "pip could not install packages from requirements.txt.\n\n" + blob,
            parent=parent,
        )

    _load_psutil()
    if psutil is None:
        app_root = app_dir()
        vpy = _venv_python(os.path.join(app_root, ".venv"))
        if vpy and os.path.isfile(vpy):
            hint = (
                f"Try:\n  {shlex.quote(vpy)} -m pip install -r {shlex.quote(req)}\n"
                f"  {shlex.quote(vpy)} {shlex.quote(os.path.join(app_root, 'main.py'))}"
            )
        elif sys.platform.startswith("linux"):
            hint = (
                "On Linux, from the project folder:\n"
                "  python3 -m venv .venv\n"
                "  .venv/bin/pip install -r requirements.txt\n"
                "  .venv/bin/python main.py\n"
                "If venv fails: sudo apt install python3-venv python3-full"
            )
        else:
            hint = f'  "{sys.executable}" -m pip install -r "{req}"'
        messagebox.showwarning(
            "psutil missing",
            "CPU/RAM/disk panel will be limited until psutil installs correctly.\n\n" + hint,
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


def wind_tunnel_runner_running() -> bool:
    code, out, _ = run_cmd(
        ["docker", "ps", "-q", "--filter", f"ancestor={IMAGE}", "--filter", "status=running"],
        timeout=20,
    )
    return code == 0 and bool((out or "").strip())


def build_diagnosis_text() -> str:
    blocks: list[str] = []
    if not docker_cli_ok():
        blocks.append(
            "DOCKER IS NOT READY\n"
            "— Open “Docker Desktop” from the Start menu and wait until it says Docker is running "
            "(whale icon in the taskbar).\n"
            "— If Docker is not installed: use the “Install Docker Desktop” button in this app, "
            "or install from docker.com and restart the PC if asked.\n"
            "— On Windows, Docker needs WSL 2 with a Linux distro (e.g. Ubuntu). "
            "If installs fail, search “WSL install” on learn.microsoft.com."
        )
    elif sys.platform == "win32" and not wsl2_environment_ready():
        blocks.append(
            "WSL 2 IS NOT READY (Windows)\n"
            "Docker Desktop’s Linux engine needs WSL 2 and a Linux distribution.\n"
            "— In an Administrator PowerShell run: wsl --install\n"
            "— Restart if Windows asks, finish Ubuntu setup, then start Docker again."
        )
    if psutil is not None:
        try:
            vm = psutil.virtual_memory()
            if vm.total < MIN_RAM_BYTES:
                blocks.append(
                    f"LOW RAM FOR GUIDE MINIMUM\n"
                    f"— Holo’s guide asks for about 8 GiB RAM; this PC reports about {vm.total // (1024**3)} GiB total.\n"
                    f"— The app may still run, but performance could be poor."
                )
            du = None
            for p in ("C:\\", "/"):
                try:
                    du = psutil.disk_usage(p)
                    break
                except OSError:
                    continue
            if du and du.free < MIN_DISK_FREE_BYTES:
                blocks.append(
                    f"LOW FREE DISK SPACE\n"
                    f"— Guide asks for about 10 GiB free; this drive has about {du.free // (1024**3)} GiB free.\n"
                    f"— Free space before pulling the Wind Tunnel image."
                )
        except OSError:
            pass

    if docker_cli_ok() and not wind_tunnel_runner_running():
        blocks.append(
            "WIND TUNNEL CONTAINER IS NOT RUNNING\n"
            "— Set your node name (e.g. nomad-client-yourname-01), then use “Download Wind Tunnel image” "
            "and “Start Wind Tunnel”.\n"
            "— If start fails, open the “Expert tools & logs” tab and read the red error text."
        )

    if not blocks:
        return (
            "No obvious problems detected.\n\n"
            "If something still fails, use the Expert tab → command log, or ask in Holo / Wind Tunnel community channels."
        )
    return "\n\n— — —\n\n".join(blocks)


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
        bootstrap_requirements(root, force_install=first and not is_frozen())
        if first and not is_frozen():
            offer_docker_on_first_launch(root)
        elif first and is_frozen():
            if not docker_cli_ok():
                messagebox.showinfo(
                    "One-time setup: Docker",
                    "HWTW controls the Wind Tunnel using Docker.\n\n"
                    "1) Install Docker Desktop for Windows (if you have not already).\n"
                    "2) Start Docker Desktop and wait until it is fully running.\n"
                    "3) Come back to this app — green status means you are ready.\n\n"
                    "Use Help → “Why isn’t it working?” anytime.",
                    parent=root,
                )
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


class ToolTip:
    """Small hover hint (delay before show)."""

    def __init__(self, widget: tk.Widget, text: str, delay_ms: int = 450) -> None:
        self.widget = widget
        self.text = text
        self.delay_ms = delay_ms
        self._tip: tk.Toplevel | None = None
        self._after_id: str | None = None
        widget.bind("<Enter>", self._schedule, add=True)
        widget.bind("<Leave>", self._hide, add=True)
        widget.bind("<ButtonPress>", self._hide, add=True)

    def _schedule(self, _event: object | None = None) -> None:
        self._hide()
        self._after_id = self.widget.after(self.delay_ms, self._show)

    def _show(self) -> None:
        self._after_id = None
        if self._tip is not None:
            return
        try:
            x = self.widget.winfo_rootx() + 12
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        except tk.TclError:
            return
        self._tip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        try:
            tw.wm_attributes("-topmost", True)
        except tk.TclError:
            pass
        lb = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background="#fffde7",
            relief=tk.SOLID,
            borderwidth=1,
            font=("Segoe UI", 9),
            wraplength=340,
            padx=8,
            pady=6,
        )
        lb.pack()
        tw.update_idletasks()
        tw.geometry(f"+{x}+{y}")

    def _hide(self, _event: object | None = None) -> None:
        if self._after_id:
            try:
                self.widget.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None
        if self._tip:
            try:
                self._tip.destroy()
            except tk.TclError:
                pass
            self._tip = None


class WindTunnelApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_SHORT} v{__version__} — Holo Wind Tunnel Runner")
        self.minsize(760, 640)
        self.geometry("980x780")

        self._docker_busy = threading.Lock()
        self._poll_after_id: str | None = None
        self._preflight_after_id: str | None = None
        self._easy_dash_after_id: str | None = None
        self._cpu_history: deque[float] = deque(maxlen=90)
        self._welcome_win: tk.Toplevel | None = None

        cfg = load_config()
        self._sv_ttk = _import_sv_ttk()
        dark = bool(cfg.get("dark_theme", False))
        self._var_dark = tk.BooleanVar(value=dark)
        if self._sv_ttk:
            self._sv_ttk.set_theme("dark" if dark else "light")

        hn = cfg.get("hostname")
        self.var_hostname = tk.StringVar(value=hn if isinstance(hn, str) and hn.strip() else "nomad-client-")
        self.var_runner_status_url = tk.StringVar(
            value=runner_status_check_url(self.var_hostname.get())
        )
        self.var_hostname.trace_add("write", lambda *_: self._sync_runner_status_url())
        self.var_log_tail = tk.IntVar(value=int(cfg.get("log_tail", DEFAULT_LOG_TAIL)))

        self._build_menubar()
        self._build_ui()
        self._start_resource_poll()
        self._start_docker_status_poll()
        self._start_preflight_poll()

        if not cfg.get("hide_welcome_easy"):
            self.after(900, lambda: self._show_welcome_easy_dialog(force=False))

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
        help_m = tk.Menu(menubar, tearoff=0)
        help_m.add_command(label="Welcome tips…", command=lambda: self._show_welcome_easy_dialog(force=True))
        help_m.add_command(label="Why isn’t it working? …", command=self.show_diagnosis_window)
        help_m.add_command(label="Open Wind Tunnel guide (web)", command=self.open_guide_web)
        help_m.add_command(label="Open official PDF", command=self.open_guide_pdf)
        help_m.add_command(
            label="Holochain runner status page…",
            command=self._on_open_runner_status_url,
        )
        menubar.add_cascade(label="Help", menu=help_m)
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

        nb = ttk.Notebook(main)
        nb.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        tab_easy = ttk.Frame(nb, padding=8)
        nb.add(tab_easy, text="Easy start (recommended)")
        self._build_easy_tab(tab_easy)
        tab_expert = ttk.Frame(nb, padding=4)
        nb.add(tab_expert, text="Expert tools & logs")
        self._build_expert_tab(tab_expert)

        foot = ttk.Frame(main)
        foot.pack(fill=tk.X)
        ttk.Label(
            foot,
            text="Wind Tunnel needs Docker (separate install on Windows: Docker Desktop + WSL 2). "
            "The .exe bundles this app only — not Docker. "
            "Flags --privileged / --net=host apply inside Docker’s Linux engine.",
            font=("Segoe UI", 8),
            foreground="#555",
            wraplength=880,
        ).pack(anchor=tk.W)

        self._update_hostname_label()
        self.after(500, self._update_hostname_label_loop)
        self.on_refresh_ps()
        self._refresh_docker_status()
        self.after(400, self._update_easy_dashboard)

    def _build_easy_tab(self, tab: ttk.Frame) -> None:
        intro = ttk.Label(
            tab,
            text=(
                "Follow the colored boxes below. Green = good. When Docker and (on Windows) WSL are green, "
                "enter your node name, download the image once, then press Start. "
                "Use Help → “Why isn’t it working?” for plain-language fixes."
            ),
            wraplength=860,
            font=("Segoe UI", 10),
        )
        intro.pack(anchor=tk.W, pady=(0, 12))

        pills = ttk.Frame(tab)
        pills.pack(fill=tk.X, pady=(0, 12))
        for c in range(4):
            pills.columnconfigure(c, weight=1)

        def make_pill(col: int) -> tuple[tk.Frame, tk.Label]:
            fr = tk.Frame(pills, bd=2, relief=tk.GROOVE, padx=8, pady=8)
            fr.grid(row=0, column=col, padx=4, sticky=tk.NSEW)
            lb = tk.Label(fr, text="…", font=("Segoe UI", 10, "bold"), justify=tk.CENTER, wraplength=180)
            lb.pack(fill=tk.BOTH, expand=True)
            return fr, lb

        self._easy_fr_docker, self._easy_pill_docker = make_pill(0)
        self._easy_fr_wsl, self._easy_pill_wsl = make_pill(1)
        self._easy_fr_runner, self._easy_pill_runner = make_pill(2)
        self._easy_fr_pc, self._easy_pill_pc = make_pill(3)
        self._easy_pill_frames = [
            self._easy_fr_docker,
            self._easy_fr_wsl,
            self._easy_fr_runner,
            self._easy_fr_pc,
        ]

        _tip_docker = (
            "Docker Desktop (or another Docker engine) must be installed and running. "
            "The whale icon in the taskbar should be steady — open Docker and wait if it says Starting."
        )
        ToolTip(self._easy_fr_docker, _tip_docker)
        ToolTip(self._easy_pill_docker, _tip_docker)
        _tip_wsl = (
            "On Windows, Docker’s Linux engine needs WSL 2 and a Linux distro (e.g. Ubuntu). "
            "If this stays red, install WSL from an Administrator PowerShell: wsl --install"
        )
        ToolTip(self._easy_fr_wsl, _tip_wsl)
        ToolTip(self._easy_pill_wsl, _tip_wsl)
        _tip_runner = (
            "Shows whether the official wind-tunnel-runner container is running on this PC. "
            "Use Download image, then Start Wind Tunnel below."
        )
        ToolTip(self._easy_fr_runner, _tip_runner)
        ToolTip(self._easy_pill_runner, _tip_runner)
        _tip_pc = (
            "Holo’s guide suggests at least 8 GiB RAM and 10 GiB free disk. "
            "Orange/red here means your PC may be below that — it can still work but may be tight."
        )
        ToolTip(self._easy_fr_pc, _tip_pc)
        ToolTip(self._easy_pill_pc, _tip_pc)
        self._easy_canvas = tk.Canvas(
            tab, height=72, background="#f5f5f5", highlightthickness=1, highlightbackground="#ccc"
        )
        self._easy_canvas.pack(fill=tk.X, pady=(4, 8))
        self._easy_canvas.bind("<Configure>", lambda _e: self._draw_cpu_sparkline())
        ToolTip(
            self._easy_canvas,
            "Rough trend of overall CPU use on this PC (not only Wind Tunnel). Updates every couple of seconds.",
        )

        self._var_prog_cpu = tk.DoubleVar(value=0.0)
        self._var_prog_ram = tk.DoubleVar(value=0.0)
        self._var_prog_disk = tk.DoubleVar(value=0.0)
        gf = ttk.Frame(tab)
        gf.pack(fill=tk.X, pady=4)
        ttk.Label(gf, text="CPU", width=10).grid(row=0, column=0, sticky=tk.W)
        ttk.Progressbar(gf, variable=self._var_prog_cpu, maximum=100, length=400).grid(
            row=0, column=1, sticky=tk.EW, padx=4
        )
        self._lbl_easy_cpu = ttk.Label(gf, text="0%", width=8)
        self._lbl_easy_cpu.grid(row=0, column=2)
        ttk.Label(gf, text="RAM used", width=10).grid(row=1, column=0, sticky=tk.W, pady=4)
        ttk.Progressbar(gf, variable=self._var_prog_ram, maximum=100, length=400).grid(
            row=1, column=1, sticky=tk.EW, padx=4, pady=4
        )
        self._lbl_easy_ram = ttk.Label(gf, text="0%", width=8)
        self._lbl_easy_ram.grid(row=1, column=2, pady=4)
        ttk.Label(gf, text="Disk used", width=10).grid(row=2, column=0, sticky=tk.W)
        ttk.Progressbar(gf, variable=self._var_prog_disk, maximum=100, length=400).grid(
            row=2, column=1, sticky=tk.EW, padx=4
        )
        self._lbl_easy_disk = ttk.Label(gf, text="0%", width=8)
        self._lbl_easy_disk.grid(row=2, column=2)
        gf.columnconfigure(1, weight=1)

        hn_easy = ttk.LabelFrame(tab, text="Your node name (must be unique — see Holo guide)", padding=8)
        hn_easy.pack(fill=tk.X, pady=(12, 8))
        ttk.Label(
            hn_easy,
            text="Example: nomad-client-jane-01   (change “jane” and “01” to match you)",
        ).pack(anchor=tk.W)
        erow = ttk.Frame(hn_easy)
        erow.pack(fill=tk.X, pady=(6, 0))
        ttk.Entry(erow, textvariable=self.var_hostname, width=55).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(
            hn_easy,
            text="Holochain status check — full URL (paste into your browser’s address bar):",
            wraplength=520,
        ).pack(anchor=tk.W, pady=(10, 0))
        url_inner = ttk.Frame(hn_easy)
        url_inner.pack(fill=tk.X, pady=(4, 0))
        self._entry_runner_status_easy = ttk.Entry(url_inner, textvariable=self.var_runner_status_url)
        self._entry_runner_status_easy.pack(side=tk.LEFT, fill=tk.X, expand=True)
        try:
            self._entry_runner_status_easy.configure(state="readonly")
        except tk.TclError:
            pass
        ttk.Button(url_inner, text="Copy URL", command=self._on_copy_runner_status_url).pack(
            side=tk.LEFT, padx=(6, 0)
        )
        ttk.Button(url_inner, text="Open", command=self._on_open_runner_status_url).pack(side=tk.LEFT, padx=(6, 0))

        big = ttk.Frame(tab)
        big.pack(fill=tk.X, pady=16)
        ttk.Button(big, text="Install / fix Docker (Windows helper)", command=self.on_install_docker).pack(
            fill=tk.X, pady=3, ipady=6
        )
        ttk.Button(big, text="1 — Download Wind Tunnel image (first time, may take a while)", command=self.on_pull).pack(
            fill=tk.X, pady=3, ipady=8
        )
        ttk.Button(big, text="2 — Start Wind Tunnel on this PC", command=self.on_start_runner).pack(
            fill=tk.X, pady=3, ipady=8
        )
        ttk.Button(big, text="Stop Wind Tunnel", command=self.on_stop_runner).pack(fill=tk.X, pady=3, ipady=6)
        ttk.Button(big, text="Why isn’t it working? …", command=self.show_diagnosis_window).pack(
            fill=tk.X, pady=8, ipady=6
        )

    def _build_expert_tab(self, tab: ttk.Frame) -> None:
        pf = ttk.LabelFrame(tab, text="Preflight (Holo guide: ≥8 GiB RAM, ≥10 GiB free disk)", padding=8)
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

        hn_frame = ttk.LabelFrame(tab, text="Wind Tunnel hostname (guide: nomad-client-<you>-<nn>)", padding=8)
        hn_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(
            hn_frame,
            text="Example: nomad-client-rob-01 — saved when you close the app.",
        ).pack(anchor=tk.W)
        row = ttk.Frame(hn_frame)
        row.pack(fill=tk.X, pady=(6, 0))
        self.entry_hostname = ttk.Entry(row, textvariable=self.var_hostname, width=50)
        self.entry_hostname.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(row, text="Copy docker run …", command=self.on_copy_run_command).pack(side=tk.LEFT, padx=(8, 0))

        st_fr = ttk.Frame(hn_frame)
        st_fr.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(
            st_fr,
            text="Holochain runner status (wind-tunnel-runner-status.holochain.org) — full URL:",
            wraplength=640,
        ).pack(anchor=tk.W)
        st_row = ttk.Frame(st_fr)
        st_row.pack(fill=tk.X, pady=(4, 0))
        self._entry_runner_status_expert = ttk.Entry(st_row, textvariable=self.var_runner_status_url)
        self._entry_runner_status_expert.pack(side=tk.LEFT, fill=tk.X, expand=True)
        try:
            self._entry_runner_status_expert.configure(state="readonly")
        except tk.TclError:
            pass
        ttk.Button(st_row, text="Copy URL", command=self._on_copy_runner_status_url).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(st_row, text="Open in browser", command=self._on_open_runner_status_url).pack(
            side=tk.LEFT, padx=(6, 0)
        )

        act = ttk.LabelFrame(tab, text="Docker actions (official guide steps)", padding=8)
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

        status = ttk.LabelFrame(tab, text="Behind the scenes", padding=8)
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
                text="Resources need psutil — use source install or a full release build.",
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

    def show_diagnosis_window(self) -> None:
        win = tk.Toplevel(self)
        win.title("HWTW — What might be wrong?")
        win.minsize(520, 360)
        win.geometry("680x420")
        body = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Segoe UI", 10), padx=8, pady=8)
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        body.insert("1.0", build_diagnosis_text())
        body.configure(state=tk.DISABLED)
        ttk.Button(win, text="Close", command=win.destroy).pack(pady=6)

    def _show_welcome_easy_dialog(self, *, force: bool) -> None:
        if not force and load_config().get("hide_welcome_easy"):
            return
        if self._welcome_win is not None:
            try:
                if self._welcome_win.winfo_exists():
                    self._welcome_win.lift()
                    self._welcome_win.focus_force()
                    return
            except tk.TclError:
                pass
            self._welcome_win = None

        win = tk.Toplevel(self)
        self._welcome_win = win
        win.title("Welcome — HWTW")
        win.minsize(440, 380)
        win.geometry("520x420")
        win.transient(self)
        frm = ttk.Frame(win, padding=16)
        frm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frm, text="Holo Wind Tunnel helper (HWTW)", font=("Segoe UI", 12, "bold")).pack(anchor=tk.W)
        msg = (
            "You are on the Easy start tab — best for most people.\n\n"
            "1) One-time: install Docker Desktop for Windows and start it (this app cannot bundle Docker).\n"
            "2) Wait until the Docker and WSL tiles turn green.\n"
            "3) Type a node name like nomad-client-yourname-01.\n"
            "4) Tap “Download Wind Tunnel image”, then “Start Wind Tunnel”.\n\n"
            "Hover the colored tiles for hints. Use Help → “Why isn’t it working?” if anything is red.\n\n"
            "Advanced users: switch to “Expert tools & logs” for full Docker output."
        )
        ttk.Label(frm, text=msg, wraplength=460, font=("Segoe UI", 10)).pack(anchor=tk.W, pady=(12, 8))

        var_hide = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frm,
            text="Don’t show this welcome window again",
            variable=var_hide,
        ).pack(anchor=tk.W, pady=(8, 12))

        def _close() -> None:
            if var_hide.get():
                save_config(hide_welcome_easy=True)
            try:
                win.destroy()
            except tk.TclError:
                pass
            self._welcome_win = None

        win.protocol("WM_DELETE_WINDOW", _close)
        ttk.Button(frm, text="Got it — let’s go", command=_close).pack(anchor=tk.E, pady=4)

    def _easy_set_pill(self, index: int, line1: str, line2: str, ok: bool | None) -> None:
        lbl = (self._easy_pill_docker, self._easy_pill_wsl, self._easy_pill_runner, self._easy_pill_pc)[index]
        fr = self._easy_pill_frames[index]
        if ok is True:
            bg = "#c8e6c9"
        elif ok is False:
            bg = "#ffcdd2"
        else:
            bg = "#eceff1"
        fr.configure(bg=bg)
        lbl.configure(bg=bg, text=f"{line1}\n{line2}")

    def _draw_cpu_sparkline(self) -> None:
        cv = self._easy_canvas
        cv.delete("all")
        pts = list(self._cpu_history)
        if len(pts) < 2:
            return
        w = max(cv.winfo_width(), 200)
        h = max(cv.winfo_height(), 60)
        n = len(pts)
        coords: list[float] = []
        for i, p in enumerate(pts):
            x = 4 + (w - 8) * i / max(n - 1, 1)
            y = h - 4 - (h - 8) * min(100.0, max(0.0, p)) / 100.0
            coords.extend([x, y])
        if len(coords) >= 4:
            cv.create_line(*coords, fill="#1565c0", width=2, smooth=True)

    def _update_easy_dashboard(self) -> None:
        if self._easy_dash_after_id:
            try:
                self.after_cancel(self._easy_dash_after_id)
            except tk.TclError:
                pass
            self._easy_dash_after_id = None
        try:
            d_ok = docker_cli_ok()
            self._easy_set_pill(0, "Docker engine", "Running ✓" if d_ok else "Not ready ✗", d_ok)

            if sys.platform == "win32":
                w_ok = wsl2_environment_ready()
                self._easy_set_pill(1, "WSL 2 (Windows)", "Ready ✓" if w_ok else "Set up WSL ✗", w_ok)
            else:
                self._easy_set_pill(1, "WSL 2", "Not needed", None)

            if d_ok:
                r_ok = wind_tunnel_runner_running()
                self._easy_set_pill(2, "Wind Tunnel", "Container up ✓" if r_ok else "Not running", r_ok)
            else:
                self._easy_set_pill(2, "Wind Tunnel", "Need Docker first", False)

            pc_ok = None
            pc_sub = "—"
            if psutil is not None:
                try:
                    vm = psutil.virtual_memory()
                    du = None
                    for p in ("C:\\", "/"):
                        try:
                            du = psutil.disk_usage(p)
                            break
                        except OSError:
                            continue
                    ram_b = vm.total >= MIN_RAM_BYTES
                    disk_b = du is None or du.free >= MIN_DISK_FREE_BYTES
                    pc_ok = ram_b and disk_b
                    pc_sub = f"{vm.total // (1024**3)} GiB RAM"
                    if du:
                        pc_sub += f", {du.free // (1024**3)} GiB free"
                except OSError:
                    pc_ok = None
                    pc_sub = "unknown"
            self._easy_set_pill(3, "This PC", pc_sub, pc_ok)

            if psutil is not None:
                cpu = float(psutil.cpu_percent(interval=None))
                self._cpu_history.append(cpu)
                vm = psutil.virtual_memory()
                self._var_prog_cpu.set(cpu)
                self._var_prog_ram.set(float(vm.percent))
                self._lbl_easy_cpu.configure(text=f"{cpu:.0f}%")
                self._lbl_easy_ram.configure(text=f"{vm.percent:.0f}%")
                du = None
                for p in ("C:\\", "/"):
                    try:
                        du = psutil.disk_usage(p)
                        break
                    except OSError:
                        continue
                if du:
                    pct = 100.0 * (du.used / du.total) if du.total else 0.0
                    self._var_prog_disk.set(pct)
                    self._lbl_easy_disk.configure(text=f"{pct:.0f}%")
            self._draw_cpu_sparkline()
        except tk.TclError:
            return
        self._easy_dash_after_id = self.after(1500, self._update_easy_dashboard)

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
        if self._easy_dash_after_id:
            try:
                self.after_cancel(self._easy_dash_after_id)
            except tk.TclError:
                pass
            self._easy_dash_after_id = None
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

    def _sync_runner_status_url(self) -> None:
        url = runner_status_check_url(self.var_hostname.get())
        entries = (
            getattr(self, "_entry_runner_status_easy", None),
            getattr(self, "_entry_runner_status_expert", None),
        )
        for w in entries:
            if w is not None:
                try:
                    w.configure(state="normal")
                except tk.TclError:
                    pass
        self.var_runner_status_url.set(url)
        for w in entries:
            if w is not None:
                try:
                    w.configure(state="readonly")
                except tk.TclError:
                    pass

    def _on_copy_runner_status_url(self) -> None:
        url = runner_status_check_url(self.var_hostname.get())
        self.var_runner_status_url.set(url)
        self.clipboard_clear()
        self.clipboard_append(url)
        self.update_idletasks()
        messagebox.showinfo("Copied", "Status check URL copied to the clipboard.", parent=self)

    def _on_open_runner_status_url(self) -> None:
        _open_url(runner_status_check_url(self.var_hostname.get()))

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
