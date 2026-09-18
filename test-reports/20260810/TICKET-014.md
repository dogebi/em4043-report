# TICKET-014 会话状态 active 到 completed 流转测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-014 |
| 测试标题 | 会话状态流转：active → completed |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | issue_updated Listener 仅处理 `issuetype` 变更，未处理 Jira 工单状态变为“已关闭”的 Webhook，也未发现触发知识蒸馏流程。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 18 定义 `TICKET-014` 要求 Jira 工单关闭后会话状态变为 completed，可查看/导出/归档，并触发知识蒸馏。 |
| 检查关闭状态 Webhook | FAIL | `JiraIssueWebhookListener::handleUpdated()` 只从 changelog 查找 `field=issuetype`，未处理 `status` 变更。 |
| 检查 active→completed | FAIL | 代码中的完成路径主要是手动阶段推进到最后时置 `SessionStatusEnum::ARCHIVED`，不是关闭 Webhook 置 completed。 |
| 检查知识蒸馏触发 | FAIL | `rg` 未找到工单关闭触发知识蒸馏的实现。 |
| 执行真实关闭事件 | NOT RUN | 本轮未在 Jira 关闭工单。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Listeners\JiraIssueWebhookListener.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\IssueService.php`

## 当前结论

本用例应标记为 `FAIL`。缺少 Jira status closed Webhook 到 completed/蒸馏的链路。
