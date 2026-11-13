"""Bluelium : « Les plus visités » et « Fermés récemment » dans Shimmer.

Shimmer est écrit comme extension : il appelle chrome.topSites,
chrome.sessions, chrome.permissions et l'API de favicons des extensions
(chrome.runtime.getURL('/_favicon/')), absents d'une page interne. Ici :
- un gestionnaire natif (chrome.send) renvoie les sites les plus visités
  (TopSites), les onglets fermés récemment (TabRestoreService) et rouvre un
  onglet ;
- glyphe-shim.js, chargé avant Shimmer, recrée ces API par-dessus ;
- les icônes passent par chrome://favicon2 (déjà servi par la page).
"""

UI = 'chrome/browser/ui/webui/new_tab_page/glyphe_shimmer_ui.cc'

SHIM = r'''// Bluelium : API d'extension attendues par Shimmer, sur chrome.send.
(() => {
  if (typeof chrome === 'undefined' || !chrome.send) {
    return;
  }
  const pending = new Map();
  let next = 0;
  const call = (name, ...args) => new Promise((resolve) => {
    const id = 'glyphe' + (++next);
    pending.set(id, resolve);
    chrome.send(name, [id, ...args]);
  });
  window.cr = window.cr || {};
  const previous = window.cr.webUIResponse;
  window.cr.webUIResponse = (id, ok, value) => {
    const resolve = pending.get(id);
    if (resolve) {
      pending.delete(id);
      resolve(value);
    } else if (previous) {
      previous(id, ok, value);
    }
  };
  const events = {addListener() {}, removeListener() {}, hasListener() { return false; }};
  chrome.topSites = {
    get(callback) { call('glypheTopSites').then(callback); },
  };
  chrome.sessions = {
    getRecentlyClosed(options, callback) {
      call('glypheRecentlyClosed').then(callback);
    },
    restore(sessionId) { return call('glypheRestore', String(sessionId)); },
    onChanged: events,
  };
  // Seules les permissions d'API sont « accordées » : pas d'accès aux sites.
  const granted = (request) => !!(request && request.permissions &&
                                  !(request.origins && request.origins.length));
  chrome.permissions = {
    contains: async (request) => granted(request),
    request: async (request) => granted(request),
    onAdded: events,
    onRemoved: events,
  };
  chrome.runtime = chrome.runtime || {};
  if (!chrome.runtime.getURL) {
    chrome.runtime.getURL = (path) => path.startsWith('/_favicon/')
        ? 'chrome://favicon2/' : new URL(path, location.href).href;
  }
  if (!chrome.runtime.getManifest) {
    chrome.runtime.getManifest = () => ({name: 'Shimmer', version: '1.3.0'});
  }
})();
'''

HANDLER = '''
// Bluelium : sites les plus visités, onglets fermés et réouverture pour
// Shimmer (via glyphe-shim.js).
class GlypheShimmerHandler : public content::WebUIMessageHandler {
 public:
  explicit GlypheShimmerHandler(Profile* profile) : profile_(profile) {}
  GlypheShimmerHandler(const GlypheShimmerHandler&) = delete;
  GlypheShimmerHandler& operator=(const GlypheShimmerHandler&) = delete;
  ~GlypheShimmerHandler() override = default;

  void RegisterMessages() override {
    web_ui()->RegisterMessageCallback(
        "glypheTopSites",
        base::BindRepeating(&GlypheShimmerHandler::HandleTopSites,
                            base::Unretained(this)));
    web_ui()->RegisterMessageCallback(
        "glypheRecentlyClosed",
        base::BindRepeating(&GlypheShimmerHandler::HandleRecentlyClosed,
                            base::Unretained(this)));
    web_ui()->RegisterMessageCallback(
        "glypheRestore",
        base::BindRepeating(&GlypheShimmerHandler::HandleRestore,
                            base::Unretained(this)));
  }

 private:
  void HandleTopSites(const base::ListValue& args) {
    AllowJavascript();
    const std::string callback_id = args[0].GetString();
    scoped_refptr<history::TopSites> top_sites =
        TopSitesFactory::GetForProfile(profile_);
    if (!top_sites) {
      ResolveJavascriptCallback(base::Value(callback_id),
                                base::Value(base::ListValue()));
      return;
    }
    top_sites->GetMostVisitedURLs(
        base::BindOnce(&GlypheShimmerHandler::OnTopSites,
                       weak_factory_.GetWeakPtr(), callback_id));
  }

  void OnTopSites(const std::string& callback_id,
                  const history::MostVisitedURLList& urls) {
    if (!IsJavascriptAllowed()) {
      return;
    }
    base::ListValue list;
    for (const history::MostVisitedURL& site : urls) {
      base::DictValue entry;
      entry.Set("title", base::UTF16ToUTF8(site.title));
      entry.Set("url", site.url.spec());
      list.Append(std::move(entry));
    }
    ResolveJavascriptCallback(base::Value(callback_id),
                              base::Value(std::move(list)));
  }

  void HandleRecentlyClosed(const base::ListValue& args) {
    AllowJavascript();
    base::ListValue list;
    if (sessions::TabRestoreService* service =
            TabRestoreServiceFactory::GetForProfile(profile_)) {
      service->LoadTabsFromLastSession();
      for (const auto& entry : service->entries()) {
        if (entry->type != sessions::tab_restore::Type::TAB) {
          continue;
        }
        const auto& tab =
            static_cast<const sessions::tab_restore::Tab&>(*entry);
        if (tab.navigations.empty()) {
          continue;
        }
        const sessions::SerializedNavigationEntry& navigation =
            tab.navigations[tab.normalized_navigation_index()];
        base::DictValue closed_tab;
        closed_tab.Set("url", navigation.virtual_url().spec());
        closed_tab.Set("title", base::UTF16ToUTF8(navigation.title()));
        closed_tab.Set("sessionId", base::NumberToString(entry->id.id()));
        base::DictValue item;
        item.Set("tab", std::move(closed_tab));
        list.Append(std::move(item));
        if (list.size() >= 10) {
          break;
        }
      }
    }
    ResolveJavascriptCallback(args[0], base::Value(std::move(list)));
  }

  void HandleRestore(const base::ListValue& args) {
    AllowJavascript();
    int session_id = 0;
    sessions::TabRestoreService* service =
        TabRestoreServiceFactory::GetForProfile(profile_);
    sessions::LiveTabContext* context =
        BrowserLiveTabContext::FindContextForWebContents(
            web_ui()->GetWebContents());
    const bool ok = service && context && args.size() > 1 &&
                    base::StringToInt(args[1].GetString(), &session_id);
    if (ok) {
      service->RestoreEntryById(context,
                                SessionID::FromSerializedValue(session_id),
                                WindowOpenDisposition::NEW_FOREGROUND_TAB);
    }
    ResolveJavascriptCallback(args[0], base::Value(ok));
  }

  raw_ptr<Profile> profile_;
  base::WeakPtrFactory<GlypheShimmerHandler> weak_factory_{this};
};

}  // namespace

GlypheShimmerUI::GlypheShimmerUI(content::WebUI* web_ui)'''

