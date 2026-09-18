// 로컬 HTML 채팅 페이지에서 CSC AI API를 CORS 없이 호출하도록 중계하는 최소 프록시입니다.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const target = (process.env.CSC_AI_TARGET || 'https://csc-ai.natec.cn').replace(/\/$/, '');
const upstreamProxy = process.env.CSC_AI_PROXY || 'http://127.0.0.1:1099';
const port = Number(process.env.PORT || 8787);

const mime = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8'
};

function send(res, code, body, type = 'text/plain; charset=utf-8') {
  res.writeHead(code, { 'content-type': type, 'access-control-allow-origin': '*' });
  res.end(body);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', (c) => chunks.push(c));
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

async function proxyApi(req, res, url) {
  const body = await readBody(req);
  const accept = req.headers.accept || '*/*';
  const isSse = String(accept).includes('text/event-stream') || url.pathname.endsWith('/stream');
  const args = [
    '--silent', '--show-error', '--no-buffer', '--location',
    '--proxy', upstreamProxy,
    '--request', req.method || 'GET',
    '--header', `Accept: ${accept}`,
    '--header', `User-Agent: Mozilla/5.0`,
  ];
  if (req.headers.authorization) args.push('--header', `Authorization: ${req.headers.authorization}`);
  if (req.headers.hubid) args.push('--header', `Hubid: ${req.headers.hubid}`);
  if (req.headers['content-type']) args.push('--header', `Content-Type: ${req.headers['content-type']}`);
  if (body.length) args.push('--data-binary', '@-');
  args.push(`${target}${url.pathname}${url.search}`);

  res.writeHead(200, {
    'content-type': isSse ? 'text/event-stream; charset=utf-8' : 'application/json; charset=utf-8',
    'cache-control': 'no-cache',
    'access-control-allow-origin': '*',
  });

  const child = spawn('curl.exe', args, { stdio: ['pipe', 'pipe', 'pipe'] });
  if (body.length) child.stdin.end(body); else child.stdin.end();
  child.stdout.pipe(res, { end: false });
  let stderr = '';
  child.stderr.on('data', (c) => { stderr += c.toString(); });
  child.on('close', (code) => {
    if (code !== 0 && !res.writableEnded) res.write(`\n[proxy curl error ${code}] ${stderr}`);
    res.end();
  });
  req.on('close', () => child.kill());
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === 'OPTIONS') return send(res, 204, '');
    const url = new URL(req.url || '/', `http://127.0.0.1:${port}`);
    if (url.pathname.startsWith('/agent-work-api/')) return proxyApi(req, res, url);

    const file = url.pathname === '/' ? 'api-chat.html' : url.pathname.slice(1);
    const full = path.resolve(__dirname, file);
    if (!full.startsWith(__dirname)) return send(res, 403, 'Forbidden');
    if (!fs.existsSync(full)) return send(res, 404, 'Not found');
    send(res, 200, fs.readFileSync(full), mime[path.extname(full)] || 'application/octet-stream');
  } catch (err) {
    send(res, 500, err?.stack || String(err));
  }
});

server.listen(port, '127.0.0.1', () => {
  console.log(`API chat proxy: http://127.0.0.1:${port}/api-chat.html`);
  console.log(`Proxy target: ${target}`);
  console.log(`Upstream proxy: ${upstreamProxy}`);
});
