# Bluelium : filtre de lumière chaude sur le contenu web, sans conversion.
# Bluelium : Alt+Maj+N et la pref historique restent compatibles.

WARM_FILTER = """void ContentsWebView::UpdateGlypheRedNight() {
  // Bluelium : point d'intégration OLED, indépendant du filtre des pages.
  ui::Layer* page_layer = layer();
#if defined(USE_AURA)
  // Bluelium : secours Linux si le flag de gestion des calques est désactivé.
  if (!holder()->layer_managed_by_views()) {
    content::WebContents* contents = web_contents();
    gfx::NativeView native_view = contents ? contents->GetNativeView() : nullptr;
    page_layer = native_view ? native_view->layer() : nullptr;
  }
#endif
  if (!page_layer) {
    return;
  }
  const bool enabled = glyphe_pref_registrar_.prefs() &&
      glyphe_pref_registrar_.prefs()->GetBoolean(prefs::kGlypheRedNightEnabled);
  if (!enabled) {
    if (page_layer->LayerHasCustomColorMatrix()) {
      page_layer->ClearLayerCustomColorMatrix();
    }
    return;
  }
  // Bluelium : ce calque contient le NativeViewHost et la surface de la page,
  // Bluelium : y compris RenderWidgetHostViewMac via SetParentUiLayer().
  // Bluelium : R reste intact, G à 85 %, B à 65 % ; noir et alpha préservés.
  // Bluelium : ni désaturation, ni inversion, ni mode sombre forcé de Blink.
  const cc::FilterOperation::Matrix matrix = {
      1.0f, 0.0f,  0.0f,  0.0f, 0.0f,
      0.0f, 0.85f, 0.0f,  0.0f, 0.0f,
      0.0f, 0.0f,  0.65f, 0.0f, 0.0f,
      0.0f, 0.0f,  0.0f,  1.0f, 0.0f};
  page_layer->SetLayerCustomColorMatrix(matrix);
  // Bluelium : filtre de lumière chaude appliqué au calque de contenu.
}
"""

