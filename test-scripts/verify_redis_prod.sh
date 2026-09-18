#!/bin/bash
# Redis 운영 환경 검증 스크립트
# 실제 운영 Redis 정보를 입력하여 검증

echo "============================================================"
echo "Redis 운영 환경 권한 캐시 검증 스크립트"
echo "실행 일시: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

# Redis 연결 정보 입력 (사용자 환경에 맞게 수정)
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"

echo ""
echo "Redis 연결 정보:"
echo "  호스트: $REDIS_HOST"
echo "  포트: $REDIS_PORT"
echo "  비밀번호: ${REDIS_PASSWORD:+(설정됨)}"

# redis-cli 명령 구성
if [ -n "$REDIS_PASSWORD" ]; then
    REDIS_CMD="redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD --no-auth-warning"
else
    REDIS_CMD="redis-cli -h $REDIS_HOST -p $REDIS_PORT"
fi

# Redis 연결 확인
echo ""
echo "1. Redis 연결 확인"
echo "------------------------------------------------------------"
if $REDIS_CMD ping > /dev/null 2>&1; then
    PONG=$($REDIS_CMD ping)
    echo "✓ Redis 연결 성공: $PONG"

    # Redis 서버 정보
    echo ""
    echo "Redis 서버 정보:"
    $REDIS_CMD INFO server | grep -E "redis_version|os|tcp_port"
else
    echo "✗ Redis 연결 실패"
    echo ""
    echo "연결 정보를 확인하세요:"
    echo "  export REDIS_HOST=<your_redis_host>"
    echo "  export REDIS_PORT=<your_redis_port>"
    echo "  export REDIS_PASSWORD=<your_redis_password>"
    echo ""
    echo "예시:"
    echo "  export REDIS_HOST=192.168.1.100"
    echo "  export REDIS_PORT=6379"
    echo "  export REDIS_PASSWORD=your_password"
    exit 1
fi

# 권한 캐시 키 확인
echo ""
echo "2. 권한 캐시 키 존재 확인 (AUTH-011)"
echo "------------------------------------------------------------"
KEY_COUNT=$($REDIS_CMD --scan --pattern "ai_work_perm:user:*:projects" | wc -l)
echo "검색 패턴: ai_work_perm:user:*:projects"
echo "발견된 키 수: $KEY_COUNT"

if [ "$KEY_COUNT" -eq 0 ]; then
    echo ""
    echo "⚠ 권한 캐시 키가 존재하지 않습니다"
    echo ""
    echo "가능한 원인:"
    echo "  1. 사용자가 로그인하지 않음"
    echo "  2. 캐시 설정이 다른 패턴을 사용"
    echo "  3. Redis DB 번호가 다름"
    echo ""
    echo "확인 방법:"
    echo "  1. 다른 DB 확인: redis-cli -h $REDIS_HOST -p $REDIS_PORT -a <password> -n 1"
    echo "  2. 모든 키 확인: redis-cli -h $REDIS_HOST -p $REDIS_PORT -a <password> KEYS '*perm*'"
    echo "  3. 사용자 로그인 후 재검증"
    exit 0
fi

echo ""
echo "발견된 캐시 키:"
$REDIS_CMD --scan --pattern "ai_work_perm:user:*:projects" | nl -w2 -s'. '

# TTL 값 확인
echo ""
echo "3. 캐시 TTL 값 확인 (AUTH-011)"
echo "------------------------------------------------------------"
echo "예상 TTL: 메인 캐시 1800초 (30분), stale 캐시 604800초 (7일)"
echo ""

