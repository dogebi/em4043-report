# AUTH-007 知识库项目资产权限隔离测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-007 |
| 测试标题 | 知识库项目资产权限隔离 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 项目列表和项目详情具备项目访问权限收敛，但知识库检索链路没有发现按当前用户可访问项目过滤检索结果的完整实现，不能证明“仅返回项目X知识文档，项目Y文档不出现”。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 12 定义 `AUTH-007` 要求用户A仅有项目X权限时，关键词同时匹配X/Y项目文档，结果仅返回X项目文档并标注来源项目。 |
| 检查项目列表权限收敛 | PASS | `ProjectService::list()` 使用 `whereIn('id', accessibleProjectIds())`，项目列表只返回当前用户可访问项目。 |
| 实际调用项目列表 | PASS | 使用用户提供 Bearer token 调用 `GET http://csc-ai.natec.cn/agent-work-api/v1/projects` 返回 HTTP 200，当前可见项目数为 3。 |
| 检查项目级知识库列表 | PASS | `GET /agent-work-api/v1/projects/3/knowledge-bases` 返回 HTTP 200，项目3知识库数量为 7。 |
| 检查知识库全局列表是否自动按项目权限过滤 | FAIL | `GET /agent-work-api/v1/knowledge/bases` 返回 HTTP 200，数量为 11；代码中未传 `project_id` 时 `applyProjectKnowledgeBaseFilter()` 直接返回原列表。 |
| 检查RAG检索结果是否按项目权限过滤 | FAIL | `RagNewNodeHandler::performRagRetrieval()` 仅向 RAG 服务传 `dataset_ids`，返回后用 `AigcAgentKnowledgeFile::whereIn(rag_document_id)` 补充文件信息，未发现 `ProjectAccessCacheService`、`accessibleProjectIds()` 或 `project_id` 过滤。 |
| 检查结果卡片来源项目标注 | FAIL | RAG 结果补充字段仅包含 `id/name/vector_file_id/file_type`，未发现来源项目字段。 |

## 技术检查记录

```text
GET /agent-work-api/v1/projects -> HTTP 200, visible project count=3.
GET /agent-work-api/v1/knowledge/bases -> HTTP 200, knowledge base count=11.
GET /agent-work-api/v1/knowledge/bases?project_id=3 -> HTTP 200, knowledge base count=7.
GET /agent-work-api/v1/projects/3/knowledge-bases -> HTTP 200, knowledge base count=7.
RAG handler does not call ProjectAccessCacheService or accessibleProjectIds during retrieval result filtering.
```

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\ProjectService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\Knowledge\KnowledgeCenter\KnowledgeCenterManageService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Controllers\WorkApi\V1\KnowledgeController.php`
- `D:\dev\cscAI\esm\app\AppAgent\Engine\Handlers\RagNewNodeHandler.php`

## 当前结论

本用例应标记为 `FAIL`。项目资源入口具备一定权限收敛，但知识库检索链路缺少按用户项目权限过滤和来源项目标注的证据，无法满足验收标准。
