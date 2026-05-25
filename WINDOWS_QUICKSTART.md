# Windows 快速开始 v0.2.0-dev

## 稳定版与开发版

- 稳定发布：`v0.1.0`
- 当前开发：`v0.2.0-dev`

如果你要测试当前开发分支，请优先下载 GitHub Actions artifact。

## 开发版下载

1. 打开 GitHub Actions。
2. 进入 `Build Windows EXE`。
3. 下载 artifact：`PPT-Agent-Windows-Release`。
4. 解压。
5. 双击 `PPT-Agent.exe`。

## 第一次启动

1. 等待浏览器自动打开。
2. 打开“模型配置”。
3. 填写 API Key，或切换到 Mock 模式。
4. 返回工作台上传 PDF。
5. 点击“生成 PPT”。

## Mock 模式

- Mock 模式只用于测试上传、生成、下载流程。
- Mock 不会调用真实模型。
- Mock 生成结果会显示“模拟生成完成”。
- Mock 下载文件会显示“测试文件”。

## 质量检查

- 如果质量检查通过，通常会生成 `final_deck.pptx`。
- 如果质量检查未通过，系统会提示继续精修。
- 此时通常只保留 `draft_deck.pptx`，不建议直接用于正式汇报。

## 技能库

打开“技能库”标签页后，可以：

- 搜索技能
- 从本地 zip 导入
- 从本地文件夹导入
- 从 URL 导入安全占位技能
- 启用或禁用技能

注意：

- 外部技能默认不执行脚本
- 外部技能默认不读取用户文件
- 高风险技能应保持禁用

## Token 使用详情

打开“Token 使用详情”标签页后，可以：

- 查看总 Token
- 查看本次任务
- 导出 CSV
- 导出 JSON
- 清空本地统计

## 查看日志

- 启动日志：`logs/launcher.log`
- 后端日志：`logs/backend.log`
- 质量报告：`storage/decks/<job_id>/quality_report.json`

## 查看本地数据目录

- 技能目录：`skills/` 或 `%LOCALAPPDATA%/PPT Agent/skills/`
- Token 统计：`usage/` 或 `%LOCALAPPDATA%/PPT Agent/usage/`
