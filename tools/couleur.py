#!/usr/bin/env python3
"""Bluelium : nom de couleur de la série de patchs, pour le numéro de version.

Usage : couleur.py [dépôt] [--serie | --nom | --teinte]

La version Bluelium est « <version Helium>-<couleur> », par exemple
0.22.5.1-cinabre. La couleur est tirée du dernier commit qui touche la série
(SERIE_PATHS) : mêmes patchs, même couleur, sur macOS comme sous Linux.
Une nouvelle série change de couleur ; deux séries peuvent tomber sur la même
(une chance sur le nombre de couleurs), l'auto-build Linux le signale.

Sans option : l'identifiant (« cinabre »). --serie : le commit court de la
série. --nom : le nom affiché (« Cinabre »). --teinte : le code (#DB1702).
Liste : tools/couleurs.tsv, tirée de Wikipédia.
"""
import subprocess
import sys
from pathlib import Path

SERIE_PATHS = ['specs', 'patches', 'downloads.ini', 'tools/apply_spec.py',
               'tools/apply-series.py', 'tools/rename-product.py']


def couleurs():
  lines = (Path(__file__).with_name('couleurs.tsv')).read_text().splitlines()
  return [l.split('\t') for l in lines if l and not l.startswith('#')]


def serie(repo):
  out = subprocess.run(['git', '-C', str(repo), 'log', '-1', '--format=%H', '--', *SERIE_PATHS],
                       capture_output=True, text=True, check=True).stdout.strip()
  if not out:
    sys.exit('couleur : aucun commit de la série (dépôt superficiel ?)')
  return out


def main():
  args = [a for a in sys.argv[1:] if not a.startswith('--')]
  repo = Path(args[0]) if args else Path(__file__).resolve().parent.parent
  commit = serie(repo)
  table = couleurs()
  slug, nom, teinte = table[int(commit, 16) % len(table)]
  if '--serie' in sys.argv:
    print(commit[:7])
  elif '--nom' in sys.argv:
    print(nom)
  elif '--teinte' in sys.argv:
    print(teinte)
  else:
    print(slug)


if __name__ == '__main__':
  main()
