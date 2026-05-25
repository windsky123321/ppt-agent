# Token Usage

## 是什么

Token 使用详情用于帮助你查看每次生成 PPT 的资源消耗情况，包括：

- 按任务查看
- 按阶段查看
- 按模型查看
- 导出 CSV / JSON

## Mock 模式

- Mock 模式会标记 `mock=true`
- Mock 仅用于流程测试
- Mock 的 Token 结果不代表真实计费

## 能看到什么

- 输入 Token
- 输出 Token
- 总 Token
- 请求次数
- 重试次数
- 失败次数
- 估算成本

## 看不到什么

系统不会记录：

- API Key
- 完整 prompt
- PDF 全文
- 用户隐私文本

## 为什么有些记录是 unknown

- 某些 provider 不返回 usage
- 系统会如实记录为 `unknown`
- 不会编造 token 数值

## 本地保存位置

- 开发模式：`usage/`
- Windows EXE：`%LOCALAPPDATA%/PPT Agent/usage/`

## 如何导出

- 在“Token 使用详情”面板中导出 CSV
- 或导出 JSON

## 如何清空

- 在“Token 使用详情”面板中点击“清空统计”
- 该操作只清理本地统计，不影响已有 PPT 文件
