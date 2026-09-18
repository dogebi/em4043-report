# 실패 케이스 재실행 기록

## 실행 범위

- 기준 리포트: `test-reports/20260810`
- 기준 상태: `FAIL` 50건
- 직접 실행한 자동 테스트: `worker-agent-engine`의 Agent、MCP、RAG 관련 테스트 61건
- 실행 명령: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -p pytest_asyncio.plugin -q tests/test_agent/test_executor.py tests/test_agent/test_master.py tests/test_mcp/test_knowledge_search_fields.py tests/test_mcp/test_todo.py tests/test_rag/test_kb_catalog.py tests/test_rag/test_retriever.py`

## 실행 결과

| 결과 | 건수 |
|---|---:|
| PASS | 57 |
| FAIL | 4 |
| 합계 | 61 |

자동 테스트 PASS 집계는 다음과 같다.

| 테스트 영역 | 실행 | PASS | FAIL |
|---|---:|---:|---:|
| Agent Executor | 10 | 10 | 0 |
| Master Agent | 6 | 6 | 0 |
| Knowledge Search MCP | 6 | 6 | 0 |
| Todo MCP | 16 | 13 | 3 |
| Knowledge Base Catalog | 3 | 2 | 1 |
| RAG Retriever | 20 | 20 | 0 |
| 합계 | 61 | 57 | 4 |

실패한 자동 테스트는 다음과 같다.

| 테스트 | 원인 |
|---|---|
| `TestTodoSSEEvent::test_replace_publishes_event` | 테스트가 존재하지 않는 `app.tasks.agent_tasks` 모듈 경로를 patch함 |
| `TestTodoSSEEvent::test_update_status_publishes_event` | 테스트가 존재하지 않는 `app.tasks.agent_tasks` 모듈 경로를 patch함 |
| `TestTodoSSEEvent::test_list_does_not_publish_event` | 테스트가 존재하지 않는 `app.tasks.agent_tasks` 모듈 경로를 patch함 |
| `test_list_project_knowledge_bases_maps_rows` | 테스트가 존재하지 않는 `app.models.mysql` 모듈 경로를 patch함 |

## 111개 케이스 전체 재테스트 범위

원본 111개 케이스 전체를 동일한 방식으로 확정하려면 Jira、ESM、Redis、RAGFlow、LLM、K8s、MySQL、Chrome/Edge 실행 환경과 테스트 계정·데이터가 필요하다. 현재 환경에서 실제 실행 결과로 확정된 것은 위 자동 테스트 61건이다.

나머지 케이스는 원본 리포트의 기존 결과를 임의로 PASS로 바꾸지 않고 다음과 같이 유지한다.

- 기존 `FAIL` 및 `PARTIAL` 케이스는 구현 보완 또는 실제 통합 환경 검증 후 재실행 대상이다.
- 기존 `NOT RUN` 케이스는 해당 외부 환경을 준비한 뒤 실행 대상이다.
- K8s Pod 삭제、MySQL 장애 전환、Jira/LLM 중단처럼 파괴적인 장애 주입은 승인과 복구 절차 없이 실행하지 않는다.

## 재실행 보류

다음 유형은 현재 TestCase111 폴더에서 안전하게 직접 실행할 수 없다.

- Jira 로그인·Webhook·권한 변경 및 실제 Jira 중단 복구가 필요한 케이스.
- K8s Pod 삭제, MySQL 장애 전환, Redis/LLM 중단처럼 외부 인프라 장애 주입이 필요한 케이스.
- Chrome/Edge 다중 버전 및 1920x1080 브라우저 UI 검증이 필요한 케이스.
- 코드에 요구 기능이 없다고 기록된 케이스는 테스트 실행보다 구현 보완 후 재검증이 필요하다.

## 다음 실행 순서

1. 자동 테스트의 오래된 patch 경로 4건을 현재 모듈 경로로 정비한 뒤 재실행한다.
2. P0 실패 케이스를 기능 영역별로 재실행한다.
3. 외부 환경을 준비한 뒤 Jira、Redis、성능、보안、容灾 케이스를 별도 실행한다.
