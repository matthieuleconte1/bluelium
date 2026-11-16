#!/usr/bin/env python3
"""Diagnostiquer Claude/Codex sous macOS/Linux ; --link installe leurs manifestes.
Lecture seule par défaut. Les liens conservent path et allowed_origins ; aucun
profil d'un autre navigateur n'est créé pour tromper la détection des clients.
"""
import argparse
import json
import os
import sys
from pathlib import Path

HOSTS = {
    'com.anthropic.claude_code_browser_extension':
        {'chrome-extension://fcoeoabgfenejglbffodgkkbkcdhcgfn/'},
    'com.openai.codexextension': {
        'chrome-extension://hehggadaopoacecdllhhajmbjkdcmajg/',
        'chrome-extension://odlomjlbamekndcpllcnffbgeohgkmjh/'},
}


def locations(home, config, platform):
    if platform == 'mac':
        support = home / 'Library/Application Support'
        return (support / 'Bluelium/NativeMessagingHosts', [
            support / 'Google/Chrome/NativeMessagingHosts',
            support / 'Chromium/NativeMessagingHosts',
            support / 'net.imput.helium/NativeMessagingHosts',
            Path('/Library/Google/Chrome/NativeMessagingHosts'),
            Path('/Library/Application Support/Chromium/NativeMessagingHosts')])
    chrome_config = Path(os.getenv('CHROME_CONFIG_HOME', config))
    return (config / 'bluelium/NativeMessagingHosts', [
        chrome_config / 'google-chrome/NativeMessagingHosts',
        config / 'chromium/NativeMessagingHosts',
        config / 'net.imput.helium/NativeMessagingHosts',
        config / 'helium-glyphe/NativeMessagingHosts',
        Path('/etc/chromium/native-messaging-hosts'),
        Path('/etc/opt/chrome/native-messaging-hosts')])


def validate(path):
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError('le manifeste doit être un objet JSON')
    name = data.get('name')
    if not isinstance(name, str) or name not in HOSTS or path.name != name + '.json':
        raise ValueError('nom de manifeste Claude/Codex attendu')
    executable = data.get('path')
    origins = data.get('allowed_origins')
    if not isinstance(executable, str) or not Path(executable).is_absolute():
        raise ValueError('path doit être absolu')
    if (data.get('type') != 'stdio' or not isinstance(origins, list) or
            not all(isinstance(item, str) for item in origins) or
            not HOSTS[name].intersection(origins) or
            any('*' in item for item in origins)):
        raise ValueError('type stdio et origine officielle explicite requis')
    if not Path(executable).is_file() or not os.access(executable, os.X_OK):
        raise ValueError('exécutable absent ou non exécutable')
    return data


def inspect(config, target=None, link=False, *, home=None, platform=None, manifests=()):
    home = home or Path.home()
    platform = platform or ('mac' if sys.platform == 'darwin' else 'linux')
    default, sources = locations(home, config, platform)
    target = target or default
    candidates = [*manifests]
    for folder in [target, *sources]:
        candidates.extend(folder / (name + '.json') for name in HOSTS
                          if os.path.lexists(folder / (name + '.json')))
    found, seen = [], set()
    for path in candidates:
        path = path.absolute()
        if path in seen:
            continue
        seen.add(path)
        row = {'manifest': str(path), 'name': path.stem, 'valid': False}
        try:
            data = validate(path)
            row.update(valid=True, executable_available=True)
            if link and path.parent != target.absolute():
                target.mkdir(parents=True, exist_ok=True)
                destination = target / path.name
                # La création atomique échoue aussi pour un lien cassé existant.
                try:
                    destination.symlink_to(path)
                    row['linked'] = str(destination)
                except FileExistsError:
                    row['destination_exists'] = str(destination)
            row['allowed_origins'] = data['allowed_origins']
        except (OSError, ValueError, TypeError) as exc:
            row['error'] = str(exc)
        found.append(row)
    # "present" signifie utilisable DEPUIS la cible, pas simplement vu ailleurs.
    usable = set()
    for name in HOSTS:
        try:
            validate(target / (name + '.json'))
            usable.add(name)
        except (OSError, ValueError, TypeError):
            pass
    return {'platform': platform, 'target': str(target), 'hosts': found,
            'claude_present': 'com.anthropic.claude_code_browser_extension' in usable,
            'codex_present': 'com.openai.codexextension' in usable,
            'external_browser_detection': 'Bluelium absent des listes inspectées ; '
                'les manifestes ne corrigent pas la détection de profils/processus.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--link', action='store_true')
    parser.add_argument('--platform', choices=['mac', 'linux'],
                        default='mac' if sys.platform == 'darwin' else 'linux')
    parser.add_argument('--home', type=Path, default=Path.home(),
                        help='racine utilisateur, notamment pour les tests isolés')
    parser.add_argument('--config', type=Path)
    parser.add_argument('--target', type=Path, help='NativeMessagingHosts du profil visé')
    parser.add_argument('--manifest', type=Path, action='append', default=[],
                        help='manifeste officiel existant (répétable)')
    args = parser.parse_args()
    config = args.config or Path(os.getenv('XDG_CONFIG_HOME', args.home / '.config'))
    print(json.dumps(inspect(config, args.target, args.link, home=args.home,
                            platform=args.platform, manifests=args.manifest),
                     indent=2, ensure_ascii=False))
