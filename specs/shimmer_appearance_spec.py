"""Bluelium : favicons du profil et suivi du thème natif dans Shimmer.

S'applique après shimmer-sessions. Shimmer est une WebUI, pas une extension :
les icônes passent par FaviconService, sans permission d'hôte ni lecture réseau.
Les PNG en data: restent lisibles par les canvas (analyse et teinte des icônes),
contrairement aux images chrome://favicon2 d'une autre origine.
"""

UI = 'chrome/browser/ui/webui/new_tab_page/glyphe_shimmer_ui.cc'
JS = 'third_party/shimmer/assets/index-kwRkEiyG.js'
NEW_FILES = {}

PERMISSIONS = r'''  // Bluelium : le réglage contrôle les icônes locales, sans accès aux sites.
  const iconKey = 'bluelium-native-favicons';
  const iconsEnabled = () => {
    try { return localStorage.getItem(iconKey) !== 'off'; } catch { return true; }
  };
  const event = () => {
    const listeners = new Set();
    return {
      addListener: (fn) => listeners.add(fn),
      removeListener: (fn) => listeners.delete(fn),
      hasListener: (fn) => listeners.has(fn),
      emit: (value) => { for (const fn of listeners) fn(value); },
    };
  };
  const added = event();
  const removed = event();
  const supported = (request) => !!(request && !request.origins?.length &&
      request.permissions?.length && request.permissions.every(
          (name) => ['favicon', 'topSites', 'sessions'].includes(name)));
  const granted = (request) => supported(request) &&
      (!request.permissions.includes('favicon') || iconsEnabled());
  const setIcons = (enabled) => {
    try { localStorage.setItem(iconKey, enabled ? 'on' : 'off'); } catch {}
    (iconsEnabled() ? added : removed).emit({permissions: ['favicon']});
  };
  chrome.permissions = {
    contains: async (request) => granted(request),
    request: async (request) => {
      if (!supported(request)) return false;
      if (request.permissions.includes('favicon')) setIcons(true);
      return granted(request);
    },
    remove: async (request) => {
      if (!supported(request) || request.permissions.length !== 1 ||
          request.permissions[0] !== 'favicon') return false;
      setIcons(false);
      return !iconsEnabled();
    },
    onAdded: added,
    onRemoved: removed,
  };
  window.addEventListener('storage', (event) => {
    if (event.key === iconKey || event.key === null) {
      (iconsEnabled() ? added : removed).emit({permissions: ['favicon']});
    }
  });
  // Bluelium : pont privé de la page interne, sans simuler une extension.
  window.glypheBrowser = {
    getTheme: () => call('glypheTheme'),
    getFavicon: (url) => iconsEnabled() ? call('glypheFavicon', url) : Promise.resolve(''),
  };
  const previousListener = window.cr.webUIListenerCallback;
  window.cr.webUIListenerCallback = (name, ...args) => {
    if (name === 'glyphe-theme-changed') {
      window.dispatchEvent(new Event(name));
    } else if (previousListener) {
      previousListener(name, ...args);
    }
  };'''

