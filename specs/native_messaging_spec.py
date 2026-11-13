# Helium lit déjà les chemins Chrome. Ajouter Chromium utilisateur (XDG).
NEW_FILES = {}
EDITS = [
 ('chrome/browser/extensions/api/messaging/launch_context_posix.cc',
  '#include "build/chromeos_buildflags.h"\n',
  '#include "build/chromeos_buildflags.h"\n'
  '#if BUILDFLAG(IS_LINUX)  // Glyphe : dossier Chromium XDG\n'
  '#include "base/environment.h"\n#include "base/nix/xdg_util.h"\n#endif\n'),
 ('chrome/browser/extensions/api/messaging/launch_context_posix.cc',
  '  if (result.empty()) {\n    result = FindManifestInDir(chrome::DIR_NATIVE_MESSAGING, host_name);\n  }',
  '\n'.join([
   '#if BUILDFLAG(IS_LINUX)',
   '  // Glyphe: Chromium user hosts, after Helium and Google Chrome.',
   '  // Respect NativeMessagingUserLevelHosts exactly as the primary paths do.',
   '  if (result.empty() && allow_user_level_hosts) {',
   '    auto env = base::Environment::Create();',
   '    const base::FilePath config = base::nix::GetXDGDirectory(',
   '        env.get(), base::nix::kXdgConfigHomeEnvVar, ".config");',
   '    const base::FilePath manifest = config.Append("chromium")',
   '        .Append("NativeMessagingHosts").Append(host_name + ".json");',
   '    if (base::PathExists(manifest)) {',
   '      result = manifest;',
   '    }',
   '  }',
   '#endif',
   '',
   '  if (result.empty()) {',
   '    result = FindManifestInDir(chrome::DIR_NATIVE_MESSAGING, host_name);',
   '  }']))
]
