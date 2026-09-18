#!/usr/bin/env bash
# CSC AI 실채팅 페이지 + API 중계 프록시 실행 스크립트
#   사용: bash run-chat.sh            (기본 포트 8788, xray 1098 경유)
#         PORT=8899 bash run-chat.sh
#   토큰 자동 주입(선택): 같은 폴더에 .token 파일에 access_token 한 줄을 넣어두면
#                        프록시가 Authorization 헤더를 대신 붙여줍니다. (채팅/로그에 노출 안 됨)
set -euo pipefail
cd "$(command -v readlink >/dev/null && dirname "$(readlink -f "$0")" || dirname "$0")"

PORT="${PORT:-8788}"
export CSC_AI_PROXY="${CSC_AI_PROXY:-http://127.0.0.1:1099}"
export CSC_AI_TARGET="${CSC_AI_TARGET:-https://csc-ai.natec.cn}"
export PORT

if [ -s ".token" ]; then
  export CSC_AI_TOKEN_FILE="$(pwd)/.token"
  echo "[token] .token 파일 감지 → 프록시가 헤더를 대신 주입합니다."
else
  echo "[token] .token 파일 없음 → 페이지의 Bearer Token 칸에 직접 붙여넣어야 합니다."
fi

# 이미 떠 있는 인스턴스 정리 (포트 기준)
OLD_PID="$(ss -lntp 2>/dev/null | grep ":${PORT} " | grep -oP 'pid=\K[0-9]+' | head -1 || true)"
if [ -n "${OLD_PID:-}" ]; then kill "$OLD_PID" 2>/dev/null || true; sleep 1; fi

nohup node live-chat-proxy.mjs > chat-proxy.log 2>&1 &
PID=$!
echo "[proxy] pid=$PID port=$PORT target=$CSC_AI_TARGET via $CSC_AI_PROXY"

for i in $(seq 1 30); do
  if curl -s --noproxy '*' --max-time 2 "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then break; fi
  sleep 0.5
done

curl -s --noproxy '*' --max-time 5 "http://127.0.0.1:${PORT}/health" || true
echo
echo "▶ 채팅 페이지: http://127.0.0.1:${PORT}/"
echo "▶ 중계 로그  : tail -f $(pwd)/chat-proxy.log"
echo "▶ 검증(토큰 없이 도달 확인): curl -s http://127.0.0.1:${PORT}/agent-work-api/swagger/doc | head -c 80"
