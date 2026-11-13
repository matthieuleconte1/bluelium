"""Bluelium : pastilles lisibles et extrêmes adaptés à l'apparence.

Bluelium : après prism-ui, page-color-fade et les finitions des boutons.
Bluelium : les fonds restent dessinés par les vues natives existantes.
"""

PRISM = 'ui/color/glyphe_prism'
MIXERS = 'chrome/browser/ui/color/chrome_color_mixers.cc'
BUTTON = 'chrome/browser/ui/views/toolbar/toolbar_button.cc'
PINNED = 'chrome/browser/ui/views/toolbar/pinned_action_toolbar_button.cc'

NEW_FILES = {}

OLD_PALETTE = '''GlyphePrismPalette GlyphePageColorPalette(SkColor page) {
  const SkColor page_bg = SkColorSetA(page, SK_AlphaOPAQUE);
  const bool dark = color_utils::IsDark(page_bg);
  const SkColor fg = dark ? SkColorSetRGB(0xf4, 0xf5, 0xf7)
                          : SkColorSetRGB(0x15, 0x16, 0x1a);
  // Bluelium : barre un peu décalée de la page (plus sombre sur une page
  // claire, plus claire sur une page sombre), même teinte : à la couleur
  // exacte, le bord de la page se confondait avec la barre.
  const SkColor bg = Mix(fg, page_bg, 0x14);
  return {.frame = bg,
          .card = bg,
          .tab = Mix(fg, bg, 0x1c),
          .field = Mix(fg, bg, 0x12),
          .text = fg,
          .muted = Mix(fg, bg, 0xb8),
          .subtle = Mix(fg, bg, 0x8a),
          .divider = Mix(fg, bg, 0x38),
          .accent = fg,
          .on_accent = bg,
          .dark = dark};
}
'''

NEW_PALETTE = '''bool ShouldUseGlyphePageColor(const ColorProviderKey& key) {
  // Bluelium : respecter les thèmes externes et les modes d'accessibilité.
  return !key.app_controller && key.app_background_color.has_value() &&
         !key.custom_theme && key.system_theme == SystemTheme::kDefault &&
         key.contrast_mode != ColorProviderKey::ContrastMode::kHigh &&
         key.forced_colors == ColorProviderKey::ForcedColors::kNone &&
         !IsGlypheRedNight();
}

GlyphePrismPalette GlyphePageColorPalette(SkColor page,
                                        const ColorProviderKey& key) {
  const SkColor page_bg = SkColorSetA(page, SK_AlphaOPAQUE);
  const bool near_black =
      std::max({SkColorGetR(page_bg), SkColorGetG(page_bg),
                SkColorGetB(page_bg)}) <= 0x30;
  const bool near_white =
      std::min({SkColorGetR(page_bg), SkColorGetG(page_bg),
                SkColorGetB(page_bg)}) >= 0xe0;
  // Bluelium : la clé inclut le choix clair/sombre du profil et NativeTheme
  // Bluelium : en mode Appareil, sur Linux comme sur macOS. Jamais la page.
  const bool dark_appearance =
      IsGlypheOled() || key.color_mode == ColorProviderKey::ColorMode::kDark;
  if ((dark_appearance && near_black) || (!dark_appearance && near_white)) {
    const GlyphePrismPalette* base = GetGlyphePrismPalette(key);
    GlyphePrismPalette neutral =
        base ? *base : (dark_appearance ? kThemes[0].dark : kThemes[0].light);
    const float page_luma = color_utils::GetRelativeLuminance(page_bg);
    const float base_luma = color_utils::GetRelativeLuminance(neutral.frame);
    // Bluelium : ne dépasser la base que vers le noir en sombre, vers le
    // Bluelium : blanc en clair. Garder les rôles natifs, sans pastille ajoutée.
    if (dark_appearance ? page_luma < base_luma : page_luma > base_luma) {
      neutral.frame = page_bg;
    }
    return neutral;
  }

  // Bluelium : conserver le décalage de 8 % de la barre, notamment blanc ->
  // Bluelium : gris clair en sombre et noir -> gris foncé en clair.
  const SkColor offset = color_utils::IsDark(page_bg)
                             ? SkColorSetRGB(0xf4, 0xf5, 0xf7)
                             : SkColorSetRGB(0x15, 0x16, 0x1a);
  const SkColor bg = Mix(offset, page_bg, 0x14);
  const bool dark = color_utils::GetContrastRatio(SK_ColorWHITE, bg) >
                    color_utils::GetContrastRatio(SK_ColorBLACK, bg);
  const SkColor fg = dark ? SK_ColorWHITE : SK_ColorBLACK;
  const SkColor surface_tint = dark ? SK_ColorBLACK : SK_ColorWHITE;
  const bool boxes = !near_black && !near_white;
  const auto surface = [&](int start_alpha) {
    // Bluelium : même teinte, éclaircie sous texte noir, assombrie sous blanc.
    // Bluelium : 7:1 laisse une marge pour les états de survol et d'appui.
    for (int alpha = start_alpha; alpha <= 255; ++alpha) {
      const SkColor candidate = Mix(surface_tint, bg, alpha);
      if (color_utils::GetContrastRatio(fg, candidate) >= 7.0f) {
        return candidate;
      }
    }
    return surface_tint;
  };
  const SkColor card = boxes ? surface(0x1c) : bg;
  const SkColor tab = boxes ? surface(0x2c) : Mix(fg, bg, 0x1c);
  const SkColor field = boxes ? card : Mix(fg, bg, 0x12);
  SkColor muted = fg;
  // Bluelium : vérifier les libellés secondaires sur chaque fond réellement
  // Bluelium : utilisé, y compris le cadre et les onglets inactifs au repos.
  for (int alpha = 0xb8; alpha <= 255; ++alpha) {
    const SkColor candidate = Mix(fg, bg, alpha);
    if (color_utils::GetContrastRatio(candidate, bg) >= 4.5f &&
        color_utils::GetContrastRatio(candidate, card) >= 4.5f &&
        color_utils::GetContrastRatio(candidate, tab) >= 4.5f &&
        color_utils::GetContrastRatio(candidate, field) >= 4.5f) {
      muted = candidate;
      break;
    }
  }
  return {.frame = bg,
          .card = card,
          .tab = tab,
          .field = field,
          .text = fg,
          .muted = muted,
          .subtle = Mix(fg, bg, 0x8a),
          .divider = Mix(fg, bg, 0x38),
          .accent = fg,
          .on_accent = card,
          .dark = dark,
          .page_color_boxes = boxes};
}
'''

