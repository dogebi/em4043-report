# TICKET-001 新项目首个工单 Webhook 触发测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-001 |
| 测试标题 | 新项目首个工单 Webhook 触发 |
| 执行日期 | 2026-08-10 |
| 当前状态 | PARTIAL |
| 结论 | 代码具备 issue_created 解析、项目自动创建、工单创建、任务方案匹配和会话创建链路，但未按用例的 `X-Jira-Webhook-Secret` 头验证，且会话标题不保证等于工单号。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 15 定义 `TICKET-001` 要求新项目首个工单触发 `jira:issue_created` 后自动创建项目、工单、匹配任务方案、创建 active 会话。 |
| 检查 Webhook 鉴权 | PARTIAL | 控制器支持 `X-Hub-Signature` HMAC 和 Basic Auth，不是用例写明的 `X-Jira-Webhook-Secret`。 |
| 检查项目自动创建 | PASS | `JiraProjectIssueService::createIssueFromWebhook()` 找不到项目时调用 `JiraProjectService::createProjectFromWebhook()`。 |
| 检查工单创建 | PASS | 新工单通过 `syncIssueByKey()` 写入 `aigc_work_issues`。 |
| 检查任务方案匹配 | PASS | `WorkIssueRepository::storeBefore()` 按 `issue_type` 调用 `WorkAutomationRepository::resolvePlanForIssueType()`。 |
| 检查 AI 会话创建 | PASS | `IssueService::tryMatchAutomation()` 找到方案和首阶段 Main Agent 后调用 `SessionService::createSession()`，会话状态为 `active`。 |
| 检查会话名称=工单号 | FAIL | `tryMatchAutomation()` 传入 title 为 `summary ?: remote_issue_key`，不保证等于工单号。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Controllers\JiraWebhookController.php`
- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Services\JiraProjectIssueService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Services\JiraProjectService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\IssueService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\SessionService.php`

## 当前结论

本用例应标记为 `PARTIAL`。主链路存在，但鉴权头和会话名称与验收标准不完全一致，且本轮未触发真实 Jira Webhook。
