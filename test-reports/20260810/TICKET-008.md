# TICKET-008 无匹配任务方案进入 pending 状态测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-008 |
| 测试标题 | 无匹配任务方案 → pending 状态 |
| 执行日期 | 2026-08-10 |
| 当前状态 | PARTIAL |
| 结论 | 无任务方案时会将 `session_status` 置为 `pending` 且不创建会话，但异常原因只作为返回消息出现，未看到持久化异常原因字段。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 16 定义 `TICKET-008` 要求 CustomType 无匹配时工单 pending、session_status pending、记录异常原因、不创建任务方案实例。 |
| 检查无匹配返回 | PASS | `resolvePlanForIssueType()` 未命中时返回 `task_plan_id=0`。 |
| 检查 pending 状态 | PASS | `IssueService::tryMatchAutomation()` 无 taskPlan 时设置 `session_status=SessionStatusEnum::PENDING`。 |
| 检查不创建会话 | PASS | 无 taskPlan 分支直接返回，不调用 `SessionService::createSession()`。 |
| 检查异常原因持久化 | FAIL | 仅返回消息 `未匹配到任务方案，工单已创建为草稿`，未找到 issue 上保存异常原因的字段或日志。 |
| 执行真实 CustomType 工单 | NOT RUN | 本轮未创建 CustomType 工单。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Repositories\WorkAutomationRepository.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\IssueService.php`

## 当前结论

本用例应标记为 `PARTIAL`。pending 与不创建会话满足，但“记录异常原因”缺少持久化证据。
