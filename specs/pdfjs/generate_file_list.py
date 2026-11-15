# Bluelium : embarquer le lecteur, ses traductions, décodeurs, polices et licences.
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
files = sorted(p.relative_to(root).as_posix() for p in root.rglob('*')
               if p.is_file() and (p.parts[len(root.parts)] in ('build', 'web')
                                  or p.name in ('LICENSE', 'README.chromium')))
expected = (root / 'files.txt').read_text().splitlines()
if files != expected:
    raise SystemExit('Inventaire PDF.js different de files.txt : verifier la distribution figee.')
if len(sys.argv) == 2:
    print('\n'.join(files))
else:
    Path(sys.argv[2]).write_text(json.dumps({'base_dir': str(root), 'files': files}))
