# Troubleshooting

## 找不到 PPT-Agent.exe

- 如果你下载的是 GitHub Actions artifact，请先完整解压。
- 如果你在本机构建，请确认 `release/PPT-Agent.exe` 已生成。

## Windows 阻止运行

- 右键 `PPT-Agent.exe`
- 打开“属性”
- 如看到“解除锁定”，勾选后再运行

## API Key 未配置

- 打开 Web UI 的“模型配置”
- 填写 API Key 并保存
- 如果只是验收流程，可切换到 Mock 模式

## 端口被占用

- 关闭占用 `8000` 端口的程序
- 重新双击 `PPT-Agent.exe`
- 如仍失败，查看 `logs/launcher.log`

## 生成失败

- 先查看 `logs/backend.log`
- 再查看 `logs/launcher.log`
- 可切换到 Mock 模式复测主流程

## 找不到下载文件

- 打开“生成结果”面板
- 查找 `final_deck.pptx`
- 默认输出目录为 `storage/decks`

## 杀毒软件误报

- 个别环境可能对 PyInstaller 打包程序误报
- 优先使用 GitHub Actions 生成的最新 artifact
- 必要时将 `PPT-Agent.exe` 加入白名单

## 技能导入失败

- 检查技能包是否包含 `skill.json` 或 `SKILL.md`
- 检查 zip 中是否存在 `../` 路径穿越
- 检查是否包含超大文件、二进制文件或脚本

## Token 统计显示 unknown

- 说明当前 provider 没有返回 usage
- 系统不会编造 token 数值
- 可继续使用导出功能查看已有统计
