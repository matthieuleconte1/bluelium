// Tests du contrat du pont : octets, erreurs, isolation des événements de sauvegarde.
import assert from 'node:assert/strict';
import test from 'node:test';

function fixture({ error = false, embedded = false } = {}) {
  const events = {};
  const style = {};
  const alert = { classList: { remove() {} }, textContent: '' };
  globalThis.window = { location: { origin: 'chrome-extension://pdf-test' }, addEventListener(name, fn) { events[name] = fn; } };
  globalThis.document = {
    title: 'Exemple PDF', hidden: false,
    documentElement: { style: { setProperty(key, value) { style[key] = value; } } },
    getElementById() { return alert; },
  };
  const bytes = [new Uint8Array([37, 80, 68]), new Uint8Array([70, 45, 49])];
  let readCount = 0, saves = 0, opened, settings, title;
  const info = { streamUrl: 'stream-prive', originalUrl: 'https://example.test/doc.pdf#page=2', embedded };
  const runtime = {};
  globalThis.chrome = {
    runtime,
    pdfViewerPrivate: {
      getStreamInfo(cb) { cb(info); },
      getBlueliumTheme(cb) { cb({ dark: true, surface: '#151a2b' }); },
      readPdfStream(cb) {
        if (error) {
          runtime.lastError = { message: 'ERR_CONNECTION_RESET' };
          cb();
          delete runtime.lastError;
          return;
        }
        const data = bytes[readCount++];
        cb({ done: !data, data: data?.buffer });
      },
      setPdfDocumentTitle(value) { title = value; },
      onSave: { addListener(fn) { events.save = fn; } },
      onShouldUpdateViewport: { addListener(fn) { events.viewport = fn; } },
    },
  };
  const app = {
    async run() {},
    setTitleUsingUrl(url) { assert.equal(url, info.originalUrl); },
    async open(args) { opened = args; },
    downloadOrSave() { saves++; },
    pdfViewer: {},
    pdfLinkService: { setHash(hash) { events.hash = hash; } },
  };
  return {
    app, options: { setAll(value) { settings = value; }, set(key, value) { settings[key] = value; } }, events, style, alert,
    get opened() { return opened; }, get settings() { return settings; },
    get saves() { return saves; }, get title() { return title; },
  };
}

test('préserve les octets, la base des liens et les outils PDF.js', async () => {
  const f = fixture();
  const { start } = await import('../../specs/pdfjs/bluelium.mjs?success');
  await start(f.app, f.options, {});
  f.events.pagehide();
  assert.deepEqual([...f.opened.data], [37, 80, 68, 70, 45, 49]);
  assert.equal(f.opened.docBaseUrl, 'https://example.test/doc.pdf#page=2');
  assert.equal(f.settings.enableScripting, true);
  assert.equal(f.settings.enablePermissions, true);
  assert.equal(f.settings.defaultUrl, '');
  assert.equal(f.settings.enableGuessAltText, false);
  assert.equal(f.style['--bluelium-surface'], '#151a2b');
  assert.equal(f.title, 'Exemple PDF');
  assert.equal(f.events.hash, 'page=2');
  f.events.save('autre-flux');
  assert.equal(f.saves, 0);
  f.events.save('stream-prive');
  assert.equal(f.saves, 1);
});

test('une erreur réseau ne produit pas de PDF tronqué ni de seconde requête', async () => {
  const f = fixture({ error: true });
  const { start } = await import('../../specs/pdfjs/bluelium.mjs?failure');
  const previous = console.error;
  console.error = () => {};
  try { await start(f.app, f.options, {}); } finally { console.error = previous; }
  f.events.pagehide();
  assert.equal(f.opened, undefined);
  assert.match(f.alert.textContent, /ERR_CONNECTION_RESET/);
});

test('un PDF integre ne change pas le titre de sa page hote', async () => {
  const f = fixture({ embedded: true });
  const { start } = await import('../../specs/pdfjs/bluelium.mjs?embedded');
  await start(f.app, f.options, {});
  f.events.pagehide();
  assert.equal(f.title, undefined);
  assert.equal(f.app.isViewerEmbedded, true);
  assert.ok(f.opened);
});

test('le blocage JavaScript du site est applique aux scripts du PDF', async () => {
  const f = fixture();
  chrome.contentSettings = { javascript: { get(details, callback) {
    assert.equal(details.primaryUrl, 'https://example.test/doc.pdf#page=2');
    callback({ setting: 'block' });
  } } };
  const { start } = await import('../../specs/pdfjs/bluelium.mjs?blocked-scripts');
  await start(f.app, f.options, {});
  f.events.pagehide();
  assert.equal(f.settings.enableScripting, false);
  assert.ok(f.opened);
});
