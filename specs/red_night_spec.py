# Helium Glyphe — convertisseur « nuit rouge » des pages web.
# Pages assombries par le mode sombre automatique de Blink, puis une matrice
# de couleur sur le calque de la page ne garde que la luminance, en rouge.
# Bascule : Alt+Maj+N (pref de profil glyphe.red_night.enabled).

EDITS = [
  ('chrome/common/pref_names.h',
   'inline constexpr char kWebKitForceDarkModeEnabled[] =\n'
   '    "webkit.webprefs.force_dark_mode_enabled";\n',
   'inline constexpr char kWebKitForceDarkModeEnabled[] =\n'
   '    "webkit.webprefs.force_dark_mode_enabled";\n'
   '// Helium Glyphe : pages web converties en rouge sur noir.\n'
   'inline constexpr char kGlypheRedNightEnabled[] = "glyphe.red_night.enabled";\n'),

  ('chrome/browser/ui/prefs/prefs_tab_helper.cc',
   '  registry->RegisterBooleanPref(prefs::kWebKitForceDarkModeEnabled,\n'
   '                                force_dark_mode_enabled);\n',
   '  registry->RegisterBooleanPref(prefs::kWebKitForceDarkModeEnabled,\n'
   '                                force_dark_mode_enabled);\n'
   '  registry->RegisterBooleanPref(prefs::kGlypheRedNightEnabled, false);\n'),

  ('chrome/browser/ui/prefs/pref_watcher.cc',
   '    prefs::kWebKitForceDarkModeEnabled,\n    prefs::kWebKitJavascriptEnabled,\n',
   '    prefs::kWebKitForceDarkModeEnabled,\n    prefs::kGlypheRedNightEnabled,\n'
   '    prefs::kWebKitJavascriptEnabled,\n'),

  ('chrome/browser/chrome_content_browser_client.cc',
   '  web_prefs->force_dark_mode_enabled =\n'
   '      prefs->GetBoolean(prefs::kWebKitForceDarkModeEnabled);\n',
   '  web_prefs->force_dark_mode_enabled =\n'
   '      prefs->GetBoolean(prefs::kWebKitForceDarkModeEnabled) ||\n'
   '      prefs->GetBoolean(prefs::kGlypheRedNightEnabled);\n'),

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
   '  // Helium Glyphe : applique ou retire le filtre « nuit rouge ».\n'
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
   'void ContentsWebView::UpdateGlypheRedNight() {\n'
   '#if defined(USE_AURA)\n'
   '  content::WebContents* contents = web_contents();\n'
   '  if (!contents || !glyphe_pref_registrar_.prefs()) {\n'
   '    return;\n'
   '  }\n'
   '  gfx::NativeView native_view = contents->GetNativeView();\n'
   '  if (!native_view || !native_view->layer()) {\n'
   '    return;\n'
   '  }\n'
   '  ui::Layer* page_layer = native_view->layer();\n'
   '  if (!glyphe_pref_registrar_.prefs()->GetBoolean(\n'
   '          prefs::kGlypheRedNightEnabled)) {\n'
   '    if (page_layer->LayerHasCustomColorMatrix()) {\n'
   '      page_layer->ClearLayerCustomColorMatrix();\n'
   '    }\n'
   '    return;\n'
   '  }\n'
   '  // Luminance (Rec. 709) envoyée sur le seul canal rouge, à 85 %.\n'
   '  // La page a déjà été assombrie par Blink (force_dark_mode_enabled).\n'
   '  cc::FilterOperation::Matrix matrix = {\n'
   '      0.18f, 0.61f, 0.06f, 0.0f, 0.0f,\n'
   '      0.0f,  0.0f,  0.0f,  0.0f, 0.0f,\n'
   '      0.0f,  0.0f,  0.0f,  0.0f, 0.0f,\n'
   '      0.0f,  0.0f,  0.0f,  1.0f, 0.0f};\n'
   '  page_layer->SetLayerCustomColorMatrix(matrix);\n'
   '#endif  // defined(USE_AURA)\n'
   '}\n'),
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
