# RELEASE NOTES

## v0.2.0-dev

当前分支进入功能开发阶段，重点是：

- 技能扩展能力
- Token 成本透明化

### 新增

- 技能库本地目录与注册表
- mock 技能搜索 provider
- 本地 zip / 文件夹 / URL 占位导入
- 风险扫描与默认禁用策略
- Skill Router 静态建议注入
- Token 使用详情 API
- Token 使用详情前端面板

### 安全约束

- 外部技能默认不执行脚本
- 外部技能默认不读取用户文件
- 外部技能默认不联网
- 外部技能默认不获得 API Key
- Token 统计不记录完整 prompt、PDF 全文或 API Key

## v0.1.0

稳定 Windows 预发布版已完成：

- Windows EXE 构建
- 中文 Web UI
- Low Token Mode
- Round 2 修改
- Round 3 精修
