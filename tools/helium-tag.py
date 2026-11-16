#!/usr/bin/env python3
"""Bluelium : quelle version de Helium construire, et rappel des nouvelles.

Règle : on ne suit que les versions MAJEURES de Helium (0.21 -> 0.22, qui
correspondent aux versions majeures de Chromium). Les petites versions
(0.21.2.1 -> 0.21.3.1) obligeraient à tout recompiler pour peu de chose :
on les ignore. Les pré-versions (pre-release GitHub) ne comptent pas.

  helium-tag.py choose <dépôt> [version actuelle]
      Affiche la version à construire : la version actuelle si la dernière
      version stable de <dépôt> a la même majeure, sinon cette dernière
      version stable. Sans version actuelle : la dernière version stable.
      Si GitHub ne répond pas, garde la version actuelle.

  helium-tag.py next-major <dépôt>
      Version à TESTER (pas à publier) : la plus récente de <dépôt>,
      pré-versions comprises, dont la version majeure dépasse celle de la
      dernière release Bluelium Linux. Rien si aucune. Utilisé par
      .github/workflows/veille-helium.yml.

  helium-tag.py check
      Rappel : compare les dernières releases Bluelium (Linux et macOS) aux
      versions stables de helium-linux et helium-macos. Affiche une ligne par
      nouvelle version majeure à construire (rien si tout est à jour) et
      signale les pré-versions majeures annoncées.

Exemple : python3 tools/helium-tag.py choose imputnet/helium-macos 0.21.2.1
"""
import json
import re
import sys
import urllib.request

BLUELIUM = 'matthieuleconte1/bluelium'
TAG_RE = re.compile(r'^v?(\d+(?:\.\d+)+)')


def releases(repo):
    req = urllib.request.Request(
        f'https://api.github.com/repos/{repo}/releases?per_page=50',
        headers={'Accept': 'application/vnd.github+json',
                 'User-Agent': 'bluelium-build'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return [x for x in json.load(r) if not x.get('draft')]


def version(tag):
    m = TAG_RE.match(tag or '')
    return tuple(int(n) for n in m.group(1).split('.')) if m else None


def major(tag):
    v = version(tag)
    return v[:2] if v else None


def newest(rels, prerelease=False):
    tags = [r['tag_name'] for r in rels
            if bool(r.get('prerelease')) == prerelease and version(r['tag_name'])]
    return max(tags, key=version, default=None)


def choose(repo, current):
    try:
        stable = newest(releases(repo))
    except Exception as e:  # réseau, quota GitHub…
        if current:
            print(f'helium-tag : GitHub injoignable ({e}), on garde {current}',
                  file=sys.stderr)
            return current
        raise SystemExit(f'helium-tag : GitHub injoignable ({e})')
    if not stable:
        return current or sys.exit(f'helium-tag : aucune version stable sur {repo}')
    if current and major(current) and major(stable) <= major(current):
        return current
    return stable


def built(ours, is_mac):
    """Version de Helium de la dernière release Bluelium (Linux ou macOS)."""
    mine = [r['tag_name'] for r in ours
            if r['tag_name'].endswith('-macos') == is_mac
            and version(r['tag_name'])]
    last = max(mine, key=version, default=None)
    return TAG_RE.match(last).group(1) if last else None


def next_major(repo):
    cur = built(releases(BLUELIUM), is_mac=False)
    tags = [r['tag_name'] for r in releases(repo) if version(r['tag_name'])]
    if cur:
        tags = [t for t in tags if major(t) > major(cur)]
    return max(tags, key=version, default='')


def check():
    ours = releases(BLUELIUM)
    lines = []
    for label, repo, is_mac in (('Linux', 'imputnet/helium-linux', False),
                                ('macOS', 'imputnet/helium-macos', True)):
        built_v = built(ours, is_mac)
        rels = releases(repo)
        stable, pre = newest(rels), newest(rels, prerelease=True)
        if stable and (not built_v or major(stable) > major(built_v)):
            lines.append(f'{label} : Helium {stable} (nouvelle version majeure) '
                         f'est sortie, Bluelium est sur {built_v or "?"}. '
                         f'À construire.')
        elif pre and built_v and major(pre) > major(built_v) \
                and (not stable or version(pre) > version(stable)):
            lines.append(f'{label} : Helium {pre} est annoncée en pré-version '
                         f'(Bluelium sur {built_v}). Rien à faire avant la '
                         f'version stable.')
    return lines


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == 'choose':
        print(choose(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ''))
    elif len(sys.argv) == 3 and sys.argv[1] == 'next-major':
        print(next_major(sys.argv[2]))
    elif sys.argv[1:] == ['check']:
        print('\n'.join(check()))
    else:
        sys.exit(__doc__)
