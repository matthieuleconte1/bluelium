"""Bluelium : sélecteur d'assistants (Claude, ChatGPT…) lisible sur toutes les
couleurs de page.

Le fond du panneau suit la couleur de la page (kColorTabBackgroundActiveFrame
Active), mais le texte des onglets gardait les couleurs fixes du thème :
bleu-gris illisible sur une page rouge. Le texte prend maintenant le noir ou le
blanc qui contraste le plus avec ce fond (les onglets non choisis en version
atténuée), recalculé à chaque changement de thème ou de couleur de page.

S'applique sur le résultat de reference_finishing_spec.py.
"""
NEW_FILES = {}
_CC = 'chrome/browser/ui/views/side_panel/glyphe_assistant.cc'
EDITS = [
 # Couleurs calculées depuis le fond réel du panneau.
 (_CC,
  '    separator_->SetBackground(views::CreateSolidBackground(\n'
  '        SkColorSetA(tint, dark ? 0x26 : 0x1a)));\n'
  '  }\n',
  '    separator_->SetBackground(views::CreateSolidBackground(\n'
  '        SkColorSetA(tint, dark ? 0x26 : 0x1a)));\n'
  '    // Bluelium : texte noir ou blanc selon le fond réel du panneau.\n'
  '    text_on_ = color_utils::GetColorWithMaxContrast(panel);\n'
  '    text_off_ = color_utils::AlphaBlend(text_on_, panel,\n'
  '                                        static_cast<SkAlpha>(0xa6));\n'
  '    has_text_colors_ = true;\n'
  '    UpdateButtonColors();\n'
  '  }\n'),

 (_CC,
  '      buttons_[i]->SetEnabledTextColors(\n'
  '          on ? ui::kColorSysOnSurface : ui::kColorSysOnSurfaceVariant);\n'
  '    }\n'
  '    InvalidateLayout();\n'
  '  }\n',
  '    }\n'
  '    UpdateButtonColors();\n'
  '    InvalidateLayout();\n'
  '  }\n'
  '\n'
  '  void UpdateButtonColors() {\n'
  '    const int current = CurrentAssistant(profile_);\n'
  '    for (int i = 0; i < kAssistantCount; ++i) {\n'
  '      const bool on = i == current;\n'
  '      if (has_text_colors_) {\n'
  '        buttons_[i]->SetEnabledTextColors(on ? text_on_ : text_off_);\n'
  '      } else {\n'
  '        buttons_[i]->SetEnabledTextColors(\n'
  '            on ? ui::kColorSysOnSurface : ui::kColorSysOnSurfaceVariant);\n'
  '      }\n'
  '    }\n'
  '  }\n'),

 (_CC,
  '  raw_ptr<views::View> separator_ = nullptr;\n',
  '  raw_ptr<views::View> separator_ = nullptr;\n'
  '  // Bluelium : texte des onglets, calculé dans OnThemeChanged().\n'
  '  SkColor text_on_ = SK_ColorBLACK;\n'
  '  SkColor text_off_ = SK_ColorBLACK;\n'
  '  bool has_text_colors_ = false;\n'),
]
