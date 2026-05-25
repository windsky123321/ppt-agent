# RELEASE NOTES

## v0.2.0-dev

当前分支进入功能开发阶段，重点是：

- 技能扩展能力
- Token 成本透明化
- Mock / 正式生成区分
- 中文 UI 和质量门控完善

### 本轮重点修复

- Mock 模式增加黄色提示，明确“仅用于流程测试”
- Mock 结果统一标记为“模拟生成完成”或“测试文件”
- Critic 未通过时，不再把结果标记为正式可交付
- 下载逻辑优先区分 `draft_deck.pptx` 和 `final_deck.pptx`
- 质量检查结果和论文结构预览优先显示中文

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
