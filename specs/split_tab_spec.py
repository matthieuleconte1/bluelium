"""Helium Glyphe : onglet combiné de la vue divisée (planche « Vue divisée »).

Chromium garde deux onglets côte à côte pour une vue divisée ; Helium les
dessine comme deux pastilles séparées. Ici, les deux moitiés forment une seule
pastille :
- coins intérieurs carrés, l'espace de 7 px entre elles comblé ;
- icône « vertical_split » de 14 px à la jonction, dessinée pour moitié par
  chaque onglet (chacun est découpé à ses bornes) ;
- côté actif : segment teinté (couleur primaire à 10 %), 3 px dans la
  pastille, rayon 6, arrêté à 3 px de l'icône ;
- contenu des deux moitiés décalé pour rester dans son segment
  (favicon à 5 px du bord du segment, titre arrêté à 9 px).
"""

HS = 'chrome/browser/ui/views/tabs/common/horizontal_tab_style_views.cc'

# Icône Material « vertical_split » (contour arrondi) : trois traits à gauche,
# panneau creux à droite. Barres sans recouvrement (remplissage pair-impair).
NEW_FILES = {
  'components/vector_icons/glyphe_split.icon': '''// Helium Glyphe : vue divisée (Material « vertical_split »).

CANVAS_DIMENSIONS, 24,
ROUND_RECT, 3, 5, 7, 2, 1,
ROUND_RECT, 3, 9, 7, 2, 1,
ROUND_RECT, 3, 13, 7, 2, 1,
ROUND_RECT, 3, 17, 7, 2, 1,
ROUND_RECT, 13, 5, 8, 2, 1,
ROUND_RECT, 13, 17, 8, 2, 1,
ROUND_RECT, 13, 7, 2, 10, 0,
ROUND_RECT, 19, 7, 2, 10, 0
''',
}

