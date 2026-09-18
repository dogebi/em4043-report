# TICKET-003 Webhook 幂等性与子工单排除测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-003 |
| 测试标题 | Webhook 幂等性 + 子工单排除 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 重复 issue_created 的幂等检查存在，但未发现对子工单 `parent` 字段的跳过会话创建或追加父工单上下文逻辑。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 15 定义 `TICKET-003` 要求重复事件不重复创建工单/会话，子工单跳过会话创建，并追加到父工单上下文。 |
| 检查重复 Webhook 幂等 | PASS | `createIssueFromWebhook()` 按 `remote_issue_key` 查询，已存在时返回 `status=skipped, reason=already_exists`。 |
| 检查子工单识别 | FAIL | `parseIssuePayload()` 和 `createIssueFromWebhook()` 未处理 `fields.parent`。 |
| 检查子工单跳过会话创建 | FAIL | 创建链路统一进入 `IssueService::tryMatchAutomation()`，未发现子工单排除分支。 |
| 检查父工单上下文追加 | FAIL | 未发现将子工单信息追加到父工单上下文总线或会话消息的实现。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Services\JiraWebhookService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Services\JiraProjectIssueService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\IssueService.php`

## 当前结论

本用例应标记为 `FAIL`。幂等只覆盖重复主工单，子工单验收标准未实现。