EDITS = [
  ('chrome/common/pref_names.h',
   'inline constexpr char kWebKitForceDarkModeEnabled[] =\n'
   '    "webkit.webprefs.force_dark_mode_enabled";\n',
   'inline constexpr char kWebKitForceDarkModeEnabled[] =\n'
   '    "webkit.webprefs.force_dark_mode_enabled";\n'
   '// Bluelium : filtre de lumière chaude des pages (nom de pref conservé).\n'
   'inline constexpr char kGlypheRedNightEnabled[] = "glyphe.red_night.enabled";\n'),

  ('chrome/browser/ui/prefs/prefs_tab_helper.cc',
   '  registry->RegisterBooleanPref(prefs::kWebKitForceDarkModeEnabled,\n'
   '                                force_dark_mode_enabled);\n',
   '  registry->RegisterBooleanPref(prefs::kWebKitForceDarkModeEnabled,\n'
   '                                force_dark_mode_enabled);\n'
   '  registry->RegisterBooleanPref(prefs::kGlypheRedNightEnabled, false);\n'),

  ('chrome/app/chrome_command_ids.h',
   '#define IDC_TOGGLE_ZEN_MODE_TOP_CHROME_PIN 34091\n',
   '#define IDC_TOGGLE_ZEN_MODE_TOP_CHROME_PIN 34091\n'
   '#define IDC_GLYPHE_TOGGLE_RED_NIGHT     34092\n'),

  ('chrome/browser/ui/accelerator_table.cc',
   '     IDC_TOGGLE_ZEN_MODE_TOP_CHROME_PIN},\n',
   '     IDC_TOGGLE_ZEN_MODE_TOP_CHROME_PIN},\n'
   '    {ui::VKEY_N, ui::EF_SHIFT_DOWN | ui::EF_ALT_DOWN,\n'
   '     IDC_GLYPHE_TOGGLE_RED_NIGHT},\n'),

  ('chrome/browser/ui/browser_command_controller.cc',
   '    case IDC_TOGGLE_ZEN_MODE_TOP_CHROME_PIN: {\n',
   '    case IDC_GLYPHE_TOGGLE_RED_NIGHT: {\n'
   '      PrefService* glyphe_prefs = profile()->GetPrefs();\n'
   '      glyphe_prefs->SetBoolean(\n'
   '          prefs::kGlypheRedNightEnabled,\n'
   '          !glyphe_prefs->GetBoolean(prefs::kGlypheRedNightEnabled));\n'
   '      break;\n'
   '    }\n'
   '    case IDC_TOGGLE_ZEN_MODE_TOP_CHROME_PIN: {\n'),
  ('chrome/browser/ui/browser_command_controller.cc',
   '  command_updater_->UpdateCommandEnabled(IDC_HELIUM_SERVICES_OPEN, true);\n',
   '  command_updater_->UpdateCommandEnabled(IDC_HELIUM_SERVICES_OPEN, true);\n'
   '  command_updater_->UpdateCommandEnabled(IDC_GLYPHE_TOGGLE_RED_NIGHT, true);\n'),

  ('chrome/browser/ui/views/frame/contents_web_view.h',
   '#include "chrome/browser/ui/views/frame/web_contents_close_handler_delegate.h"\n',
   '#include "chrome/browser/ui/views/frame/web_contents_close_handler_delegate.h"\n'
   '#include "components/prefs/pref_change_registrar.h"\n'),
  ('chrome/browser/ui/views/frame/contents_web_view.h',
   '  std::unique_ptr<StatusBubbleViews> status_bubble_;\n',
   '  // Bluelium : applique ou retire le filtre de lumière chaude des pages.\n'
   '  void UpdateGlypheRedNight();\n'
   '  PrefChangeRegistrar glyphe_pref_registrar_;\n\n'
   '  std::unique_ptr<StatusBubbleViews> status_bubble_;\n'),

  ('chrome/browser/ui/views/frame/contents_web_view.cc',
   '#include "chrome/browser/ui/color/chrome_color_id.h"\n',
   '#include "base/functional/bind.h"\n'
   '#include "chrome/browser/profiles/profile.h"\n'
   '#include "chrome/browser/ui/color/chrome_color_id.h"\n'
   '#include "chrome/common/pref_names.h"\n'
   '#include "components/prefs/pref_service.h"\n'
   '#include "ui/compositor/layer.h"\n'),
  ('chrome/browser/ui/views/frame/contents_web_view.cc',
   '  web_contents_close_handler_ = std::make_unique<WebContentsCloseHandler>(this);\n}\n',
   '  web_contents_close_handler_ = std::make_unique<WebContentsCloseHandler>(this);\n'
   '  if (browser_context) {\n'
   '    glyphe_pref_registrar_.Init(\n'
   '        Profile::FromBrowserContext(browser_context)->GetPrefs());\n'
   '    glyphe_pref_registrar_.Add(\n'
   '        prefs::kGlypheRedNightEnabled,\n'
   '        base::BindRepeating(&ContentsWebView::UpdateGlypheRedNight,\n'
   '                            base::Unretained(this)));\n'
   '  }\n'
   '}\n\n'
   + WARM_FILTER),
  ('chrome/browser/ui/views/frame/contents_web_view.cc',
   'void ContentsWebView::SetWebContents(content::WebContents* web_contents) {\n'
   '  views::WebView::SetWebContents(web_contents);\n',
   'void ContentsWebView::SetWebContents(content::WebContents* web_contents) {\n'
   '  views::WebView::SetWebContents(web_contents);\n'
   '  UpdateGlypheRedNight();\n'),
  ('chrome/browser/ui/views/frame/contents_web_view.cc',
   '  WebView::RenderViewReady();\n}\n',
   '  WebView::RenderViewReady();\n  UpdateGlypheRedNight();\n}\n'),
]
