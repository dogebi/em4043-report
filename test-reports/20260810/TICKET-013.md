# TICKET-013 已完成阶段不重复执行测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-013 |
| 测试标题 | 已完成阶段不重复执行 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 类型变更路径重建新会话并从新方案首阶段开始，未发现比较已完成阶段并仅追加未执行阶段的去重逻辑。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 17 定义 `TICKET-013` 要求新方案含相同类型阶段时，已完成阶段不重复执行，仅追加尚未执行阶段，并保留变更前阶段记录。 |
| 检查已完成阶段比较 | FAIL | `changeType()` 未读取旧完成阶段并与新方案阶段做差集比较。 |
| 检查仅追加未执行阶段 | FAIL | `tryMatchAutomation()` 按新方案首阶段创建会话，不是追加未执行阶段。 |
| 检查变更前阶段记录保留 | FAIL | `closeSessionsForIssue()` 将旧 `SessionWorkflowStage.issue_id` 置为 0，避免 detail 混入旧阶段。 |
| 执行真实重叠阶段类型变更 | NOT RUN | 本轮未构造重叠阶段方案进行端到端验证。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Repositories\WorkIssueRepository.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\SessionService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\IssueService.php`

## 当前结论

本用例应标记为 `FAIL`。当前实现无法满足“已完成阶段不重复执行”的追加模型。
