# TICKET-005 已有项目新工单与 Assets Webhook 测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-005 |
| 测试标题 | 已有项目新工单 + Assets Webhook |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 已有项目新工单链路可复用创建工单和会话逻辑，Basic Auth 验证存在，但 Assets Webhook Listener 仍为 TODO，未处理资产变更。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 15 定义 `TICKET-005` 要求已有项目不重复创建项目，新工单创建记录/匹配方案/创建会话，Assets Webhook Basic Auth 验证通过并处理资产变更。 |
| 检查已有项目不重复创建 | PASS | `createIssueFromWebhook()` 先按 `remote_project_key` 查项目，存在时不调用创建项目。 |
| 检查新工单创建与会话链路 | PASS | 新工单进入 `syncIssueByKey()` 和 `tryMatchAutomation()`。 |
| 检查 Assets Basic Auth | PASS | `JiraWebhookController` 支持 Authorization Basic，`JiraWebhookService::verifyBasicAuth()` 校验配置账号密码。 |
| 检查资产变更处理 | FAIL | `JiraAssetWebhookListener::handle()` 仅有 TODO，没有处理资产变更。 |
| 检查真实 Assets Webhook | NOT RUN | 本轮未发送真实 Assets Webhook。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Controllers\JiraWebhookController.php`
- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Services\JiraWebhookService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Listeners\JiraAssetWebhookListener.php`
- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Services\JiraProjectIssueService.php`

## 当前结论

本用例应标记为 `FAIL`。Assets 资产变更处理是核心验收项，目前没有实现。
