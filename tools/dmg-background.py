#!/usr/bin/env python3
"""Bluelium : dessine le fond de la fenêtre du .dmg macOS.

Usage : dmg-background.py <navigateur Chromium> [dossier de sortie]

Rend une page HTML (logotype Bluelium, flèche, consigne) avec le navigateur
en mode headless, en 1x et 2x, puis assemble assets/dmg/background.tiff
(multi-résolution, net sur écran Retina). Les positions d'icônes doivent
rester celles de scripts/dmg-settings.py : appli (165, 205), Applications
(495, 205), fenêtre 660 × 400.
"""
import base64
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
W, H = 660, 400
APP_X, APPS_X, ICON_Y = 165, 495, 205

wordmark = (REPO / 'specs/reference/bluelium/shimmer-wordmark-bluelium.svg').read_text()
wordmark = wordmark.replace('<svg ', '<svg class="mark" ', 1)
font = base64.b64encode((REPO / 'assets/InstrumentSans.ttf').read_bytes()).decode()

HTML = f"""<!doctype html><meta charset="utf-8">
<style>
@font-face {{ font-family: Instrument; src: url(data:font/ttf;base64,{font}); }}
html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; }}
body {{
  font-family: Instrument, sans-serif;
  background:
    radial-gradient(420px 260px at 18% 0%, #dfe8ff 0%, transparent 70%),
    radial-gradient(380px 260px at 100% 100%, #e9e2ff 0%, transparent 70%),
    linear-gradient(180deg, #f8faff 0%, #f1f4fb 100%);
  position: relative;
}}
.grain {{
  position: absolute; inset: 0;
  background-image: radial-gradient(#3b5bdb14 1px, transparent 1px);
  background-size: 14px 14px;
  -webkit-mask-image: radial-gradient(70% 80% at 50% 55%, #000 0%, transparent 85%);
}}
.mark {{ position: absolute; left: 50%; top: 34px; height: 30px; width: auto;
  transform: translateX(-50%); color: #1c2340; }}
.halo {{ position: absolute; width: 168px; height: 192px; border-radius: 36px;
  top: {ICON_Y - 80}px; background: #ffffffb8;
  box-shadow: 0 1px 0 #fff inset, 0 10px 30px -12px #3b4a8a40, 0 0 0 1px #3b4a8a12; }}
.arrow {{ position: absolute; left: {APP_X + 92}px; top: {ICON_Y - 30}px; }}
.hint {{ position: absolute; left: 0; right: 0; bottom: 30px; text-align: center;
  font-size: 13px; letter-spacing: .01em; color: #59607a; }}
.hint b {{ color: #1c2340; font-weight: 600; }}
</style>
<div class="grain"></div>
{wordmark}
<div class="halo" style="left:{APP_X - 84}px"></div>
<div class="halo" style="left:{APPS_X - 84}px"></div>
<svg class="arrow" width="{APPS_X - APP_X - 184}" height="48" viewBox="0 0 146 48" fill="none">
  <defs><linearGradient id="a" x1="0" x2="1"><stop offset="0" stop-color="#7c8cff" stop-opacity=".25"/>
  <stop offset="1" stop-color="#4c5fe8"/></linearGradient></defs>
  <path d="M6 30 C 40 6, 96 6, 132 26" stroke="url(#a)" stroke-width="3"
        stroke-linecap="round" stroke-dasharray="1 8"/>
  <path d="M121 15 L133 26 L118 32" stroke="#4c5fe8" stroke-width="3"
        stroke-linecap="round" stroke-linejoin="round"/>
</svg>
<div class="hint">Glissez <b>Bluelium</b> dans <b>Applications</b> pour l’installer</div>
"""


def main():
  browser = sys.argv[1]
  out = Path(sys.argv[2]) if len(sys.argv) > 2 else REPO / 'assets/dmg'
  out.mkdir(parents=True, exist_ok=True)
  with tempfile.TemporaryDirectory() as tmp:
    page = Path(tmp) / 'bg.html'
    page.write_text(HTML)
    pngs = []
    for scale in (1, 2):
      png = Path(tmp) / f'bg{scale}.png'
      subprocess.run([browser, '--headless=new', '--disable-gpu', '--hide-scrollbars',
                      f'--user-data-dir={tmp}/profile', '--no-first-run',
                      f'--force-device-scale-factor={scale}',
                      f'--window-size={W},{H}', f'--screenshot={png}', page.as_uri()],
                     check=True, capture_output=True)
      # Les PNG doivent annoncer 72 dpi (1x) et 144 dpi (2x) pour tiffutil.
      subprocess.run(['sips', '-s', 'dpiWidth', str(72 * scale), '-s', 'dpiHeight',
                      str(72 * scale), str(png)], check=True, capture_output=True)
      pngs.append(png)
      (out / f'background{"@2x" if scale == 2 else ""}.png').write_bytes(png.read_bytes())
    subprocess.run(['tiffutil', '-cathidpicheck', *map(str, pngs), '-out',
                    str(out / 'background.tiff')], check=True, capture_output=True)
  print(f'Fond du .dmg : {out / "background.tiff"}')


if __name__ == '__main__':
  main()
