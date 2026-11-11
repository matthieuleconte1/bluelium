# Helium Glyphe — Shimmer servi en page interne native (chrome://new-tab-page).
# Plus d'extension : les fichiers de Shimmer (déjà empaquetés dans
# shimmer_resources.pak) sont servis par une WebUI. Shimmer retombe sur
# localStorage sans chrome.storage. Corrige le changement de favicon au
# chargement (favicon de l'extension) : la page garde l'icône du nouvel onglet.

NEW_FILES = {
  'chrome/browser/ui/webui/new_tab_page/glyphe_shimmer_ui.h': '''// Helium Glyphe — nouvel onglet Shimmer natif.
#ifndef CHROME_BROWSER_UI_WEBUI_NEW_TAB_PAGE_GLYPHE_SHIMMER_UI_H_
#define CHROME_BROWSER_UI_WEBUI_NEW_TAB_PAGE_GLYPHE_SHIMMER_UI_H_

#include "content/public/browser/web_ui_controller.h"

class GlypheShimmerUI : public content::WebUIController {
 public:
  explicit GlypheShimmerUI(content::WebUI* web_ui);
  GlypheShimmerUI(const GlypheShimmerUI&) = delete;
  GlypheShimmerUI& operator=(const GlypheShimmerUI&) = delete;
  ~GlypheShimmerUI() override;

 private:
  WEB_UI_CONTROLLER_TYPE_DECL();
};

#endif  // CHROME_BROWSER_UI_WEBUI_NEW_TAB_PAGE_GLYPHE_SHIMMER_UI_H_
''',
  'chrome/browser/ui/webui/new_tab_page/glyphe_shimmer_ui.cc': '''// Helium Glyphe — nouvel onglet Shimmer natif.
#include "chrome/browser/ui/webui/new_tab_page/glyphe_shimmer_ui.h"

#include <memory>
#include <string_view>

#include "base/memory/ref_counted_memory.h"
#include "base/strings/stringprintf.h"
#include "chrome/browser/profiles/profile.h"
#include "chrome/browser/themes/theme_service.h"
#include "chrome/browser/themes/theme_service_factory.h"
#include "chrome/browser/ui/webui/favicon_source.h"
#include "ui/color/glyphe_prism.h"
#include "chrome/common/webui_url_constants.h"
#include "components/favicon_base/favicon_url_parser.h"
#include "content/public/browser/url_data_source.h"
#include "content/public/browser/web_ui.h"
#include "content/public/browser/web_ui_data_source.h"
#include "services/network/public/mojom/content_security_policy.mojom.h"
#include "third_party/shimmer/resources/grit/shimmer_resources.h"
#include "third_party/shimmer/resources/grit/shimmer_resources_map.h"

namespace {

// Couleur du thème du navigateur pour Shimmer (« suivre le navigateur ») :
// la couleur choisie, ou Prism si aucune (gris, réinitialisation).
std::string GlypheThemeJson(Profile* profile) {
  SkColor seed = ui::kGlyphePrismSeed;
  if (const ThemeService* theme = ThemeServiceFactory::GetForProfile(profile);
      theme && !theme->GetIsGrayscale() && theme->GetUserColor()) {
    seed = *theme->GetUserColor();
  }
  return base::StringPrintf(R"({"seed":"#%02x%02x%02x"})", SkColorGetR(seed),
                            SkColorGetG(seed), SkColorGetB(seed));
}

}  // namespace

GlypheShimmerUI::GlypheShimmerUI(content::WebUI* web_ui)
    : content::WebUIController(web_ui) {
  Profile* profile = Profile::FromWebUI(web_ui);
  content::WebUIDataSource* source = content::WebUIDataSource::CreateAndAdd(
      profile, chrome::kChromeUINewTabPageHost);

  constexpr std::string_view kPrefix = "shimmer/";
  for (const webui::ResourcePath& resource : kShimmerResources) {
    std::string_view path = resource.path;
    if (path.starts_with(kPrefix)) {
      path.remove_prefix(kPrefix.size());
    }
    if (path == "manifest.json" || path == "favicon.svg") {
      continue;
    }
    source->AddResourcePath(path, resource.id);
  }
  source->SetDefaultResource(IDR_SHIMMER_INDEX_HTML);
  source->SetRequestFilter(
      base::BindRepeating(
          [](const std::string& path) { return path == "glyphe-theme.json"; }),
      base::BindRepeating(
          [](Profile* profile, const std::string&,
             content::WebUIDataSource::GotDataCallback callback) {
            std::move(callback).Run(base::MakeRefCounted<base::RefCountedString>(
                GlypheThemeJson(profile)));
          },
          base::Unretained(profile)));

  using Directive = network::mojom::CSPDirectiveName;
  source->OverrideContentSecurityPolicy(Directive::ScriptSrc,
                                        "script-src 'self';");
  source->OverrideContentSecurityPolicy(Directive::StyleSrc,
                                        "style-src 'self' 'unsafe-inline';");
  source->OverrideContentSecurityPolicy(
      Directive::ImgSrc,
      "img-src 'self' https: data: blob: chrome://favicon2;");
  source->OverrideContentSecurityPolicy(Directive::ConnectSrc,
                                        "connect-src 'self' https:;");
  source->OverrideContentSecurityPolicy(Directive::FontSrc,
                                        "font-src 'self' data:;");
  source->OverrideContentSecurityPolicy(
      Directive::MediaSrc, "media-src 'self' https: data: blob:;");
  source->DisableTrustedTypesCSP();

  content::URLDataSource::Add(
      profile, std::make_unique<FaviconSource>(
                   profile, chrome::FaviconUrlFormat::kFavicon2));
}

GlypheShimmerUI::~GlypheShimmerUI() = default;

WEB_UI_CONTROLLER_TYPE_IMPL(GlypheShimmerUI)
''',
}

