"""Bluelium : pages d'erreur (et le jeu hors ligne) aux couleurs du navigateur.

Avant : la page d'erreur gardait le gris de Chromium (#202124 en sombre,
blanc en clair) alors que le cadre prenait la couleur du thème.

Après : à chaque page d'erreur, et à chaque changement de couleurs de
l'onglet (fondu du cadre, changement de thème), NetErrorTabHelper transmet
la couleur du cadre (kColorSysHeader) à la page, dans un monde isolé : la
page la prend pour fond et suit donc le fondu du cadre. Sans cette valeur
(autre navigateur, pages d'interstitiel hors onglet), le gris d'origine reste.

Entrée animée : le jeu, le texte et les boutons arrivent en fondu avec un
léger glissement, l'un après l'autre (40 ms). Rien si « réduire les
animations ». Seuls opacity et translate bougent (composités).

Après offline-game (neterror.css).
"""

H = 'chrome/browser/net/net_error_tab_helper.h'
CC = 'chrome/browser/net/net_error_tab_helper.cc'
CORE = 'components/security_interstitials/core/common/resources/interstitial_core.css'
NETERROR_CSS = 'components/neterror/resources/neterror.css'

NEW_FILES = {}

EDITS = [
  (H,
   '  void DidFinishNavigation(\n'
   '      content::NavigationHandle* navigation_handle) override;\n'
   '\n'
   '  // chrome::mojom::NetErrorPageSupport:\n',
   '  void DidFinishNavigation(\n'
   '      content::NavigationHandle* navigation_handle) override;\n'
   '  // Bluelium : la page d\'erreur suit la couleur du cadre.\n'
   '  void OnColorProviderChanged() override;\n'
   '\n'
   '  // chrome::mojom::NetErrorPageSupport:\n'),
  (H,
   ' private:\n'
   '  void OnMainFrameDnsError();\n',
   ' private:\n'
   '  // Bluelium : transmet la couleur du cadre à la page d\'erreur affichée.\n'
   '  void UpdateBlueliumErrorPageColor();\n'
   '\n'
   '  void OnMainFrameDnsError();\n'),
  (CC,
   '#include "base/logging.h"\n',
   '#include "base/logging.h"\n'
   '#include "base/strings/stringprintf.h"\n'
   '#include "base/strings/utf_string_conversions.h"\n'),
  (CC,
   '#include "chrome/common/pref_names.h"\n',
   '#include "chrome/common/chrome_isolated_world_ids.h"\n'
   '#include "chrome/common/pref_names.h"\n'),
  (CC,
   '#include "ui/base/page_transition_types.h"\n',
   '#include "ui/base/page_transition_types.h"\n'
   '#include "ui/color/color_id.h"\n'
   '#include "ui/color/color_provider.h"\n'),
  (CC,
   '  // Resend status every time an error page commits; this is somewhat spammy,\n',
   '  // Bluelium : fond de la page d\'erreur à la couleur du cadre.\n'
   '  if (navigation_handle->HasCommitted() && navigation_handle->IsErrorPage()) {\n'
   '    UpdateBlueliumErrorPageColor();\n'
   '  }\n'
   '\n'
   '  // Resend status every time an error page commits; this is somewhat spammy,\n'),
  (CC,
   'void NetErrorTabHelper::DidFinishNavigation(\n',
   '''void NetErrorTabHelper::OnColorProviderChanged() {
  UpdateBlueliumErrorPageColor();
}

void NetErrorTabHelper::UpdateBlueliumErrorPageColor() {
  content::RenderFrameHost* frame = web_contents()->GetPrimaryMainFrame();
  if (!frame || !frame->IsErrorDocument() || !frame->IsRenderFrameLive()) {
    return;
  }
  const SkColor color =
      web_contents()->GetColorProvider().GetColor(ui::kColorSysHeader);
  // Bluelium : monde isolé ; le style posé sur <html> est partagé avec la
  // page. La valeur est une couleur #rrggbb, rien d'autre n'est injecté.
  const std::string script = base::StringPrintf(
      "document.documentElement.style.setProperty("
      "'--bluelium-page-background', '#%02x%02x%02x');",
      SkColorGetR(color), SkColorGetG(color), SkColorGetB(color));
  frame->ExecuteJavaScriptInIsolatedWorld(base::UTF8ToUTF16(script),
                                          base::NullCallback(),
                                          ISOLATED_WORLD_ID_CHROME_INTERNAL);
}

void NetErrorTabHelper::DidFinishNavigation(
'''),
  (CORE,
   '  --text-color: var(--google-gray-700);\n'
   '  background: var(--background-color);\n',
   '  --text-color: var(--google-gray-700);\n'
   '  /* Bluelium : couleur du cadre, transmise par le navigateur. */\n'
   '  background: var(--bluelium-page-background, var(--background-color));\n'),
  (NETERROR_CSS,
   '  #main-frame-error.showing-details #main-content,\n'
   '  #main-frame-error.showing-details .runner-container {\n'
   '    display: none;\n'
   '  }\n'
   '}\n',
   '  #main-frame-error.showing-details #main-content,\n'
   '  #main-frame-error.showing-details .runner-container {\n'
   '    display: none;\n'
   '  }\n'
   '}\n'
   '\n'
   '/* Bluelium : le jeu, le texte puis les boutons arrivent en fondu. */\n'
   '@keyframes bluelium-page-enter {\n'
   '  from {\n'
   '    opacity: 0;\n'
   '    translate: 0 8px;\n'
   '  }\n'
   '}\n'
   '\n'
   '@media (prefers-reduced-motion: no-preference) {\n'
   '  .interstitial-wrapper > *,\n'
   '  #buttons {\n'
   '    animation: bluelium-page-enter 280ms cubic-bezier(0.2, 0.8, 0.2, 1)\n'
   '        backwards;\n'
   '    animation-delay: calc((min(sibling-index(), 6) - 1) * 40ms);\n'
   '  }\n'
   '\n'
   '  #buttons {\n'
   '    animation-delay: 160ms;\n'
   '  }\n'
   '}\n'),
]
