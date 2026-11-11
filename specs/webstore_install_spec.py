# Helium Glyphe : autoriser les CRX du service officiel, avec confirmation
# native et validation CRX conservées. Les autres sources gardent leur politique.
NEW_FILES = {}
EDITS = [
 ('chrome/browser/extensions/extension_management.cc',
  '  // No allowed install sites specified, disallow by default.\n',
  '  // Glyphe: the Helium store helper downloads CRX directly from Google.\n'
  '  // Keep explicit MIME-handling overrides and all installer/policy checks.\n'
  '  if (!command_line.HasSwitch("extension-mime-request-handling") &&\n'
  '      url.SchemeIs("https") &&\n'
  '      ((url.host() == "clients2.google.com" &&\n'
  '        url.path() == "/service/update2/crx") ||\n'
  '       (url.host() == "clients2.googleusercontent.com" &&\n'
  '        url.path().starts_with("/crx/blobs/")))) {\n'
  '    return true;\n'
  '  }\n'
  '  // No allowed install sites specified, disallow by default.\n'),
]
