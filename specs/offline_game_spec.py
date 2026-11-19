"""Bluelium : « Paquet perdu », jeu original de la page hors ligne.

Remplace le jeu du dinosaure de Chromium sur la page « Aucune connexion
Internet » (et chrome://dino). Un paquet réseau file sur le câble et saute
par-dessus les pare-feu, puis les pigeons voyageurs (RFC 1149) à partir de 250
points. Espace, ↑ ou un clic pour sauter (maintenir pour sauter plus haut),
↓ pour redescendre. Couleurs : texte de la page et bleu Bluelium, clair ou
sombre selon la page ; « réduire les animations » respecté ; score annoncé
aux lecteurs d'écran. La politique qui désactive le dinosaure
(disabledEasterEgg) désactive aussi ce jeu.

Les sources du dinosaure restent compilées mais ne sont plus importées.
Source du jeu : reference/bluelium/packet_game.ts.
"""
from pathlib import Path

GAME = (Path(__file__).parent / 'reference/bluelium/packet_game.ts').read_text()
R = 'components/neterror/resources/'

NEW_FILES = {
  R + 'bluelium_game/packet_game.ts': GAME,
}

EDITS = [
  (R + 'BUILD.gn',
   '  "dino_game/utils.ts",\n',
   '  "dino_game/utils.ts",\n'
   '  "bluelium_game/packet_game.ts",  # Bluelium : jeu hors ligne\n'),
  (R + 'neterror.ts',
   "import {Runner} from './dino_game/offline.js';\n",
   "// Bluelium : « Paquet perdu » à la place du dinosaure.\n"
   "import {PacketGame} from './bluelium_game/packet_game.js';\n"),
  (R + 'neterror.ts',
   "      Runner.initializeInstance('.interstitial-wrapper');\n",
   "      PacketGame.initialize('.interstitial-wrapper');\n"),
  (R + 'neterror.css',
   '#offline-resources {\n',
   '/* Bluelium : jeu « Paquet perdu » à la place du dinosaure. */\n'
   '.bluelium-packet-game .icon-offline {\n'
   '  display: none;\n'
   '}\n'
   '\n'
   '.offline.bluelium-packet-game .interstitial-wrapper {\n'
   '  padding-top: 48px;\n'
   '}\n'
   '\n'
   '.offline .bluelium-packet {\n'
   '  border-radius: 8px;\n'
   '  color: var(--text-color);\n'
   '  height: 150px;\n'
   '  margin-bottom: 24px;\n'
   '  outline: none;\n'
   '}\n'
   '\n'
   '.offline .bluelium-packet:focus-visible {\n'
   '  outline: 2px solid var(--google-blue-300);\n'
   '  outline-offset: 4px;\n'
   '}\n'
   '\n'
   '.bluelium-packet-canvas {\n'
   '  display: block;\n'
   '  touch-action: manipulation;\n'
   '}\n'
   '\n'
   '#offline-resources {\n'),
]
