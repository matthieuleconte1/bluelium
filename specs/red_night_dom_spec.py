# Helium Glyphe — vrai convertisseur « nuit rouge » des pages web.
# Remplace le filtre de calque et le mode sombre forcé de Blink par un script
# qui convertit le CSS et le DOM de chaque cadre (monde isolé), injecté par un
# tab helper natif quand la pref glyphe.red_night.enabled est active.
from pathlib import Path

JS = Path('/root/glyphe/glyphe_night.js').read_text()
assert ')glyphe"' not in JS

OLD_MATRIX = '''#if defined(USE_AURA)
  content::WebContents* contents = web_contents();
  if (!contents || !glyphe_pref_registrar_.prefs()) {
    return;
  }
  gfx::NativeView native_view = contents->GetNativeView();
  if (!native_view || !native_view->layer()) {
    return;
  }
  ui::Layer* page_layer = native_view->layer();
  if (!glyphe_pref_registrar_.prefs()->GetBoolean(
          prefs::kGlypheRedNightEnabled)) {
    if (page_layer->LayerHasCustomColorMatrix()) {
      page_layer->ClearLayerCustomColorMatrix();
    }
    return;
  }
  // Luminance (Rec. 709) envoyée sur le seul canal rouge, à 85 %.
  // La page a déjà été assombrie par Blink (force_dark_mode_enabled).
  cc::FilterOperation::Matrix matrix = {
      0.18f, 0.61f, 0.06f, 0.0f, 0.0f,
      0.0f,  0.0f,  0.0f,  0.0f, 0.0f,
      0.0f,  0.0f,  0.0f,  0.0f, 0.0f,
      0.0f,  0.0f,  0.0f,  1.0f, 0.0f};
  page_layer->SetLayerCustomColorMatrix(matrix);
#endif  // defined(USE_AURA)
'''

NEW_FILES = {
  'chrome/browser/ui/glyphe_night_script.inc':
      '// Généré depuis glyphe_night.js (Helium Glyphe).\n'
      'constexpr char kGlypheNightScript[] = R"glyphe(' + JS + ')glyphe";\n',

  'chrome/browser/ui/glyphe_night_tab_helper.h': '''// Helium Glyphe — injecte le convertisseur « nuit rouge » dans les pages.
#ifndef CHROME_BROWSER_UI_GLYPHE_NIGHT_TAB_HELPER_H_
#define CHROME_BROWSER_UI_GLYPHE_NIGHT_TAB_HELPER_H_

#include "components/prefs/pref_change_registrar.h"
#include "content/public/browser/web_contents_observer.h"
#include "content/public/browser/web_contents_user_data.h"

class GlypheNightTabHelper
    : public content::WebContentsObserver,
      public content::WebContentsUserData<GlypheNightTabHelper> {
 public:
  GlypheNightTabHelper(const GlypheNightTabHelper&) = delete;
  GlypheNightTabHelper& operator=(const GlypheNightTabHelper&) = delete;
  ~GlypheNightTabHelper() override;

 private:
  friend class content::WebContentsUserData<GlypheNightTabHelper>;
  explicit GlypheNightTabHelper(content::WebContents* web_contents);

  bool IsEnabled() const;
  void OnPrefChanged();
  void Inject(content::RenderFrameHost* render_frame_host);

  // content::WebContentsObserver:
  void PrimaryMainDocumentElementAvailable() override;
  void DOMContentLoaded(content::RenderFrameHost* render_frame_host) override;

  PrefChangeRegistrar registrar_;
  bool enabled_ = false;

  WEB_CONTENTS_USER_DATA_KEY_DECL();
};

#endif  // CHROME_BROWSER_UI_GLYPHE_NIGHT_TAB_HELPER_H_
''',

  'chrome/browser/ui/glyphe_night_tab_helper.cc': '''// Helium Glyphe — injecte le convertisseur « nuit rouge » dans les pages.
#include "chrome/browser/ui/glyphe_night_tab_helper.h"

#include "base/functional/bind.h"
#include <string_view>

#include "base/no_destructor.h"
#include "base/strings/utf_string_conversions.h"
#include "chrome/browser/profiles/profile.h"
#include "chrome/common/chrome_isolated_world_ids.h"
#include "chrome/common/pref_names.h"
#include "components/prefs/pref_service.h"
#include "content/public/browser/navigation_controller.h"
#include "content/public/browser/reload_type.h"
#include "content/public/browser/render_frame_host.h"
#include "content/public/browser/web_contents.h"
#include "url/gurl.h"

namespace {

#include "chrome/browser/ui/glyphe_night_script.inc"

const std::u16string& Script() {
  static const base::NoDestructor<std::u16string> script(
      base::UTF8ToUTF16(std::string_view(kGlypheNightScript)));
  return *script;
}

}  // namespace

GlypheNightTabHelper::GlypheNightTabHelper(content::WebContents* web_contents)
    : content::WebContentsObserver(web_contents),
      content::WebContentsUserData<GlypheNightTabHelper>(*web_contents) {
  registrar_.Init(
      Profile::FromBrowserContext(web_contents->GetBrowserContext())
          ->GetPrefs());
  registrar_.Add(prefs::kGlypheRedNightEnabled,
                 base::BindRepeating(&GlypheNightTabHelper::OnPrefChanged,
                                     base::Unretained(this)));
  enabled_ = IsEnabled();
}

GlypheNightTabHelper::~GlypheNightTabHelper() = default;

bool GlypheNightTabHelper::IsEnabled() const {
  return registrar_.prefs() &&
         registrar_.prefs()->GetBoolean(prefs::kGlypheRedNightEnabled);
}

void GlypheNightTabHelper::OnPrefChanged() {
  const bool now = IsEnabled();
  if (now == enabled_) {
    return;
  }
  enabled_ = now;
  if (enabled_) {
    web_contents()->GetPrimaryMainFrame()->ForEachRenderFrameHost(
        [this](content::RenderFrameHost* rfh) { Inject(rfh); });
  } else {
    // Retour à la page d'origine : rechargement.
    web_contents()->GetController().Reload(content::ReloadType::NORMAL,
                                           /*check_for_repost=*/false);
  }
}

void GlypheNightTabHelper::Inject(content::RenderFrameHost* rfh) {
  if (!enabled_ || !rfh || !rfh->IsRenderFrameLive()) {
    return;
  }
  const GURL& url = rfh->GetLastCommittedURL();
  if (!url.SchemeIsHTTPOrHTTPS() && !url.SchemeIsFile() &&
      !url.IsAboutBlank()) {
    return;
  }
  rfh->ExecuteJavaScriptInIsolatedWorld(Script(), base::NullCallback(),
                                        ISOLATED_WORLD_ID_CHROME_INTERNAL);
}

void GlypheNightTabHelper::PrimaryMainDocumentElementAvailable() {
  Inject(web_contents()->GetPrimaryMainFrame());
}

void GlypheNightTabHelper::DOMContentLoaded(
    content::RenderFrameHost* render_frame_host) {
  Inject(render_frame_host);
}

WEB_CONTENTS_USER_DATA_KEY_IMPL(GlypheNightTabHelper);
''',
}

