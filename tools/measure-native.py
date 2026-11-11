#!/usr/bin/env python3
"""Échantillons natifs PIL. Usage : measure-native.py capture.png sortie.json.
Les captures Spectacle incluent l'ombre KWin : --crop x,y,w,h la retire.
Les couleurs sont celles de la capture, avec la gestion de couleurs du bureau.
"""
import argparse
import json
from collections import Counter
from pathlib import Path
from PIL import Image

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('image', type=Path)
p.add_argument('output', type=Path)
p.add_argument('--crop', default='16,10,1440,900')
a = p.parse_args()
x, y, w, h = map(int, a.crop.split(','))
im = Image.open(a.image).convert('RGB').crop((x, y, x+w, y+h))
result = {'source': str(a.image), 'crop': [x,y,w,h], 'size': [w,h], 'columns': {}}
for cx in [110, w-445, w-443, w-435, w-430, w-240, w-40, w-10]:
    runs = []
    previous = None
    for cy in range(75, 155):
        color = im.getpixel((cx,cy))
        if color != previous:
            runs.append({'y':cy, 'rgb':list(color)})
            previous=color
    result['columns'][str(cx)] = runs
result['samples'] = {f'{cx},{cy}':im.getpixel((cx,cy))
                     for cx,cy in [(200,2),(200,56),(1400,80),(1400,120),(1400,125),(1400,126)]}
a.output.write_text(json.dumps(result, indent=2)+'\n')
im.save(a.output.with_suffix('.png'))
