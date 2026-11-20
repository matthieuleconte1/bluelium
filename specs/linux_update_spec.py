"""Bluelium (Linux) : mise à jour signalée dans le navigateur, comme Sparkle.

Avant : l'AppImage se remplaçait en arrière-plan (autobuild/appimage-update)
sans rien dire ; la nouvelle version ne servait qu'au lancement suivant. Le
détecteur de Chromium ne voyait rien : il interroge le binaire en cours, qui
reste celui de l'AppImage montée.

Après :
- appimage-update écrit la version téléchargée dans
  ~/.cache/bluelium/update-ready ; AppRun exporte BLUELIUM_VERSION (version
  en cours) et efface ce fichier une fois la nouvelle version lancée ;
- le détecteur de Chromium lit ce fichier : si la version prête diffère de
  celle en cours, il signale une mise à jour. Le menu affiche alors
  « Relancer pour mettre à jour » et la page À propos un bouton Relancer ;
- la relance passe par le lanceur (CHROME_WRAPPER, l'AppImage) et non par le
  binaire de l'image montée, qui disparaît à la fermeture : c'est la nouvelle
  AppImage qui démarre.
Sans BLUELIUM_VERSION (build lancé à la main), comportement de Chromium.
Plateforme : linux seulement (voir specs/SERIES).
"""

VERSION_LINUX = 'chrome/browser/upgrade_detector/get_installed_version_linux.cc'
UPGRADE_UTIL = 'chrome/browser/first_run/upgrade_util.cc'

NEW_FILES = {}

EDITS = [
  (VERSION_LINUX,
   '#include <string>\n',
   '#include <memory>\n'
   '#include <optional>\n'
   '#include <string>\n',
  ),
  (VERSION_LINUX,
   '#include "base/command_line.h"\n',
   '#include "base/command_line.h"\n'
   '#include "base/environment.h"\n'
   '#include "base/files/file_path.h"\n'
   '#include "base/files/file_util.h"\n'
   '#include "base/nix/xdg_util.h"\n'
   '#include "base/strings/strcat.h"\n'),
  (VERSION_LINUX,
   '#include "chrome/common/chrome_switches.h"\n',
   '#include "chrome/common/chrome_switches.h"\n'
   '#include "components/version_info/version_info.h"\n'),
  (VERSION_LINUX,
   'InstalledAndCriticalVersion GetInstalledVersionSynchronous() {\n',
   '''// Bluelium : version téléchargée par appimage-update, prête au prochain
// lancement. Renvoie une version invalide s'il n'y en a pas.
base::Version GetBlueliumReadyVersion() {
  std::unique_ptr<base::Environment> env = base::Environment::Create();
  const std::optional<std::string> running = env->GetVar("BLUELIUM_VERSION");
  if (!running || running->empty()) {
    return base::Version();
  }
  const base::FilePath marker =
      base::nix::GetXDGDirectory(env.get(), "XDG_CACHE_HOME", ".cache")
          .Append("bluelium")
          .Append("update-ready");
  std::string ready;
  if (!base::ReadFileToStringWithMaxSize(marker, &ready, 256)) {
    return base::Version();
  }
  ready = std::string(base::TrimWhitespaceASCII(ready, base::TRIM_ALL));
  if (ready.empty() || ready == *running) {
    return base::Version();
  }
  // Deux versions de Bluelium peuvent partager la version de Chromium : un
  // composant de plus suffit à la rendre plus récente que celle en cours.
  return base::Version(base::StrCat({version_info::GetVersionNumber(), ".1"}));
}

InstalledAndCriticalVersion GetInstalledVersionSynchronous() {
  if (base::Version ready = GetBlueliumReadyVersion(); ready.IsValid()) {
    return InstalledAndCriticalVersion(std::move(ready));
  }
'''),
  (UPGRADE_UTIL,
   '#include "chrome/common/chrome_switches.h"\n'
   '#include "content/public/browser/browser_thread.h"\n',
   '#include "chrome/common/chrome_switches.h"\n'
   '#include "content/public/browser/browser_thread.h"\n'
   '\n'
   '#if BUILDFLAG(IS_LINUX)\n'
   '#include "base/environment.h"\n'
   '#include "base/files/file_util.h"\n'
   '#endif\n'),
  (UPGRADE_UTIL,
   '  base::CommandLine new_cl(old_cl.GetProgram());\n',
   '  base::CommandLine new_cl(old_cl.GetProgram());\n'
   '#if BUILDFLAG(IS_LINUX)\n'
   '  // Bluelium : relancer par le lanceur (AppImage ou helium-wrapper). Le\n'
   '  // binaire de l\'AppImage montée disparaît à la fermeture, et seule la\n'
   '  // nouvelle AppImage contient la mise à jour.\n'
   '  if (const std::optional<std::string> wrapper =\n'
   '          base::Environment::Create()->GetVar("CHROME_WRAPPER");\n'
   '      wrapper && !wrapper->empty() &&\n'
   '      base::PathExists(base::FilePath(*wrapper))) {\n'
   '    new_cl.SetProgram(base::FilePath(*wrapper));\n'
   '  }\n'
   '#endif\n'),
]