NEW_FILES = {}

EDITS = [
  (UI,
   '#include "base/memory/ref_counted_memory.h"\n',
   '#include "base/memory/ref_counted_memory.h"\n'
   '#include "base/memory/raw_ptr.h"\n'
   '#include "base/memory/weak_ptr.h"\n'
   '#include "base/strings/string_number_conversions.h"\n'
   '#include "base/strings/utf_string_conversions.h"\n'
   '#include "base/values.h"\n'
   '#include "chrome/browser/history/top_sites_factory.h"  // nogncheck\n'
   '#include "chrome/browser/sessions/tab_restore_service_factory.h"  // nogncheck\n'
   '#include "chrome/browser/ui/browser_live_tab_context.h"  // nogncheck\n'
   '#include "components/history/core/browser/top_sites.h"\n'
   '#include "components/sessions/core/tab_restore_service.h"\n'
   '#include "components/sessions/core/tab_restore_types.h"\n'
   '#include "content/public/browser/web_ui_message_handler.h"\n'
   '#include "ui/base/window_open_disposition.h"\n'),
  (UI,
   '}  // namespace\n\nGlypheShimmerUI::GlypheShimmerUI(content::WebUI* web_ui)',
   '// Bluelium : API d\'extension attendues par Shimmer (voir glyphe-shim.js).\n'
   'constexpr char kGlypheShim[] = R"JS(' + SHIM + ')JS";\n'
   + HANDLER),
  (UI,
   '          [](const std::string& path) { return path == "glyphe-theme.json"; }),\n',
   '          [](const std::string& path) {\n'
   '            return path == "glyphe-theme.json" || path == "glyphe-shim.js";\n'
   '          }),\n'),
  (UI,
   '          [](Profile* profile, const std::string&,\n'
   '             content::WebUIDataSource::GotDataCallback callback) {\n'
   '            std::move(callback).Run(base::MakeRefCounted<base::RefCountedString>(\n'
   '                GlypheThemeJson(profile)));\n'
   '          },\n',
   '          [](Profile* profile, const std::string& path,\n'
   '             content::WebUIDataSource::GotDataCallback callback) {\n'
   '            std::move(callback).Run(base::MakeRefCounted<base::RefCountedString>(\n'
   '                path == "glyphe-shim.js" ? std::string(kGlypheShim)\n'
   '                                         : GlypheThemeJson(profile)));\n'
   '          },\n'),
  (UI,
   '  content::URLDataSource::Add(\n'
   '      profile, std::make_unique<FaviconSource>(\n'
   '                   profile, chrome::FaviconUrlFormat::kFavicon2));\n',
   '  content::URLDataSource::Add(\n'
   '      profile, std::make_unique<FaviconSource>(\n'
   '                   profile, chrome::FaviconUrlFormat::kFavicon2));\n'
   '  web_ui->AddMessageHandler(\n'
   '      std::make_unique<GlypheShimmerHandler>(profile));  // Bluelium\n'),
  ('third_party/shimmer/index.html',
   '      <script type="module" crossorigin src="./assets/index-kwRkEiyG.js"></script>\n',
   '      <script src="./glyphe-shim.js"></script>\n'
   '      <script type="module" crossorigin src="./assets/index-kwRkEiyG.js"></script>\n'),
]
