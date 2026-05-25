# PPT Agent v0.2.0-dev

当前分支为 `v0.2.0-dev`，重点验证两件事：

- 技能库 Skill Library
- Token 使用详情

稳定 Windows 发布版仍以 `v0.1.0` Release 为准；当前分支用于继续开发和验收。

## 当前能力

- PDF 转 PPT
- 中文 Web UI
- Windows 双击启动
- Mock 模式流程测试
- Low Token Mode
- Round 2 修改
- Round 3 精修
- 技能库管理
- Token 使用详情

## 重要说明

### Mock 模式

- Mock 模式只用于测试上传、生成、下载和界面流程。
- Mock 模式不会调用真实模型。
- Mock 结果会标记为“模拟生成完成”或“测试文件”。
- Mock 结果不能视为正式汇报质量。

### 正式生成

- 正式生成前必须在“模型配置”中填写 API Key。
- 如果 Provider 不是 `mock` 且未配置 API Key，系统会阻止正式生成。
- 质量检查未通过时，不建议直接用于汇报。

### 质量门控

- 如果 Critic 未通过，系统不会把结果当作最终可交付 PPT。
- 此时通常只保留 `draft_deck.pptx`。
- 请查看 `quality_report.json` 并继续精修。

## Windows 使用说明

如果你要测试稳定发布版：

1. 打开 GitHub Release 页面。
2. 下载 `PPT-Agent-Windows-v0.1.0.zip`。
3. 解压后进入目录。
4. 双击 `PPT-Agent.exe`。

如果你要测试当前开发分支：

1. 运行 `Build Windows EXE` workflow。
2. 下载 artifact `PPT-Agent-Windows-Release`。
3. 解压后双击 `PPT-Agent.exe`。

## 文档

- [技能库说明](C:\Users\windysky\Documents\ppt agent\SKILL_LIBRARY.md)
- [Token 使用详情](C:\Users\windysky\Documents\ppt agent\TOKEN_USAGE.md)
- [Windows 快速开始](C:\Users\windysky\Documents\ppt agent\WINDOWS_QUICKSTART.md)
- [隐私说明](C:\Users\windysky\Documents\ppt agent\PRIVACY.md)
- [安全说明](C:\Users\windysky\Documents\ppt agent\SECURITY.md)
- [故障排查](C:\Users\windysky\Documents\ppt agent\TROUBLESHOOTING.md)
