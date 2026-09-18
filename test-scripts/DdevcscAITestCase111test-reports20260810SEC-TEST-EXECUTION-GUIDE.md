# 보안 테스트 실행 가이드

## 실행 전 준비

### 1. Redis 설치 (권한 캐시 테스트)
```bash
# Docker Redis 실행
docker run -d --name redis-test -p 6379:6379 redis:7-alpine
```

### 2. API 테스트를 위한 인증 정보 준비
```bash
# 테스트 사용자 인증 정보
export TEST_USER_TOKEN=<유효한_JWT_토큰>
export TEST_ADMIN_TOKEN=<관리자_JWT_토큰>
```

### 3. Webhook Secret 확인
```bash
# Webhook Secret 확인
export WEBHOOK_SECRET=<Jira_Webhook_Secret>
```

## 테스트 실행 순서

### 1단계: SQL Injection 테스트
```bash
curl -X POST https://csc-ai.natec.cn/api/v1/issues \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TEST_USER_TOKEN" \
  -d '{"query": "' OR 1=1 --"}'

# 예상 결과: 400/422 (차단됨)
# 위험한 경우: 200 + 데이터 노출
```

### 2단계: 권한 확인 테스트
```bash
# 횡向 권한: 다른 프로젝트 워크 접근
curl -X GET https://csc-ai.natec.cn/api/v1/issues/OTHER_PROJECT_ISSUE \
  -H "Authorization: Bearer $TEST_USER_TOKEN"

# 예상 결과: 403 Forbidden
# 위험한 경우: 200 + 데이터 반환
```

### 3단계: XSS 테스트
```bash
curl -X POST https://csc-ai.natec.cn/api/v1/sessions/{session_id}/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TEST_USER_TOKEN" \
  -d '{"content": "<script>alert('XSS')</script>"}'

# 예상 결과: 스크립트 태그 제거됨
# 위험한 경우: 스크립트가 그대로 반환됨
```

### 4단계: CSRF 테스트
```bash
# CSRF 토큰 없이 POST 요청
curl -X POST https://csc-ai.natec.cn/api/v1/admin/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TEST_USER_TOKEN" \
  -d '{"username": "test", "role": "admin"}'

# 예상 결과: 403 Forbidden
# 위험한 경우: 요청 성공 (CSRF 보호 없음)
```

### 5단계: Rate Limiting 테스트
```bash
# 15회 연속 로그인 시도
for i in {1..15}; do
  curl -X POST https://csc-ai.natec.cn/api/v1/auth/login \
    -d '{"username": "test", "password": "wrong"}'
  echo "요청 #${i} 완료"
  sleep 1
done

# 예상 결과:
# 1~10회: 200 또는 401 (인증 실패)
# 11회~: 429 Too Many Requests
```

## 검증 항목

### SQL Injection (SEC-014)
- [ ] 파라미터화 쿼리 사용
- [ ] 에러 메시지에 스택 트레이스 없음
- [ ] OR, UNION, DROP, 등 위험 키워드 필터링
- [ ] 모든 엔드포인트 보호

### 권한 확인 (SEC-001/002)
- [ ] 횡向 권한: 다른 프로젝트 데이터 접근 차단
- [ ] 종向 권한: 관리자 API 일반 사용자 차단
- [ ] 403 응답과 적절한 에러 메시지
- [ ] 감사 로그에 기록

### XSS (SEC-015)
- [ ] 입력 시 HTML 태그 필터링
- [ ] 출력 시 HTML 엔티티 인코딩
- [ ] Content-Security-Policy 헤더
- [ ] X-XSS-Protection 헤더

### CSRF (SEC-016)
- [ ] 상태 변경 요청에 CSRF 토큰 필요
- [ ] CSRF 토큰 유효성 검증
- [ ] SameSite 쿠키 설정
- [ ] Referer 헤더 검증

### Rate Limiting (SEC-017)
- [ ] 로그인: 10회/분/IP
- [ ] 일반 API: 100회/분/IP
- [ ] 초과 시 429 응답
- [ ] Retry-After 헤더 포함

## 결과 보고서

테스트 완료 후 다음 파일에 상세 결과 저장:
```
D:\dev\cscAI\TestCase111	est-reports60810\SEC-COMPREHENSIVE-REPORT.json
```

---

**작성자**: AI 테스트 시스템
**최종 업데이트**: 2026-08-14
**상태**: 시뮬레이션 완료, 실제 환경 테스트 대기
