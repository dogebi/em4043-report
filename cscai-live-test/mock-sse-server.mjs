// 로컬 SSE 목 서버 — 실서버 계약(esm SessionService::getSseCallback)과 동일한 프레임을 흘려
// live-chat.html 의 파서/렌더링/전송흐름을 인증 없이 검증한다.
//   id: {msgId}\nevent: {type}\ndata: {json}\n\n
// 실행: node mock-sse-server.mjs   (기본 127.0.0.1:8790)
import http from 'node:http';

const PORT = Number(process.env.PORT || 8790);
const sessions = [
  { session_id: 'S-MOCK-001', title: '[MOCK] 검증용 세션 A' },
  { session_id: 'S-MOCK-002', title: '[MOCK] 검증용 세션 B' },
];

const json = (res, code, obj) => {
  res.writeHead(code, { 'content-type': 'application/json; charset=utf-8', 'access-control-allow-origin': '*' });
  res.end(JSON.stringify(obj));
};

function sse(res, frames, delayMs = 220) {
  res.writeHead(200, {
    'content-type': 'text/event-stream; charset=utf-8',
    'cache-control': 'no-cache',
    connection: 'keep-alive',
    'access-control-allow-origin': '*',
  });
  let i = 0;
  const t = setInterval(() => {
    if (i >= frames.length) { clearInterval(t); res.end(); return; }
    const f = frames[i++];
    res.write(`id: ${i}\nevent: ${f.event}\ndata: ${JSON.stringify(f.data)}\n\n`);
  }, delayMs);
  res.on('close', () => clearInterval(t));
}

http.createServer((req, res) => {
  const url = new URL(req.url || '/', `http://127.0.0.1:${PORT}`);
  const p = url.pathname;
  let body = '';
  req.on('data', (c) => (body += c));
  req.on('end', () => {
    if (req.method === 'OPTIONS') {
      res.writeHead(204, {
        'access-control-allow-origin': '*',
        'access-control-allow-headers': '*',
        'access-control-allow-methods': 'GET,POST,PUT,DELETE,PATCH,OPTIONS',
      });
      return res.end();
    }
    if (p === '/agent-work-api/v1/sessions') return json(res, 200, { code: 0, data: { total: sessions.length, list: sessions } });
    if (p.endsWith('/messages') && req.method === 'GET') {
      return json(res, 200, { code: 0, data: { list: [
        { role: 'user', content: '[MOCK] 이전 사용자 메시지' },
        { role: 'assistant', content: '[MOCK] 이전 AI 응답' },
      ] } });
    }
    if (p.endsWith('/messages') && req.method === 'POST') {
      console.log('POST', p, body.slice(0, 200));
      return json(res, 200, { code: 0, message: 'success', data: { message_id: 'M-123' } });
    }
    if (p.endsWith('/stream')) {
      console.log('SSE', p);
      return sse(res, [
        { event: 'message_start', data: { type: 'message_start', message_id: 'M-123' } },
        { event: 'chunk', data: { type: 'chunk', content: '생각 중: 질문을 분해합니다. ', source: 'thinking' } },
        { event: 'chunk', data: { type: 'chunk', content: '생각 중: 도구 호출이 필요합니다.', source: 'thinking' } },
        { event: 'tool_call', data: { type: 'tool_call', name: 'jira_search', arguments: { jql: 'project = SM' }, source: 'body' } },
        { event: 'tool_result', data: { type: 'tool_result', content: '{"total":40}' } },
        { event: 'knowledge_search', data: { type: 'knowledge_search', knowledge_refs: [{ name: '운영 매뉴얼 A' }, { name: '장애 대응 가이드' }] } },
        { event: 'chunk', data: { type: 'chunk', content: '요약: 미해결 티켓은 ' } },
        { event: 'chunk', data: { type: 'chunk', content: '40건입니다.' } },
        { event: 'message_end', data: { type: 'message_end', metadata: { token_usage: { prompt_tokens: 120, completion_tokens: 45 }, ttft_ms: 480 } } },
      ]);
    }
    return json(res, 404, { error: 'mock: no route ' + p });
  });
}).listen(PORT, '0.0.0.0', () => console.log(`mock SSE server: http://127.0.0.1:${PORT}`));
