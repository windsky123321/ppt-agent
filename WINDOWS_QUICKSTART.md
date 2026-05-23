# Windows 快速开始

## 运行 EXE

1. 从 GitHub Actions 下载 artifact `PPT-Agent-Windows-Release`
2. 解压后进入 `release/`
3. 双击 `PPT-Agent.exe`
4. 等待浏览器自动打开 Web UI

## 第一次启动

如果本机还没有 `.env`：

- 启动器会基于 `.env.example` 自动创建
- 不会覆盖用户已有 `.env`

首次使用建议：

1. 打开“模型配置”
2. 填写 API Key，或直接切换到 Mock 模式
3. 返回工作台上传 PDF
4. 点击“生成 PPT”
5. 在“生成结果”中下载 PPT

## 如何生成 EXE

本机 Windows：

```bat
build_release_windows.bat
```

GitHub Actions：

1. 打开 `Actions`
2. 运行 `Build Windows EXE`
3. 下载 artifact `PPT-Agent-Windows-Release`

## PyInstaller 安装失败怎么办

先尝试：

```bat
python -m pip install pyinstaller
```

如果网络受限：

1. 在可联网机器下载 PyInstaller wheel
2. 放入 `packaging/wheelhouse/`
3. 重新运行 `build_release_windows.bat`

## Mock 模式测试

如果你暂时没有 API Key：

- 进入“模型配置”
- 点击“切换到 Mock 模式”
- 保存后即可上传测试 PDF 验证完整流程

## 日志与输出

- 启动日志：`logs/launcher.log`
- 后端日志：`logs/backend.log`
- 前端日志：`logs/frontend.log`
- 默认输出目录：`storage/decks`

## Portable 兜底包

如果 EXE 构建失败，脚本会生成：

- `release/PPT-Agent-Portable/`

说明：

- Portable 包不是最终 EXE
- 可用于先跑通本地服务
- EXE 仍是最终推荐交付物
