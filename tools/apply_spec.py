#!/usr/bin/env python3
"""Applique une spécification de patch Glyphe dans build/src et écrit le .patch.

Usage : apply_spec.py <src> <spec.py> <patch_out>
La spec définit NEW_FILES = {chemin: contenu} et EDITS = [(chemin, ancien, nouveau)].
Idempotent : une modification déjà présente est ignorée.
Une édition peut porter un 4e élément, un texte qui signale que Helium fait
déjà la même chose : s'il est dans le fichier et que l'ancien motif n'y est
plus, l'édition est sautée (la spec vaut ainsi avant et après le changement
de Helium).
Lit et écrit en UTF-8 avec des fins de ligne LF, sur Windows comme ailleurs.
"""
import difflib
import runpy
import sys
from pathlib import Path

src, spec_path, patch_out = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
spec = runpy.run_path(spec_path)
new_files = spec.get('NEW_FILES', {})
edits = [(e[0], e[1], e[2], e[3] if len(e) > 3 else None) for e in spec.get('EDITS', [])]

originals = {}
current = {}
skipped = set()
for index, (path, old, new, upstream) in enumerate(edits):
  if new in old:
    sys.exit(f'ERREUR : le remplacement est contenu dans le motif dans {path} '
             f'(serait pris pour déjà appliqué) ; ajouter un commentaire.\n{old[:200]}')
  if not new:
    sys.exit(f'ERREUR : remplacement vide dans {path} (jamais appliqué) ; '
             f'utiliser un commentaire.\n{old[:200]}')
  # Tout se fait en mémoire : rien n'est écrit si une édition échoue (une
  # application partielle laissait des doublons à la relance).
  text = current.get(path)
  if text is None:
    text = (src / path).read_text(encoding='utf-8')
    originals[path] = text
  if new in text:
    current[path] = text
    continue
  if upstream and upstream in text and old not in text:
    print(f'Déjà dans Helium, sauté : {path}')
    current[path] = text
    skipped.add(index)
    continue
  if text.count(old) != 1:
    sys.exit(f'ERREUR : motif introuvable ou ambigu ({text.count(old)}) dans {path} '
             f'(aucun fichier modifié) :\n{old[:200]}')
  current[path] = text.replace(old, new, 1)

for path, text in current.items():
  if text != originals[path]:
    (src / path).write_text(text, encoding='utf-8', newline='\n')

for path, content in new_files.items():
  (src / path).parent.mkdir(parents=True, exist_ok=True)
  (src / path).write_text(content, encoding='utf-8', newline='\n')

out = []
for path, content in new_files.items():
  out += difflib.unified_diff([], content.splitlines(True), '/dev/null', 'b/' + path, n=3)
for path in dict.fromkeys(p for p, _, _, _ in edits):
  before = originals[path]
  for index, (p2, old, new, _) in enumerate(edits):
    if p2 == path and index not in skipped and new in before:
      before = before.replace(new, old, 1)
  after = (src / path).read_text(encoding='utf-8')
  out += difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                              'a/' + path, 'b/' + path, n=3)
Path(patch_out).write_text(''.join(out), encoding='utf-8', newline='\n')
print('OK', patch_out, len(new_files) + len(dict.fromkeys(p for p, _, _, _ in edits)), 'fichiers')
