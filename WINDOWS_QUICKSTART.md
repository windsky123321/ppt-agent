# Windows 快速开始

## 启动应用

- 双击 `start_windows.bat`
- 浏览器会自动打开 `http://127.0.0.1:8000`
- 停止服务时双击 `stop_windows.bat`

启动前请先安装：

- Python 3.11+
- Node.js 18+

## 生成 EXE

双击 `build_release_windows.bat` 即可一键构建 Windows 发布包。

默认输出：

- `release/PPT-Agent.exe`
- `release/README.md`
- `release/WINDOWS_QUICKSTART.md`
- `release/RELEASE_NOTES.md`
- `release/.env.example`

同时会生成 portable 兜底包：

- `release/PPT-Agent-Portable/`

## 通过 GitHub Actions 生成 EXE

1. 打开 GitHub 仓库的 `Actions`
2. 选择 `Build Windows EXE`
3. 点击 `Run workflow`
4. 等待构建完成
5. 下载 artifact `PPT-Agent-Windows-Release`

下载后可在 artifact 中找到：

- `release/PPT-Agent.exe`
- `release/README.md`
- `release/WINDOWS_QUICKSTART.md`
- `release/RELEASE_NOTES.md`
- `release/.env.example`

## PyInstaller 安装失败怎么办

如果脚本提示：

- “未检测到 PyInstaller，正在尝试自动安装……”
- “自动安装失败，可能是网络受限。请先执行 `python -m pip install pyinstaller` 后重新运行本脚本。”

请按以下方式处理：

1. 在线安装：`python -m pip install pyinstaller`
2. 离线安装：把 PyInstaller wheel 放到 `packaging/wheelhouse/` 后重新运行 `build_release_windows.bat`

## 网络受限时怎么办

推荐做法：

1. 在可联网机器下载 PyInstaller 对应 wheel
2. 复制到 `packaging/wheelhouse/`
3. 回到目标 Windows 机器重新执行 `build_release_windows.bat`

构建脚本会优先从本地 wheelhouse 离线安装 PyInstaller。

## Portable 包说明

- `PPT-Agent.exe` 是最终用户优先使用的桌面入口
- `PPT-Agent-Portable/` 是 EXE 构建失败时的兜底运行包
- portable 包不会伪装成 EXE 成功，只用于先跑通本地服务

## API Key 配置

- API Key 不会被写入 EXE
- API Key 不会被写入示例配置
- 请在 `.env` 或 Web UI 运行时配置中填写自己的 Key
- `.env.example` 仅保留空占位
- GitHub Actions 构建产物同样不会内置真实 API Key
