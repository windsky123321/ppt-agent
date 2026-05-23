# PPT Agent Windows v0.1.0

## 版本信息

- 版本：`v0.1.0`
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
- GitHub Actions 自动构建 Windows EXE

## 使用方式

1. 打开 GitHub Release 页面
2. 下载 `PPT-Agent-Windows-v0.1.0.zip`
3. 解压后进入 `PPT-Agent-Windows-v0.1.0/`
4. 双击 `PPT-Agent.exe`
5. 如果 Windows 阻止运行，点击“更多信息” -> “仍要运行”
6. 第一次使用填写 API Key，或切换到 Mock 模式
7. 上传 PDF
8. 点击“生成 PPT”
9. 在“生成结果”区域下载 `final_deck.pptx`

## 已知限制

- 首次真实生成需要配置 OpenAI API Key
- Windows 可能提示未知发布者
- 当前 EXE 未做代码签名
- 杀毒软件可能误报
- 真实生成质量依赖 PDF 内容和模型能力

## 常见问题

- Windows 阻止运行
- API Key 未配置
- 端口被占用
- 生成失败
- 找不到下载文件
- 杀毒软件误报

## 安全说明

- API Key 不会打包进 EXE
- `.env` 不会上传到 GitHub Release
- 用户 PDF 和生成 PPT 不会包含在发布包中
- `logs/`、`outputs/`、`uploads/`、`temp/` 不会包含在发布包中
- 日志不会记录 API Key
