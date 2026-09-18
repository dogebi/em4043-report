# AUTH-008 SOP任务方案级权限突破测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-008 |
| 测试标题 | SOP任务方案级权限突破 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 当前代码未发现任务方案级 SOP 的独立检索模型、`scope_type=task_plan` 元数据、跨项目放行逻辑和结果标注能力，不能满足任务方案级 SOP 不受项目权限限制的验收标准。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 12 定义 `AUTH-008` 要求任务方案级 SOP 正常返回，标注 `scope_type=task_plan`，标注来源项目Y，且不受项目权限限制。 |
| 检查任务方案 scope 定义 | FAIL | `AigcWorkPlan` 仅声明 `scope_type` 为 `global, project`，未发现 `task_plan` scope。 |
| 检查SOP检索结果是否标注 `scope_type=task_plan` | FAIL | `RagNewNodeHandler` 的结果补充字段未包含 `scope_type`、`task_plan_id` 或来源项目。 |
| 检查跨项目放行逻辑 | FAIL | 未发现针对任务方案级 SOP 的“跳过项目权限过滤”分支。 |
| 检查实际数据/接口 | NOT RUN | 未发现可直接验证 `scope_type=task_plan` SOP 的现成接口或测试数据。 |

## 技术检查记录

```text
AigcWorkPlan scope comment: global, project.
WorkPlanRepository filters plan options by apply scope, not SOP retrieval scope.
RAG result enrichment returns id/name/vector_file_id/file_type only.
No code search hit proving task_plan scoped SOP retrieval exemption.
```

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Models\AigcWorkPlan.php`
- `D:\dev\cscAI\esm\app\AppAgent\Repositories\WorkPlanRepository.php`
- `D:\dev\cscAI\esm\app\AppAgent\Engine\Handlers\RagNewNodeHandler.php`
- `D:\dev\cscAI\esm\database\db-work\init.sql`

## 当前结论

本用例应标记为 `FAIL`。当前实现未覆盖“任务方案级 SOP 跨项目可检索并标注来源”的核心要求。
