# TICKET-004 工单删除 Webhook 处理测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-004 |
| 测试标题 | 工单删除 Webhook 处理 |
| 执行日期 | 2026-08-10 |
| 当前状态 | PARTIAL |
| 结论 | issue_deleted 会将 active 会话和工单会话状态标记为 `expired`，并软删除工单，但未调用任务取消逻辑，审计可查看也未做端到端验证。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 15 定义 `TICKET-004` 要求删除工单后终止执行中的 AI 任务、会话 expired、历史保留、审计可查看。 |
| 检查 issue_deleted 分发 | PASS | `JiraIssueWebhookListener` 对 `jira:issue_deleted` 调用 `handleDeleted()`。 |
| 检查会话 expired | PASS | `handleDeleted()` 将该工单 active sessions 更新为 `expired`，并将 issue `session_status` 置为 `expired`。 |
| 检查历史保留 | PASS | `AigcWorkIssue` 开启 `$softDelete = true`，删除是软删除路径。 |
| 检查 AI 任务终止 | FAIL | 删除路径未调用 `SessionService::cancelTask()` 或 `closeSessionsForIssue()`，仅更新 session 状态。 |
| 检查审计可查看 | NOT RUN | 本轮未在界面或日志表验证删除后审计查询。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Listeners\JiraIssueWebhookListener.php`
- `D:\dev\cscAI\esm\app\AppAgent\Models\AigcWorkIssue.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\SessionService.php`

## 当前结论

本用例应标记为 `PARTIAL`。状态流转与软删除存在，但执行中任务取消和审计查询未满足或未验证。
