# TICKET-017 创建任务方案基本定义测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-017 |
| 测试标题 | 创建任务方案基本定义 |
| 执行日期 | 2026-08-10 |
| 当前状态 | PARTIAL |
| 结论 | 任务方案可创建，名称格式和唯一性校验、默认启用状态存在；但用例要求的 `Issue_Type` 单选不在任务方案表单中，而是在自动化路由绑定侧实现。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 进入任务方案管理并新建 | PASS | `WorkPlanRepository::store()` 调用父级新增并写入任务方案。 |
| 填写名称和保存 | PASS | `storeBefore()` 执行 `validateNameFormat()` 和 `checkNameUnique()`。 |
| 默认启用状态 | PASS | `store()` 强制设置 `status = WorkPlanStatusEnum::ENABLED`。 |
| 设置范围 | PARTIAL | 模型和编辑数据存在 `scopeProject`、`scope_project_name`，但 `WorkPlan\FormSchemaTrait` 中范围区块被注释。 |
| Issue_Type 单选 | FAIL | 当前任务方案表单未发现 `Issue_Type` 控件；类型到方案的选择属于 `WorkAutomationRepository` 路由匹配逻辑。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Repositories\WorkPlanRepository.php`
- `D:\dev\cscAI\esm\app\AppAgent\AmisSchema\WorkPlan\FormSchemaTrait.php`
- `D:\dev\cscAI\esm\app\AppAgent\Repositories\WorkAutomationRepository.php`

## 当前结论

本用例标记为 `PARTIAL`。基础任务方案创建能力存在，但未满足“任务方案创建表单内 Issue_Type 单选和范围配置”的完整验收。
