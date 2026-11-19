"""Fournit la police et sa licence aux cibles GN des deux plateformes."""
from base64 import b64encode
from pathlib import Path
from textwrap import fill

ASSETS = Path(__file__).resolve().parent.parent / 'assets'
FONT = 'third_party/bluelium_instrument_sans/'

# NEW_FILES écrit du texte. GN décode la police originale dans gen/ avant de
# l'ajouter aux ressources de l'application.
NEW_FILES = {
    FONT + 'InstrumentSans.ttf.base64':
        fill(b64encode((ASSETS / 'InstrumentSans.ttf').read_bytes()).decode('ascii'),
             width=76) + '\n',
    FONT + 'OFL-InstrumentSans.txt': (ASSETS / 'OFL-InstrumentSans.txt').read_text(),
    FONT + 'BUILD.gn': '''action("decode_font") {
  script = "decode_font.py"
  inputs = [ "InstrumentSans.ttf.base64" ]
  outputs = [ "$target_gen_dir/InstrumentSans.ttf" ]
  args = rebase_path(inputs + outputs, root_build_dir)
}
''',
    FONT + 'decode_font.py': '''"""Reconstitue le TTF original à partir de l'entrée texte de la spec."""
import base64
import sys
from pathlib import Path

source, output = map(Path, sys.argv[1:])
output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(base64.b64decode(b"".join(source.read_bytes().split()),
                                    validate=True))
''',
}
