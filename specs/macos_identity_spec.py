"""Bluelium (macOS) : identité propre, distincte de Helium installé à côté.

Sous Linux, le lanceur passe --user-data-dir ; sur macOS l'appli s'ouvre par
LaunchServices, qui confond deux applis au même identifiant. Ici :
  - identifiant de bundle propre (les assistants « .helper » en dérivent) ;
  - profil dans ~/Library/Application Support/Bluelium ;
  - clé de chiffrement du trousseau à part (« Bluelium Storage Key ») : on ne
    lit ni n'écrase celle de Helium.
Le nom affiché (Bluelium.app, barre de menus) est posé à l'empaquetage
(scripts/package-macos.sh) : PRODUCT_FULLNAME reste « Helium », dont dépendent
les noms des cibles et du framework.
Plateforme : mac seulement (voir specs/SERIES).
"""

NEW_FILES = {}

EDITS = [
  ('chrome/app/theme/chromium/BRANDING',
   'MAC_BUNDLE_ID=net.imput.helium\n',
   'MAC_BUNDLE_ID=io.github.matthieuleconte1.bluelium\n'),
  ('chrome/common/chrome_paths_mac.mm',
   '      product_dir_name = "net.imput.helium";\n',
   '      product_dir_name = "Bluelium";  // Bluelium : profil distinct de Helium\n'),
  ('components/os_crypt/common/keychain_password_mac.mm',
   'const char kDefaultServiceName[] = "Helium Storage Key";\n'
   'const char kDefaultAccountName[] = "Helium";\n',
   '// Bluelium : clé à part, pour ne pas partager celle de Helium.\n'
   'const char kDefaultServiceName[] = "Bluelium Storage Key";\n'
   'const char kDefaultAccountName[] = "Bluelium";\n'),
]
