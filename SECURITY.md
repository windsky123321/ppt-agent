# Security

当前版本的安全边界：
- 不在代码、日志、示例配置中硬编码真实 API Key
- 默认使用本地文件存储
- EXE 打包时排除 `.env`、`logs`、`storage`、`uploads`、`release`
- 长需求只能影响展示方式，不能绕过论文事实约束

Windows 打包建议：
- 只从可信 Python 环境构建
- 构建后检查 `release/` 目录内容
- 不要将用户生成物随安装包再次分发

如果发现安全问题：
- 先停止分发当前构建
- 保留 `logs/build_windows.log` 便于排查
- 清理含敏感配置的本地文件后再重新打包
