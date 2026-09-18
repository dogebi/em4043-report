// CSC AI Work API 중계 프록시 v3 (CORS·차단 우회, 순수 Node)
//   정적: / → live-chat.html
//   API : /agent-work-api/* → https://csc-ai.natec.cn (xray CONNECT 터널 경유)
//   v3 변경: ① 커넥션 재사용 제거(keepAlive:false) — 만료된 터널 소켓 재사용으로 생기던
//            "socket disconnected before secure TLS connection was established" 제거
//            ② 연결 단계 실패 시 프록시 레벨 자동 재시도(최대 3회, 300/700ms)
//            ③ ?_mock=1 로 목 서버(8790) 전환 가능(검증용)
// 실행: node live-chat-proxy.mjs   (기본 127.0.0.1:8788)
// 환경: PORT, CSC_AI_TARGET, CSC_AI_PROXY, CSC_AI_TOKEN_FILE, MOCK_TARGET
import http from 'node:http';
import net from 'node:net';
import tls from 'node:tls';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TARGET_URL = new URL(process.env.CSC_AI_TARGET || 'https://csc-ai.natec.cn');
const TARGET_HOST = TARGET_URL.hostname;
const TARGET_PORT = Number(TARGET_URL.port || 443);
const MOCK_URL = new URL(process.env.MOCK_TARGET || 'http://127.0.0.1:8790');
const PROXY_URL = new URL(process.env.CSC_AI_PROXY || 'http://127.0.0.1:1099');
const PORT = Number(process.env.PORT || 8788);
const DEFAULT_PAGE = 'live-chat.html';
const MAX_TRIES = Number(process.env.PROXY_TRIES || 3);

const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8' };

/* ---- xray CONNECT 터널 Agent: 요청마다 새 터널(재사용 없음) ---- */
class TunnelAgent extends http.Agent {
  constructor() { super({ keepAlive: false, maxSockets: 32 }); }
  createConnection(options, cb) {
    const sock = net.connect(Number(PROXY_URL.port), PROXY_URL.hostname);
    let buf = '', settled = false;
    const fail = (e) => { if (!settled) { settled = true; e.connectPhase = true; cb(e); } sock.destroy(); };
    const timer = setTimeout(() => fail(new Error('CONNECT timeout 20s')), 20000);
    sock.on('error', fail);
    sock.on('connect', () => sock.write(`CONNECT ${options.host}:${options.port} HTTP/1.1\r\nHost: ${options.host}:${options.port}\r\nProxy-Connection: keep-alive\r\n\r\n`));
    sock.on('data', function onData(d) {
      buf += d.toString('latin1');
      if (buf.indexOf('\r\n\r\n') === -1) return;
      sock.removeListener('data', onData);
      const status = Number((buf.match(/^HTTP\/\d(?:\.\d)?\s+(\d{3})/) || [])[1] || 0);
      if (status !== 200) { clearTimeout(timer); return fail(new Error(`CONNECT ${status || 'no-status'}: ${buf.split('\r\n')[0]}`)); }
      const t = tls.connect({ socket: sock, servername: options.host, rejectUnauthorized: false }, () => {
        clearTimeout(timer);
        if (!settled) { settled = true; cb(null, t); }
      });
      t.on('error', (e) => { if (!settled) { settled = true; e.connectPhase = true; cb(e); } });
    });
  }
}
const tunnel = new TunnelAgent();
const plainAgent = new http.Agent({ keepAlive: false });

function tokenFromFile() {
  const f = process.env.CSC_AI_TOKEN_FILE;
  if (!f) return '';
  try { return fs.readFileSync(f, 'utf8').trim(); } catch { return ''; }
}