EDITS = [
  # Plus de mode sombre forcé de Blink : le script s'en charge.
  ('chrome/browser/chrome_content_browser_client.cc',
   '  web_prefs->force_dark_mode_enabled =\n'
   '      prefs->GetBoolean(prefs::kWebKitForceDarkModeEnabled) ||\n'
   '      prefs->GetBoolean(prefs::kGlypheRedNightEnabled);\n',
   '  web_prefs->force_dark_mode_enabled =\n'
   '      prefs->GetBoolean(prefs::kWebKitForceDarkModeEnabled);\n'),

  # Plus de matrice de couleur sur le calque de la page.
  ('chrome/browser/ui/views/frame/contents_web_view.cc', OLD_MATRIX,
   '  // Les pages sont converties par GlypheNightTabHelper.\n'),

  ('chrome/browser/ui/tab_helpers.cc',
   '  infobars::ContentInfoBarManager::CreateForWebContents(web_contents);\n',
   '  infobars::ContentInfoBarManager::CreateForWebContents(web_contents);\n\n'
   '  // Helium Glyphe : convertisseur « nuit rouge » des pages.\n'
   '  GlypheNightTabHelper::CreateForWebContents(web_contents);\n'),
  ('chrome/browser/ui/tab_helpers.cc',
   '#include "chrome/browser/ui/tab_helpers.h"\n',
   '#include "chrome/browser/ui/tab_helpers.h"\n\n'
   '#include "chrome/browser/ui/glyphe_night_tab_helper.h"\n'),

  ('chrome/browser/ui/BUILD.gn',
   '  sources = [ "tab_helpers.cc" ]\n',
   '  sources = [\n'
   '    "glyphe_night_script.inc",\n'
   '    "glyphe_night_tab_helper.cc",\n'
   '    "glyphe_night_tab_helper.h",\n'
   '    "tab_helpers.cc",\n'
   '  ]\n'),
]
