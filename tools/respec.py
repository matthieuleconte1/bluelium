#!/usr/bin/env python3
"""Met à jour un arbre déjà patché quand une spec change.

Usage : respec.py <src> <ancienne_spec.py> <nouvelle_spec.py>

apply_spec.py cherche le texte d'origine (« old ») : une fois la spec
appliquée, changer son « new » ne peut plus s'appliquer. Ici, pour chaque
édition (même chemin, même rang), l'ancien « new » présent dans l'arbre est
remplacé par le nouveau ; les NEW_FILES sont réécrits. Ensuite, relancer
apply_spec.py avec la nouvelle spec pour régénérer le .patch.
"""
import runpy
import sys
from collections import defaultdict
from pathlib import Path

src, old_path, new_path = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
old, new = runpy.run_path(old_path), runpy.run_path(new_path)

for path, content in new.get('NEW_FILES', {}).items():
  (src / path).parent.mkdir(parents=True, exist_ok=True)
  (src / path).write_text(content)


def by_path(edits):
  groups = defaultdict(list)
  for path, before, after in edits:
    groups[path].append((before, after))
  return groups


old_edits, new_edits = by_path(old.get('EDITS', [])), by_path(new.get('EDITS', []))
for path in new_edits:
  if len(old_edits.get(path, [])) > len(new_edits[path]):
    sys.exit(f'ERREUR : éditions retirées pour {path} ; mettre à jour à la main.')
  text = (src / path).read_text()
  for (_, prev), (_, cur) in zip(old_edits[path], new_edits[path]):
    if prev == cur or cur in text:
      continue
    if text.count(prev) != 1:
      sys.exit(f'ERREUR : ancien remplacement introuvable ou ambigu dans {path} :\n{prev[:200]}')
    text = text.replace(prev, cur, 1)
    print(f'mis à jour : {path}')
  # Éditions ajoutées à la fin : appliquées normalement par apply_spec.py.
  (src / path).write_text(text)
