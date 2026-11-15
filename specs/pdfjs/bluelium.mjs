// Bluelium : le lecteur Mozilla complet consomme le flux intercepté par Chromium.
const api = chrome.pdfViewerPrivate;
const invoke = (name, ...args) => new Promise((resolve, reject) => {
  api[name](...args, value => {
    const error = chrome.runtime.lastError;
    error ? reject(new Error(error.message)) : resolve(value);
  });
});

export async function start(app, options, config) {
  options.setAll({
    defaultUrl: "",
    disablePreferences: true,
    disableHistory: true,
    enableScripting: true,
    enablePermissions: true,
    externalLinkTarget: 2,
    enableGuessAltText: false,
    enableNewAltTextWhenAddingImage: false,
    enableUpdatedAddImage: false,
    // Aucun téléchargement de modèle ni service distant.
    enableAltText: false,
    enableSignatureVerification: false,
  });
  try {
    const info = await invoke("getStreamInfo");
    app.isViewerEmbedded = info.embedded;
    // Respecter le blocage JavaScript du site, comme le lecteur Chromium.
    if (chrome.contentSettings) {
      const setting = await new Promise(resolve => {
        chrome.contentSettings.javascript.get({
          primaryUrl: info.originalUrl, secondaryUrl: window.location.origin,
        }, result => {
          const error = chrome.runtime.lastError;
          resolve(!error && result?.setting === "allow");
        });
      });
      options.set("enableScripting", setting);
    }
    const refreshTheme = async () => {
      try {
        const theme = await invoke("getBlueliumTheme");
        const root = document.documentElement;
        root.style.colorScheme = theme.dark ? "dark" : "light";
        for (const [key, value] of Object.entries(theme)) {
          if (key !== "dark") root.style.setProperty(`--bluelium-${key}`, value);
        }
      } catch { /* Le document peut avoir été fermé entre deux lectures. */ }
    };
    await refreshTheme();
    // Les couleurs système changent aussi quand le profil impose clair/sombre.
    // Actualiser les lecteurs visibles et au retour de la fenêtre, sans recharger.
    window.addEventListener("focus", refreshTheme);
    const timer = setInterval(() => {
      if (!document.hidden) refreshTheme();
    }, 2000);
    window.addEventListener("pagehide", () => clearInterval(timer), { once: true });
    await app.run(config);
    app.setTitleUsingUrl(info.originalUrl);
    const chunks = [];
    let total = 0;
    for (;;) {
      const chunk = await invoke("readPdfStream");
      if (chunk.done) break;
      const bytes = new Uint8Array(chunk.data);
      chunks.push(bytes);
      total += bytes.length;
    }
    const data = new Uint8Array(total);
    let offset = 0;
    for (const chunk of chunks) {
      data.set(chunk, offset);
      offset += chunk.length;
    }
    chunks.length = 0;
    // La base d'origine conserve les liens relatifs sans refaire le chargement.
    await app.open({ data, docBaseUrl: info.originalUrl });
    // L'API native refuse les documents integres a une page HTML.
    if (!info.embedded) api.setPdfDocumentTitle(document.title);
    if (app.pdfViewer) {
      const hash = new URL(info.originalUrl).hash.slice(1);
      if (hash) app.pdfLinkService.setHash(hash);
    }
    api.onSave.addListener(streamUrl => {
      if (streamUrl === info.streamUrl) app.downloadOrSave();
    });
    api.onShouldUpdateViewport.addListener((streamUrl, url) => {
      if (streamUrl === info.streamUrl) app.pdfLinkService.setHash(new URL(url).hash.slice(1));
    });
    // Chromium garde l'URL PDF dans la barre : les raccourcis doivent cibler
    // le lecteur lorsqu'ils sont traités dans cette frame.
  } catch (error) {
    console.error("Bluelium PDF.js:", error);
    const alert = document.getElementById("viewer-alert");
    alert.classList.remove("visuallyHidden");
    alert.textContent = `Impossible d’ouvrir ce PDF. ${error.message}`;
  }
}
