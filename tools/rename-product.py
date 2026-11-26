#!/usr/bin/env python3
"""Bluelium : remplace le nom « Helium » par « Bluelium » dans les textes affichés.

Usage : rename-product.py <src>

Même méthode que utils/name_substitution.py de Helium (GPL-3.0), un cran plus
loin : réécrit les messages des fichiers .grd/.grdp, recalcule leur empreinte
GRIT, puis met à jour les traductions .xtb (texte et identifiant). Le logo de
Helium est conservé ; seul le nom change.

Restent « Helium » : les messages de copyright (« The Helium Authors ») qui
créditent l'équipe de Helium, et tout ce qui n'est pas un mot entier (adresses
helium.computer, identifiants en minuscules). Idempotent : « Bluelium » ne
contient pas le mot « Helium ».
Les adresses internes helium:// deviennent bluelium:// (voir
specs/bluelium_scheme_spec.py).
"""
import os
import re
import sys
import xml.etree.ElementTree as xml
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

NAME = re.compile(r'\bHelium\b')
# Adresses internes : helium://settings → bluelium://settings.
SCHEME = re.compile(r'\bhelium://')


def has_name(text):
  return bool(NAME.search(text) or SCHEME.search(text))


def rename(text):
  return SCHEME.sub('bluelium://', NAME.sub('Bluelium', text))
# Messages laissés tels quels (crédits de l'équipe Helium).
KEEP = re.compile(r'Helium (Authors|Projects)')
IGNORE_DIRS = {'.pc', 'chromeos', 'remoting', 'ash', 'testdata', 'out'}


def add_grit(tree):
  sys.path.insert(0, str(tree / 'tools' / 'grit'))


def message_text(message):
  text = message.text or ''
  for elem in message.findall('ph'):
    text += elem.get('name').upper() + (elem.tail or '')
  text = text.strip()
  if text.startswith("'''"):
    text = text[3:]
  if text.endswith("'''"):
    text = text[:-3]
  return text.strip()


def fingerprint(message):
  import grit.extern.tclib  # pylint: disable=import-outside-toplevel,import-error
  return grit.extern.tclib.GenerateMessageId(message_text(message),
                                             message.get('meaning', ''))


def full_text(elem):
  return ''.join(elem.itertext())


def replace_in(elem, is_root=True):
  changed = False
  if elem.text and has_name(elem.text):
    elem.text = rename(elem.text)
    changed = True
  if not is_root and elem.tail and has_name(elem.tail):
    elem.tail = rename(elem.tail)
    changed = True
  for child in elem:
    # Les exemples de traducteur (<ex>) n'apparaissent jamais à l'écran.
    if child.tag == 'ex':
      continue
    changed |= replace_in(child, is_root=False)
  return changed


def write_xml(path, original, root):
  # Garde l'en-tête d'origine (déclaration XML, commentaires) tel quel :
  # l'accueil de Helium lit son .grdp avec un analyseur qui veut <grit-part>
  # en premier nœud.
  start = re.search(rf'<{re.escape(root.tag)}[\s>]', original).start()
  body = xml.tostring(root, encoding='unicode')
  path.write_text(original[:start] + body.replace('!!dollar!!', '&#36;') + '\n',
                  encoding='utf-8', newline='\n')


def parser():
  return xml.XMLParser(target=xml.TreeBuilder(insert_comments=True))


def files(tree, exts):
  for root, dirs, names in os.walk(tree):
    dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
    for name in names:
      if not name.startswith('.') and name.rsplit('.', 1)[-1].lower() in exts:
        yield Path(root) / name


def do_grit(args):
  path, tree = args
  add_grit(tree)
  text = path.read_text(encoding='utf-8')
  if not has_name(text):
    return {}, set()
  root = xml.fromstring(text.replace('&#36;', '!!dollar!!'), parser())
  fp_map, kept, changed = {}, set(), False
  for message in root.iter('message'):
    if not has_name(full_text(message)):
      continue
    old = fingerprint(message)
    if KEEP.search(full_text(message)):
      kept.add(old)
      continue
    if replace_in(message):
      changed = True
      # Le contenu des <ph> (liens helium://) ne compte pas dans l'empreinte.
      new = fingerprint(message)
      if new != old:
        fp_map[old] = new
  if changed:
    write_xml(path, text, root)
  return fp_map, kept


def do_xtb(args):
  path, fp_map, kept = args
  text = path.read_text(encoding='utf-8')
  if not has_name(text):
    return 0
  root = xml.fromstring(text.replace('&#36;', '!!dollar!!'), parser())
  changed, seen = 0, set()
  for tr in root.iter('translation'):
    tid = tr.get('id')
    if tid not in kept and replace_in(tr):
      changed += 1
      tr.set('id', fp_map.get(tid, tid))
    # Deux messages devenus identiques : décaler l'identifiant, comme Helium.
    tid = tr.get('id')
    while tid in seen and tid.isdigit():
      tid = str(int(tid) + 1)
    tr.set('id', tid)
    seen.add(tid)
  if changed:
    write_xml(path, text, root)
  return changed


def main():
  tree = Path(sys.argv[1]).resolve()
  if not (tree / 'OWNERS').exists():
    sys.exit(f'{tree} n\'est pas un arbre Chromium')
  for sample, expected in (('Customize Helium', 'Customize Bluelium'),
                           ("Helium's", "Bluelium's"), ('helium.computer', 'helium.computer'),
                           ('Bluelium', 'Bluelium'), ('HeliumX', 'HeliumX')):
    assert rename(sample) == expected, sample
  assert rename('helium://settings') == 'bluelium://settings'
  workers = os.cpu_count() or 4
  with ProcessPoolExecutor(workers) as pool:
    results = list(pool.map(do_grit, [(p, tree) for p in files(tree, {'grd', 'grdp'})]))
  fp_map, kept = {}, set()
  for m, k in results:
    fp_map.update(m)
    kept |= k
  with ProcessPoolExecutor(workers) as pool:
    counts = list(pool.map(do_xtb, [(p, fp_map, kept) for p in files(tree, {'xtb'})]))
  print(f'Nom Bluelium : {len(fp_map)} messages, {sum(counts)} traductions '
        f'({len(kept)} crédits Helium gardés)')


if __name__ == '__main__':
  main()