THEME = '''// Bluelium : couleurs réellement calculées par le navigateur (Prism,
// accent libre, OLED et nuit), plutôt qu'une seconde palette Material.
base::DictValue GlypheShimmerTheme(Profile* profile,
                                  const ui::ColorProvider& provider) {
  const auto hex = [](SkColor color) {
    return base::StringPrintf("#%02x%02x%02x", SkColorGetR(color),
                              SkColorGetG(color), SkColorGetB(color));
  };
  SkColor seed = ui::kGlyphePrismSeed;
  if (const ThemeService* theme = ThemeServiceFactory::GetForProfile(profile);
      theme && !theme->GetIsGrayscale() && theme->GetUserColor()) {
    seed = *theme->GetUserColor();
  }
  base::DictValue result;
  result.Set("seed", hex(seed));
  result.Set("dark", color_utils::IsDark(provider.GetColor(ui::kColorSysSurface)));
  base::DictValue colors;
  const auto add = [&](const char* name, ui::ColorId id) {
    colors.Set(name, hex(provider.GetColor(id)));
  };
  add("--bg-surface", ui::kColorSysSurface);
  add("--background", ui::kColorSysSurface);
  add("--primary", ui::kColorSysOnSurface);
  add("--secondary", ui::kColorSysOnSurfaceVariant);
  add("--tertiary", ui::kColorSysOutline);
  add("--white", ui::kColorSysOnPrimary);
  add("--helium-blue", ui::kColorSysPrimary);
  add("--helium-blue-hover", ui::kColorSysPrimary);
  add("--helium-blue-press", ui::kColorSysPrimary);
  add("--helium-elevated", ui::kColorSysPrimary);
  add("--tooltip-bg", ui::kColorSysSurfaceContainerHigh);
  add("--bg-gradient-start", ui::kColorSysSurfaceContainerLow);
  add("--bg-gradient-end", ui::kColorSysPrimaryContainer);
  add("--intro-gradient-start", ui::kColorSysSurfaceContainerLow);
  add("--intro-gradient-end", ui::kColorSysPrimaryContainer);
  add("--stars-top", ui::kColorSysSurfaceContainerLowest);
  add("--stars-bottom", ui::kColorSysPrimaryContainer);
  add("--star-color", ui::kColorSysOnPrimaryContainer);
  result.Set("colors", std::move(colors));
  return result;
}

'''

METHODS = '''  // Bluelium : observer le fournisseur de la fenêtre couvre aussi le mode
  // système et les mises à jour différées des couleurs après Personnaliser.
  void OnColorProviderChanged() override {
    if (web_contents() && IsJavascriptAllowed()) {
      FireWebUIListener("glyphe-theme-changed");
    }
  }

  void OnJavascriptDisallowed() override {
    favicon_tasks_.TryCancelAll();
    weak_factory_.InvalidateWeakPtrs();
  }

  void HandleTheme(const base::ListValue& args) {
    if (args.size() != 1 || !args[0].is_string()) {
      return;
    }
    AllowJavascript();
    ResolveJavascriptCallback(
        args[0], GlypheShimmerTheme(profile_, web_contents()->GetColorProvider()));
  }

  // Bluelium : consultation de la base locale uniquement, aucun fetch du site.
  void HandleFavicon(const base::ListValue& args) {
    if (args.size() != 2 || !args[0].is_string() || !args[1].is_string()) {
      return;
    }
    AllowJavascript();
    const GURL url(args[1].GetString());
    auto* service = FaviconServiceFactory::GetForProfile(
        profile_, ServiceAccessType::EXPLICIT_ACCESS);
    if (!service || !url.is_valid() || !url.SchemeIsHTTPOrHTTPS()) {
      ResolveJavascriptCallback(args[0], base::Value(""));
      return;
    }
    service->GetRawFaviconForPageURL(
        url, {favicon_base::IconType::kFavicon}, 64, true,
        base::BindOnce(&GlypheShimmerHandler::OnFavicon,
                       weak_factory_.GetWeakPtr(), args[0].GetString()),
        &favicon_tasks_);
  }

  void OnFavicon(const std::string& callback_id,
                 const favicon_base::FaviconRawBitmapResult& bitmap) {
    if (!IsJavascriptAllowed()) {
      return;
    }
    std::string data;
    if (bitmap.is_valid()) {
      data = "data:image/png;base64," + base::Base64Encode(*bitmap.bitmap_data);
    }
    ResolveJavascriptCallback(base::Value(callback_id), base::Value(data));
  }

'''

