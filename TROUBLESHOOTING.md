# Troubleshooting

## Windows EXE 构建失败

请先查看：

- `logs/build_windows.log`

常见原因：

- 未安装 Python 3.11+
- 未安装 Node.js / npm
- `frontend/dist/index.html` 缺失
- 未安装 PyInstaller
- 当前网络受限，导致 `pip install pyinstaller` 失败

## GitHub Actions 如何下载 EXE

1. 打开仓库的 `Actions`
2. 进入 `Build Windows EXE`
3. 打开成功的运行记录
4. 在页面底部下载 artifact `PPT-Agent-Windows-Release`

下载的 artifact 中会包含 `release/PPT-Agent.exe`。

## PyInstaller 安装失败

先尝试：

```bash
python -m pip install pyinstaller
```

如果网络受限：

1. 在可联网机器下载 PyInstaller wheel
2. 放到 `packaging/wheelhouse/`
3. 重新运行 `build_release_windows.bat`

## 只有 portable 包，没有 EXE

说明本次 EXE 打包未通过，但 portable 兜底包已生成：

- `release/PPT-Agent-Portable/`

此时可以先用：

- `release/PPT-Agent-Portable/start_windows.bat`

后续再根据 `logs/build_windows.log` 修复 EXE 构建问题。

## exe 启动失败：No module named app.storage

- 这通常表示发布包中缺少后端模块，或 EXE 运行时的 `backend` 路径配置错误
- 请重新运行最新 GitHub Actions 的 `Build Windows EXE`
- 下载最新 artifact 后重新测试
- 查看 `logs/launcher.log`，重点关注：
  - `frozen`
  - `backend_root`
  - `PYTHONPATH`
  - `app.storage import`
