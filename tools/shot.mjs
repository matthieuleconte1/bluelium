// Capture une page avant/après le convertisseur Glyphe (CDP, sans dépendance).
// Usage : node shot.mjs <script.js> <dossier_sortie> <url>...
import { spawn } from 'node:child_process';
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [script, outDir, ...urls] = process.argv.slice(2);
const code = readFileSync(script, 'utf8');
const profile = mkdtempSync(join(tmpdir(), 'glyphe-shot-'));
const browser = spawn(process.env.BROWSER || 'helium-browser', [
  '--headless=new', '--remote-debugging-port=9333', `--user-data-dir=${profile}`,
  '--window-size=1280,860', '--hide-scrollbars', 'about:blank'], { stdio: 'ignore' });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let targets;
for (let i = 0; i < 50; i++) {
  try { targets = await (await fetch('http://127.0.0.1:9333/json')).json(); break; } catch { await sleep(200); }
}
const page = targets.find((t) => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener('open', r, { once: true }));
let id = 0;
const waiters = new Map();
const events = [];
ws.addEventListener('message', (e) => {
  const m = JSON.parse(e.data);
  if (m.id && waiters.has(m.id)) { waiters.get(m.id)(m); waiters.delete(m.id); }
  else if (m.method) events.push(m);
});
const send = (method, params = {}) => new Promise((r) => { const i = ++id; waiters.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });

await send('Page.enable');
let n = 0;
for (const url of urls) {
  n++;
  events.length = 0;
  await send('Page.navigate', { url });
  for (let i = 0; i < 100 && !events.some((e) => e.method === 'Page.loadEventFired'); i++) await sleep(150);
  await sleep(1500);
  let shot = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync(join(outDir, `${n}-avant.png`), Buffer.from(shot.result.data, 'base64'));
  const t0 = Date.now();
  const res = await send('Runtime.evaluate', { expression: code, awaitPromise: false });
  if (res.result?.exceptionDetails) console.log('ERREUR', url, JSON.stringify(res.result.exceptionDetails).slice(0, 400));
  await sleep(800);
  shot = await send('Page.captureScreenshot', { format: 'png' });
  writeFileSync(join(outDir, `${n}-apres.png`), Buffer.from(shot.result.data, 'base64'));
  console.log(n, url, 'conversion', Date.now() - t0 - 800, 'ms');
}
ws.close();
browser.kill();
