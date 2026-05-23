# Windows 一键启动说明

## 1. 运行环境

请先确保你的 Windows 电脑安装了：

- Python 3.11 或更高版本
- Node.js 18 或更高版本

## 2. 一键启动

直接双击项目根目录中的：

- `start_windows.bat`

它会自动：

1. 检查 Python / Node.js / npm
2. 创建后端虚拟环境（如果缺失）
3. 安装后端依赖
4. 安装前端依赖
5. 自动创建 `.env`
6. 启动后端
7. 启动前端
8. 自动打开浏览器

默认地址：

- 前端：http://127.0.0.1:5173
- 后端：http://127.0.0.1:8000

## 3. Web UI 使用流程

1. 打开网页
2. 进入“模型配置”
3. 如果没有 API Key，点击“使用 Mock 模式”
4. 上传论文 PDF
5. 选择或创建 Profile
6. 选择 Deck Mode
7. 在长需求输入框中粘贴自然语言要求
8. 点击生成 PPT
9. 下载 `final_deck.pptx`

## 4. 如何配置模型

推荐流程：

- 如果只是本地体验：使用 Mock 模式
- 如果使用 OpenAI-Compatible 服务：
  - 填入 Base URL
  - 填入 API Key
  - 填入模型名称
  - 点击“测试连接”
  - 再保存配置

## 5. 如何停止服务

双击：

- `stop_windows.bat`

## 6. 常见问题排查

### Python not found

提示未找到 Python：

- 请安装 Python 3.11+
- 安装时勾选“Add Python to PATH”

### Node not found

提示未找到 Node.js：

- 请安装 Node.js 18+

### 端口被占用

如果提示 8000 或 5173 被占用：

- 关闭占用该端口的程序
- 再重新双击 `start_windows.bat`

### API Key 无效

- 检查 Base URL 是否正确
- 检查 API Key 是否填写错误
- 检查模型名称是否可用
- 可以先切换到 Mock 模式验证整套流程

### 后端启动失败

查看：

- `logs/backend.log`
- `logs/startup.log`

### 前端空白页

查看：

- `logs/frontend.log`

### PDF 解析失败

- 可能是扫描版 PDF 或加密 PDF
- 可先用文本型 PDF 测试

### PPTX 生成失败

- 查看 `logs/backend.log`
- 检查是否有异常 artifact

## 7. 日志位置

- `logs/backend.log`
- `logs/frontend.log`
- `logs/startup.log`
