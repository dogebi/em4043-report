# 2026-08-12 Current Test Run Summary

## Scope

- Source test plan: the `.docx` test plan in `TestCase111`
- Extracted testcase count: 111
- Existing testcase report files: 111 in `test-reports/20260810`
- Automatically runnable scope found for this run: `worker-agent-engine` focused pytest suite, 61 tests

## Testcase Distribution

| Prefix | Count |
|---|---:|
| AUTH | 17 |
| TICKET | 20 |
| EXEC | 24 |
| KB | 15 |
| SEC | 18 |
| INT | 5 |
| DR | 4 |
| PERF | 4 |
| COMP | 4 |
| Total | 111 |

## Commands Run

Initial full focused command:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'; python -m pytest -p pytest_asyncio.plugin -q tests/test_agent/test_executor.py tests/test_agent/test_master.py tests/test_mcp/test_knowledge_search_fields.py tests/test_mcp/test_todo.py tests/test_rag/test_kb_catalog.py tests/test_rag/test_retriever.py
```

Result: timed out after 124 seconds before useful pytest output was emitted.

Split commands:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'; python -m pytest -p pytest_asyncio.plugin -q tests/test_agent/test_executor.py tests/test_agent/test_master.py
```

Result: 16 passed in 115.93s. Python emitted an ignored Redis async connection deallocator warning after pytest completion.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'; python -m pytest -p pytest_asyncio.plugin -q tests/test_mcp/test_knowledge_search_fields.py tests/test_mcp/test_todo.py
```

Result: 19 passed, 3 failed in 10.75s.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'; python -m pytest -p pytest_asyncio.plugin -q tests/test_rag/test_kb_catalog.py tests/test_rag/test_retriever.py
```

Result: 22 passed, 1 failed in 1.60s.

## Automated Result

| Status | Count |
|---|---:|
| PASS | 57 |
| FAIL | 4 |
| Total | 61 |

## Failures

| Test | Failure Summary |
|---|---|
| `tests/test_mcp/test_todo.py::TestTodoSSEEvent::test_replace_publishes_event` | `unittest.mock.patch("app.tasks.agent_tasks._publish_event")` cannot resolve `app.tasks.agent_tasks`; `app.tasks` has no `agent_tasks` attribute at patch time. |
| `tests/test_mcp/test_todo.py::TestTodoSSEEvent::test_update_status_publishes_event` | Same patch target resolution failure for `app.tasks.agent_tasks._publish_event`. |
| `tests/test_mcp/test_todo.py::TestTodoSSEEvent::test_list_does_not_publish_event` | Same patch target resolution failure for `app.tasks.agent_tasks._publish_event`. |
| `tests/test_rag/test_kb_catalog.py::test_list_project_knowledge_bases_maps_rows` | `unittest.mock.patch("app.models.mysql.async_session_factory")` cannot resolve `app.models`; `app` has no `models` attribute at patch time. |

## Manual Scope Still Required

The full 111-case plan includes Jira, ESM, Redis, RAGFlow, LLM, K8s, MySQL, and browser-extension flows. Those were not re-run manually in this pass. Existing per-case reports remain in `test-reports/20260810`, with the 2026-08-11 `AUTH-002` strict recheck still recorded separately.
