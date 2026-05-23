# Troubleshooting

## Windows 阻止运行

- 右键 `PPT-Agent.exe`
- 打开“属性”
- 如果看到“解除锁定”，勾选后再运行

## API Key 未配置

- 打开 Web UI 的“模型配置”
- 填写 API Key 并保存
- 如果只是验收流程，可直接切换到 Mock 模式

## 端口占用

- 关闭占用 `8000` 端口的程序
- 重新双击 `PPT-Agent.exe`
- 如仍失败，查看 `logs/launcher.log`

## 生成失败

- 先查看 `logs/backend.log`
- 再查看 `logs/launcher.log`
- 必要时切换到 Mock 模式复测链路

## 找不到下载文件

- 打开“生成结果”面板
- 查找 `final_deck.pptx`
- 默认输出目录为 `storage/decks`

## 杀毒软件误报

- 个别环境可能对 PyInstaller 打包程序误报
- 优先使用 GitHub Actions 生成的最新 artifact
- 如企业环境有白名单机制，请将 `PPT-Agent.exe` 加入白名单
