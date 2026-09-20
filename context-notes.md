# Context Notes

- 2026-08-12 current test run: DOCX plan contains 111 unique testcase IDs: AUTH 17, TICKET 20, EXEC 24, KB 15, SEC 18, INT 5, DR 4, PERF 4, COMP 4.
- 2026-08-12 existing testcase coverage: `test-reports/20260810` contains 111 per-case markdown reports matching the DOCX testcase count.
- 2026-08-12 automated retest: initial 61-test focused pytest command timed out after 124 seconds, so it was split by area.
- 2026-08-12 split automated result: 57 PASS, 4 FAIL. Failures remain three `TestTodoSSEEvent` patch-target resolution failures for `app.tasks.agent_tasks` and one `test_list_project_knowledge_bases_maps_rows` patch-target resolution failure for `app.models.mysql`.
- 2026-08-12 manual scope note: full 111-case execution still requires live Jira/ESM/Redis/RAGFlow/LLM/K8s/MySQL/browser-extension environments and was not completed in this automated pass.

- 2026-08-11 AUTH-002 recheck: `manifest.json` grants `cookies`; `popup.js` calls `chrome.cookies.getAll`, posts `session_cookie` to `/sso/login` with `_slug=jira_session`, and stores the returned token.
- Strict result remains FAIL because the flow is manual after popup open, not automatic on plugin-icon click, and no logged-in-state UI is rendered.
- Static verification passed with `node --check popup.js` and `php -l` for the four AUTH-002 PHP files.

- 요청 범위는 기존 두 파일의 테스트 케이스 및 테스트 실행 현황을 다시 통계/정리하는 것이다.
- 원본 파일은 수정하지 않고 읽기 기반으로 집계한다.
- XLSX는 9개 시트가 있으나 현재 읽힌 값은 각 시트 헤더 1행뿐이라 상세 케이스 집계 기준으로 쓰지 않았다.
- DOCX 상세 표 기준 테스트 케이스는 111건이며, `test-reports/20260810`의 케이스별 리포트 111건과 ID 기준으로 1:1 매칭된다.
- DOCX 상세 행의 우선순위 합계는 P0 72건, P1 39건이다. 문서 마지막 요약표는 P0 69건, P1 42건으로 KB/SEC 쪽 상세 행과 3건 차이가 있다.
- 2026-08-11 실패 케이스 재실행에서 worker-agent-engine 관련 자동 테스트 61건은 57 PASS, 4 FAIL이었다. 4건 모두 테스트가 현재 저장소에 없는 `app.tasks.agent_tasks` 또는 `app.models.mysql` 경로를 patch하는 테스트 하니스 불일치이다.
- 111개 전체 케이스는 외부 실행 환경과 계정·데이터가 없어 모두 자동 확정할 수 없었다. PASS는 실제 실행된 자동 테스트 57건만 보고서에 반영하고, 기존 FAIL/PARTIAL/NOT RUN은 임의로 변경하지 않았다.

- 2026-08-13 PERF-001 scope: user requested 20 concurrent users for 30 minutes against https://csc-ai.natec.cn/work-agent/#/project/4/process/task/20. This run measures HTTP page shell response time, not browser-rendered RUM load time.

- 2026-08-13 PERF-001 result: FAIL. 20 HTTP workers ran for 1810.49 seconds, total 3280 requests, 136 HTTP 200, 3144 errors, error rate 95.8537%, P95 11385.88 ms. Most errors were SSL UNEXPECTED_EOF_WHILE_READING.

- 2026-08-13 PERF-001 rerun result: FAIL. 20 HTTP workers ran for 1800.89 seconds, total 10390 requests, 727 HTTP 200, 9663 errors, error rate 93.0029%, P95 6910.05 ms. Dominant error was WinError 10061 connection refused.

- 本次汇报补充参考 `D:\dev\cscAI\skill_Agent.html`，将 Skill 归纳为文档与表格生成、报告生成、工单处理、知识检索与技术分析、自动化与外部工具五类。
- 知识库摘要采用发布汇报所需的抽象层级，概括为写入、双路检索、结果优化、异步增强和存储分工。
