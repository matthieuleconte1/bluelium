#!/usr/bin/env python3
"""Applique le patch « Shimmer Tab intégré » dans build/src et écrit le fichier .patch.

Usage : make_shimmer_patch.py <src> <ext_dir> <key_b64_file> <ext_id> <patch_out>
"""
import difflib
import json
import shutil
import sys
from pathlib import Path

src, ext_dir, key_file, ext_id, patch_out = sys.argv[1:6]
src = Path(src)
key = Path(key_file).read_text().strip()
sha1 = __import__('hashlib').sha1(ext_id.encode()).hexdigest().upper()

new_files = {}
edits = []  # (path, old, new)

# --- fichiers neufs -------------------------------------------------------
new_files['third_party/shimmer/README.chromium'] = """Name: Shimmer Tab
Short Name: shimmer
URL: https://github.com/dmitthedazed/shimmer-tab
Version: 1.3.0
License: GPL-3.0
License File: LICENSE
Shipped: yes
Security Critical: no

Description:
A new tab page for the Helium browser, built with Helium Prism.

Local Modifications:
Patched in a public key into manifest so the component ID is stable.
"""

new_files['third_party/shimmer/BUILD.gn'] = """# Helium Glyphe — Shimmer Tab livré comme extension composant.
# GPL-3.0, voir third_party/shimmer/README.chromium.

import("//ui/webui/resources/tools/generate_grd.gni")
import("//tools/grit/grit_rule.gni")

file_list = "$target_gen_dir/files.json"
generated_grd = "$target_gen_dir/shimmer_resources.grd"

action("generate_file_list") {
  script = "generate_file_list.py"
  args = [
    rebase_path("."),
    rebase_path(file_list),
  ]
  inputs = [
    "manifest.json",
    "generate_file_list.py",
  ]
  outputs = [ file_list ]
}

generate_grd("shimmer_grd") {
  out_grd = generated_grd
  grd_prefix = "shimmer"
  resource_path_prefix = "shimmer"
  manifest_files = [ file_list ]
  deps = [ ":generate_file_list" ]
}

grit("shimmer") {
  source = generated_grd
  enable_input_discovery_for_gn_analyze = false
  use_brotli = true
  output_dir = "$target_gen_dir/resources"
  outputs = [
    "grit/shimmer_resources.h",
    "grit/shimmer_resources_map.cc",
    "grit/shimmer_resources_map.h",
    "shimmer_resources.pak",
  ]
  deps = [ ":shimmer_grd" ]
}
"""

new_files['third_party/shimmer/generate_file_list.py'] = """# Helium Glyphe — liste les fichiers de Shimmer Tab pour generate_grd.
import json
import os
from fnmatch import fnmatchcase
from pathlib import Path
from sys import argv

EXCLUDED_FILES = ('BUILD.gn', 'README.chromium', 'LICENSE',
                  'generate_file_list.py')

shimmer_src = Path(argv[1])
out_file = argv[2]
files = []

for root, _, filenames in os.walk(shimmer_src):
  for filename in filenames:
    relative = (Path(root) / filename).relative_to(shimmer_src).as_posix()
    if any(fnmatchcase(relative, p) for p in EXCLUDED_FILES):
      continue
    files.append(relative)

with open(out_file, 'w') as f:
  json.dump({'base_dir': shimmer_src.as_posix(), 'files': sorted(files)}, f)
"""

# --- modifications de fichiers existants ---------------------------------
edits.append(('third_party/shimmer/manifest.json',
  '    "default_locale": "en"\n}',
  '    "default_locale": "en",\n    "key": "%s"\n}' % key))

edits.append(('tools/gritsettings/resource_ids.spec',
  '"<(SHARED_INTERMEDIATE_DIR)/chrome/browser/resources/ash/print_preview/resources.grd": {',
  '"<(SHARED_INTERMEDIATE_DIR)/third_party/shimmer/shimmer_resources.grd": {'))

edits.append(('chrome/chrome_paks.gni',
  '      "$root_gen_dir/third_party/ublock/resources/ublock_resources.pak",\n',
  '      "$root_gen_dir/third_party/ublock/resources/ublock_resources.pak",\n'
  '      "$root_gen_dir/third_party/shimmer/resources/shimmer_resources.pak",\n'))
edits.append(('chrome/chrome_paks.gni',
  '      "//third_party/ublock",\n',
  '      "//third_party/ublock",\n      "//third_party/shimmer",\n'))

edits.append(('chrome/browser/extensions/BUILD.gn',
  '    "//third_party/ublock",\n',
  '    "//third_party/ublock",\n    "//third_party/shimmer",\n'))

edits.append(('components/helium_services/extension_ids.h',
  '}  // namespace helium',
  'inline constexpr char kShimmerTabComponentId[] =\n'
  '    "%s";\n\n'
  'inline constexpr char kShimmerTabComponentIdHashed[] =\n'
  '    // SHA1(kShimmerTabComponentId)\n'
  '    "%s";\n\n'
  '}  // namespace helium' % (ext_id, sha1)))

