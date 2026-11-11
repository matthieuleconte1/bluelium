"""Helium Glyphe : bouton « + » du nouvel onglet plus épais et un peu plus grand.

Icône dédiée (trait de 3,4 px sur 24, bouts arrondis, au lieu de 2,3 px),
icônes des boutons de la barre d'onglets en 18 px au lieu de 16.
LabelButton centre l'icône sur toute la hauteur du bouton, marges comprises,
alors que le survol suit la zone sans marges : avec les marges asymétriques
de layout_spacing_spec.py, l'icône restait 4 px au-dessus du survol.
L'icône est donc recentrée sur la zone sans marges.
"""

NEW_FILES = {
  'components/vector_icons/glyphe_add_bold.icon': '''// Helium Glyphe : « + » épais du nouvel onglet.

CANVAS_DIMENSIONS, 24,
FILL_RULE_NONZERO,
ROUND_RECT, 4.5f, 10.3f, 15, 3.4f, 1.7f,
ROUND_RECT, 10.3f, 4.5f, 3.4f, 15, 1.7f
''',
}

EDITS = [
  ('components/vector_icons/BUILD.gn',
   '      "add_weight500_custom.icon",\n',
   '      "add_weight500_custom.icon",\n      "glyphe_add_bold.icon",\n'),
  ('chrome/browser/ui/views/frame/horizontal_tab_strip_region_view.cc',
   '            features::IsRoundedIconsEnabled()\n'
   '                ? vector_icons::kAddWeight500CustomIcon\n'
   '                : vector_icons::kAddOldIcon,\n',
   '            vector_icons::kGlypheAddBoldIcon,  // Glyphe : « + » épais\n'),
  ('chrome/browser/ui/views/tabs/tab_strip_control_button.cc',
   'const int TabStripControlButton::kIconSize = 16;',
   'const int TabStripControlButton::kIconSize = 18;  // Glyphe'),
  # SetImageCentered() ne joue que sur les libellés multilignes : sans effet
  # ici. Gardé pour que respec.py retrouve l'édition déjà appliquée.
  ('chrome/browser/ui/views/tabs/new_tab_button.cc',
   '  set_paint_transparent_for_glass(true);\n}\n',
   '  set_paint_transparent_for_glass(true);\n'
   '  SetImageCentered(false);  // Glyphe : icône centrée sur la zone de survol\n}\n'),
  # Icône centrée verticalement sur la zone sans marges, comme le survol.
  ('chrome/browser/ui/views/tabs/tab_strip_control_button.h',
   '  // views::View\n'
   '  gfx::Size CalculatePreferredSize(\n'
   '      const views::SizeBounds& available_size) const override;\n',
   '  // views::View\n'
   '  gfx::Size CalculatePreferredSize(\n'
   '      const views::SizeBounds& available_size) const override;\n'
   '  // Glyphe : icône centrée sur la zone de survol (marges exclues).\n'
   '  views::ProposedLayout CalculateProposedLayout(\n'
   '      const views::SizeBounds& size_bounds) const override;\n'),
  ('chrome/browser/ui/views/tabs/tab_strip_control_button.cc',
   'void TabStripControlButton::AddedToWidget() {\n',
   'views::ProposedLayout TabStripControlButton::CalculateProposedLayout(\n'
   '    const views::SizeBounds& size_bounds) const {\n'
   '  views::ProposedLayout layout =\n'
   '      views::LabelButton::CalculateProposedLayout(size_bounds);\n'
   '  // Glyphe : LabelButton centre l\'icône sur toute la hauteur, marges\n'
   '  // comprises ; le survol (GetContentsBounds) les exclut.\n'
   '  if (!size_bounds.height().is_bounded()) {\n'
   '    return layout;\n'
   '  }\n'
   '  const gfx::Insets insets = GetInsets();\n'
   '  const int content_height = size_bounds.height().value() - insets.height();\n'
   '  const views::View* const image = image_container_view();\n'
   '  for (auto& child : layout.child_layouts) {\n'
   '    if (child.child_view.get() == image) {\n'
   '      child.bounds.set_y(insets.top() +\n'
   '                         (content_height - child.bounds.height()) / 2);\n'
   '    }\n'
   '  }\n'
   '  return layout;\n'
   '}\n'
   '\n'
   'void TabStripControlButton::AddedToWidget() {\n'),
]
