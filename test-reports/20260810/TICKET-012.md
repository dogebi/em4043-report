# TICKET-012 类型变更后执行时间重新计时测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-012 |
| 测试标题 | 类型变更后执行时间重新计时 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 由于类型变更不是追加阶段而是重建会话，未发现“追加时刻重新计时 600 秒”的专用计时规则。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 17 定义 `TICKET-012` 要求新阶段从追加时刻重新计算 600 秒超时，不累计变更前已用时间。 |
| 检查类型变更执行模型 | FAIL | `changeType()` 关闭旧会话并新建会话，不存在追加阶段起点。 |
| 检查 600 秒超时规则 | FAIL | 在类型变更链路未发现 600 秒超时重置逻辑。 |
| 检查不累计旧时间 | NOT RUN | 无追加计时实现可验证。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Repositories\WorkIssueRepository.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\SessionService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Models\AigcWorkPlanStage.php`

## 当前结论

本用例应标记为 `FAIL`。当前代码未实现用例要求的追加阶段 600 秒重新计时语义。
