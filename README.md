# PPT Agent v0.1.0

PPT Agent 是一个本地优先的论文 PDF 转 PPT 工具。`v0.1.0` 为 Windows 预发布版本，当前重点支持：

- 双击 `PPT-Agent.exe` 启动本地 Web UI
- 上传 PDF 生成可编辑 PPTX
- Mock 模式验收，无需真实 API Key
- Round 2 / Round 3 精修指定页面
- High-Quality Low-Token Mode 默认参数

## 下载与运行

1. 打开仓库的 `Actions`
2. 进入 `Build Windows EXE`
3. 下载 artifact `PPT-Agent-Windows-Release`
4. 解压后进入 `release/`
5. 双击 `PPT-Agent.exe`
6. 等待浏览器自动打开

如果是第一次运行：

1. 打开“模型配置”
2. 填写 API Key，或切换到 Mock 模式
3. 返回工作台上传 PDF
4. 点击“生成 PPT”
5. 在“生成结果”中下载 PPT

## 本机构建 EXE

```bat
build_release_windows.bat
```

输出目录：

- `release/PPT-Agent.exe`
- `release/README.md`
- `release/WINDOWS_QUICKSTART.md`
- `release/RELEASE_NOTES.md`
- `release/.env.example`

如果 EXE 构建失败，还会生成：

- `release/PPT-Agent-Portable/`

## GitHub Actions 构建

工作流名称：

- `Build Windows EXE`

artifact 名称：

- `PPT-Agent-Windows-Release`

## API Key 说明

- EXE 不会内置真实 API Key
- artifact 不会写入真实 API Key
- `.env.example` 只保留空占位
- API Key 只保存在用户本机配置中
- 首次验收可直接使用 Mock 模式

## Mock 模式

Mock 模式适合首轮验收和回归测试：

- 无需真实 API Key
- 可上传测试 PDF
- 可完整跑通生成、下载、Round 2、Round 3

## release 包检查

release 包应包含：

- `PPT-Agent.exe`
- `README.md`
- `WINDOWS_QUICKSTART.md`
- `RELEASE_NOTES.md`
- `.env.example`

release 包不应包含：

- `.env`
- `logs/`
- `outputs/`
- `uploads/`
- `temp/`
- `node_modules/`
- `__pycache__/`
- 用户 PDF
- 生成的 PPTX

## 日志与输出目录

- 启动日志：`logs/launcher.log`
- 后端日志：`logs/backend.log`
- 前端日志：`logs/frontend.log`
- 默认输出目录：`storage/decks`

## 常见问题

- Windows 阻止运行：右键 EXE，打开“属性”，如果看到“解除锁定”则勾选后再运行。
- API Key 未配置：去“模型配置”填写 API Key，或切换到 Mock 模式。
- 端口占用：关闭占用 `8000` 端口的程序后重试。
- 生成失败：先查看 `logs/backend.log` 和 `logs/launcher.log`。
- 找不到下载文件：检查“生成结果”面板中的 `final_deck.pptx` 路径。
- 杀毒软件误报：优先使用 GitHub Actions 最新 artifact，并按需加入白名单。

更多 Windows 使用说明见 [WINDOWS_QUICKSTART.md](C:\Users\windysky\Documents\ppt agent\WINDOWS_QUICKSTART.md)。
