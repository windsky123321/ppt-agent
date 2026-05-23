# PPT Agent v0.1.0

PPT Agent `v0.1.0` 是面向 Windows 用户的预发布版本，当前已经支持：

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

## 普通用户如何下载和运行

1. 打开 GitHub Release 页面
2. 下载 `PPT-Agent-Windows-Release.zip`
3. 解压后进入 `release/`
4. 双击 `PPT-Agent.exe`
5. 如果 Windows 阻止运行，点击“更多信息” -> “仍要运行”
6. 第一次使用时填写 API Key，或直接切换到 Mock 模式
7. 上传 PDF
8. 点击“生成 PPT”
9. 在“生成结果”中下载 `final_deck.pptx`

## GitHub Actions artifact

工作流名称：

- `Build Windows EXE`

artifact 名称：

- `PPT-Agent-Windows-Release`

## release 包内容

应包含：

- `PPT-Agent.exe`
- `README.md`
- `WINDOWS_QUICKSTART.md`
- `RELEASE_NOTES.md`
- `.env.example`

不应包含：

- `.env`
- `logs/`
- `outputs/`
- `uploads/`
- `temp/`
- 用户 PDF
- 生成 PPTX
- `node_modules/`
- `__pycache__/`

## API Key 说明

- EXE 不会内置真实 API Key
- GitHub Actions artifact 不会写入真实 API Key
- `.env.example` 只保留空占位
- API Key 只保存在用户本机配置中

## Mock 模式说明

Mock 模式适合首次验收和回归测试：

- 无需真实 API Key
- 可以上传测试 PDF
- 可以完整跑通生成、下载、Round 2、Round 3

## 常见问题

- Windows 阻止运行：右键 EXE，打开“属性”，如有“解除锁定”则先勾选。
- API Key 未配置：去“模型配置”填写 API Key，或切换到 Mock 模式。
- 端口占用：关闭占用 `8000` 端口的程序后重试。
- 生成失败：查看 `logs/backend.log` 和 `logs/launcher.log`。
- 找不到下载文件：查看“生成结果”面板中的 `final_deck.pptx` 路径。
- 杀毒软件误报：优先使用最新 artifact，必要时加入白名单。
