import importlib.util
import py_compile
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.runtime_config import RuntimeModelConfig
from app.storage.config_storage import ConfigStorage


ROOT = Path(__file__).resolve().parents[2]


def load_module(module_name: str, relative_path: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_static_frontend_or_root_health_available():
    client = TestClient(app)
    root = client.get("/")
    assert root.status_code == 200
    health = client.get("/api/health")
    assert health.status_code == 200


def test_low_token_runtime_defaults():
    config = RuntimeModelConfig()
    assert config.llm_model == "gpt-5.5"
    assert config.fallback_llm_model == "gpt-4.1-mini"
    assert config.reasoning_effort == "low"
    assert config.verbosity == "low"
    assert config.temperature == 0.2
    assert config.patch_mode is True
    assert config.revision_max_output_tokens == 1200
    assert config.normal_max_output_tokens == 4000


def test_windows_product_files_exist():
    expected = [
        "desktop/launcher.py",
        "packaging/launcher.spec",
        "packaging/requirements-packaging.txt",
        "packaging/preflight_windows.py",
        "packaging/install_packaging_deps.py",
        "build_release_windows.bat",
        ".github/workflows/build-windows-exe.yml",
        "scripts/check_windows_release.py",
        "README.md",
        "RELEASE_NOTES.md",
        "WINDOWS_QUICKSTART.md",
        "start_windows.bat",
        "stop_windows.bat",
    ]
    for relative in expected:
        assert (ROOT / relative).exists(), relative


def test_model_config_output_dir_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_DIR", str(tmp_path / "storage"))
    storage = ConfigStorage()
    config = RuntimeModelConfig(output_dir="D:/Reports/PPT")
    storage.save_model_config(config)
    loaded = storage.load_model_config()
    assert loaded.output_dir == "D:/Reports/PPT"


def test_preflight_missing_pyinstaller_message():
    module = load_module("preflight_windows_missing_pyinstaller", "packaging/preflight_windows.py")
    module._pyinstaller_available = lambda _python_exe: False
    ok, messages = module.run_preflight(auto_install=False)
    assert ok is False
    assert any("PyInstaller" in message for message in messages)


def test_preflight_missing_frontend_dist_message(monkeypatch, tmp_path):
    module = load_module("preflight_windows_missing_dist", "packaging/preflight_windows.py")
    monkeypatch.setattr(module, "FRONTEND_DIST", tmp_path / "missing" / "index.html")
    monkeypatch.setattr(module, "_frontend_dist_dir", lambda: tmp_path / "missing")
    monkeypatch.setattr(module, "_pyinstaller_available", lambda _python_exe: True)
    monkeypatch.setattr(module, "_release_dir_writable", lambda _: True)
    ok, messages = module.run_preflight(auto_install=False)
    assert ok is False
    assert any("frontend/dist/index.html" in message for message in messages)


def test_preflight_release_not_writable_message(monkeypatch):
    module = load_module("preflight_windows_release_not_writable", "packaging/preflight_windows.py")
    monkeypatch.setattr(module, "_pyinstaller_available", lambda _python_exe: True)
    monkeypatch.setattr(module, "_release_dir_writable", lambda _: False)
    ok, messages = module.run_preflight(auto_install=False)
    assert ok is False
    assert any("release 目录不可写" in message for message in messages)


def test_install_packaging_deps_prefers_wheelhouse(tmp_path):
    module = load_module("install_packaging_deps_local", "packaging/install_packaging_deps.py")
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    (wheelhouse / "pyinstaller-6.10.0-py3-none-any.whl").write_text("wheel", encoding="utf-8")
    assert module.has_local_pyinstaller_wheel(wheelhouse) is True


def test_launcher_spec_validation():
    spec_text = (ROOT / "packaging" / "launcher.spec").read_text(encoding="utf-8")
    assert 'name="PPT-Agent"' in spec_text
    assert "frontend/dist" in spec_text
    assert "packaging/app.ico" in spec_text or "app.ico" in spec_text
    assert ".env" in spec_text
    assert "logs" in spec_text
    assert "outputs" in spec_text
    assert "temp" in spec_text
    assert "uploads" in spec_text
    assert "storage" in spec_text


def test_launcher_python_compiles():
    py_compile.compile(str(ROOT / "desktop" / "launcher.py"), doraise=True)


def test_windows_scripts_exist_and_remain_callable():
    start_script = (ROOT / "start_windows.bat").read_text(encoding="utf-8")
    stop_script = (ROOT / "stop_windows.bat").read_text(encoding="utf-8")
    assert "uvicorn" in start_script
    assert "stop_windows.bat" in start_script
    assert "taskkill" in stop_script
    assert "backend.pid" in stop_script


def test_build_release_script_smoke_strings():
    script_text = (ROOT / "build_release_windows.bat").read_text(encoding="utf-8")
    assert "packaging\\preflight_windows.py" in script_text
    assert "python -m PyInstaller packaging\\launcher.spec" in script_text
    assert "python -m PyInstaller --version" in script_text
    assert "python -m pip install pyinstaller" in script_text
    assert "logs\\build_windows.log" in script_text
    assert "release\\PPT-Agent.exe" in script_text
    assert "release\\PPT-Agent-Portable" in script_text
    assert "CI_STRICT_MODE" in script_text


def test_github_actions_workflow_exists_and_is_windows():
    workflow_text = (ROOT / ".github" / "workflows" / "build-windows-exe.yml").read_text(encoding="utf-8")
    assert "name: Build Windows EXE" in workflow_text
    assert "windows-latest" in workflow_text
    assert "python -m pip install --upgrade pip" in workflow_text
    assert "python -m pip install pyinstaller" in workflow_text
    assert "python -m PyInstaller --version" in workflow_text
    assert "build_release_windows.bat" in workflow_text
    assert "actions/upload-artifact@v4" in workflow_text
    assert "PPT-Agent-Windows-Release" in workflow_text


def test_release_check_script_exists_and_validates_expected_files():
    script_text = (ROOT / "scripts" / "check_windows_release.py").read_text(encoding="utf-8")
    assert "PPT-Agent.exe" in script_text
    assert "README.md" in script_text
    assert "WINDOWS_QUICKSTART.md" in script_text
    assert ".env.example" in script_text
    assert "未找到 PPT-Agent.exe" in script_text
    assert "当前目录" in script_text
    assert "release 目录内容" in script_text
    assert "packaging/launcher.spec 是否存在" in script_text
    assert "desktop/launcher.py 是否存在" in script_text
    assert "frontend/dist/index.html 是否存在" in script_text
    assert "logs" in script_text
    assert "outputs" in script_text
    assert "temp" in script_text
    assert "uploads" in script_text
