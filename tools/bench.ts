// Banc d'essai Helium Glyphe vs Helium officiel (Deno, sans dépendance).
// Usage : deno run -A tools/bench.ts <binaire> <étiquette> <dossier-sortie> [runs]
// Mesure : démarrage (lancement -> page about:blank prête), Speedometer 3.1
// (score), mémoire totale (PSS) des processus avec 5 sites ouverts.

const [bin, label, outDir, runsArg] = Deno.args;
const runs = Number(runsArg ?? 2);
const port = 9400 + Math.floor(Math.random() * 400);
const profile = await Deno.makeTempDir({ prefix: `bench-${label}-` });

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

async function json(path: string): Promise<any> {
  const r = await fetch(`http://127.0.0.1:${port}${path}`);
  return await r.json();
}

class Cdp {
  ws: WebSocket;
  id = 0;
  pending = new Map<number, (v: any) => void>();
  constructor(ws: WebSocket) {
    this.ws = ws;
    ws.onmessage = (e) => {
      const m = JSON.parse(e.data);
      if (m.id && this.pending.has(m.id)) {
        this.pending.get(m.id)!(m);
        this.pending.delete(m.id);
      }
    };
  }
  static async open(url: string) {
    const ws = new WebSocket(url);
    await new Promise((r, j) => {
      ws.onopen = r;
      ws.onerror = j;
    });
    return new Cdp(ws);
  }
  send(method: string, params: any = {}): Promise<any> {
    const id = ++this.id;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((r) => this.pending.set(id, r));
  }
  async eval(expr: string): Promise<any> {
    const m = await this.send("Runtime.evaluate", {
      expression: expr,
      returnByValue: true,
      awaitPromise: true,
    });
    return m.result?.result?.value;
  }
}

async function pageTarget(): Promise<any> {
  for (let i = 0; i < 200; i++) {
    try {
      const list = await json("/json/list");
      const page = list.find((t: any) => t.type === "page");
      if (page) return page;
    } catch { /* pas encore prêt */ }
    await sleep(50);
  }
  throw new Error("pas de page CDP");
}

function launch(url: string) {
  return new Deno.Command(bin, {
    args: [
      `--user-data-dir=${profile}`,
      `--remote-debugging-port=${port}`,
      "--no-first-run",
      "--no-default-browser-check",
      "--disable-features=Translate",
      "--window-size=1440,900",
      "--window-position=80,80",
      url,
    ],
    stdout: "null",
    stderr: "null",
  }).spawn();
}

async function stop(child: Deno.ChildProcess) {
  try {
    child.kill("SIGTERM");
  } catch { /* déjà fini */ }
  await child.status;
  await sleep(1500);
}

function pss(rootPid: number): number {
  // Somme des PSS (ko) du processus et de tous ses descendants.
  const kids = new Map<number, number[]>();
  for (const e of Deno.readDirSync("/proc")) {
    if (!/^\d+$/.test(e.name)) continue;
    try {
      const st = Deno.readTextFileSync(`/proc/${e.name}/stat`);
      const ppid = Number(st.slice(st.lastIndexOf(")") + 2).split(" ")[1]);
      kids.set(ppid, [...(kids.get(ppid) ?? []), Number(e.name)]);
    } catch { /* disparu */ }
  }
  let total = 0;
  const todo = [rootPid];
  while (todo.length) {
    const pid = todo.pop()!;
    try {
      const r = Deno.readTextFileSync(`/proc/${pid}/smaps_rollup`);
      total += Number(/^Pss:\s+(\d+)/m.exec(r)?.[1] ?? 0);
    } catch { /* disparu */ }
    todo.push(...(kids.get(pid) ?? []));
  }
  return total;
}

const result: any = { label, bin, startup_ms: [], speedometer: [], pss_mb: null };

// 1. Démarrage à froid du profil (3 fois, profil déjà créé après la 1re).
for (let i = 0; i < 4; i++) {
  const t0 = performance.now();
  const child = launch("about:blank");
  const page = await pageTarget();
  const cdp = await Cdp.open(page.webSocketDebuggerUrl);
  await cdp.eval("document.readyState");
  const t = performance.now() - t0;
  if (i > 0) result.startup_ms.push(Math.round(t)); // 1re = création du profil
  cdp.ws.close();
  await stop(child);
}

// 2. Speedometer 3.1.
for (let i = 0; i < runs; i++) {
  const child = launch("https://browserbench.org/Speedometer3.1/?startAutomatically=true");
  const page = await pageTarget();
  const cdp = await Cdp.open(page.webSocketDebuggerUrl);
  let score: number | null = null;
  const deadline = Date.now() + 15 * 60 * 1000;
  while (Date.now() < deadline) {
    await sleep(3000);
    const v = await cdp.eval(
      `location.hash === '#summary' ? document.querySelector('#result-number')?.textContent : null`,
    );
    if (v) {
      score = Number(String(v).trim());
      break;
    }
  }
  result.speedometer.push(score);
  console.error(`${label} Speedometer ${i + 1}/${runs} : ${score}`);
  cdp.ws.close();
  await stop(child);
}

// 3. Mémoire avec 5 sites.
{
  const child = launch("about:blank");
  const page = await pageTarget();
  const cdp = await Cdp.open(page.webSocketDebuggerUrl);
  const sites = [
    "https://fr.wikipedia.org/wiki/Typographie",
    "https://github.com/imputnet/helium",
    "https://news.ycombinator.com/",
    "https://developer.mozilla.org/fr/",
    "https://helium.computer/",
  ];
  await cdp.send("Page.navigate", { url: sites[0] });
  for (const s of sites.slice(1)) {
    await fetch(`http://127.0.0.1:${port}/json/new?${s}`, { method: "PUT" });
  }
  await sleep(20000);
  result.pss_mb = Math.round(pss(child.pid) / 1024);
  cdp.ws.close();
  await stop(child);
}

await Deno.remove(profile, { recursive: true });
await Deno.writeTextFile(`${outDir}/bench-${label}.json`, JSON.stringify(result, null, 2));
console.log(JSON.stringify(result));
