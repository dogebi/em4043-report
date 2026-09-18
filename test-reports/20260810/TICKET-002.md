# TICKET-002 Webhook Secret 验证失败测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-002 |
| 测试标题 | Webhook Secret 验证失败 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 鉴权失败会阻断业务并记录 Webhook 日志，但返回码为 HTTP 403，不是用例要求的 HTTP 401，且实现使用 `X-Hub-Signature`/Basic Auth 而非 `X-Jira-Webhook-Secret`。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 15 定义 `TICKET-002` 要求错误 `X-Jira-Webhook-Secret` 返回 HTTP 401，不处理业务逻辑，并记录安全日志。 |
| 检查错误鉴权响应 | FAIL | `JiraWebhookController` 在 HMAC、Basic、无鉴权失败时均返回 HTTP 403。 |
| 检查业务逻辑阻断 | PASS | 鉴权失败在 payload 解析和 `dispatchWebhookEvent()` 之前直接返回。 |
| 检查日志记录 | PASS | `createLog()` 先写入日志，失败后 `markLog()` 更新为 `AUTH_FAILED` 或 `NO_AUTH`。 |
| 检查指定 Secret Header | FAIL | 当前代码读取 `X-Hub-Signature`，未读取 `X-Jira-Webhook-Secret`。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Controllers\JiraWebhookController.php`
- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Services\JiraWebhookService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Models\AigcWorkWebhookLog.php`

## 当前结论

本用例应标记为 `FAIL`。安全拦截存在，但关键验收点 HTTP 401 和 `X-Jira-Webhook-Secret` 不满足。
