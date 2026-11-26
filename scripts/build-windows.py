#!/usr/bin/env python3
"""Bluelium : build Windows (x64) à partir de helium-windows.

Même déroulé que macOS et Linux : étapes de Helium (téléchargement, élagage,
patchs, substitutions, traductions, version, ressources), PUIS la série
Bluelium (specs/SERIES, plateforme « win »), compilation, installateur.
Tourne sur Windows, dans un dépôt helium-windows (sous-modules compris) :
réutilise ses scripts (dossier scripts/ de helium-windows).

Usage (depuis n'importe où) :
  build-windows.py prepare  <helium-windows> <dépôt bluelium> <version>
      Sources + série Bluelium + gn gen. Écrit build/meta.env, build/series.log
      et les .patch régénérés dans build/patches-<version>/.
  build-windows.py compile  <helium-windows> [début du job (epoch) minutes]
      Compile. Sans échéance : jusqu'au bout. Avec : s'arrête à temps
      (RESERVE_MIN minutes avant la fin du job, défaut 60) et sort en 42
      (à reprendre au job suivant). 0 : compilation finie.
  build-windows.py package  <helium-windows> <dossier de sortie>
      Installateur non signé bluelium-<version>-windows-x64-installer.exe
      (+ .sha256), à partir du script NSIS de Helium renommé.

Variables : JOBS (tâches de compilation), RESERVE_MIN.
Non signé, sans mise à jour intégrée (WinSparkle coupé : pas de clé).
"""
import configparser
import hashlib
import io
import os
import re
import subprocess
import sys
import time
from pathlib import Path


def helium(root):
  root = Path(root).resolve()
  if not (root / 'build.py').is_file() or not (root / 'helium-chromium' / 'utils').is_dir():
    sys.exit(f'{root} : pas un dépôt helium-windows avec ses sous-modules')
  sys.path.insert(0, str(root))
  sys.path.insert(0, str(root / 'helium-chromium' / 'utils'))
  os.chdir(root)
  return root


def meta(root):
  values = {}
  for line in (root / 'build' / 'meta.env').read_text(encoding='utf-8').splitlines():
    key, _, value = line.partition('=')
    values[key] = value.strip('"')
  return values


def prepare(root, repo, version):
  repo = Path(repo).resolve()  # avant helium(), qui change de dossier
  root = helium(root)
  from scripts import BUILD_DIR, SOURCE_TREE, gn, remoteexec, source
  from scripts.toolchain import make_tmp_paths
  from _common import USE_REGISTRY, ExtractorEnum

  # Sources en plus de Bluelium (Shimmer Tab, PDF.js) : tout sauf l'archive
  # Chromium Linux, que helium-windows remplace par la sienne.
  ours = configparser.RawConfigParser()
  ours.read(repo / 'downloads.ini', encoding='utf-8')
  extra = configparser.RawConfigParser()
  for section in ours.sections():
    if not section.startswith('chromium-'):
      extra[section] = ours[section]
  buf = io.StringIO()
  extra.write(buf)
  downloads = root / 'downloads.ini'
  text = downloads.read_text(encoding='utf-8')
  if '[shimmer-tab]' not in text:
    downloads.write_text(text.rstrip('\n') + '\n\n' + buf.getvalue(), encoding='utf-8',
                         newline='\n')

  # Étapes de Helium, comme build.py prepare_source (archive x64 préparée).
  SOURCE_TREE.mkdir(parents=True, exist_ok=True)
  (BUILD_DIR / 'download_cache').mkdir(parents=True, exist_ok=True)
  make_tmp_paths()
  source.fetch(True, False, {ExtractorEnum.SEVENZIP: USE_REGISTRY,
                             ExtractorEnum.WINRAR: USE_REGISTRY})
  source.prune()
  source.apply_patches()
  source.substitute()
  source.set_version()
  source.copy_resources()

  # Série Bluelium sur l'arbre final.
  out = BUILD_DIR / f'patches-{version}'
  env = dict(os.environ, PYTHONUTF8='1',
             PATCH_BIN=str(SOURCE_TREE / 'third_party/git/usr/bin/patch.exe'))
  result = subprocess.run(
      [sys.executable, str(repo / 'tools' / 'apply-series.py'), str(SOURCE_TREE), str(repo),
       str(out), 'win'], env=env, capture_output=True, text=True, encoding='utf-8')
  log = result.stdout + result.stderr
  (BUILD_DIR / 'series.log').write_text(log, encoding='utf-8')
  print(log)
  if result.returncode != 0:
    failed = next((l for l in log.splitlines() if 'ÉCHEC' in l), '?')
    sys.exit(f'ÉCHEC : un patch Bluelium ne s\'applique pas sur Helium Windows : {failed[:160]}')

  remoteexec.configure()
  gn.write_args(False, False)
  gn.gen()

  couleur = [sys.executable, str(repo / 'tools' / 'couleur.py'), str(repo)]
  serie = subprocess.run(couleur + ['--serie'], capture_output=True, text=True,
                         check=True).stdout.strip()
  nom = subprocess.run(couleur + ['--nom'], capture_output=True, text=True,
                       encoding='utf-8', check=True).stdout.strip()
  (BUILD_DIR / 'meta.env').write_text(
      f'VERSION={version}\nHELIUM_TAG={version.split("-", 1)[0]}\nSERIE={serie}\n'
      f'NOM="{nom}"\nARCH=x64\n', encoding='utf-8', newline='\n')
  print(f'=== préparé : Bluelium {version} (Windows x64), compilation à lancer')


