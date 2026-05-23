# Release Notes

## 版本

- `v0.1.0`
- 发布名称：`PPT Agent Windows v0.1.0`
- 发布时间：`2026-05-24`

## 主要功能

- PDF 转 PPT
- 中文 Web UI
- Windows 双击启动
- Mock 模式测试
- Low Token Mode
- Round 2 修改
- Round 3 精修
- 输出目录管理
- 日志查看
- GitHub Actions 自动构建 Windows exe

## 使用方式

1. 打开 GitHub Release 页面
2. 下载 `PPT-Agent-Windows-Release.zip`
3. 解压并双击 `PPT-Agent.exe`
4. 如果 Windows 阻止运行，点击“更多信息” -> “仍要运行”
5. 第一次使用填写 API Key，或切换到 Mock 模式
6. 上传 PDF，点击“生成 PPT”
7. 在“生成结果”中下载 `final_deck.pptx`

## 已知限制

- 首次使用需要配置 OpenAI API Key，或改用 Mock 模式
- Windows 可能提示未知发布者
- 当前 exe 未做代码签名
- 杀毒软件可能误报
- 真实生成质量依赖模型和 PDF 内容质量

## 常见问题

- Windows 阻止运行
- API Key 未配置
- 端口占用
- 生成失败
- 找不到下载文件
- 杀毒软件误报

## 安全说明

- EXE 不会内置真实 API Key
- release 包不会包含 `.env`
- release 包不会包含 `logs/`、`outputs/`、`uploads/`、`temp/`
- GitHub Actions artifact 不会写入真实 API Key
