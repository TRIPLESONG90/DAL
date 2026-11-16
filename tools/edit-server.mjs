// 슬라이드 편집용 로컬 서버.
// 실행: node tools/edit-server.mjs [포트]   (기본 8765)
// http://127.0.0.1:<포트>/week2/week2.html 로 열면 배치·글자 편집이 그 HTML 파일에 바로 저장된다.
// 이 PC(127.0.0.1)에서만 접속되고, 저장은 이미 있는 .html 파일 덮어쓰기만 허용한다.
import { createServer } from 'node:http';
import { promises as fs } from 'node:fs';
import { exec } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const port = Number(process.argv[2] || process.env.PORT || 8765);
const host = '127.0.0.1';
const startPage = '/week2/week2.html';
const maxBody = 50 * 1024 * 1024;
const types = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8', '.md': 'text/plain; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
  '.svg': 'image/svg+xml', '.webp': 'image/webp', '.ico': 'image/x-icon', '.pdf': 'application/pdf',
  '.ttf': 'font/ttf', '.otf': 'font/otf', '.woff': 'font/woff', '.woff2': 'font/woff2', '.mp4': 'video/mp4',
};

function resolveInRoot(urlPath) {
  let rel;
  try { rel = decodeURIComponent(urlPath.split('?')[0]); } catch { return null; }
  const full = path.resolve(root, '.' + rel);
  if (full !== root && !full.startsWith(root + path.sep)) return null;
  if (path.relative(root, full).split(path.sep).some(part => part.startsWith('.'))) return null; // .git 등 숨김 경로 차단
  return full;
}

function send(res, status, body, type = 'text/plain; charset=utf-8') {
  res.writeHead(status, { 'Content-Type': type, 'Cache-Control': 'no-store' });
  res.end(body);
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = []; let size = 0;
    req.on('data', c => { size += c.length; if (size > maxBody) { reject(new Error('too large')); req.destroy(); } else chunks.push(c); });
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

const server = createServer(async (req, res) => {
  try {
    const url = req.url || '/';
    if (url === '/' ) { res.writeHead(302, { Location: startPage }); return res.end(); }
    if (url.split('?')[0] === '/__dal-save') return send(res, 200, JSON.stringify({ ok: true }), 'application/json; charset=utf-8');

    if (req.method === 'PUT') {
      // 다른 사이트에서 이 서버로 저장 요청을 보내지 못하게 막는다.
      const origin = req.headers.origin;
      const allowed = [`http://${host}:${port}`, `http://localhost:${port}`];
      if (req.headers['x-dal-save'] !== '1' || (origin && !allowed.includes(origin))) return send(res, 403, 'forbidden');
      const file = resolveInRoot(url);
      if (!file || path.extname(file).toLowerCase() !== '.html') return send(res, 400, 'html 파일만 저장할 수 있습니다');
      const stat = await fs.stat(file).catch(() => null);
      if (!stat?.isFile()) return send(res, 404, '없는 파일입니다');
      const body = await readBody(req);
      const tmp = `${file}.saving-${process.pid}`;
      await fs.writeFile(tmp, body);
      await fs.rename(tmp, file);
      console.log(`${new Date().toLocaleTimeString('ko-KR', { hour12: false })} 저장: ${path.relative(root, file)} (${body.length.toLocaleString()} bytes)`);
      return send(res, 200, JSON.stringify({ ok: true, bytes: body.length }), 'application/json; charset=utf-8');
    }

    if (req.method !== 'GET' && req.method !== 'HEAD') return send(res, 405, 'method not allowed');
    let file = resolveInRoot(url);
    if (!file) return send(res, 403, 'forbidden');
    let stat = await fs.stat(file).catch(() => null);
    if (stat?.isDirectory()) { file = path.join(file, 'index.html'); stat = await fs.stat(file).catch(() => null); }
    if (!stat?.isFile()) return send(res, 404, 'not found');
    res.writeHead(200, { 'Content-Type': types[path.extname(file).toLowerCase()] || 'application/octet-stream', 'Content-Length': stat.size, 'Cache-Control': 'no-store' });
    if (req.method === 'HEAD') return res.end();
    res.end(await fs.readFile(file));
  } catch (e) {
    console.error(e);
    if (!res.headersSent) send(res, 500, '서버 오류: ' + e.message);
  }
});

server.on('error', e => {
  if (e.code === 'EADDRINUSE') console.error(`포트 ${port}를 이미 쓰고 있습니다. 다른 포트로 실행하세요: node tools/edit-server.mjs 8766`);
  else console.error(e);
  process.exit(1);
});

server.listen(port, host, () => {
  const url = `http://${host}:${port}${startPage}`;
  console.log(`편집 서버 실행 중: ${url}`);
  console.log('배치 편집(E)에서 고친 내용이 HTML 파일에 바로 저장됩니다. 끝내려면 Ctrl+C.');
  if (!process.argv.includes('--no-open')) {
    const cmd = process.platform === 'win32' ? `start "" "${url}"` : process.platform === 'darwin' ? `open "${url}"` : `xdg-open "${url}"`;
    exec(cmd, () => {});
  }
});