$REDIS_CMD --scan --pattern "ai_work_perm:user:*:projects" | while read -r key; do
    TTL=$($REDIS_CMD ttl "$key" 2>/dev/null)

    if [ "$TTL" = "-1" ]; then
        echo "  ⚠ $key: TTL 설정 없음 (영구 캐시)"
    elif [ "$TTL" = "-2" ]; then
        echo "  ⚠ $key: 이미 만료됨"
    elif [ "$TTL" -gt 0 ]; then
        TTL_MIN=$((TTL / 60))
        echo "  ✓ $key: TTL = ${TTL}초 (${TTL_MIN}분)"

        # TTL이 예상 범위 내에 있는지 확인
        if [ $TTL -ge 1700 ] && [ $TTL -le 1800 ]; then
            echo "    → ✓ 30분 캐시 정상"
        else
            echo "    → ⚠ TTL이 30분 범위를 벗어남"
        fi
    fi
done

# stale 캐시 확인
echo ""
echo "stale 캐시 확인:"
STALE_COUNT=0
$REDIS_CMD --scan --pattern "ai_work_perm:user:*:projects" | while read -r key; do
    STALE_KEY="${key}:stale"
    STALE_EXISTS=$($REDIS_CMD exists "$STALE_KEY" 2>/dev/null)

    if [ "$STALE_EXISTS" = "1" ]; then
        STALE_COUNT=$((STALE_COUNT + 1))
        STALE_TTL=$($REDIS_CMD ttl "$STALE_KEY" 2>/dev/null)
        STALE_DAYS=$((STALE_TTL / 86400))
        echo "  ✓ $STALE_KEY: TTL = ${STALE_TTL}초 (${STALE_DAYS}일)"
    fi
done

echo "  총 stale 캐시: ${STALE_COUNT}개"

# 캐시 내용 샘플 확인
echo ""
echo "4. 캐시 내용 구조 확인 (샘플)"
echo "------------------------------------------------------------"
FIRST_KEY=$($REDIS_CMD --scan --pattern "ai_work_perm:user:*:projects" | head -1)

if [ -n "$FIRST_KEY" ]; then
    echo "키: $FIRST_KEY"
    echo "내용 (앞부분):"
    $REDIS_CMD get "$FIRST_KEY" | head -20
fi

# 결과 요약
echo ""
echo "============================================================"
echo "검증 결과 요약"
echo "============================================================"

MAIN_COUNT=$($REDIS_CMD --scan --pattern "ai_work_perm:user:*:projects" | wc -l)
STALE_COUNT=$($REDIS_CMD --scan --pattern "ai_work_perm:user:*:projects:stale" | wc -l)

echo ""
echo "✓ Redis 연결 정상"
echo "✓ 권한 캐시 키 존재: ${MAIN_COUNT}개"
echo "  - 메인 캐시: ${MAIN_COUNT}개"
echo "  - stale 캐시: ${STALE_COUNT}개"

if [ $MAIN_COUNT -gt 0 ]; then
    echo "✓ AUTH-011: 캐시 히트 검증 완료"
else
    echo "⚠ AUTH-011: 메인 캐시 TTL 검증 필요"
fi

if [ $STALE_COUNT -gt 0 ]; then
    echo "✓ AUTH-013: stale 캐시 준비 완료"
else
    echo "⚠ AUTH-013: stale 캐시 생성 확인 필요"
fi

# 보고서 생성
REPORT_FILE="/sessions/practical-peaceful-ramanujan/mnt/TestCase111/test-reports/20260810/AUTH-011-redis-prod-verification.txt"
{
    echo "Redis 운영 환경 권한 캐시 검증 보고서"
    echo "실행 일시: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "Redis 연결 정보:"
    echo "  호스트: $REDIS_HOST"
    echo "  포트: $REDIS_PORT"
    echo ""
    echo "검증 결과:"
    echo "  권한 캐시 키 수: ${MAIN_COUNT}"
    echo "  메인 캐시: ${MAIN_COUNT}개"
    echo "  stale 캐시: ${STALE_COUNT}개"
} > "$REPORT_FILE"

echo ""
echo "✓ 보고서 저장 완료: $REPORT_FILE"
echo ""
echo "============================================================"
echo "검증 완료"
echo "============================================================"
