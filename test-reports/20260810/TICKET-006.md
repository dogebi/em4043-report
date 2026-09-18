# TICKET-006 Issue_Type 到任务方案全局默认路由测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-006 |
| 测试标题 | Issue_Type → 任务方案全局默认路由 |
| 执行日期 | 2026-08-10 |
| 当前状态 | PARTIAL |
| 结论 | 代码支持无项目级覆盖时回退到租户级/系统级默认任务方案，并加载阶段和 Main Agent 创建会话，但本轮未创建真实 Incident 工单验证配置数据。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 16 定义 `TICKET-006` 要求 Incident 无项目级覆盖时匹配全局默认任务方案，加载阶段和 Agent，并绑定会话。 |
| 检查全局默认匹配 | PASS | `WorkAutomationRepository::resolvePlanForIssueType()` 依次匹配项目级、租户级 `project_id=0`、系统级 `project_id=0,data_space_id=0`。 |
| 检查阶段和 Agent 加载 | PASS | `IssueService::tryMatchAutomation()` 查询首个 `AigcWorkPlanStage`，要求存在 `master_agent_id`。 |
| 检查会话绑定任务方案 | PASS | `SessionService::createSession()` 写入 issue `session_id/session_status/current_stage_id/total_stages`。 |
| 执行真实 Incident Webhook | NOT RUN | 本轮未在 Jira 创建 Incident 工单。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Repositories\WorkAutomationRepository.php`
- `D:\dev\cscAI\esm\app\AppAgent\Repositories\WorkIssueRepository.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\IssueService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\SessionService.php`

## 当前结论

本用例应标记为 `PARTIAL`。代码路径满足主要逻辑，但缺少真实配置和 Webhook 端到端验证。
