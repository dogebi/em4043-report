# EXEC-008 manual 流转人工驳回测试报告

| 项目 | 内容 |
|---|---|
| 用例编号 | EXEC-008 |
| 测试标题 | manual流转：人工驳回 |
| 执行日期 | 2026-08-10 |
| 当前状态 | PARTIAL |
| 结论 | 后端存在 `rollbackStage()` 可回退阶段，表单响应支持 `skip`；但未发现 manual 审核驳回按钮与“不进入下一阶段”的专用状态闭环。 |

## 证据

- `IssueService::rollbackStage()` 可将阶段回退并重新触发目标阶段。
- `submitFormResponse(..., skip=true)` 可提交跳过状态。

## 未满足项

- 未验证人工驳回 UI。
- 未证明驳回原因和重新执行提示。
