# Windows 快速开始 v0.1.0

## 下载安装

1. 打开仓库 `Actions`
2. 进入 `Build Windows EXE`
3. 下载 artifact `PPT-Agent-Windows-Release`
4. 解压后进入 `release/`
5. 双击 `PPT-Agent.exe`

## 第一次启动

如果本机还没有 `.env`：

- 启动器会基于 `.env.example` 自动创建
- 不会覆盖已有 `.env`

首次使用建议：

1. 打开“模型配置”
2. 填写 API Key，或切换到 Mock 模式
3. 返回工作台上传 PDF
4. 点击“生成 PPT”
5. 在“生成结果”中下载 PPT

## 本机构建

```bat
build_release_windows.bat
```

输出目录：

- `release/PPT-Agent.exe`
- `release/README.md`
- `release/WINDOWS_QUICKSTART.md`
- `release/RELEASE_NOTES.md`
- `release/.env.example`

## Mock 模式

如果暂时没有 API Key：

1. 进入“模型配置”
2. 点击“切换到 Mock 模式”
3. 保存配置
4. 上传测试 PDF 验证完整流程

## API Key 说明

- API Key 不会写入 EXE
- API Key 不会写入 GitHub Actions artifact
- API Key 不会写入示例配置
- 真实 Key 仅保存在本机运行时配置中

## 常见问题

- Windows 阻止运行：右键 EXE，检查“解除锁定”。
- API Key 未配置：去“模型配置”填写，或改用 Mock 模式。
- 端口占用：关闭占用 `8000` 端口的程序。
- 生成失败：查看 `logs/backend.log` 与 `logs/launcher.log`。
- 找不到下载文件：查看“生成结果”里的 `final_deck.pptx` 路径。
- 杀毒软件误报：优先使用最新 artifact，并加入白名单。
