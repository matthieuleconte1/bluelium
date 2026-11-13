"""Bluelium : Personnaliser > Barre d'outils à jour avec la barre Bluelium.

- Le bouton IA (onglet IA) apparaît dans la liste, catégorie « Votre
  navigateur » ; l'activer ou le désactiver passe par le modèle des boutons
  épinglés (et donc par glyphe.assistant.unpinned).
- Profils : caché par défaut (kShowAvatarButton à faux), l'interrupteur de la
  liste le fait réapparaître (voir toolbar_final_layout_spec.py).
"""

H = ('chrome/browser/ui/webui/side_panel/customize_chrome/customize_toolbar/'
     'customize_toolbar_handler.cc')
MOJOM = ('chrome/browser/ui/webui/side_panel/customize_chrome/customize_toolbar/'
         'customize_toolbar.mojom')

NEW_FILES = {}

EDITS = [
  ('chrome/browser/ui/browser_ui_prefs.cc',
   '  registry->RegisterBooleanPref(prefs::kShowAvatarButton, true);\n',
   '  // Bluelium : bouton de profil caché par défaut (réglable).\n'
   '  registry->RegisterBooleanPref(prefs::kShowAvatarButton, false);\n'),
  (MOJOM,
   '  kSplitTab,\n  kContextualTasks,\n};\n',
   '  kSplitTab,\n  kContextualTasks,\n  // Bluelium : onglet IA.\n  kGlypheAssistant,\n};\n'),
  (H,
   '    case kActionSidePanelShowContextualTasks:\n'
   '      return side_panel::customize_chrome::mojom::ActionId::kContextualTasks;\n'
   '    default:\n',
   '    case kActionSidePanelShowContextualTasks:\n'
   '      return side_panel::customize_chrome::mojom::ActionId::kContextualTasks;\n'
   '    case kActionSidePanelShowGlypheAssistant:  // Bluelium\n'
   '      return side_panel::customize_chrome::mojom::ActionId::kGlypheAssistant;\n'
   '    default:\n'),
  (H,
   '    case side_panel::customize_chrome::mojom::ActionId::kContextualTasks:\n'
   '      return kActionSidePanelShowContextualTasks;\n'
   '    default:\n',
   '    case side_panel::customize_chrome::mojom::ActionId::kContextualTasks:\n'
   '      return kActionSidePanelShowContextualTasks;\n'
   '    case side_panel::customize_chrome::mojom::ActionId::kGlypheAssistant:\n'
   '      return kActionSidePanelShowGlypheAssistant;  // Bluelium\n'
   '    default:\n'),
  (H,
   '  add_action(kActionTabSearch,\n'
   '             side_panel::customize_chrome::mojom::CategoryId::kTools);\n',
   '  // Bluelium : onglet IA, avec les boutons du navigateur.\n'
   '  add_action(kActionSidePanelShowGlypheAssistant,\n'
   '             side_panel::customize_chrome::mojom::CategoryId::kYourChrome);\n'
   '  add_action(kActionTabSearch,\n'
   '             side_panel::customize_chrome::mojom::CategoryId::kTools);\n'),
]
