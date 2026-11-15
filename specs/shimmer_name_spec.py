"""Bluelium : le nom « Bluelium » dans Shimmer Tab, avec le logo de Helium.

- Logo avec le nom (option « wordmark » du nouvel onglet) : l'astérisque de
  Helium à l'identique, suivi de « Bluelium » en Instrument Sans (la police de
  Shimmer), à la hauteur de capitale du « Helium » d'origine.
- Libellé de cette option dans les réglages : « Bluelium ».
Restent « Helium » : le raccourci vers helium.computer et la mention « logo de
Helium » (c'est toujours son logo).
"""
from pathlib import Path

REF = Path(__file__).parent / 'reference'
OLD_WORDMARK = (REF / 'upstream/shimmer-wordmark-helium.svg').read_text()
NEW_WORDMARK = (REF / 'bluelium/shimmer-wordmark-bluelium.svg').read_text()

NEW_FILES = {}
EDITS = [
  ('third_party/shimmer/assets/index-kwRkEiyG.js',
   'Qr(`' + OLD_WORDMARK + '`)',
   'Qr(`' + NEW_WORDMARK + '`)'),
  ('third_party/shimmer/assets/Settings-BJLII9Xe.js',
   "label:n().chromeLogo?`Chrome`:`Helium`}",
   "label:n().chromeLogo?`Chrome`:`Bluelium`}"),
]
