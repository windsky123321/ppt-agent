# Release Notes

## 发布候选修复

本轮完成了发布前必要修复：

- 修复 Windows `PPT-Agent.exe` 启动链路
- 修复 `app.storage` 打包缺失问题
- 修复 frozen 环境下 `uvicorn` 日志初始化失败
- 修复 Web UI 关键页面中文乱码
- 增加首启引导、API Key 提示、Mock 模式说明
- 增加 Mock 端到端生成与下载校验
- 保持 Round 2 / Round 3 与 Low Token Mode 不回退

## 安全说明

- EXE 不会内置真实 API Key
- release 包不会包含 `.env`
- release 包不会包含 `logs/`、`outputs/`、`temp/`、`uploads/`
- GitHub Actions artifact 不会写入真实 API Key

## 产物

- `release/PPT-Agent.exe`
- `release/README.md`
- `release/WINDOWS_QUICKSTART.md`
- `release/RELEASE_NOTES.md`
- `release/.env.example`
