# CSC AI Work API 실채팅 (검증 노트)

## 결론 — 채팅은 이 두 경로가 정본

| 용도 | 메서드 · 경로 | 비고 |
|---|---|---|
| 세션 목록 | `GET /agent-work-api/v1/sessions?page=1&page_size=30` | 목록에서 sessionId 획득 |
| 이력 | `GET /agent-work-api/v1/sessions/{id}/messages` | 페이지네이션 |
| **메시지 전송** | `POST /agent-work-api/v1/sessions/{id}/messages` | body: `{content, run_mode:'agent'\|'qa', deep_thinking:false\|'low'\|'medium'\|'xhigh', context?, attachments?, model_config_id?}` |
| **스트리밍 응답** | `GET /agent-work-api/v1/sessions/{id}/stream?token={jwt}` | `Accept: text/event-stream` |
| 서브태스크 스트림 | `GET /agent-work-api/v1/sessions/{id}/tasks/{taskHash}/stream` | |
| 취소 | `POST /agent-work-api/v1/sessions/{id}/cancel-task` | |

없는 경로(실측): `POST /v1/chat`, `POST /v1/sessions`, `POST /v1/conversations`
→ work-api의 세션 생성 API는 `POST /v1/knowledge/sessions`(지식기반)뿐. 대화 로그 관리 리소스는 `admin-api/agent-hub/conversation`.
(참고: 이 서버는 미존재 경로에도 POST면 405를 돌려주는 catch-all 라우트가 있어, 405만으로 존재 판정하면 오답이 됩니다. 판정 근거는 라이브 OpenAPI `/agent-work-api/swagger/doc` 와 소스 `esm/app/AppAgent/Routes/work-api.php`.)

## 인증 요건 (소스 근거)

- 미들웨어: `sso.auth` + `agent.work.api.app-auth` → **Bearer 토큰 + Hubid** 필요
  (`app/AppAgent/Middleware/ApiWorkAppAuthenticate.php` — hubId는 없거나 어긋나면 SSO 사용자 기준 인스턴스 값으로 서버가 덮어씀)
- 토큰 저장 위치(실서비스 프론트): `localStorage.access_token` (`worker-agent-client/frontend-react/src/utils/index.ts`)
  → 로그인된 Chrome에서 F12 → Console: `copy(localStorage.getItem('access_token'))`
- SSE도 토큰 필요: 쿼리 `?token=` 로 전달 (헤더 인증도 허용)

## 구성 파일

- `live-chat.html` — 단일 파일 채팅 클라이언트 (세션 목록→선택→이력→전송→SSE)
  - SSE 처리: `event:`(=type) 우선, `source:'thinking'` → 별도 접이식 박스, `tool_call`/`tool_result`/`knowledge_search`/`message_end`(토큰·ttft) 표시
  - 네트워크: 3회 재시도 + 지수 백오프(0.5→1→2s), 요청당 40s 타임아웃
- `live-chat-proxy.mjs` — CORS·차단 우회 중계 (순수 Node, **curl 불필요**)
  - xray CONNECT 터널(기본 `http://127.0.0.1:1098`) → `https://csc-ai.natec.cn`
  - 업스트림 상태코드/본문/SSE 그대로 전달 (CORS 헤더 부착)
  - `.token` 파일이 있으면 Authorization 헤더를 서버측에서 주입 → 토큰이 채팅/브라우저에 노출되지 않음
- `mock-sse-server.mjs` — 실서버와 동일한 SSE 프레임을 흘리는 목 서버(무인증 검증용, 8790)
- `run-chat.sh` — 프록시 기동 + 헬스체크 + 접속 URL 출력
- `api-chat.html` / `api-chat-proxy.mjs` — 이전에 만들어진 초기 버전(보존)

## 실행

```bash
cd /mnt/d/dev/cscAI/TestCase111/cscai-live-test
bash run-chat.sh                 # → http://127.0.0.1:8788/
tail -f chat-proxy.log           # 중계 로그(업스트림 상태코드)
```

토큰 없이 토큰 파일로 자동 주입하려면:

```bash
printf '%s' '<access_token>' > .token   # 한 줄, 파일 권한은 본인만
bash run-chat.sh
```

페이지 사용 순서: ① 토큰 입력(또는 `.token` 사용 시 생략) → ② 세션 목록 불러오기 → ③ 세션 선택 → ④ 메시지 전송
(전송은 `POST .../messages` 후 자동으로 `GET .../stream` SSE 연결)

## 검증 상태 (2026-09-16)

| 항목 | 결과 | 근거 |
|---|---|---|
| 페이지·프록시 기동 | ✅ | `GET /health` 200, 페이지 200 (16,912B) |
| 프록시 → 실서버 도달 | ✅ | `GET swagger/doc` 200 / 293,596B |
| 실서버 인증 벽 확인 | ✅ | 무토큰 `GET /v1/sessions` → HTTP 500 `{"error":"请配置实例！"}` |
| 일시적 터널 실패 복구 | ✅ | 1회 502 후 재시도에서 200/500 정상 수신 |
| 클라이언트 전 구간(전송→SSE→렌더) | ✅ | `mock-sse-server.mjs` 대상으로 thinking/tool_call/tool_result/knowledge/토큰·ttft 렌더 확인 |
| **실서버 실제 채팅 1건** | ⏳ **미완** | access_token 필요 (세션 인증 없이는 호출 불가) |

## 알려진 이슈 — 502 "Client network socket disconnected before secure TLS connection was established"

원인은 프록시 코드가 아니라 **xray 경유지 선택**이었습니다 (2026-09-16 실측):

| 경유 | `GET /agent-work-api/swagger/doc` 성공률 |
|---|---|
| `http://127.0.0.1:1098` (WSL xray) | 0/8 |
| `http://127.0.0.1:1099` (Windows xray) | 8/8 |

→ 중계 기본 경유지와 `run-chat.sh` 기본값을 **1099** 로 변경했습니다. 변경 후 동일 요청 10회 연속 **502 0건**.
프록시 레벨 재시도는 유지(최대 3회, 300/700ms) — 연결 단계 실패만 재시도하며 응답 헤더가 이미 온 경우는 재시도하지 않습니다.
경유지를 바꾸려면 `CSC_AI_PROXY=http://127.0.0.1:1098 bash run-chat.sh`.

## 남은 한 단계

`.token` 파일(또는 페이지의 토큰 칸)에 access_token을 넣으면 즉시 실채팅 검증이 가능합니다.
토큰은 자격증명이므로 채팅에 붙여넣지 말고 파일 또는 페이지 입력칸으로만 넣어주세요.
