# AUTH-011 Redis 캐시 검증 가이드 및 테스트 리포트

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-011 |
| 测试标题 | 权限缓存命中（TTL>5min） |
| 执行日期 | 2026-08-14 |
| 当前状态 | NOT VERIFIED (로컬 환경) |
| 실행 방식 | 검증 스크립트 작성 완료, 운영 환경 검증 필요 |

## 테스트 환경 구성

### 방법 1: Docker Redis 실행 (로컬 테스트)

```bash
# Docker 설치 확인
docker --version

# Redis 컨테이너 실행
docker run -d --name redis-test \
  -p 6379:6379 \
  redis:7-alpine

# Redis 연결 확인
redis-cli ping
# 응답: PONG

# 스크립트 실행
chmod +x /path/to/verify_redis_cache.sh
./verify_redis_cache.sh
```

### 방법 2: 운영 환경 Redis 검증

```bash
# Redis 연결 정보 설정
export REDIS_HOST=<운영_Redis_호스트>
export REDIS_PORT=6379
export REDIS_PASSWORD=<Redis_비밀번호>

# 스크립트 실행
chmod +x /path/to/verify_redis_prod.sh
./verify_redis_prod.sh
```

### 방법 3: Python 스크립트 실행

```bash
# Redis Python 패키지 설치
pip install redis --break-system-packages

# 스크립트 실행
python3 /path/to/verify_redis_cache.py
```

## 검증 항목

### 1. 권한 캐시 키 존재 확인 (AUTH-011)

**검증 패턴**: `ai_work_perm:user:*:projects`

**예상 결과**:
- 사용자 로그인 후 캐시 키 생성 확인
- 키 수 ≥ 1

**검증 명령어**:
```bash
redis-cli -h <host> -p <port> -a <password> --scan --pattern "ai_work_perm:user:*:projects"
```

### 2. TTL 값 확인

**예상 TTL**:
- 메인 캐시: 1800초 (30분)
- stale 캐시: 604800초 (7일)

**검증 명령어**:
```bash
# 메인 캐시 TTL
redis-cli -h <host> -p <port> -a <password> ttl <cache_key>

# stale 캐시 TTL
redis-cli -h <host> -p <port> -a <password> ttl <cache_key>:stale
```

**판정 기준**:
- TTL이 1700~1800초 범위 내: PASS
- TTL이 600000~610000초 범위 내 (stale): PASS
- TTL이 -1 (영구): FAIL
- TTL이 -2 (만료): 정보 수집 후 재검증 필요

### 3. 캐시 히트 성능 확인

**예상 결과**: 평균 응답시간 < 50ms

**검증 방법**: 동일 키를 10회 조회하여 평균 시간 측정

### 4. 캉내용 구조 확인

**예상 구조**:
```json
{
  "projects": ["project_a", "project_b", ...],
  "timestamp": 1692000000,
  "user_id": "user_001"
}
```

## 검증 스크립트 위치

1. **Bash 스크립트 (로컬)**:
   - `D:\dev\cscAI\TestCase111\test-scripts\verify_redis_cache.sh`

2. **Bash 스크립트 (운영 환경)**:
   - `D:\dev\cscAI\TestCase111\test-scripts\verify_redis_prod.sh`

3. **Python 스크립트**:
   - `D:\dev\cscAI\TestCase111\test-scripts\verify_redis_cache.py`

## 검증 실행 절차

### Step 1: Redis 연결 확인

```bash
redis-cli -h <host> -p <port> -a <password> ping
# 예상 응답: PONG
```

### Step 2: 캉키 확인

```bash
redis-cli -h <host> -p <port> -a <password> --scan --pattern "ai_work_perm:user:*:projects"
```

### Step 3: TTL 확인

```bash
KEY=$(redis-cli -h <host> -p <port> -a <password> --scan --pattern "ai_work_perm:user:*:projects" | head -1)
redis-cli -h <host> -p <port> -a <password> ttl "$KEY"
```

### Step 4: 캉내용 확인

```bash
redis-cli -h <host> -p <port> -a <password> get "$KEY" | jq .
```

### Step 5: stale 캉확인

```bash
redis-cli -h <host> -p <port> -a <password> exists "$KEY:stale"
# 1 = 존재, 0 = 부재
```

## 예상 검증 결과

### PASS 시나리오

```text
✓ Redis 연결 성공: PONG
✓ 권한 캉키 존재: 3개
✓ ai_work_perm:user:test_user_001:projects: TTL = 1750초 (29분)
  → ✓ 30분 캉정상
✓ ai_work_perm:user:test_user_001:projects:stale: TTL = 603000씄 (6일)
  → ✓ 7일 stale 캉정상
✓ 평균 응답시간: 15ms
  → ✓ 50ms 미만
```

### FAIL 시나리오

```text
✗ Redis 연결 실패
  → Redis 서비스 상태 확인
⚠ 권한 캉키 존재하지 않음: 0개
  → 사용자 로그인 후 재검증
⚠ TTL = -1 (영구 캉)
  → TTL 설정 로직 확인
```

## 보고서 생성

검증 완료 후 다음 파일에 보고서가 자동 생성됩니다:

```
D:\dev\cscAI\TestCase111\test-reports\20260810\AUTH-011-redis-verification.txt
```

## 다음 단계

1. **Redis 환경 구성**: 위 방법 중 하나로 Redis 실행
2. **사용자 로그인**: 테스트 사용자로 시스템에 로그인
3. **캉생성 확인**: 권한 캉키가 생성되는지 확인
4. **검증 실행**: 제공된 스크립트로 검증 실행
5. **결과 보고**: 검증 결과를 AUTH-011 리포트에 업데이트

## 보안 규칙

- Redis 비밀번호를 절대 리포트나 로그에 저장하지 않음
- 환경 변수로만 비밀번호 전달
- 검증 후 Redis 세션 종료
- 운영 환경 검증 시 반드시 보안 팀 동반

## 연관 테스트 케이스

- **AUTH-011**: 권한 캉命中 (TTL>5min) - 본 케이스
- **AUTH-012**: 캉만료 후 Jira 재조회
- **AUTH-013**: Jira 불가 시 stale 캉사용

---

**작성자**: AI 테스트 시스템  
**최종 업데이트**: 2026-08-14  
**상태**: 검증 스크립트 준비 완료, 운영 환경 검증 대기
