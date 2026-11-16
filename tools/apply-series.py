#!/usr/bin/env python3
"""Applique toute la série Bluelium sur un arbre Helium et régénère les patchs.

Usage : apply-series.py <src> <dépôt bluelium> <dossier des .patch générés> [linux|mac]

La plateforme (linux par défaut) écarte les lignes de specs/SERIES réservées
à une autre plateforme (troisième colonne facultative).

Lit specs/SERIES : chaque spec passe par apply_spec.py (qui écrit le .patch
correspondant) ; une ligne « - » applique le .patch figé de patches/glyphe/
avec `patch -p1` et le recopie tel quel. À lancer après toutes les étapes de
Helium. S'arrête au premier échec en indiquant le patch fautif ; avec
KEEP_GOING=1, continue et liste tous les échecs à la fin (test d'une nouvelle
version de Helium : tools/test-serie-helium.sh).
Remplace ensuite le nom affiché « Helium » par « Bluelium » (tools/rename-product.py).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

src, repo, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
platform = sys.argv[4] if len(sys.argv) > 4 else 'linux'
if platform not in ('linux', 'mac'):
  sys.exit(f'plateforme inconnue : {platform} (linux ou mac)')
out.mkdir(parents=True, exist_ok=True)
apply_spec = repo / 'tools' / 'apply_spec.py'

entries = []
for line in (repo / 'specs' / 'SERIES').read_text().splitlines():
  line = line.split('#', 1)[0].strip()
  if line:
    patch, spec, *rest = line.split()
    platforms = rest[0].split(',') if rest else ['linux', 'mac']
    if platform in platforms:
      entries.append((patch, spec))

keep_going = os.environ.get('KEEP_GOING') == '1'
failures = []


def fail(message):
  if not keep_going:
    sys.exit(message)
  print(message, flush=True)
  failures.append(message.splitlines()[0])


for index, (patch, spec) in enumerate(entries, 1):
  label = f'[{index}/{len(entries)}] {patch}'
  if spec == '-':
    fixed = repo / 'patches' / 'glyphe' / patch
    result = subprocess.run(
        ['patch', '-p1', '--forward', '--no-backup-if-mismatch', '-d', str(src),
         '-i', str(fixed)], capture_output=True, text=True)
    if result.returncode != 0:
      fail(f'{label} : ÉCHEC du patch figé\n{result.stdout[-2000:]}')
      continue
    shutil.copy(fixed, out / patch)
  else:
    result = subprocess.run(
        [sys.executable, str(apply_spec), str(src), str(repo / 'specs' / spec),
         str(out / patch)], capture_output=True, text=True)
    if result.returncode != 0:
      fail(f'{label} : ÉCHEC de {spec}\n{result.stdout}{result.stderr}')
      continue
  print(label, 'OK')
if failures:
  sys.exit(f'{len(failures)} échec(s) sur {len(entries)} patchs :\n' + '\n'.join(failures))
print(f'Série complète ({platform}) :', len(entries), 'patchs')

# Bluelium : le nom affiché devient « Bluelium » (le logo de Helium reste).
result = subprocess.run([sys.executable, str(repo / 'tools' / 'rename-product.py'), str(src)],
                        capture_output=True, text=True)
if result.returncode != 0:
  sys.exit(f'nom Bluelium : ÉCHEC\n{result.stdout}{result.stderr}')
print(result.stdout.strip())