EDITS = [
  # Paire plus large : 200 px par moitié, comme un onglet simple de 240 px
  # moins la zone de l'icône.
  ('chrome/browser/ui/tabs/tab_style.cc',
   'constexpr int kSplitTabWidth = 250;\n',
   'constexpr int kSplitTabWidth = 400;  // Glyphe\n'),
  ('components/vector_icons/BUILD.gn',
   '      "glyphe_add_bold.icon",\n',
   '      "glyphe_add_bold.icon",\n      "glyphe_split.icon",\n'),

  # Une seule pastille pour les deux moitiés : la gauche va jusqu'à son bord
  # droit, la droite part juste après le pixel de recouvrement des onglets.
  (HS,
   '    // Radii are clockwise from top left.\n',
   '    // Glyphe : vue divisée, les deux moitiés forment une seule pastille.\n'
   '    if (delegate_->IsLeftSplitTab()) {\n'
   '      right = aligned_bounds.right();\n'
   '      top_right_corner_radius = 0;\n'
   '      bottom_right_corner_radius = 0;\n'
   '    } else if (delegate_->IsRightSplitTab()) {\n'
   '      left = aligned_bounds.x() + tab_style()->GetTabOverlap() * scale;\n'
   '      top_left_corner_radius = 0;\n'
   '      bottom_left_corner_radius = 0;\n'
   '    }\n'
   '\n'
   '    // Radii are clockwise from top left.\n'),

  # Contenu dans son segment : la jonction est au bord droit de l'onglet de
  # gauche (= 1 px dans celui de droite). Segment gauche [7, w-10], droit
  # [11, w-7] ; marges de base 14 px de chaque côté.
  (HS,
   '  gfx::Insets split_insets = gfx::Insets(0);\n',
   '  gfx::Insets split_insets = gfx::Insets(0);\n'
   '  // Glyphe : contenu de chaque moitié dans son segment.\n'
   '  if (delegate_->IsLeftSplitTab()) {\n'
   '    split_insets = gfx::Insets::TLBR(0, -2, 0, 5);\n'
   '  } else if (delegate_->IsRightSplitTab()) {\n'
   '    split_insets = gfx::Insets::TLBR(0, 2, 0, 2);\n'
   '  }\n'),

  ('chrome/browser/ui/views/tabs/tab.cc',
   '#include "ui/gfx/paint_vector_icon.h"\n',
   '#include "ui/gfx/paint_vector_icon.h"\n'
   '#include "cc/paint/paint_flags.h"\n'
   '#include "components/vector_icons/vector_icons.h"\n'
   '#include "ui/color/color_id.h"\n'
   '#include "ui/color/color_provider.h"\n'),

  ('chrome/browser/ui/views/tabs/tab.cc',
   'void Tab::OnPaint(gfx::Canvas* canvas) {\n'
   '  tab_style_views()->PaintTab(canvas);\n'
   '}\n',
   'void Tab::OnPaint(gfx::Canvas* canvas) {\n'
   '  tab_style_views()->PaintTab(canvas);\n'
   '\n'
   '  // Glyphe : onglet combiné de la vue divisée (segment actif + icône).\n'
   '  if (!split().has_value() || !GetColorProvider()) {\n'
   '    return;\n'
   '  }\n'
   '  const std::vector<Tab*> pair = controller()->GetTabsInSplit(this);\n'
   '  if (pair.size() != 2) {\n'
   '    return;\n'
   '  }\n'
   '  const bool is_left = pair[base::i18n::IsRTL() ? 1 : 0] == this;\n'
   '  const gfx::RectF pill = gfx::SkRectToRectF(\n'
   '      tab_style_views()\n'
   '          ->GetPath(TabStyle::PathType::kActiveTab, 1.0f, TabPathFlags())\n'
   '          .getBounds());\n'
   '  // Jonction : bord droit de l\'onglet de gauche, x=1 dans celui de droite.\n'
   '  const float junction = is_left ? width() : 1.0f;\n'
   '  constexpr float kInset = 3.0f;\n'
   '  constexpr float kIconSize = 14.0f;\n'
   '  constexpr float kIconGap = 3.0f;\n'
   '  const float half_zone = kIconSize / 2 + kIconGap;\n'
   '\n'
   '  if (IsActive() && controller_->IsActiveTab(this)) {\n'
   '    gfx::RectF segment = pill;\n'
   '    segment.Inset(kInset);\n'
   '    if (is_left) {\n'
   '      segment.set_width(junction - half_zone - segment.x());\n'
   '    } else {\n'
   '      const float right = segment.right();\n'
   '      segment.set_x(junction + half_zone);\n'
   '      segment.set_width(right - segment.x());\n'
   '    }\n'
   '    if (!segment.IsEmpty()) {\n'
   '      cc::PaintFlags flags;\n'
   '      flags.setAntiAlias(true);\n'
   '      flags.setColor(SkColorSetA(\n'
   '          GetColorProvider()->GetColor(ui::kColorSysPrimary), 0x1A));\n'
   '      canvas->DrawRoundRect(segment, 6.0f, flags);\n'
   '    }\n'
   '  }\n'
   '\n'
   '  const SkColor foreground =\n'
   '      tab_style_views()->CalculateTargetColors().foreground_color;\n'
   '  canvas->Save();\n'
   '  if (!is_left) {\n'
   '    // Colonne x=0 déjà couverte par l\'onglet de gauche.\n'
   '    canvas->ClipRect(gfx::Rect(1, 0, width() - 1, height()));\n'
   '  }\n'
   '  canvas->Translate(gfx::Vector2d(\n'
   '      static_cast<int>(junction - kIconSize / 2),\n'
   '      static_cast<int>(pill.CenterPoint().y() - kIconSize / 2)));\n'
   '  gfx::PaintVectorIcon(canvas, vector_icons::kGlypheSplitIcon,\n'
   '                       static_cast<int>(kIconSize),\n'
   '                       SkColorSetA(foreground, 0x99));\n'
   '  canvas->Restore();\n'
   '}\n'),
]
