"""Bluelium : Shimmer Tab en français.

Shimmer 1.3.0 choisit sa langue d'après le navigateur (navigator.languages)
parmi les locales embarquées, mais n'embarque que l'anglais. On ajoute la
locale « fr » au même tableau : l'interface et les messages d'accueil passent
en français quand le navigateur est en français, et restent en anglais sinon.
Une clé absente de fr.json retombe sur l'anglais (comportement de Shimmer).

La traduction est dans reference/shimmer/fr.json, aux clés de
helium-newtab/src/locales/en.json (identiques en 1.3.0).
"""
import json
from pathlib import Path

FR = json.loads((Path(__file__).parent / 'reference/shimmer/fr.json').read_text())

NEW_FILES = {}
EDITS = [
  ('third_party/shimmer/assets/index-kwRkEiyG.js',
   'io=Object.assign({"./locales/en.json":ro});',
   'io=Object.assign({"./locales/en.json":ro,'
   '"./locales/fr.json":' + json.dumps(FR, ensure_ascii=False, separators=(',', ':')) + '});'),
]
