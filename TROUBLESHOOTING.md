# Troubleshooting

## 如何下载 EXE

1. 打开仓库 `Actions`
2. 进入 `Build Windows EXE`
3. 下载 artifact `PPT-Agent-Windows-Release`

## EXE 被 Windows 阻止

- 右键 `PPT-Agent.exe`
- 打开“属性”
- 如果看到“解除锁定”，勾选后再运行

## API Key 未配置

- 打开 Web UI 的“模型配置”
- 填写 API Key 并保存
- 如果只想验收流程，可直接切换到 Mock 模式

## 端口被占用

- 关闭占用 `8000` 端口的程序
- 重新双击 `PPT-Agent.exe`
- 如仍失败，查看 `logs/launcher.log`

## 生成失败

- 先查看 `logs/backend.log`
- 再查看 `logs/launcher.log`
- 可切换到 Mock 模式复测链路

## 下载文件找不到

- 打开“生成结果”面板
- 查找 `final_deck.pptx`
- 默认输出目录为 `storage/decks`

## 杀毒软件误报

- 个别环境可能对 PyInstaller 打包程序误报
- 请优先使用 GitHub Actions 生成的最新 artifact
- 若企业环境有白名单机制，请将 `PPT-Agent.exe` 加入白名单

## PyInstaller 安装失败

先尝试：

```bat
python -m pip install pyinstaller
```

如果网络受限：

1. 下载对应 wheel
2. 放入 `packaging/wheelhouse/`
3. 重新运行 `build_release_windows.bat`

## EXE 启动失败：No module named app.storage

- 说明发布包缺少后端 storage 模块，或下载到旧 artifact
- 请重新运行最新 GitHub Actions 构建
- 下载最新 artifact 后重试
- 查看 `logs/launcher.log`

## EXE 启动失败：Unable to configure formatter default

- 说明旧构建包里的后端日志初始化有问题
- 请下载最新 artifact 后重试
- 查看 `logs/launcher.log` 与 `logs/backend.log`
