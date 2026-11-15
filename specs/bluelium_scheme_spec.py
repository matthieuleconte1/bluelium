"""Bluelium : adresses internes en bluelium:// au lieu de helium://.

Helium remplace chrome:// par son propre schéma (patch
helium/core/override-chrome-protocol.patch, constante kHeliumUIScheme). On
garde tout ce mécanisme et on change seulement le nom du schéma : la barre
d'adresse affiche bluelium://settings, et on peut taper bluelium://… ;
chrome://… reste accepté. Les textes de l'interface qui citent helium://
sont réécrits par tools/rename-product.py.
"""
NEW_FILES = {}
EDITS = [
 ('content/public/common/url_constants.h',
  'inline constexpr char kHeliumUIScheme[] = "helium";',
  'inline constexpr char kHeliumUIScheme[] = "bluelium";  // Bluelium'),

 ('components/url_formatter/url_fixer.cc',
  'const char kHeliumUIScheme[] = "helium";',
  'const char kHeliumUIScheme[] = "bluelium";  // Bluelium'),

 # Suggestions pendant la saisie : chrome://x → bluelium://x.
 ('components/omnibox/browser/builtin_provider.cc',
  'AddBuiltinMatch(std::u16string(url).replace(0, 6, u"helium"),',
  'AddBuiltinMatch(std::u16string(url).replace(0, 6, u"bluelium"),'),

 # Recherche d'onglets : préfixe affiché devant les pages internes.
 ('chrome/browser/resources/tab_search/tab_search_item.ts',
  "    if (protocol === 'chrome:' || protocol === 'helium:') {\n"
  "      this.$.secondaryTextInner.prepend(document.createTextNode('helium://'));",
  "    if (protocol === 'chrome:' || protocol === 'bluelium:') {\n"
  "      this.$.secondaryTextInner.prepend(document.createTextNode('bluelium://'));"),
]
