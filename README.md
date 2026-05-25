# PPT Agent v0.2.0-dev

当前分支是 `v0.2.0-dev`，目标是在现有 Windows EXE 基础上增加：

- 技能库 Skill Library
- 全网技能搜索的安全 provider 架构
- 本地技能导入、启用、禁用、删除
- Token 使用详情统计

稳定版 Windows 下载仍以 `v0.1.0` Release 为准；当前分支用于继续开发和验证。

## 当前能力

- PDF 转 PPT
- 中文 Web UI
- Windows 双击启动
- Mock 模式测试
- Low Token Mode
- Round 2 修改
- Round 3 精修
- 技能库管理
- Token 使用详情

## v0.2.0-dev 新功能

### 技能库

- 本地技能目录：
  - 开发模式：`skills/`
  - Windows EXE：`%LOCALAPPDATA%/PPT Agent/skills/`
- 支持：
  - 搜索技能
  - 导入本地 zip
  - 导入本地文件夹
  - 导入 mock URL / GitHub 占位来源
  - 启用技能
  - 禁用技能
  - 删除技能
- 外部技能默认：
  - `enabled = false`
  - `trusted = false`
  - 不执行脚本
  - 不读取用户文件
  - 不联网
  - 不获取 API Key

### Token 使用详情

- 本地统计目录：
  - 开发模式：`usage/`
  - Windows EXE：`%LOCALAPPDATA%/PPT Agent/usage/`
- 支持：
  - 查看总 Token
  - 按任务查看阶段明细
  - 导出 CSV
  - 导出 JSON
  - 清空本地统计

## Windows 使用说明

如果你要测试稳定发布版：

1. 打开 GitHub Release 页面
2. 下载 `PPT-Agent-Windows-v0.1.0.zip`
3. 解压后进入对应目录
4. 双击 `PPT-Agent.exe`

如果你要测试当前开发分支：

1. 运行 `Build Windows EXE` workflow
2. 下载 artifact `PPT-Agent-Windows-Release`
3. 解压后双击 `PPT-Agent.exe`

## Mock 模式

Mock 模式适合本地验收和回归测试：

- 无需真实 API Key
- 可验证上传、生成、下载主流程
- 可验证技能库和 Token 统计界面

## API Key 说明

- EXE 不会内置真实 API Key
- 技能不会自动获得 API Key
- Token 统计不会记录 API Key
- 日志不会记录 API Key

## 文档

- [技能库说明](C:\Users\windysky\Documents\ppt agent\SKILL_LIBRARY.md)
- [Token 使用详情](C:\Users\windysky\Documents\ppt agent\TOKEN_USAGE.md)
- [Windows 快速开始](C:\Users\windysky\Documents\ppt agent\WINDOWS_QUICKSTART.md)
- [隐私说明](C:\Users\windysky\Documents\ppt agent\PRIVACY.md)
- [安全说明](C:\Users\windysky\Documents\ppt agent\SECURITY.md)
- [故障排查](C:\Users\windysky\Documents\ppt agent\TROUBLESHOOTING.md)
