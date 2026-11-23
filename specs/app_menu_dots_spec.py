"""Bluelium : bouton « ⋯ » du menu, trois points ronds horizontaux.

L'icône d'origine (Material « more_vert », points verticaux fins) est
remplacée, pour ce seul bouton, par trois points ronds horizontaux plus
francs, à la couleur des autres boutons de la barre.
"""

BAMB_CC = 'chrome/browser/ui/views/toolbar/browser_app_menu_button.cc'

NEW_FILES = {
    'chrome/app/vector_icons/bluelium_more.icon': '''// Bluelium : menu « ⋯ », trois points ronds horizontaux.
CANVAS_DIMENSIONS, 20,
CIRCLE, 4.5, 10, 1.75,
CIRCLE, 10, 10, 1.75,
CIRCLE, 15.5, 10, 1.75
''',
}

EDITS = [
    ('chrome/app/vector_icons/BUILD.gn',
     '    "more_vert.icon",\n',
     '    "more_vert.icon",\n'
     '    "bluelium_more.icon",\n'),
    (BAMB_CC,
     '  const gfx::VectorIcon& icon =\n'
     '      ui::TouchUiController::Get()->touch_ui()\n'
     '          ? features::IsRoundedIconsEnabled() ? kMoreVertIcon\n'
     '                                              : kBrowserToolsTouchOldIcon\n'
     '      : features::IsRoundedIconsEnabled() ? kMoreVertIcon\n'
     '                                          : kBrowserToolsChromeRefreshOldIcon;\n',
     '  // Bluelium : trois points ronds horizontaux, en tactile comme à la souris.\n'
     '  const gfx::VectorIcon& icon = kBlueliumMoreIcon;\n'),
]
