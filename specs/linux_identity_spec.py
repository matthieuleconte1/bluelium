"""Bluelium (Linux) : identité propre dans le navigateur, comme sur macOS.

Avant : l'identité venait seulement du lanceur de l'AppImage (AppRun), qui
passait CHROME_USER_DATA_DIR et CHROME_DESKTOP. Or Helium lit HELIUM_DESKTOP,
pas CHROME_DESKTOP : le nom d'application (WM_CLASS X11, app_id Wayland)
restait « helium », et la barre des tâches confondait Bluelium et Helium.
Lancé hors AppImage (archive), le navigateur ouvrait le profil de Helium.

Après, dans le binaire :
  - profil par défaut ~/.config/bluelium (celui qu'utilise déjà l'AppImage) ;
  - fichier .desktop et nom d'application « bluelium » ;
  - icône « bluelium ».
--user-data-dir et HELIUM_DESKTOP gardent la priorité. La clé du trousseau
(« Helium Safe Storage ») ne change pas : les profils existants, chiffrés
avec elle, restent lisibles.
Plateforme : linux seulement (voir specs/SERIES).
"""

NEW_FILES = {}

EDITS = [
  ('chrome/common/chrome_paths_linux.cc',
   '  std::string data_dir_basename = "net.imput.helium";\n',
   '  std::string data_dir_basename = "bluelium";  // Bluelium : profil propre\n'),
  ('chrome/common/channel_info_posix.cc',
   '  return "helium.desktop";\n',
   '  return "bluelium.desktop";  // Bluelium : nom d\'application propre\n'),
  ('chrome/browser/shell_integration_linux.cc',
   'std::string GetIconName() {\n  return "helium";\n}\n',
   'std::string GetIconName() {\n  return "bluelium";  // Bluelium\n}\n'),
]
