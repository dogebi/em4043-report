# TICKET-007 项目级路由覆盖全局默认测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-007 |
| 测试标题 | 项目级路由覆盖全局默认 |
| 执行日期 | 2026-08-10 |
| 当前状态 | PARTIAL |
| 结论 | 代码优先匹配项目级任务方案，能覆盖全局默认，但未发现返回或界面展示配置来源为“项目级”的证据。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 16 定义 `TICKET-007` 要求项目 X 的 Incident 优先使用项目级任务方案，不使用全局默认，界面显示来源为“项目级”。 |
| 检查项目级优先级 | PASS | `resolvePlanForIssueType()` 的 `orderByRaw CASE` 将 `project_id=当前项目 AND data_space_id=项目数据空间` 排第一。 |
| 检查不使用全局默认 | PASS | 匹配排序在项目级命中时不会落到后续租户级或系统级默认。 |
| 检查界面显示来源 | FAIL | `resolvePlanForIssueType()` 仅返回 `task_plan_id/name/display_name`，未返回 `source=项目级` 等来源字段。 |
| 执行项目 X Incident Webhook | NOT RUN | 本轮未在 Jira 创建项目 X Incident 工单。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Repositories\WorkAutomationRepository.php`
- `D:\dev\cscAI\esm\app\AppAgent\AmisSchema\WorkIssue\TableSchemaTrait.php`

## 当前结论

本用例应标记为 `PARTIAL`。路由覆盖逻辑存在，但界面来源展示和端到端数据验证未满足。
