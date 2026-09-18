# AUTH-009 SOP项目级权限控制测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-009 |
| 测试标题 | SOP项目级权限控制 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 当前实现没有发现项目级 SOP 与任务方案级 SOP 的检索分流，也没有在RAG返回后按项目权限过滤项目级 SOP 的逻辑，因此不能证明项目Y项目级 SOP 不返回。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 12 定义 `AUTH-009` 要求项目Y项目级 SOP 不返回，仅返回项目X项目级 SOP 和所有任务方案级 SOP。 |
| 检查项目级知识库过滤能力 | PARTIAL | `KnowledgeCenterManageService::applyProjectKnowledgeBaseFilter()` 在传入 `project_id` 时可按项目关联 base_id 过滤。 |
| 检查未传项目时的默认安全行为 | FAIL | `projectId === null || <=0` 时直接返回原知识库列表，未按当前用户项目权限自动收敛。 |
| 检查RAG结果过滤 | FAIL | `RagNewNodeHandler` 未按 `scope_type=project`、`scope_project_id` 或当前用户可访问项目过滤返回文档。 |
| 检查任务方案级 SOP 例外返回 | FAIL | 未发现 `scope_type=task_plan` SOP 识别和例外放行逻辑。 |

## 技术检查记录

```text
GET /agent-work-api/v1/knowledge/bases?project_id=3 -> HTTP 200, count=7.
GET /agent-work-api/v1/knowledge/bases -> HTTP 200, count=11.
applyProjectKnowledgeBaseFilter only works when project_id is supplied.
RAG retrieval result enrichment does not include scope_type/source_project/project_id.
```

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Services\Knowledge\KnowledgeCenter\KnowledgeCenterManageService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Engine\Handlers\RagNewNodeHandler.php`
- `D:\dev\cscAI\esm\app\AppAgent\Models\AigcWorkPlan.php`

## 当前结论

本用例应标记为 `FAIL`。项目级 SOP 权限控制的核心需要是“检索结果层面的项目权限过滤”，当前证据显示该闭环不存在或不完整。
