# TICKET-016 工单与会话一一对应测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-016 |
| 测试标题 | 工单-会话一一对应验证 |
| 执行日期 | 2026-08-10 |
| 当前状态 | PARTIAL |
| 结论 | 重复 issue_created Webhook 会因 `remote_issue_key` 已存在而跳过，但会话创建层未看到唯一约束或创建前查重，类型变更还会主动重建新会话。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 18 定义 `TICKET-016` 要求同一工单多次打开和重复 Webhook 始终只有一个会话，且会话名称始终等于工单号。 |
| 检查重复 Webhook | PASS | `createIssueFromWebhook()` 命中已存在 `remote_issue_key` 后直接 `skipped`，不再创建工单/会话。 |
| 检查会话创建唯一性 | FAIL | `SessionService::createSession()` 直接新建 `Session`，未按 `issue_id` 查找已存在会话。 |
| 检查多次打开不创建新会话 | PARTIAL | 详情读取路径只读现有 issue/session，但未执行浏览器多次打开验证。 |
| 检查会话名称=工单号 | FAIL | 首会话 title 为 `summary ?: remote_issue_key`，后续阶段 title 才使用 `remote_issue_key`。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Services\JiraProjectIssueService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\SessionService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\IssueService.php`

## 当前结论

本用例应标记为 `PARTIAL`。重复 Webhook 幂等满足，但会话层 1:1 约束和工单号命名未完全满足。