def compile_(root, start=None, minutes=None):
  helium(root)
  from scripts import gn, remoteexec
  remoteexec.set_environment()
  timeout = None
  if start is not None:
    reserve = int(os.environ.get('RESERVE_MIN', '60'))
    timeout = int(minutes) * 60 - reserve * 60 - (int(time.time()) - int(start))
    if timeout <= 600:
      sys.exit(f'ÉCHEC : plus assez de temps dans ce job ({timeout} s)')
    print(f'Compilation pendant au plus {timeout // 60} min')
  jobs = os.environ.get('JOBS') or None
  # Sort en 42 si l'échéance tombe (scripts/toolchain.py de Helium).
  gn.autoninja(gn.RELEASE_TARGETS, jobs, timeout)
  print('=== compilation terminée')


def package(root, dest):
  dest = Path(dest).resolve()  # avant helium(), qui change de dossier
  root = helium(root)
  from scripts import OUT_DIR, SOURCE_TREE
  info = meta(root)
  version = info['VERSION']
  dest.mkdir(parents=True, exist_ok=True)

  # Script NSIS de Helium, au nom de Bluelium, installé dans
  # %LOCALAPPDATA%\Bluelium (ou Program Files\Bluelium), comme la spec
  # windows_identity.
  nsi = (root / 'installer' / 'helium.nsi').read_text(encoding='utf-8')
  for old, new in (
      ('!define PRODUCT_NAME "Helium"', '!define PRODUCT_NAME "Bluelium"'),
      ('!define PRODUCT_PUBLISHER "imput"', '!define PRODUCT_PUBLISHER "Bluelium"'),
      ('!define PRODUCT_GUID "{FB68A146-637A-48C2-A0C4-1565DE45FEBD}"',
       '!define PRODUCT_GUID "{6D8633B0-A1F1-4A06-8086-5C623F31B488}"'),
      ('\\${PRODUCT_COMPANY_PATH}\\${PRODUCT_NAME}\\', '\\${PRODUCT_NAME}\\'),
      ('VIAddVersionKey "LegalCopyright" "Copyright The Helium Authors"',
       'VIAddVersionKey "LegalCopyright" "Copyright The Helium Authors, Bluelium"'),
      ('$TEMP\\helium_install', '$TEMP\\bluelium_install')):
    if old not in nsi:
      sys.exit(f'ÉCHEC : installer/helium.nsi a changé, introuvable : {old}')
    nsi = nsi.replace(old, new)
  if 'PRODUCT_COMPANY_PATH}\\' in nsi:
    sys.exit('ÉCHEC : installer/helium.nsi : chemin avec la société restant')
  script = root / 'build' / 'bluelium.nsi'
  script.write_text(nsi, encoding='utf-8')

  # VIProductVersion veut quatre nombres : la version de Helium.
  numbers = re.match(r'\d+(\.\d+){3}', version)
  if not numbers:
    sys.exit(f'ÉCHEC : version {version} sans quatre nombres')
  name = f'bluelium-{version}-windows-x64-installer.exe'
  output = dest / name
  subprocess.run([
      str(SOURCE_TREE / 'third_party' / 'nsis' / 'makensis.exe'), '-NOCD',
      f'-DVERSION={numbers.group(0)}', '-DARCH=x64',
      f'-DSETUP_EXE={OUT_DIR / "setup.exe"}',
      f'-DHELIUM_7Z={OUT_DIR / "helium.packed.7z"}',
      f'-DICON_FILE={SOURCE_TREE / "chrome/app/theme/chromium/win/chromium.ico"}',
      f'-DOUTPUT_FILE={output}', f'-DLICENSE_FILE={root / "LICENSE"}',
      str(script)], check=True)
  digest = hashlib.sha256(output.read_bytes()).hexdigest()
  (dest / f'{name}.sha256').write_text(f'{digest}  {name}\n', encoding='utf-8', newline='\n')
  (dest / 'meta.env').write_bytes((root / 'build' / 'meta.env').read_bytes())
  print(f'=== paquet : {output}')


if __name__ == '__main__':
  # Commande : (fonction, nombres d'arguments acceptés).
  commands = {'prepare': (prepare, (3,)), 'compile': (compile_, (1, 3)),
              'package': (package, (2,))}
  command, *rest = sys.argv[1:] or ['']
  if command not in commands or len(rest) not in commands[command][1]:
    sys.exit(__doc__)
  commands[command][0](*rest)