function staticFile(res, url) {
  const rel = url.pathname === '/' ? DEFAULT_PAGE : decodeURIComponent(url.pathname.replace(/^\/+/, ''));
  const full = path.resolve(__dirname, rel);
  if (!full.startsWith(__dirname)) { res.writeHead(403).end('Forbidden'); return; }
  if (!fs.existsSync(full) || !fs.statSync(full).isFile()) { res.writeHead(404).end('Not found: ' + rel); return; }
  res.writeHead(200, { 'content-type': MIME[path.extname(full)] || 'application/octet-stream', 'cache-control': 'no-store' });
  fs.createReadStream(full).pipe(res);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/* 1회 시도. 연결 단계에서 실패하면 {retry:true} 로 알린다(서버에 요청이 도달하지 않은 상태). */
function attempt(req, res, url, body, useMock, attemptNo) {
  return new Promise((resolve) => {
    const hdrs = { accept: req.headers.accept || '*/*', 'user-agent': req.headers['user-agent'] || 'Mozilla/5.0' };
    const tk = req.headers.authorization || (tokenFromFile() ? `Bearer ${tokenFromFile()}` : '');
    if (tk) hdrs.authorization = tk;
    if (req.headers.hubid) hdrs.hubid = req.headers.hubid;
    if (req.headers['content-type']) hdrs['content-type'] = req.headers['content-type'];
    if (req.headers['last-event-id']) hdrs['last-event-id'] = req.headers['last-event-id'];

    const opts = useMock
      ? { host: MOCK_URL.hostname, port: Number(MOCK_URL.port), path: url.pathname + url.search, method: req.method, headers: hdrs, agent: plainAgent, protocol: 'http:' }
      : { host: TARGET_HOST, port: TARGET_PORT, path: url.pathname + url.search, method: req.method, headers: hdrs, agent: tunnel };

    let answered = false;
    const up = http.request(opts, (ur) => {
      answered = true;
      const out = { 'content-type': ur.headers['content-type'] || 'application/json; charset=utf-8', 'cache-control': 'no-cache', 'access-control-allow-origin': '*', 'x-proxy-attempts': String(attemptNo) };
      if (ur.headers['content-encoding']) out['content-encoding'] = ur.headers['content-encoding'];
      res.writeHead(ur.statusCode || 502, out);
      ur.pipe(res);
      console.log(`${req.method} ${url.pathname} → ${ur.statusCode} (try ${attemptNo})`);
      resolve();
    });
    up.on('error', async (e) => {
      const connectPhase = e.connectPhase || !answered;
      console.log(`${req.method} ${url.pathname} → ERR(try ${attemptNo}) ${e.message}`);
      if (connectPhase && attemptNo < MAX_TRIES) return resolve({ retry: true });
      if (!res.headersSent) res.writeHead(502, { 'content-type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify({ proxy_error: e.message, attempts: attemptNo }));
      resolve();
    });
    if (body && body.length) up.end(body); else up.end();
  });
}

async function proxy(req, res, url, body) {
  const useMock = url.searchParams.get('_mock') === '1';
  for (let i = 1; i <= MAX_TRIES; i++) {
    const r = await attempt(req, res, url, body, useMock, i);
    if (!r || !r.retry) return;
    await sleep(i === 1 ? 300 : 700);
  }
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const c = [];
    req.on('data', (x) => c.push(x));
    req.on('end', () => resolve(Buffer.concat(c)));
    req.on('error', reject);
  });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url || '/', `http://127.0.0.1:${PORT}`);
  if (req.method === 'OPTIONS') {
    res.writeHead(204, { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': '*' });
    return res.end();
  }
  if (url.pathname === '/health') {
    res.writeHead(200, { 'content-type': 'application/json' });
    return res.end(JSON.stringify({ ok: true, target: `${TARGET_HOST}:${TARGET_PORT}`, mock: MOCK_URL.href, proxy: PROXY_URL.href, tokenFile: !!process.env.CSC_AI_TOKEN_FILE, tries: MAX_TRIES }));
  }
  if (url.pathname.startsWith('/agent-work-api/')) {
    const body = await readBody(req);
    return proxy(req, res, url, body);
  }
  return staticFile(res, url);
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`채팅 페이지 : http://127.0.0.1:${PORT}/`);
  console.log(`API 중계    : https://${TARGET_HOST} via ${PROXY_URL.href} (터널 재사용 없음, 실패 시 최대 ${MAX_TRIES}회 재시도)`);
  console.log(`목 서버     : ${MOCK_URL.href} → 경로에 ?_mock=1 붙이면 전환`);
  console.log(`토큰 파일   : ${process.env.CSC_AI_TOKEN_FILE || '(미사용)'}`);
});
