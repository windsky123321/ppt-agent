# Windows 快速开始 v0.1.0

## 下载

推荐从 GitHub Release 下载正式发布包：

1. 打开 GitHub Release 页面
2. 下载 `PPT-Agent-Windows-v0.1.0.zip`
3. 解压后进入 `PPT-Agent-Windows-v0.1.0/`

如果你是在验证构建流程，也可以从 GitHub Actions 下载：

- workflow：`Build Windows EXE`
- artifact：`PPT-Agent-Windows-Release`

## 运行

1. 双击 `PPT-Agent.exe`
2. 如果 Windows 阻止运行，点击“更多信息” -> “仍要运行”
3. 等待浏览器自动打开

## 第一次启动

如果本机还没有 `.env`：

- 启动器会基于 `.env.example` 自动创建
- 不会覆盖已有 `.env`

建议按以下顺序操作：

1. 打开“模型配置”
2. 填写 API Key，或切换到 Mock 模式
3. 返回工作台上传 PDF
4. 点击“生成 PPT”
5. 在“生成结果”区域下载 `final_deck.pptx`

## Mock 模式

如果暂时没有 API Key：

1. 进入“模型配置”
2. 点击“切换到 Mock 模式”
3. 保存配置
4. 上传测试 PDF 验证完整流程

## API Key 说明

- API Key 不会写入 EXE
- API Key 不会写入 GitHub Release zip
- API Key 不会写入 GitHub Actions artifact
- API Key 不会写入示例配置
- 真实 Key 仅保存在本机运行时配置中

## 日志与输出

- 启动日志：`logs/launcher.log`
- 后端日志：`logs/backend.log`
- 生成结果：网页中的“生成结果”区域
- 输出目录：可在网页中直接打开

## 常见问题

- Windows 阻止运行
- API Key 未配置
- 端口被占用
- 生成失败
- 找不到下载文件
- 杀毒软件误报
