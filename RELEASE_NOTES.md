# Release Notes

## Windows EXE Packaging Fix

本次更新补齐了 Windows `.exe` 打包的最后一公里：

- 新增 Windows 打包预检
- 新增 PyInstaller 自动安装与中文失败提示
- 新增 `packaging/wheelhouse/` 离线安装支持
- 修复 `packaging/launcher.spec`，输出 `PPT-Agent.exe`
- 修复 frozen 场景下的前端静态资源与运行目录解析
- 新增 `release/PPT-Agent-Portable/` portable 兜底包
- 构建日志统一输出到 `logs/build_windows.log`
- 新增 GitHub Actions `Build Windows EXE` 自动构建流程
- 新增 `scripts/check_windows_release.py` 发布目录校验脚本

安全说明：

- EXE 不会内置真实 API Key
- 发布包不会打入 `.env`
- 发布包不会打入 `logs`、`storage`、`outputs`、`temp` 中的用户文件

已知说明：

- 当前桌面入口仍采用“launcher + 默认浏览器”模式
- 如果当前环境无法联网安装 PyInstaller，脚本会明确提示手动执行 `python -m pip install pyinstaller`
- GitHub Actions 构建完成后，可直接下载 artifact `PPT-Agent-Windows-Release`