EDITS = [
    (UI, '#include "base/memory/raw_ptr.h"\n',
     '#include "base/memory/raw_ptr.h"\n'
     '#include "base/base64.h"\n'
     '#include "base/task/cancelable_task_tracker.h"\n'
     '#include "chrome/browser/favicon/favicon_service_factory.h"\n'
     '#include "components/favicon/core/favicon_service.h"\n'
     '#include "content/public/browser/web_contents.h"\n'
     '#include "content/public/browser/web_contents_observer.h"\n'
     '#include "ui/color/color_id.h"\n'
     '#include "ui/color/color_provider.h"\n'
     '#include "ui/gfx/color_utils.h"\n'),
    (UI, '// Bluelium : API d\'extension attendues par Shimmer (voir glyphe-shim.js).\n',
     THEME + '// Bluelium : API d\'extension attendues par Shimmer (voir glyphe-shim.js).\n'),
    (UI, '''  // Seules les permissions d'API sont « accordées » : pas d'accès aux sites.
  const granted = (request) => !!(request && request.permissions &&
                                  !(request.origins && request.origins.length));
  chrome.permissions = {
    contains: async (request) => granted(request),
    request: async (request) => granted(request),
    onAdded: events,
    onRemoved: events,
  };''', PERMISSIONS),
    (UI, 'class GlypheShimmerHandler : public content::WebUIMessageHandler {',
     'class GlypheShimmerHandler : public content::WebUIMessageHandler,\n'
     '                             public content::WebContentsObserver {'),
    (UI, '  void RegisterMessages() override {\n',
     '  void RegisterMessages() override {\n'
     '    Observe(web_ui()->GetWebContents());\n'
     '    web_ui()->RegisterMessageCallback(\n'
     '        "glypheTheme",\n'
     '        base::BindRepeating(&GlypheShimmerHandler::HandleTheme,\n'
     '                            base::Unretained(this)));\n'
     '    web_ui()->RegisterMessageCallback(\n'
     '        "glypheFavicon",\n'
     '        base::BindRepeating(&GlypheShimmerHandler::HandleFavicon,\n'
     '                            base::Unretained(this)));\n'),
    (UI, ' private:\n  void HandleTopSites(', ' private:\n' + METHODS + '  void HandleTopSites('),
    (UI, '  raw_ptr<Profile> profile_;\n',
     '  raw_ptr<Profile> profile_;\n  base::CancelableTaskTracker favicon_tasks_;\n'),
    ('chrome/browser/ui/webui/new_tab_page/BUILD.gn',
     '    "//chrome/browser/contextual_tasks",\n',
     '    "//chrome/browser/contextual_tasks",\n'
     '    "//chrome/browser/favicon",  # Bluelium : favicons locaux de Shimmer.\n'),
    # Bluelium : remplacer la demande d'accès réseau par le réglage local.
    (JS, 'Wo={origins:[`https://*/*`,`http://*/*`]}', 'Wo={permissions:[`favicon`]}/* Bluelium : icônes locales. */'),
    (JS, 'read_sites_own_hq:`Asks to read sites for their icons. Without it, some show a letter`',
     'read_sites_own_hq:`Uses icons saved by the browser. Sites without a saved icon show a letter`'),
    # Bluelium : contourner le cache vide des anciennes tentatives et les fetchs
    # réservés aux extensions ; les data: fonctionnent aussi dans les canvas.
    (JS, 'function Vp(e){let t=xp(e),n=e,r=bp.get(n);return r||(r=(async()=>{let n=zp()?null:await Fp(e);if(n){let e=pp+(n.s??n.l),t=await Sp(e);if(t?.src)return t;let r=await Lp(n);if(r)return await Cp(e,r),r;Bp()}let r=fp+t,i=await Sp(r);if(i&&Date.now()-i.at<up)return i;if(!await Zo())return i?.src?i:Gp(t);let a=await jp(t);return!a.src&&i?.src?i:(await Cp(r,a),a)})(),bp.set(n,r),r)}',
     'function Vp(e){return Zo().then(t=>t?Gp(e):{src:``,fullBleed:!1})}/* Bluelium : base locale. */'),
    (JS, 'async function Gp(e){let t={src:``,fullBleed:!1};if(typeof chrome>`u`||!chrome.runtime?.id)return t;let n=Hp(e);Wp??=Up(Hp(`https://unknown.invalid/`));let[r,i]=await Promise.all([Up(n),Wp]);return!r||r===i?t:{src:n,fullBleed:!1,...await vp(n)??{}}}',
     'async function Gp(e){let n=await window.glypheBrowser.getFavicon(e);return{src:n,fullBleed:!1,...(n?await vp(n)??{}:{})}}/* Bluelium : PNG natif. */'),
    # Bluelium : garder le choix de suivi de Shimmer, mais employer les jetons
    # natifs et leur mode plutôt que la couleur du système ou du fond animé.
    (JS, 'function Uo(e,t=0){let n=document.documentElement,',
     'var glypheBrowserTheme=null,glypheFollowBrowser=!1;function Uo(e,t=0){glypheFollowBrowser&&glypheBrowserTheme&&(e=glypheBrowserTheme.dark?`dark`:`light`);let n=document.documentElement,'),
    (JS, 'async function jh(){try{let e=await fetch(`glyphe-theme.json`,{cache:`no-store`});if(e.ok){let t=(await e.json()).seed;if(typeof t==`string`&&/^#[0-9a-f]{6}$/i.test(t))return t}}catch{}return null}/*Glyphe*/',
     'async function jh(){try{let e=await window.glypheBrowser.getTheme();if(e&&/^#[0-9a-f]{6}$/i.test(e.seed)&&e.colors){glypheBrowserTheme=e;return e.seed}}catch{}return null}/* Bluelium : thème natif. */'),
    (JS, 'function Mh(e){if(xh?.seed!==e)return!1;',
     'function Mh(e){if(glypheFollowBrowser&&glypheBrowserTheme?.seed===e){let t=JSON.stringify(glypheBrowserTheme),n=Ch!==t;Uo(glypheBrowserTheme.dark?`dark`:`light`);for(let[e,t]of Object.entries(glypheBrowserTheme.colors))document.documentElement.style.setProperty(e,t);return yh=e,Ch=t,n}if(xh?.seed!==e)return!1;'),
    (JS, 'async function Fh(e=``){let t=await jh(),',
     'async function Fh(e=``){glypheFollowBrowser=!0;let t=await jh(),'),
    (JS, 'return xh?.seed!==n&&await Sh(n),{changed:Mh(n),fromPolicy:!!t}',
     'return !glypheBrowserTheme&&xh?.seed!==n&&await Sh(n),{changed:Mh(n),fromPolicy:!!t}/* Bluelium : palette native prioritaire. */'),
    (JS, 'function Bh(e){return vh.addEventListener(`change`,e),()=>vh.removeEventListener(`change`,e)}',
     'function Bh(e){const t=()=>e();window.addEventListener(`glyphe-theme-changed`,t);vh.addEventListener(`change`,t);return()=>{window.removeEventListener(`glyphe-theme-changed`,t);vh.removeEventListener(`change`,t)}}/* Bluelium : suivi en direct. */'),
    (JS, 'if(!U(i).browserTheme){P(me,null),',
     'if(!U(i).browserTheme){glypheFollowBrowser=!1;glypheBrowserTheme=null;for(let e of [`--intro-gradient-start`,`--intro-gradient-end`])document.documentElement.style.removeProperty(e);Uo(U(S));P(me,null),'),
    (JS, ':(P(me,null),Vh()&&rn(pe))',
     ':(P(me,null),Vh(),Uo(U(S)),rn(pe))/* Bluelium : restaurer le mode du fond. */'),
    (JS, 'function Vh(){let e=Ch!==``,t=document.documentElement.style;for(let e of Object.keys(bh))t.removeProperty(e);',
     'function Vh(){glypheFollowBrowser=!1;glypheBrowserTheme=null;let e=Ch!==``,t=document.documentElement.style;for(let e of [...Object.keys(bh),`--intro-gradient-start`,`--intro-gradient-end`])t.removeProperty(e);'),
]
