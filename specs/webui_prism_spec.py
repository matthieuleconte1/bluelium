"""Bluelium : pages internes aux couleurs du thème, avec une entrée animée.

Pages concernées : toutes celles qui chargent text_defaults_md.css
(Réglages, Historique, Téléchargements, Extensions, Favoris et la plupart des
pages chrome://). Les jetons --color-sys-* suivent déjà Prism ; le fond des
pages et des cartes venait d'autres variables (gris de Chromium, blanc).

- Fond de page : couleur de base du thème (kColorSysHeader, celle du cadre),
  donc la page se fond dans la fenêtre. Repli : Canvas (clair/sombre).
- Cartes : surface Prism (kColorSysSurface), coins de 12 px.
- Accent : déjà fourni par --color-sys-primary (prism_ui).
- Entrée : fondu et glissement de 8 px vers le haut, 280 ms, courbe Bluelium.
  Les sections des Réglages et les cartes d'extensions arrivent l'une après
  l'autre (30 ms d'écart). Seuls les 10 premiers éléments s'animent : une
  ligne ajoutée plus tard (défilement d'une liste longue) apparaît sans délai.
  Rien si « réduire les animations ». Seuls opacity et translate bougent.
Clair, Sombre, OLED et Nuit suivent, puisque tout passe par les jetons.
"""

ENTER = 'bluelium-page-enter 280ms cubic-bezier(0.2, 0.8, 0.2, 1) backwards'
STAGGER = 'calc((sibling-index() - 1) * 30ms)'

KEYFRAMES = (
    '@keyframes bluelium-page-enter {\n'
    '  from {\n'
    '    opacity: 0;\n'
    '    translate: 0 8px;\n'
    '  }\n'
    '}\n')


def host_animation(comment):
  return (
      '/* Bluelium : ' + comment + ' */\n' + KEYFRAMES + '\n'
      '@media (prefers-reduced-motion: no-preference) {\n'
      '  :host(:nth-child(-n + 10)) {\n'
      '    animation: ' + ENTER + ';\n'
      '    animation-delay: ' + STAGGER + ';\n'
      '  }\n'
      '}\n\n')


NEW_FILES = {}
EDITS = [
  ('ui/webui/resources/css/text_defaults_md.css',
   'button {\n'
   '  font-family: $i18nRaw{fontfamilyMd};\n'
   '}\n',
   'button {\n'
   '  font-family: $i18nRaw{fontfamilyMd};\n'
   '}\n'
   '\n'
   '/* Bluelium : fond et cartes aux couleurs du thème. Les variables passent\n'
   ' * les shadow roots ; !important l\'emporte sur cr_shared_vars et sur les\n'
   ' * styles propres à chaque page. */\n'
   'html:root {\n'
   '  --bluelium-page-background: var(--color-sys-header, Canvas);\n'
   '  --md-background-color: var(--bluelium-page-background) !important;\n'
   '  --color-webui-page-background: var(--bluelium-page-background) !important;\n'
   '  --color-settings-webui-page-background:\n'
   '      var(--bluelium-page-background) !important;\n'
   '  --cr-card-background-color: var(--color-sys-surface, Canvas) !important;\n'
   '  --cr-card-border-radius: 12px !important;\n'
   '  background: var(--bluelium-page-background) !important;\n'
   '}\n'
   '\n'
   '/* Bluelium : entrée de la page en fondu, avec un léger glissement. */\n'
   + KEYFRAMES +
   '\n'
   '@media (prefers-reduced-motion: no-preference) {\n'
   '  body > :not(script, style, link, template, dialog) {\n'
   '    animation: ' + ENTER + ';\n'
   '  }\n'
   '}\n'),
  ('chrome/browser/resources/settings/settings_page/settings_section.css',
   ' * #css_wrapper_metadata_end */\n\n:host {\n',
   ' * #css_wrapper_metadata_end */\n\n'
   + host_animation('les sections arrivent l\'une après l\'autre.') +
   ':host {\n'),
  # Bluelium : listes de l'Historique, des Téléchargements et des Favoris.
  # Les listes virtuelles n'insèrent que les lignes visibles : seules
  # celles-ci s'animent, le défilement ne relance rien.
  ('chrome/browser/resources/history/history_item.css',
   ' * #css_wrapper_metadata_end */\n\n:host {\n',
   ' * #css_wrapper_metadata_end */\n\n'
   + host_animation('les visites arrivent l\'une après l\'autre.') +
   ':host {\n'),
  ('chrome/browser/resources/downloads/item.css',
   ' * #css_wrapper_metadata_end */\n\n:host {\n',
   ' * #css_wrapper_metadata_end */\n\n'
   + host_animation('les téléchargements arrivent l\'un après l\'autre.') +
   ':host {\n'),
  ('chrome/browser/resources/bookmarks/item.css',
   ' * #css_wrapper_metadata_end */\n\n:host {\n',
   ' * #css_wrapper_metadata_end */\n\n'
   + host_animation('les favoris arrivent l\'un après l\'autre.') +
   ':host {\n'),
  ('chrome/browser/resources/extensions/item.css',
   '#card {\n'
   '  background-color: var(--cr-card-background-color);\n',
   host_animation('les cartes arrivent l\'une après l\'autre.') +
   '#card {\n'
   '  background-color: var(--cr-card-background-color);\n'),
]
