# EXEC-006 auto 流转 AI 自判进入下一阶段测试报告

| 项目 | 内容 |
|---|---|
| 用例编号 | EXEC-006 |
| 测试标题 | auto流转：AI自判进入下一阶段 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 阶段模型有 `auto_advance` 字段，但 Laravel 推进主要由 `advanceStage()` 手动接口触发，未看到 Main Agent 自动评估后进入下一阶段的闭环实现。 |

## 证据

- `AigcWorkPlanStage` 和 `PlanStage` 有 `auto_advance`。
- `IssueService::advanceStage()` 是显式推进逻辑。

## 未满足项

- 未发现 Main Agent 自动判定通过的保存与日志。
- 未验证无需人工干预自动进入阶段 2。
