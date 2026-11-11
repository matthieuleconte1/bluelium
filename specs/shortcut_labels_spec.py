# Helium Glyphe — libellés des raccourcis Glyphe.
# Avec les raccourcis personnalisables (kCustomizableBrowserShortcuts), une
# commande sans libellé est retirée de la table : Alt+Maj+N/C/G ne marchaient pas.

EDITS = [
  ('chrome/browser/ui/browser_shortcuts/browser_shortcut_metadata.cc',
   '    case IDC_TOGGLE_ZEN_MODE_TOP_CHROME_PIN:\n'
   '      return Label(IDS_SHORTCUT_COMMAND_TOGGLE_ZEN_MODE_TOP_CHROME_PIN);\n',
   '    case IDC_TOGGLE_ZEN_MODE_TOP_CHROME_PIN:\n'
   '      return Label(IDS_SHORTCUT_COMMAND_TOGGLE_ZEN_MODE_TOP_CHROME_PIN);\n'
   '    case IDC_GLYPHE_TOGGLE_RED_NIGHT:\n'
   '      return Label(IDS_WILDCARD, u"Mode nuit rouge");\n'
   '    case IDC_GLYPHE_ASSISTANT_CLAUDE:\n'
   '      return Label(IDS_WILDCARD, u"Ouvrir Claude dans le panneau latéral");\n'
   '    case IDC_GLYPHE_ASSISTANT_CHATGPT:\n'
   '      return Label(IDS_WILDCARD, u"Ouvrir ChatGPT dans le panneau latéral");\n'),
]
