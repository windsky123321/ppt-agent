# PPT Agent

PPT Agent 是一个本地优先的论文 PDF 转 PPT 工具，支持：

- 上传 PDF 并生成可编辑 PPTX
- Mock 模式验收，无需真实 API Key
- Round 2 / Round 3 精修指定页面
- High-Quality Low-Token Mode 默认参数
- Windows `PPT-Agent.exe` 一键启动

## 快速开始

1. 下载 GitHub Actions 产物 `PPT-Agent-Windows-Release`
2. 解压后双击 `release/PPT-Agent.exe`
3. 浏览器会自动打开 Web UI
4. 第一次使用时去“模型配置”填写 API Key，或直接切换到 Mock 模式
5. 上传 PDF，点击“生成 PPT”
6. 生成完成后在右侧“生成结果”下载 PPT

## GitHub Actions 下载方式

1. 打开仓库的 `Actions`
2. 进入 `Build Windows EXE`
3. 打开成功运行记录
4. 下载 artifact `PPT-Agent-Windows-Release`

## Windows EXE 构建

本机构建：

```bat
build_release_windows.bat
```

构建输出：

- `release/PPT-Agent.exe`
- `release/README.md`
- `release/WINDOWS_QUICKSTART.md`
- `release/RELEASE_NOTES.md`
- `release/.env.example`

若 EXE 构建失败，会额外生成：

- `release/PPT-Agent-Portable/`

## API Key 说明

- `PPT-Agent.exe` 不会内置真实 API Key
- GitHub Actions artifact 不会写入真实 API Key
- `.env.example` 只保留空占位
- API Key 只保存在用户本机配置中

## Mock 模式

Mock 模式用于首轮验收和回归测试：

- 无需真实 API Key
- 可上传测试 PDF
- 可完整跑通生成、下载、Round 2、Round 3

## 日志与输出目录

- 启动日志：`logs/launcher.log`
- 后端日志：`logs/backend.log`
- 前端日志：`logs/frontend.log`
- 默认输出目录：`storage/decks`

## 常用测试

```bat
cd backend
python -m pytest -q
python scripts/smoke_test.py
python scripts/smoke_round2.py
python scripts/smoke_windows.py
```

```bat
cd frontend
npm run build
```

更多 Windows 使用说明见 [WINDOWS_QUICKSTART.md](C:\Users\windysky\Documents\ppt agent\WINDOWS_QUICKSTART.md)。