EDITS = [
  # Le nouvel onglet sert Shimmer au lieu de la page Chromium.
  ('chrome/browser/ui/webui/new_tab_page/new_tab_page_ui.cc',
   '  return std::make_unique<NewTabPageUI>(web_ui);\n}\n',
   '  // Helium Glyphe : Shimmer en page interne native.\n'
   '  return std::make_unique<GlypheShimmerUI>(web_ui);\n}\n'),
  ('chrome/browser/ui/webui/new_tab_page/new_tab_page_ui.cc',
   '#include "chrome/browser/ui/webui/new_tab_page/new_tab_page_ui.h"\n',
   '#include "chrome/browser/ui/webui/new_tab_page/new_tab_page_ui.h"\n\n'
   '#include "chrome/browser/ui/webui/new_tab_page/glyphe_shimmer_ui.h"\n'),
  ('chrome/browser/ui/webui/new_tab_page/BUILD.gn',
   '    "new_tab_page_ui.cc",\n',
   '    "glyphe_shimmer_ui.cc",\n    "glyphe_shimmer_ui.h",\n    "new_tab_page_ui.cc",\n'),

  # Plus d'extension qui remplace chrome://newtab.
  ('chrome/browser/extensions/component_loader.cc',
   '    AddUBlock();\n    AddShimmerTab();\n',
   '    AddUBlock();\n'
   '    // Helium Glyphe : Shimmer servi en page interne (glyphe_shimmer_ui).\n'),

  # Pas de favicon propre à Shimmer : l'onglet garde l'icône du nouvel onglet.
  ('third_party/shimmer/index.html',
   '<link rel="icon" type="image/svg+xml" href="./favicon.svg" />',
   '<!-- Helium Glyphe : pas de favicon Shimmer (icône du nouvel onglet) -->'),

  # Le convertisseur nuit rouge s'applique aussi au nouvel onglet.
  ('chrome/browser/ui/glyphe_night_tab_helper.cc',
   '  if (!url.SchemeIsHTTPOrHTTPS() && !url.SchemeIsFile() &&\n'
   '      !url.IsAboutBlank()) {\n',
   '  const bool is_new_tab_page = url.SchemeIs("chrome") &&\n'
   '                               url.host() == "new-tab-page";\n'
   '  if (!url.SchemeIsHTTPOrHTTPS() && !url.SchemeIsFile() &&\n'
   '      !url.IsAboutBlank() && !is_new_tab_page) {\n'),
]

# Shimmer suit le thème Glyphe : la « stratégie BrowserThemeColor » qu'il
# cherchait dans /etc est remplacée par glyphe-theme.json (couleur du thème),
# et l'option « Couleurs du navigateur » est activée par défaut.
EDITS += [
  ('third_party/shimmer/assets/index-kwRkEiyG.js',
   'async function jh(){for(let e of hh){let t=await Ah(e);if(!t)continue;let n=[...t.matchAll(/addRow\\("([^"]+\\.json)"/g)].map(e=>e[1]);for(let t of n.sort())try{let n=JSON.parse(await Ah(e+t)??`{}`).BrowserThemeColor;if(typeof n==`string`&&/^#[0-9a-f]{6}$/i.test(n))return n}catch{}}return null}',
   'async function jh(){try{let e=await fetch(`glyphe-theme.json`,{cache:`no-store`});if(e.ok){let t=(await e.json()).seed;if(typeof t==`string`&&/^#[0-9a-f]{6}$/i.test(t))return t}}catch{}return null}/*Glyphe*/'),
  ('third_party/shimmer/assets/index-kwRkEiyG.js', 'browserTheme:!1,themeColor:``', 'browserTheme:!0/*Glyphe*/,themeColor:``'),
]
