# Release Notes

## v0.1.0 Windows Pre-release

`v0.1.0` 是 PPT Agent 的首个 Windows 预发布版本，当前已完成：

- `PPT-Agent.exe` 启动器可打开浏览器和本地 Web UI
- 修复 `app.storage` 打包缺失问题
- 修复 frozen 环境下 `uvicorn` 日志初始化失败
- 修复首屏和关键操作区中文文案
- 增加首次启动说明、API Key 提示、Mock 模式说明
- 增加 Mock 端到端生成与下载校验
- 保持 Round 2 / Round 3 与 Low Token Mode 不回退

## 构建与交付

GitHub Actions 工作流：

- `Build Windows EXE`

artifact 名称：

- `PPT-Agent-Windows-Release`

release 包目标内容：

- `PPT-Agent.exe`
- `README.md`
- `WINDOWS_QUICKSTART.md`
- `RELEASE_NOTES.md`
- `.env.example`

## 安全说明

- EXE 不会内置真实 API Key
- release 包不会包含 `.env`
- release 包不会包含 `logs/`、`outputs/`、`uploads/`、`temp/`
- GitHub Actions artifact 不会写入真实 API Key