EDITS = [
    (PRISM + '.h',
     '  bool dark;\n',
     '  bool dark;\n'
     '  // Bluelium : fonds arrondis supplémentaires sur les pages colorées.\n'
     '  bool page_color_boxes = false;\n'),
    (PRISM + '.h',
     'COMPONENT_EXPORT(COLOR) GlyphePrismPalette GlyphePageColorPalette(SkColor page);\n',
     'COMPONENT_EXPORT(COLOR) bool ShouldUseGlyphePageColor(\n'
     '    const ColorProviderKey& key);\n'
     'COMPONENT_EXPORT(COLOR) GlyphePrismPalette GlyphePageColorPalette(\n'
     '    SkColor page, const ColorProviderKey& key);\n'),
    (PRISM + '.cc', '#include <atomic>\n',
     '#include <algorithm>\n#include <atomic>\n#include <optional>\n'),
    (PRISM + '.cc', OLD_PALETTE, NEW_PALETTE),
    (PRISM + '.cc',
     '  const GlyphePrismPalette* p = GetGlyphePrismPalette(key);\n',
     '  // Bluelium : seule la barre du haut suit la page (voir la fin du\n'
     '  // mixer) ; menus, bulles et panneaux gardent le thème, sinon ils\n'
     '  // héritent du fond de la page avec le texte du thème.\n'
     '  std::optional<GlyphePrismPalette> page;\n'
     '  if (ShouldUseGlyphePageColor(key)) {\n'
     '    page = GlyphePageColorPalette(*key.app_background_color, key);\n'
     '  }\n'
     '  const GlyphePrismPalette* base = GetGlyphePrismPalette(key);\n'
     '  const GlyphePrismPalette* p = base ? base : (page ? &*page : nullptr);\n'),
    (PRISM + '.cc',
     '  mixer[kColorSysStateOnTextHighlight] = {p->text};\n}\n',
     '  mixer[kColorSysStateOnTextHighlight] = {p->text};\n'
     '  if (page && p != &*page) {\n'
     '    // Bluelium : jetons d’en-tête seulement (cadre, onglets, adresse).\n'
     '    const GlyphePrismPalette& h = *page;\n'
     '    const SkColor header_tint = h.dark ? h.text : h.accent;\n'
     '    ColorMixer& header = provider->AddMixer();\n'
     '    header[kColorSysHeader] = {h.frame};\n'
     '    header[kColorSysHeaderInactive] = {h.frame};\n'
     '    header[kColorSysHeaderContainer] = {h.tab};\n'
     '    header[kColorSysHeaderContainerInactive] = {h.tab};\n'
     '    header[kColorSysOnHeaderPrimary] = {h.muted};\n'
     '    header[kColorSysOnHeaderPrimaryInactive] = {h.subtle};\n'
     '    header[kColorSysOnHeaderDivider] = {h.divider};\n'
     '    header[kColorSysOnHeaderDividerInactive] = {h.divider};\n'
     '    header[kColorSysOmniboxContainer] = {h.field};\n'
     '    header[kColorSysStateHeaderHover] = {SkColorSetA(header_tint, 0x1a)};\n'
     '    header[kColorSysStateHeaderHoverInactive] = {SkColorSetA(header_tint, 0x14)};\n'
     '    header[kColorSysStateHeaderSelect] = {SkColorSetA(header_tint, 0x24)};\n'
     '  }\n'
     '}\n'),
    (MIXERS,
     '  if (!key.app_controller && key.app_background_color.has_value() &&\n'
     '      !ui::IsGlypheRedNight()) {\n'
     '    glyphe_page = ui::GlyphePageColorPalette(*key.app_background_color);\n',
     '  if (ui::ShouldUseGlyphePageColor(key)) {\n'
     '    glyphe_page = ui::GlyphePageColorPalette(*key.app_background_color, key);\n'),
    (MIXERS,
     '    p[kColorTabBackgroundInactiveFrameActive] = {\n'
     '        SkColorSetA(prism->tab, SK_AlphaTRANSPARENT)};\n'
     '    p[kColorTabBackgroundInactiveFrameInactive] = {\n'
     '        SkColorSetA(prism->tab, SK_AlphaTRANSPARENT)};\n'
     '    p[kColorTabBackgroundInactiveHoverFrameActive] = {\n'
     '        SkColorSetA(prism->tab, 0x80)};\n'
     '    p[kColorTabBackgroundInactiveHoverFrameInactive] = {\n'
     '        SkColorSetA(prism->tab, 0x80)};\n',
     '    // Bluelium : conserver la pastille des onglets inactifs au repos.\n'
     '    const bool boxes = prism->page_color_boxes;\n'
     '    const SkColor inactive = boxes ? prism->card\n'
     '        : SkColorSetA(prism->tab, SK_AlphaTRANSPARENT);\n'
     '    const SkColor hovered = boxes ? prism->tab\n'
     '        : SkColorSetA(prism->tab, 0x80);\n'
     '    p[kColorTabBackgroundInactiveFrameActive] = {inactive};\n'
     '    p[kColorTabBackgroundInactiveFrameInactive] = {inactive};\n'
     '    p[kColorTabBackgroundInactiveHoverFrameActive] = {hovered};\n'
     '    p[kColorTabBackgroundInactiveHoverFrameInactive] = {hovered};\n'),
    (MIXERS,
     '    p[kColorNewTabButtonForegroundFrameActive] = {prism->muted};\n',
     '    p[kColorNewTabButtonForegroundFrameActive] = {prism->muted};\n'
     '    p[kColorNewTabButtonForegroundFrameInactive] = {prism->muted};\n'
     '    p[kColorNewTabButtonCRForegroundFrameActive] = {prism->muted};\n'
     '    p[kColorNewTabButtonCRForegroundFrameInactive] = {prism->muted};\n'),
    (MIXERS,
     '    p[kColorToolbarExtensionSeparatorEnabled] = {prism->divider};\n',
     '    p[kColorToolbarExtensionSeparatorEnabled] = {prism->divider};\n'
     '    if (boxes) {\n'
     '      // Bluelium : un alias de card pour les boutons natifs au repos.\n'
     '      p[kColorGlyphePageColorButtonBackground] = {prism->card};\n'
     '      p[kColorToolbarButtonBackgroundHighlightedDefault] = {prism->tab};\n'
     '      p[kColorToolbarButtonText] = {prism->text};\n'
     '      p[kColorLocationBarBackgroundHovered] = {prism->field};\n'
     '      p[kColorToolbarInkDropHover] = {SkColorSetA(prism->text, 0x14)};\n'
     '      p[kColorToolbarInkDropRipple] = {SkColorSetA(prism->text, 0x1f)};\n'
     '    }\n'),
    ('chrome/browser/ui/color/chrome_color_id.h',
     '  E_CPONLY(kColorToolbarButtonBackgroundHighlightedDefault) \\\n',
     '  /* Bluelium : alias de card, transparent sans pastille de page. */ \\\n'
     '  E_CPONLY(kColorGlyphePageColorButtonBackground) \\\n'
     '  E_CPONLY(kColorToolbarButtonBackgroundHighlightedDefault) \\\n'),
    ('chrome/browser/ui/color/chrome_color_mixer.cc',
     '  mixer[kColorToolbarButtonBackgroundHighlightedDefault] =\n',
     '  // Bluelium : aucun fond supplémentaire hors des pages colorées.\n'
     '  mixer[kColorGlyphePageColorButtonBackground] = {SK_ColorTRANSPARENT};\n'
     '  mixer[kColorToolbarButtonBackgroundHighlightedDefault] =\n'),
    (BUTTON,
     '  SetEnabledTextColors(highlight_color_animation_.GetTextColor());\n',
     '  const auto* const colors = GetColorProvider();\n'
     '  const SkColor page_background = colors\n'
     '      ? colors->GetColor(kColorGlyphePageColorButtonBackground)\n'
     '      : SK_ColorTRANSPARENT;\n'
     '  auto text_color = highlight_color_animation_.GetTextColor();\n'
     ),
    (BUTTON,
     '  std::optional<SkColor> background_color =\n'
     '      highlight_color_animation_.GetBackgroundColor();\n'
     '  if (background_color) {\n',
     '  std::optional<SkColor> background_color =\n'
     '      highlight_color_animation_.GetBackgroundColor();\n'
     '  // Bluelium : réutiliser le fond arrondi natif, aussi sans survol.\n'
     '  if (SkColorGetA(page_background) != SK_AlphaTRANSPARENT) {\n'
     '    background_color = background_color\n'
     '        ? color_utils::GetResultingPaintColor(*background_color,\n'
     '                                             page_background)\n'
     '        : page_background;\n'
     '    // Bluelium : ne pas faire disparaître le texte pendant le fondu\n'
     '    // Bluelium : du surlignage ; vérifier son contraste sur le fond final.\n'
     '    const SkColor readable =\n'
     '        color_utils::GetContrastRatio(SK_ColorWHITE, *background_color) >\n'
     '                color_utils::GetContrastRatio(SK_ColorBLACK, *background_color)\n'
     '            ? SK_ColorWHITE : SK_ColorBLACK;\n'
     '    text_color = color_utils::BlendForMinContrast(\n'
     '        SkColorSetA(text_color.value_or(\n'
     '            colors->GetColor(kColorToolbarButtonText)), SK_AlphaOPAQUE),\n'
     '        *background_color, readable, 4.5f).color;\n'
     '  }\n'
     '  SetEnabledTextColors(text_color);\n'
     '  if (background_color) {\n'),
    ('chrome/browser/ui/views/toolbar/toolbar_chip_button.cc',
     'void ToolbarChipButton::UpdateColorsAndInsets() {\n',
     'void ToolbarChipButton::UpdateColorsAndInsets() {\n'
     '  // Bluelium : le bouton Extensions ne doit pas effacer sa pastille.\n'
     '  const auto* colors = GetColorProvider();\n'
     '  if (colors && SkColorGetA(colors->GetColor(\n'
     '                    kColorGlyphePageColorButtonBackground)) !=\n'
     '                    SK_AlphaTRANSPARENT) {\n'
     '    ToolbarButton::UpdateColorsAndInsets();\n'
     '    return;\n'
     '  }\n'),
    ('chrome/browser/ui/views/toolbar/toolbar_chip_button.cc',
     '#include "chrome/browser/ui/layout_constants.h"\n',
     '#include "chrome/browser/ui/layout_constants.h"\n'
     '#include "ui/color/color_provider.h"\n'),
    ('chrome/browser/ui/views/toolbar/toolbar_action_view.h',
     '  void AddedToWidget() override;\n',
     '  void AddedToWidget() override;\n'
     '  void OnThemeChanged() override;\n'),
    ('chrome/browser/ui/views/toolbar/toolbar_action_view.cc',
     '#include "ui/views/border.h"\n',
     '#include "ui/views/border.h"\n'
     '#include "ui/views/background.h"\n'
     '#include "ui/color/color_provider.h"\n'),
    ('chrome/browser/ui/views/toolbar/toolbar_action_view.cc',
     'void ToolbarActionView::RemovedFromWidget() {\n',
     'void ToolbarActionView::OnThemeChanged() {\n'
     '  MenuButton::OnThemeChanged();\n'
     '  const auto* colors = GetColorProvider();\n'
     '  if (!colors) {\n'
     '    return;\n'
     '  }\n'
     '  // Bluelium : même fond natif pour le bouclier, son compteur et les\n'
     '  // Bluelium : autres extensions, recalculé à chaque étape du fondu.\n'
     '  const SkColor background =\n'
     '      colors->GetColor(kColorGlyphePageColorButtonBackground);\n'
     '  if (SkColorGetA(background) != SK_AlphaTRANSPARENT) {\n'
     '    SetBackground(views::CreateRoundedRectBackground(background, 15));\n'
     '    label()->SetBackgroundColor(background);\n'
     '  } else {\n'
     '    SetBackground(nullptr);\n'
     '    label()->SetBackgroundColor(colors->GetColor(kColorToolbar));\n'
     '  }\n'
     '  UpdateState();\n'
     '}\n\n'
     'void ToolbarActionView::RemovedFromWidget() {\n'),
    (PINNED,
     '  const SkColor icon = glyphe_active\n'
     '                           ? SK_ColorWHITE\n',
     '  // Bluelium : garder aussi le logo actif lisible sur un accent clair.\n'
     '  const SkColor on_seed =\n'
     '      color_utils::GetContrastRatio(SK_ColorWHITE, seed) >\n'
     '              color_utils::GetContrastRatio(SK_ColorBLACK, seed)\n'
     '          ? SK_ColorWHITE : SK_ColorBLACK;\n'
     '  const SkColor icon = glyphe_active\n'
     '                           ? on_seed\n'),
    (PINNED,
     '                           : colors->GetColor(ui::kColorSysOnSurface);\n'
     '  const SkColor background =\n'
     '      glyphe_active\n'
     '          ? seed\n'
     '          : color_utils::AlphaBlend(icon, colors->GetColor(kColorToolbar),\n'
     '                                    SkAlpha{0x14});\n',
     '                           : colors->GetColor(kColorToolbarButtonIcon);\n'
     '  const SkColor page_background =\n'
     '      colors->GetColor(kColorGlyphePageColorButtonBackground);\n'
     '  // Bluelium : au repos, la même pastille lisible que les autres outils.\n'
     '  const SkColor background = glyphe_active ? seed\n'
     '      : SkColorGetA(page_background) != SK_AlphaTRANSPARENT\n'
     '          ? page_background\n'
     '          : color_utils::AlphaBlend(icon, colors->GetColor(kColorToolbar),\n'
     '                                    SkAlpha{0x14});\n'),
    ('chrome/browser/ui/views/helium/native_frame_materials.cc',
     '  return profile &&\n'
     '         profile->GetPrefs()->GetBoolean(prefs::kHeliumNativeFrameMaterials);\n',
     '  // Bluelium : une barre qui suit la page doit rester opaque, y compris\n'
     '  // Bluelium : ses onglets inactifs et le bouton nouvel onglet sur macOS.\n'
     '  return profile &&\n'
     '         !profile->GetPrefs()->GetBoolean(prefs::kGlypheFollowPageColor) &&\n'
     '         profile->GetPrefs()->GetBoolean(prefs::kHeliumNativeFrameMaterials);\n'),
    ('chrome/browser/ui/views/tabs/common/horizontal_tab_style_views.cc',
     '  if (helium::ShouldUseNativeFrameMaterials(\n'
     '          delegate_->GetBrowserWindowInterface())) {\n'
     '    return selection_state != TabStyle::TabSelectionState::kInactive ||\n',
     '  // Bluelium : dessiner aussi le fond inactif sans survol (pastille).\n'
     '  const auto* colors = delegate_->GetView()->GetColorProvider();\n'
     '  if (colors && SkColorGetA(colors->GetColor(\n'
     '                    kColorGlyphePageColorButtonBackground)) !=\n'
     '                    SK_AlphaTRANSPARENT) {\n'
     '    return true;\n'
     '  }\n'
     '  if (helium::ShouldUseNativeFrameMaterials(\n'
     '          delegate_->GetBrowserWindowInterface())) {\n'
     '    return selection_state != TabStyle::TabSelectionState::kInactive ||\n'),
    ('chrome/browser/ui/color/chrome_color_mixers.cc',
     '    p[kColorToolbarText] = {prism->text};\n',
     '    p[kColorToolbarText] = {prism->text};\n    // Bluelium : icônes de la barre d’adresse (cadenas, puces) sur la\n    // couleur de la barre, puisque les jetons système gardent le thème.\n    p[kColorPageInfoForeground] = {prism->text};\n    p[kColorOmniboxSecurityChipDefault] = {prism->text};\n    p[kColorOmniboxChipForegroundNormalVisibility] = {prism->text};\n    p[kColorOmniboxChipForegroundLowVisibility] = {prism->muted};\n    p[kColorLocationBarClearAllButtonIcon] = {prism->muted};\n'),
]