edits.append(('chrome/browser/extensions/component_loader.h',
  '  void AddUBlock();\n',
  '  void AddUBlock();\n  void AddShimmerTab();\n'))

edits.append(('chrome/browser/extensions/component_loader.cc',
  '#include "third_party/ublock/resources/grit/ublock_resources.h"\n',
  '#include "third_party/ublock/resources/grit/ublock_resources.h"\n'
  '#include "third_party/shimmer/resources/grit/shimmer_resources.h"\n'))
edits.append(('chrome/browser/extensions/component_loader.cc',
  '#if BUILDFLAG(IS_CHROMEOS)\nvoid ComponentLoader::AddChromeApp() {',
  'void ComponentLoader::AddShimmerTab() {\n'
  '  Add(IDR_SHIMMER_MANIFEST_JSON,\n'
  '      base::FilePath(FILE_PATH_LITERAL("shimmer")));\n\n'
  '  using namespace extension_l10n_util;\n'
  '  ComponentExtensionInfo& info = component_extensions_.back();\n'
  '  std::string error;\n'
  '  if (!LocalizeExtension(info.root_directory, &info.manifest,\n'
  '                         GzippedMessagesPermission::kAllowForTrustedSource,\n'
  '                         &error, true)) {\n'
  '    LOG(ERROR) << "Failed to localize Shimmer Tab: " << error;\n'
  '  }\n'
  '}\n\n'
  '#if BUILDFLAG(IS_CHROMEOS)\nvoid ComponentLoader::AddChromeApp() {'))
edits.append(('chrome/browser/extensions/component_loader.cc',
  '    AddUBlock();\n',
  '    AddUBlock();\n    AddShimmerTab();\n'))

edits.append(('chrome/browser/extensions/component_extensions_allowlist/allowlist.cc',
  '#include "third_party/ublock/resources/grit/ublock_resources.h"\n',
  '#include "third_party/ublock/resources/grit/ublock_resources.h"\n'
  '#include "third_party/shimmer/resources/grit/shimmer_resources.h"\n'))
edits.append(('chrome/browser/extensions/component_extensions_allowlist/allowlist.cc',
  '      helium::kUBlockOriginComponentId,\n',
  '      helium::kUBlockOriginComponentId,\n      helium::kShimmerTabComponentId,\n'))
edits.append(('chrome/browser/extensions/component_extensions_allowlist/allowlist.cc',
  '    case IDR_UBLOCK_MANIFEST_JSON:\n',
  '    case IDR_UBLOCK_MANIFEST_JSON:\n    case IDR_SHIMMER_MANIFEST_JSON:\n'))

edits.append(('chrome/browser/extensions/chrome_component_extension_resource_manager.cc',
  '#include "third_party/ublock/resources/grit/ublock_resources_map.h"\n',
  '#include "third_party/ublock/resources/grit/ublock_resources_map.h"\n'
  '#include "third_party/shimmer/resources/grit/shimmer_resources_map.h"\n'))
edits.append(('chrome/browser/extensions/chrome_component_extension_resource_manager.cc',
  '  AddComponentResourceEntries(kUblockResources);\n',
  '  AddComponentResourceEntries(kUblockResources);\n'
  '  AddComponentResourceEntries(kShimmerResources);\n'))

# --- application ----------------------------------------------------------
originals = {}
# Shimmer est « téléchargé » dans third_party/shimmer avant les patchs.
dst = src / 'third_party/shimmer'
if not (dst / 'manifest.json').exists():
  shutil.copytree(ext_dir, dst, dirs_exist_ok=True)

for path, old, new in edits:
  p = src / path
  text = p.read_text()
  originals.setdefault(path, text)
  if new in text:
    continue  # déjà appliqué
  if text.count(old) != 1:
    sys.exit(f'ERREUR : motif introuvable ou ambigu dans {path} :\n{old[:120]}')
  p.write_text(text.replace(old, new, 1))

for path, content in new_files.items():
  (src / path).write_text(content)

# --- écriture du patch ----------------------------------------------------
out = []
for path, content in new_files.items():
  out += difflib.unified_diff([], content.splitlines(True),
                              '/dev/null', 'b/' + path, n=3)
for path in dict.fromkeys(p for p, _, _ in edits):
  before = originals[path]
  # avant = texte d'origine, sans nos ajouts éventuels déjà présents
  for p2, old, new in edits:
    if p2 == path and new in before:
      before = before.replace(new, old, 1)
  after = (src / path).read_text()
  out += difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                              'a/' + path, 'b/' + path, n=3)
Path(patch_out).write_text(''.join(out))
print('OK', patch_out, sum(1 for l in out if l.startswith(('+++', '---'))) // 2, 'fichiers')
