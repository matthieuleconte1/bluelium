#!/usr/bin/env python3
"""Diagnostiquer les hôtes Chrome/Chromium ; --link crée des liens sans écraser.
Les manifestes conservent leurs allowed_origins et leur exécutable d'origine.
"""
import argparse
import json
import os
from pathlib import Path


def inspect(config, target, link=False):
    sources = [config / 'google-chrome/NativeMessagingHosts',
               config / 'chromium/NativeMessagingHosts',
               Path('/etc/chromium/native-messaging-hosts'),
               Path('/etc/opt/chrome/native-messaging-hosts')]
    found = []
    for folder in [target, *sources]:
        for path in sorted(folder.glob('*.json')):
            try:
                data = json.loads(path.read_text())
                executable = Path(data.get('path', ''))
                valid = (data.get('name') == path.stem and data.get('type') == 'stdio'
                         and executable.is_absolute() and executable.is_file()
                         and os.access(executable, os.X_OK)
                         and bool(data.get('allowed_origins')))
                row = {'manifest': str(path), 'name': data.get('name'),
                       'executable_available': valid}
                if link and valid and folder != target:
                    target.mkdir(parents=True, exist_ok=True)
                    destination = target / path.name
                    # lexists includes broken symlinks: never overwrite them.
                    if not os.path.lexists(destination):
                        destination.symlink_to(path.absolute())
                        row['linked'] = str(destination)
                found.append(row)
            except (OSError, ValueError, TypeError) as exc:
                found.append({'manifest': str(path), 'error': str(exc)})
    names = {row.get('name') for row in found}
    return {'hosts': found, 'claude_present':
            'com.anthropic.claude_code_browser_extension' in names,
            'codex_present': 'com.openai.codexextension' in names}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--link', action='store_true')
    parser.add_argument('--config', type=Path,
                        default=Path(os.getenv('XDG_CONFIG_HOME', Path.home() / '.config')))
    parser.add_argument('--target', type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect(args.config, args.target or args.config / 'helium-glyphe/NativeMessagingHosts',
                             args.link), indent=2, ensure_ascii=False))
