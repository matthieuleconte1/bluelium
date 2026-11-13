"""Bluelium : vignettes des thèmes en mini-fenêtre (Personnaliser > Apparence).

Le dessin de Chrome (bandeau d'accent + deux cases) ne montrait pas le rendu
réel. La vignette dessine maintenant une fenêtre Bluelium avec les couleurs
de la palette (prism-ui les fournit déjà) :
  fond   (backgroundColor) : cadre ;
  base   (baseColor)       : onglet actif, champ d'adresse (75 %), page (55 %) ;
  accent (foregroundColor) : point à gauche de l'onglet (la coche de
                             sélection occupe le coin haut droit).
La vignette de couleur libre (background-color-hidden) garde son aplat.
"""

D = 'ui/webui/resources/cr_components/theme_color_picker/'

NEW_FILES = {}

EDITS = [
  (D + 'theme_color.html.ts',
   '  <svg viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg"\n'
   '      xlink="http://www.w3.org/1999/xlink">\n'
   '    <rect id="foreground" x="0" y="0" width="50" height="50"></rect>\n'
   '    <rect id="background" x="0" y="25" width="50" height="25"></rect>\n'
   '    <rect id="base" x="25" y="25" width="25" height="25"></rect>\n'
   '  </svg>\n',
   '  <svg viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg"\n'
   '      xlink="http://www.w3.org/1999/xlink">\n'
   '    <!-- Bluelium : mini-fenêtre ; aplat seul pour la couleur libre. -->\n'
   '    <rect id="foreground" x="0" y="0" width="50" height="50"></rect>\n'
   '    <g class="mini">\n'
   '      <rect id="background" x="0" y="0" width="50" height="50"></rect>\n'
   '      <rect id="base" x="14" y="6" width="21" height="9" rx="3"></rect>\n'
   '      <rect class="field" x="5" y="19" width="40" height="6" rx="3"></rect>\n'
   '      <rect class="page" x="3" y="29" width="44" height="18" rx="4"></rect>\n'
   '      <circle class="accent" cx="8.5" cy="10.5" r="3"></circle>\n'
   '    </g>\n'
   '  </svg>\n'),
  (D + 'theme_color.css',
   '#base {\n  fill: var(--cr-theme-color-base-color);\n}\n',
   '#base {\n  fill: var(--cr-theme-color-base-color);\n}\n'
   '\n'
   '/* Bluelium : champ, page et accent de la mini-fenêtre. */\n'
   '.field {\n  fill: var(--cr-theme-color-base-color);\n  opacity: .75;\n}\n'
   '\n'
   '.page {\n  fill: var(--cr-theme-color-base-color);\n  opacity: .55;\n}\n'
   '\n'
   '.accent {\n  fill: var(--cr-theme-color-foreground-color);\n}\n'
   '\n'
   ':host([background-color-hidden]) .mini {\n  display: none;\n}\n'),
]
