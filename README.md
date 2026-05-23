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
- GitHub Actions 自动构建 Windows EXE

## 最新版本下载

普通用户建议从 GitHub Release 下载正式发布包：

1. 打开 GitHub Release 页面
2. 下载 `PPT-Agent-Windows-v0.1.0.zip`
3. 解压后进入 `PPT-Agent-Windows-v0.1.0/`
4. 双击 `PPT-Agent.exe`

如果你是在验证持续集成构建，也可以从 GitHub Actions 下载构建 artifact：

- workflow：`Build Windows EXE`
- artifact：`PPT-Agent-Windows-Release`

## Windows 运行说明

1. 双击 `PPT-Agent.exe`
2. 如果 Windows 阻止运行，点击“更多信息” -> “仍要运行”
3. 等待浏览器自动打开中文 Web UI
4. 第一次使用时填写 API Key，或切换到 Mock 模式
5. 上传 PDF
6. 点击“生成 PPT”
7. 在“生成结果”区域下载 `final_deck.pptx`

## 发布包内容

正式发布 zip 解压后应包含：

- `PPT-Agent.exe`
- `README.md`
- `WINDOWS_QUICKSTART.md`
- `RELEASE_NOTES.md`
- `TROUBLESHOOTING.md`
- `.env.example`

正式发布包不会包含：

- `.env`
- `logs/`
- `outputs/`
- `uploads/`
- `temp/`
- 用户 PDF
- 生成的 PPTX
- `node_modules/`
- `__pycache__/`

## API Key 说明

- EXE 不会内置真实 API Key
- GitHub Release zip 不会写入真实 API Key
- GitHub Actions artifact 不会写入真实 API Key
- `.env.example` 只保留空占位
- API Key 只保存在用户本机配置中

## Mock 模式说明

Mock 模式适合首次验收和回归测试：

- 无需真实 API Key
- 可上传测试 PDF
- 可完整验证上传、生成、下载流程
- 可用于 Round 2 和 Round 3 回归检查

## 常见问题

- Windows 阻止运行：右键 EXE，打开“属性”，如有“解除锁定”则先勾选。
- API Key 未配置：进入“模型配置”填写 API Key，或切换到 Mock 模式。
- 端口被占用：关闭占用 `8000` 端口的程序后重试。
- 生成失败：查看 `logs/backend.log` 和 `logs/launcher.log`。
- 找不到下载文件：查看“生成结果”区域中的输出文件路径。
- 杀毒软件误报：优先使用最新 Release 包，必要时加入白名单。
