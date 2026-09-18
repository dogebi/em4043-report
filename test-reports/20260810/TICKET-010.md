# TICKET-010 工单类型变更后阶段追加测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-010 |
| 测试标题 | 工单类型变更 → 阶段追加 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | issue_updated 能识别 `issuetype` 变更并重新匹配任务方案，但实现是关闭旧会话并重建新会话，不是将新方案阶段追加到当前会话尾部。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 17 定义 `TICKET-010` 要求类型变更后停止后续调度、等待当前子任务完成、匹配新方案、将新阶段追加到当前会话尾部并继续执行。 |
| 检查 issuetype 变更识别 | PASS | `JiraIssueWebhookListener::handleUpdated()` 从 changelog 中查找 `field=issuetype`。 |
| 检查重新匹配新方案 | PASS | Listener 调用 `WorkIssueRepository::changeType()`，内部重新调用 `resolvePlanForIssueType()`。 |
| 检查追加到当前会话尾部 | FAIL | `changeType()` 清空 `session_id/current_stage_id/current_stage_name`，调用 `closeSessionsForIssue()` 后再 `tryMatchAutomation()` 创建新会话。 |
| 检查等待当前子任务完成 ≤30 秒 | FAIL | 未发现等待当前子任务完成的 30 秒逻辑。 |
| 执行真实类型变更 Webhook | NOT RUN | 本轮未在 Jira 执行 Service Request → Incident 类型变更。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Listeners\JiraIssueWebhookListener.php`
- `D:\dev\cscAI\esm\app\AppAgent\Repositories\WorkIssueRepository.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\SessionService.php`

## 当前结论

本用例应标记为 `FAIL`。类型变更链路存在，但行为模型与“阶段追加”验收标准不一致。
