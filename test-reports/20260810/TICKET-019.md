# TICKET-019 阶段编排配置 Sub-Agent 及依赖测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-019 |
| 测试标题 | 阶段编排：配置 Sub-Agent 及依赖 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 阶段可以选择多个 Sub-Agent，默认超时 300 秒存在；但未发现 Sub-Agent A/B 依赖关系、串行依赖执行策略或依赖持久化字段。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 添加 Sub-Agent A | PASS | `InfoBaseSchemaTrait` 提供 `sub_agent_ids` 多选控件。 |
| 添加 Sub-Agent B | PASS | `sub_agent_ids` 支持多个 Sub Agent ID，模型中 cast 为 JSON。 |
| 配置 B 依赖 A | FAIL | `aigc_work_plan_stages` 只保存 `sub_agent_ids`，未发现 `dependency`、`depends_on` 或等价依赖结构。 |
| 设置执行策略 | FAIL | 未发现阶段内 Sub-Agent 串行/并行执行策略字段。 |
| 默认超时 300 秒 | PASS | 表单 `timeout_seconds` 默认值为 300，DB 字段默认值也是 300。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\AmisSchema\WorkPlanStage\InfoBaseSchemaTrait.php`
- `D:\dev\cscAI\esm\app\AppAgent\Models\AigcWorkPlanStage.php`
- `D:\dev\cscAI\esm\database\db-work\init.sql`

## 当前结论

本用例标记为 `FAIL`。Sub-Agent 列表能力存在，但依赖编排的核心验收项不存在。
