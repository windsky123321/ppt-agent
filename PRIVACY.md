# Privacy

PPT Agent 默认以本地优先方式运行。

本地会保存：
- 上传的 PDF
- 解析结果与中间 artifacts
- 生成的 PPTX
- 本地模型配置
- 启动与构建日志

不会打包进 EXE 或发布包的内容：
- 真实 API Key
- 用户 `.env`
- 用户日志目录
- 用户上传与生成文件

建议：
- 仅在受信任设备上保存 API Key
- 发布包分发前再次检查 `release/` 内容
