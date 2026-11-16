"""Bluelium : secours Chromium utilisateur sur macOS, comme sous Linux.
La découverte des profils dans Claude Code/ChatGPT est extérieure au navigateur.
"""
NEW_FILES = {}
EDITS = [
 ('chrome/browser/extensions/api/messaging/launch_context_posix.cc',
  '#include "build/chromeos_buildflags.h"\n',
  '#include "build/chromeos_buildflags.h"\n'
  '#if BUILDFLAG(IS_MAC)  // Bluelium : manifeste installé seulement pour Chromium\n'
  '#include "base/base_paths.h"\n#include "base/path_service.h"\n#endif\n'),
 ('chrome/browser/extensions/api/messaging/launch_context_posix.cc',
  '  if (result.empty()) {\n    result = FindManifestInDir(chrome::DIR_NATIVE_MESSAGING, host_name);\n  }',
  '#if BUILDFLAG(IS_MAC)\n'
  '  if (result.empty() && allow_user_level_hosts) {\n'
  '    base::FilePath home;\n'
  '    if (base::PathService::Get(base::DIR_HOME, &home)) {\n'
  '      const auto manifest = home.Append("Library/Application Support/Chromium")\n'
  '          .Append("NativeMessagingHosts").Append(host_name + ".json");\n'
  '      if (base::PathExists(manifest)) {\n'
  '        result = manifest;\n'
  '      }\n'
  '    }\n'
  '  }\n'
  '#endif\n\n'
  '  if (result.empty()) {\n    result = FindManifestInDir(chrome::DIR_NATIVE_MESSAGING, host_name);\n  }'),
]
