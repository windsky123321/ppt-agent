from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path
from tkinter import BOTH, END, LEFT, RIGHT, Button, Frame, Label, StringVar, Text, Tk, messagebox

import urllib.request


APP_NAME = "PPT Agent"
BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_DEV_URL = "http://127.0.0.1:5173"


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parents[1]


def runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


APP_ROOT = app_root()
RUNTIME_ROOT = runtime_root()
BACKEND_ROOT = APP_ROOT / "backend"
FRONTEND_DIST = APP_ROOT / "frontend" / "dist"
LOG_DIR = RUNTIME_ROOT / "logs"
BACKEND_PID = LOG_DIR / "backend.pid"
FRONTEND_PID = LOG_DIR / "frontend.pid"


def frontend_candidates() -> list[Path]:
    return [
        FRONTEND_DIST / "index.html",
        RUNTIME_ROOT / "frontend" / "dist" / "index.html",
    ]


def frontend_dist_dir() -> Path:
    for candidate in frontend_candidates():
        if candidate.exists():
            return candidate.parent
    return FRONTEND_DIST


class DesktopLauncher:
    def __init__(self) -> None:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.backend_process: subprocess.Popen | None = None
        self.frontend_process: subprocess.Popen | None = None
        self.backend_thread: threading.Thread | None = None
        self.backend_server = None
        self.backend_env: dict[str, str] | None = None

        self.root = Tk()
        self.root.title(APP_NAME)
        self.root.geometry("720x520")
        self.status = StringVar(value="未启动")

        Label(self.root, text="PPT Agent", font=("Microsoft YaHei", 20, "bold")).pack(pady=(18, 4))
        Label(self.root, textvariable=self.status, font=("Microsoft YaHei", 11)).pack(pady=(0, 12))

        toolbar = Frame(self.root)
        toolbar.pack(fill="x", padx=18, pady=6)
        Button(toolbar, text="启动", command=self.start_async, width=12).pack(side=LEFT, padx=4)
        Button(toolbar, text="打开网页", command=self.open_browser, width=12).pack(side=LEFT, padx=4)
        Button(toolbar, text="停止", command=self.stop, width=12).pack(side=LEFT, padx=4)
        Button(toolbar, text="打开日志目录", command=self.open_logs, width=14).pack(side=LEFT, padx=4)
        Button(toolbar, text="退出", command=self.quit, width=10).pack(side=RIGHT, padx=4)

        self.log_box = Text(self.root, height=22, font=("Consolas", 10))
        self.log_box.pack(fill=BOTH, expand=True, padx=18, pady=12)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

    def log(self, message: str) -> None:
        line = f"[{time.strftime('%H:%M:%S')}] {message}"
        with (LOG_DIR / "launcher.log").open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        self.log_box.insert(END, line + "\n")
        self.log_box.see(END)
        self.root.update_idletasks()

    def set_status(self, value: str) -> None:
        self.status.set(value)
        self.log(value)

    def log_runtime_diagnostics(self) -> None:
        backend_path = str(BACKEND_ROOT)
        env_pythonpath = self.backend_env.get("PYTHONPATH", "") if self.backend_env else os.environ.get("PYTHONPATH", "")
        storage_dir = BACKEND_ROOT / "app" / "storage"
        storage_init = storage_dir / "__init__.py"
        self.log(f"frozen={getattr(sys, 'frozen', False)}")
        self.log(f"app_root={APP_ROOT}")
        self.log(f"runtime_root={RUNTIME_ROOT}")
        self.log(f"backend_root={BACKEND_ROOT}")
        self.log(f"backend_root exists={BACKEND_ROOT.exists()}")
        self.log(f"backend_root/app exists={(BACKEND_ROOT / 'app').exists()}")
        self.log(f"backend_root/app/storage exists={storage_dir.exists()}")
        self.log(f"backend_root/app/storage/__init__.py exists={storage_init.exists()}")
        self.log(f"frontend_dist={frontend_dist_dir()}")
        self.log(f"sys.path[:5]={sys.path[:5]}")
        self.log(f"PYTHONPATH={env_pythonpath}")
        if storage_dir.exists():
            try:
                storage_items = sorted(str(path.relative_to(BACKEND_ROOT)) for path in storage_dir.rglob("*"))[:20]
                self.log(f"backend_root/app/storage files={storage_items}")
            except Exception as exc:
                self.log(f"backend_root/app/storage files=fail: {exc}")
        try:
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
            import importlib

            importlib.import_module("app")
            self.log("app import=ok")
            importlib.import_module("app.storage")
            self.log("app.storage import=ok")
            importlib.import_module("app.main")
            self.log("app.main import=ok")
        except Exception as exc:
            message = str(exc)
            if "app.storage" in message:
                self.log(f"app.storage import=fail: {exc}")
            elif "app.main" in message:
                self.log(f"app.main import=fail: {exc}")
            else:
                self.log(f"app import diagnostics fail: {exc}")

    def start_async(self) -> None:
        threading.Thread(target=self.start, daemon=True).start()

    def start(self) -> None:
        try:
            self.ensure_env()
            self.prepare_backend_path()
            self.log_runtime_diagnostics()
            if not self.static_frontend_ready():
                raise RuntimeError("未找到前端资源，请重新构建发布包。")
            self.ensure_ports()
            if getattr(sys, "frozen", False):
                self.start_backend_embedded()
            else:
                self.start_backend_subprocess()
            if not self.static_frontend_ready() and not getattr(sys, "frozen", False):
                self.start_frontend_dev()
            self.open_browser()
            self.set_status("已启动，可以上传 PDF 生成 PPT")
        except Exception as exc:
            self.set_status("启动失败")
            message = str(exc)
            if "app.storage" in message:
                messagebox.showerror(APP_NAME, "启动失败：发布包缺少后端 storage 模块，请重新下载最新构建包。")
            else:
                messagebox.showerror(APP_NAME, f"启动失败：{exc}\n请查看 logs/launcher.log")

    def ensure_env(self) -> None:
        os.chdir(RUNTIME_ROOT)
        for path in [
            RUNTIME_ROOT / "storage",
            RUNTIME_ROOT / "storage" / "uploads",
            RUNTIME_ROOT / "storage" / "decks",
            RUNTIME_ROOT / "storage" / "config",
            LOG_DIR,
        ]:
            path.mkdir(parents=True, exist_ok=True)

        env_path = RUNTIME_ROOT / ".env"
        example_candidates = [RUNTIME_ROOT / ".env.example", APP_ROOT / ".env.example"]
        example_path = next((path for path in example_candidates if path.exists()), None)
        if not env_path.exists() and example_path:
            env_path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")
            self.log("已创建 .env，请按需填写 API Key")

        if env_path.exists():
            text = env_path.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")
            if "OPENAI_API_KEY=\n" in text or text.endswith("OPENAI_API_KEY="):
                self.log("未检测到 API Key，可先使用 Mock 模式或在网页中配置运行时模型")

    def ensure_ports(self) -> None:
        ports = [8000]
        if not self.static_frontend_ready() and not getattr(sys, "frozen", False):
            ports.append(5173)
        for port in ports:
            if self.port_open(port):
                if port == 8000 and self.health_ok(BACKEND_URL + "/api/health"):
                    self.log("检测到现有后端服务，直接复用")
                    continue
                raise RuntimeError(f"端口 {port} 已被占用，请先关闭占用程序")

    def static_frontend_ready(self) -> bool:
        return any(path.exists() for path in frontend_candidates())

    def prepare_backend_path(self) -> None:
        backend_path = str(BACKEND_ROOT)
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        env = os.environ.copy()
        current_pythonpath = env.get("PYTHONPATH", "")
        if current_pythonpath:
            env["PYTHONPATH"] = backend_path + os.pathsep + current_pythonpath
        else:
            env["PYTHONPATH"] = backend_path
        self.backend_env = env

    def start_backend_subprocess(self) -> None:
        if self.health_ok(BACKEND_URL + "/api/health"):
            self.set_status("后端已在运行")
            return

        python_exe = RUNTIME_ROOT / "backend" / ".venv" / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = Path(sys.executable)

        backend_dir = RUNTIME_ROOT / "backend"
        env = dict(self.backend_env or os.environ.copy())

        log_handle = (LOG_DIR / "backend.log").open("a", encoding="utf-8")
        self.set_status("正在启动后端")
        self.log(f"backend command={[str(python_exe), '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000']}")
        self.log(f"backend cwd={backend_dir}")
        self.backend_process = subprocess.Popen(
            [str(python_exe), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=backend_dir,
            env=env,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        )
        BACKEND_PID.write_text(str(self.backend_process.pid), encoding="utf-8")
        self.wait_for(BACKEND_URL + "/api/health", "后端")

    def start_backend_embedded(self) -> None:
        if self.health_ok(BACKEND_URL + "/api/health"):
            self.set_status("后端已在运行")
            return

        if str(BACKEND_ROOT) not in sys.path:
            sys.path.insert(0, str(BACKEND_ROOT))

        from app.main import app as backend_app
        import uvicorn

        self.set_status("正在启动内置后端")
        self.log("backend command=embedded uvicorn app.main:app")
        self.log(f"backend cwd={BACKEND_ROOT}")
        config = uvicorn.Config(backend_app, host="127.0.0.1", port=8000, log_level="info")
        self.backend_server = uvicorn.Server(config)
        self.backend_thread = threading.Thread(target=self.backend_server.run, daemon=True)
        self.backend_thread.start()
        self.wait_for(BACKEND_URL + "/api/health", "后端")

    def start_frontend_dev(self) -> None:
        if self.health_ok(FRONTEND_DEV_URL):
            return
        npm = "npm.cmd" if os.name == "nt" else "npm"
        log_handle = (LOG_DIR / "frontend.log").open("a", encoding="utf-8")
        self.set_status("正在启动前端开发服务")
        self.frontend_process = subprocess.Popen(
            [npm, "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"],
            cwd=RUNTIME_ROOT / "frontend",
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        )
        FRONTEND_PID.write_text(str(self.frontend_process.pid), encoding="utf-8")
        self.wait_for(FRONTEND_DEV_URL, "前端")

    def wait_for(self, url: str, label: str) -> None:
        for _ in range(45):
            if self.health_ok(url):
                self.log(f"{label}已就绪")
                return
            time.sleep(1)
        raise RuntimeError(f"{label}启动超时")

    def open_browser(self) -> None:
        target = BACKEND_URL if self.static_frontend_ready() or getattr(sys, "frozen", False) else FRONTEND_DEV_URL
        webbrowser.open(target)
        self.log(f"已打开浏览器：{target}")

    def open_logs(self) -> None:
        if os.name == "nt":
            os.startfile(LOG_DIR)
        else:
            webbrowser.open(str(LOG_DIR))

    def stop(self) -> None:
        self.stop_pid(FRONTEND_PID)
        self.stop_pid(BACKEND_PID)

        if self.backend_server is not None:
            self.backend_server.should_exit = True
            if self.backend_thread is not None:
                self.backend_thread.join(timeout=10)
            self.backend_server = None
            self.backend_thread = None

        self.set_status("已停止")

    def stop_pid(self, pid_file: Path) -> None:
        if not pid_file.exists():
            return
        try:
            pid = int(pid_file.read_text(encoding="utf-8").strip())
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(pid), "/F"],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                os.kill(pid, signal.SIGTERM)
            self.log(f"已停止进程 {pid}")
        finally:
            pid_file.unlink(missing_ok=True)

    def quit(self) -> None:
        self.stop()
        self.root.destroy()

    @staticmethod
    def port_open(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.3)
            return sock.connect_ex(("127.0.0.1", port)) == 0

    @staticmethod
    def health_ok(url: str) -> bool:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                return 200 <= response.status < 500
        except Exception:
            return False

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    DesktopLauncher().run()
