"""Bluelium : mises à jour automatiques intégrées (Sparkle) depuis GitHub.

Helium embarque Sparkle sur macOS mais le pointe vers ses propres serveurs
(updates.helium.computer), et ne vérifie les mises à jour que si les
« services Helium » sont acceptés. Pour Bluelium :
- l'appcast est le fichier appcast-<arch>.xml de la release GitHub « appcast »
  du dépôt Bluelium, réécrit par scripts/package-macos.sh à chaque release ;
- la vérification ne dépend plus que du réglage « mises à jour » (activé par
  défaut), pas des services Helium : GitHub n'est pas un service Helium.

Les mises à jour sont signées avec la clé EdDSA Bluelium (clé publique passée
à GN par scripts/build-macos.sh, clé privée dans le trousseau du Mac de build).
"""
NEW_FILES = {}
_HS = 'components/helium_services/helium_services_helpers.cc'
EDITS = [
 (_HS,
  'constexpr std::string_view kUpdateBaseUrl = "https://updates.helium.computer/";',
  '// Bluelium : appcast publié sur GitHub (release « appcast »).\n'
  'constexpr std::string_view kUpdateBaseUrl =\n'
  '    "https://github.com/matthieuleconte1/bluelium/releases/download/appcast/";'),
 (_HS,
  '    "mac/appcast-" CPU_ARCH_STR ".xml";',
  '    "appcast-" CPU_ARCH_STR ".xml";'),
 (_HS,
  'bool ShouldAccessUpdateService(const PrefService& prefs) {\n'
  '  return ShouldAccessServices(prefs) &&\n'
  '         prefs.GetBoolean(prefs::kHeliumUpdateFetchingEnabled);\n'
  '}\n',
  'bool ShouldAccessUpdateService(const PrefService& prefs) {\n'
  '  // Bluelium : mises à jour depuis GitHub, sans les services Helium.\n'
  '  return prefs.GetBoolean(prefs::kHeliumUpdateFetchingEnabled);\n'
  '}\n'),
]
