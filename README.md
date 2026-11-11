# Bluelium

Navigateur personnel construit sur [Helium](https://github.com/imputnet/helium)
(Chromium) : interface Prism plus serrée, onglet IA dans le panneau latéral,
couleur de la page dans la barre, mode nuit rouge, vue divisée en un seul
onglet, nouvel onglet Shimmer natif.

> **Fork non officiel.** Bluelium n'est ni affilié à imputnet ni soutenu par
> l'équipe de Helium. Les problèmes de Bluelium se signalent ici, pas sur le
> dépôt de Helium.

État détaillé, fait et à faire : [AVANCEMENT.md](AVANCEMENT.md) (le code
interne et les patchs portent encore le nom de travail « Glyphe »).

## Installer (Linux x86_64)

1. Télécharger la dernière archive `bluelium-*.tar.zst` des
   [releases](../../releases/latest), vérifier son `.sha256`, puis :
   ```sh
   mkdir -p ~/Applications && tar --zstd -xf bluelium-*.tar.zst -C ~/Applications
   mv ~/Applications/bluelium-* ~/Applications/helium-glyphe
   ~/Applications/helium-glyphe/helium-wrapper --user-data-dir="$HOME/.config/helium-glyphe"
   ```
2. Mise à jour automatique (minuteur systemd utilisateur, toutes les 2 h) :
   ```sh
   autobuild/install-updater.sh
   ```
   `glyphe-update` lit la dernière release GitHub, vérifie le SHA-256 et
   installe la nouvelle version dès que Bluelium est fermé (sinon au prochain
   lancement, par `helium-wrapper`). La version précédente reste dans
   `~/Applications/helium-glyphe.previous`.

## Comment les versions sont produites

La machine de build vérifie chaque nuit la dernière version publiée de
[helium-linux](https://github.com/imputnet/helium-linux). À chaque nouvelle
version de Helium, ou quand les patchs Bluelium changent, elle reconstruit
tout (avec PGO), puis publie une release `v<helium>-g<patchs>`
([autobuild/autobuild.sh](autobuild/autobuild.sh)).

| Dossier | Contenu |
|---|---|
| `patches/glyphe/` | Les patchs Bluelium, au format de Helium (`patches/series` donne l'ordre) |
| `patches/series` | Série complète de helium-linux, patchs Bluelium en fin de liste |
| `downloads.ini` | Sources téléchargées en plus (Shimmer Tab, sha256 vérifié) |
| `specs/` | Spécifications Python qui génèrent chaque patch (sources de vérité) |
| `specs/glyphe_night.js` | Convertisseur de pages « nuit rouge », injecté par le navigateur |
| `tools/apply_spec.py` | Applique une spec dans `build/src` et écrit le `.patch` |
| `tools/respec.py` | Met à jour un arbre déjà patché quand une spec change |
| `tools/bench.ts` | Banc d'essai (Speedometer 3.1, démarrage, mémoire) contre un autre binaire |
| `autobuild/` | Auto-build, publication des releases et mise à jour du PC |
| `scripts/` | `build-helium.sh` (build complet avec PGO), `dev-build.sh` (incrémental) |

## Construire soi-même

Il faut une machine Linux capable de compiler Chromium (≈ 250 Go, 32 Go de
RAM ou plus). Partir de [helium-linux](https://github.com/imputnet/helium-linux),
copier `patches/glyphe/` dans ses `patches/`, ajouter les lignes `glyphe/…` de
`patches/series` à la fin de sa série et les sections en plus de
`downloads.ini`, puis suivre sa procédure de build.

Avec une machine de build accessible en SSH, `tools/sync-builder.sh --now`
envoie les patchs et lance l'auto-build. L'hôte se règle dans
`~/.config/bluelium/builder.env` (non versionné) :

```sh
BLUELIUM_BUILDER=root@ma-machine-de-build
BLUELIUM_JUMP=root@rebond      # facultatif
```

Pour publier les releases, la machine de build lit `GH_TOKEN` (jeton GitHub
limité à ce dépôt, droit « Contents: write ») dans `/root/glyphe/github.env`.

## Licences

- Bluelium est distribué sous **GPL-3.0** ([LICENSE](LICENSE)), comme Helium.
  Les parties issues d'ungoogled-chromium restent sous leur licence BSD
  ([LICENSE.ungoogled_chromium](LICENSE.ungoogled_chromium)), Chromium sous
  ses propres licences.
- [Shimmer Tab](https://github.com/dmitthedazed/shimmer-tab) : GPL-3.0.
- Instrument Sans : SIL Open Font License ([assets/OFL-InstrumentSans.txt](assets/OFL-InstrumentSans.txt)).
- Contours Material Symbols : Apache 2.0 ([assets/icons/MATERIAL_SYMBOLS_SOURCE.md](assets/icons/MATERIAL_SYMBOLS_SOURCE.md)).
- Les noms et logos Helium, Claude, ChatGPT, Gemini et Le Chat appartiennent à
  leurs propriétaires ; les logos des assistants servent seulement à
  identifier le service dans l'interface. Voir [NOTICE.md](NOTICE.md).
