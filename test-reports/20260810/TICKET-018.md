# TICKET-018 阶段编排配置 Main Agent 测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-018 |
| 测试标题 | 阶段编排：配置 Main Agent |
| 执行日期 | 2026-08-10 |
| 当前状态 | PARTIAL |
| 结论 | 阶段创建、Main Agent 绑定、默认超时和 Agent 版本关系有代码支持；但未证明阶段表单可设置 `模型规格=high_precision`，当前数据库调整中还出现过 `model_spec` 移除痕迹。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 添加阶段 1 | PASS | `WorkPlanStageRepository::store()` 自动计算同方案内 `sort_order` 后新增阶段。 |
| 配置 Main Agent | PASS | `WorkPlanStage\InfoBaseSchemaTrait` 提供必填 `master_agent_id`，并按 `WorkAgentTypeEnum::MASTER` 拉取选项。 |
| 配置名称、角色、Prompt | PARTIAL | 阶段名称存在；Agent 角色和系统 Prompt 在 `WorkAgentRepository` 中校验 `role` 必填。 |
| 模型规格为 high_precision | FAIL | 当前阶段表单只绑定 `master_agent_id`，未看到阶段级模型规格控件或保存逻辑。 |
| Prompt 版本管理生效 | PARTIAL | `AigcWorkAgent::versions()` 和 `aigc_work_agent_versions` 表存在，但本次未执行真实版本切换验证。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Repositories\WorkPlanStageRepository.php`
- `D:\dev\cscAI\esm\app\AppAgent\AmisSchema\WorkPlanStage\InfoBaseSchemaTrait.php`
- `D:\dev\cscAI\esm\app\AppAgent\Repositories\WorkAgentRepository.php`
- `D:\dev\cscAI\esm\app\AppAgent\Models\AigcWorkAgent.php`

## 当前结论

本用例标记为 `PARTIAL`。阶段和 Main Agent 绑定成立，但模型规格和 Prompt 版本生效未达到可验收闭环。
