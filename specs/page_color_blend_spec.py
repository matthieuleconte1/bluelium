"""Bluelium : changement de couleur de page en vrai dégradé, fluide.

Avant (page_color_fade_spec.py) : 180 ms en paliers de 33 ms, soit ~6
teintes : saccadé, perçu comme brutal.

Après : une teinte par image (16 ms) sur 280 ms, avec la courbe Bluelium.
L'avancement suit l'horloge : si une image prend du retard, la suivante
rattrape, la durée reste la même.

Écartés le 15 nov. : balayage du haut vers le bas, puis image figée de la
fenêtre effacée en fondu (avec ou sans flou). L'image figée masquait les
animations des onglets pendant le fondu et arrivait trop tard sur les sites
lourds (copie GPU > 120 ms), d'où un changement net.

S'applique après motion_spec.py.
"""
NEW_FILES = {}
_CC = 'chrome/browser/ui/views/frame/browser_widget.cc'
EDITS = [
 (_CC,
  '      FROM_HERE, base::Milliseconds(33),\n'
  '      base::BindRepeating(&BrowserWidget::StepGlyphePageColorFade,\n',
  '      FROM_HERE, base::Milliseconds(16),  // Bluelium : une teinte par image\n'
  '      base::BindRepeating(&BrowserWidget::StepGlyphePageColorFade,\n'),
 (_CC,
  '  constexpr base::TimeDelta kDuration = base::Milliseconds(180);'
  '  // Bluelium : même durée que les onglets\n',
  '  constexpr base::TimeDelta kDuration = base::Milliseconds(280);'
  '  // Bluelium : dégradé fluide\n'),
]
