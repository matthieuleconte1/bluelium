"""Bluelium : barre d'adresse en cours de saisie aux couleurs de la page.

Avant : avec la couleur de page active (thème sombre, page blanche), la barre
devenait claire, mais une fois la barre d'adresse cliquée Chromium la peignait
avec le fond des suggestions (kColorOmniboxResultsBackground), resté à la
couleur du thème. Résultat : champ bleu nuit dans une barre claire, et le
domaine en texte sombre sur ce fond sombre, illisible.

Après : quand la couleur de page s'applique, la saisie, la liste des
suggestions, la sélection de texte et les icônes des suggestions prennent la
palette de la page. Le thème seul (page interne, couleur de page coupée) ne
change pas. Le fondu entre deux pages couvre aussi ces couleurs.

Se place en fin de série : s'appuie sur page-color-internal et custom-accent.
"""

MIXERS = 'chrome/browser/ui/color/chrome_color_mixers.cc'

NEW_FILES = {}

EDITS = [
  (MIXERS,
   '  if (glyphe_page && SkColorGetA(*key.app_background_color) == SK_AlphaOPAQUE) {\n'
   '    add_prism_colors(provider->AddMixer(), *glyphe_page);\n',
   '  // Bluelium : barre d\'adresse en saisie et suggestions sur la couleur de\n'
   '  // la page. Chromium peint le champ actif avec le fond des suggestions,\n'
   '  // resté au thème : champ sombre dans une barre claire.\n'
   '  const auto add_page_omnibox_colors =\n'
   '      [](ui::ColorMixer& p, const ui::GlyphePrismPalette& prism) {\n'
   '    const SkColor field = prism.field;\n'
   '    const SkColor hovered =\n'
   '        color_utils::AlphaBlend(prism.text, field, SkAlpha{0x14});\n'
   '    const SkColor selected =\n'
   '        color_utils::AlphaBlend(prism.text, field, SkAlpha{0x1f});\n'
   '    p[kColorOmniboxResultsBackground] = {field};\n'
   '    p[kColorOmniboxResultsBackgroundIph] = {prism.card};\n'
   '    p[kColorOmniboxResultsBackgroundHovered] = {hovered};\n'
   '    p[kColorOmniboxResultsBackgroundHoverOverlay] = {\n'
   '        SkColorSetA(prism.text, 0x14)};\n'
   '    p[kColorOmniboxResultsBackgroundSelected] = {selected};\n'
   '    p[kColorOmniboxResultsFocusIndicator] = {prism.accent};\n'
   '    p[kColorOmniboxResultsTextSelected] = {prism.text};\n'
   '    p[kColorOmniboxResultsTextDimmed] = {prism.subtle};\n'
   '    p[kColorOmniboxResultsTextDimmedSelected] = {prism.subtle};\n'
   '    p[kColorOmniboxResultsUrl] = {prism.accent};\n'
   '    p[kColorOmniboxResultsUrlSelected] = {prism.accent};\n'
   '    p[kColorOmniboxKeywordSelected] = {prism.accent};\n'
   '    p[kColorOmniboxKeywordSeparator] = {prism.divider};\n'
   '    p[kColorOmniboxResultsIcon] = {prism.subtle};\n'
   '    p[kColorOmniboxResultsIconSelected] = {prism.subtle};\n'
   '    p[kColorOmniboxResultsIconHovered] = {SkColorSetA(prism.subtle, 0x21)};\n'
   '    p[kColorOmniboxResultsButtonBorder] = {prism.divider};\n'
   '    p[kColorOmniboxResultsButtonIcon] = {prism.text};\n'
   '    p[kColorOmniboxSelectionBackground] = {\n'
   '        color_utils::AlphaBlend(prism.text, field, SkAlpha{0x40})};\n'
   '    p[kColorOmniboxSelectionForeground] = {prism.text};\n'
   '    p[kColorOmniboxContextEntrypointText] = {prism.text};\n'
   '  };\n'
   '  if (glyphe_page && SkColorGetA(*key.app_background_color) == SK_AlphaOPAQUE) {\n'
   '    add_prism_colors(provider->AddMixer(), *glyphe_page);\n'
   '    add_page_omnibox_colors(provider->AddMixer(), *glyphe_page);\n'),
  (MIXERS,
   '      add_prism_colors(page, *glyphe_page);\n',
   '      add_prism_colors(page, *glyphe_page);\n'
   '      add_page_omnibox_colors(page, *glyphe_page);\n'),
]
