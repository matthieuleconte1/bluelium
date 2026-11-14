<p align="center">
  <img src="docs/bluelium-header.svg" alt="Schéma de la fenêtre Bluelium : onglets, barre d'adresse, page et panneau IA" width="820">
</p>

<h1 align="center">Bluelium</h1>

<p align="center">
  Un navigateur personnel : <a href="https://github.com/imputnet/helium">Helium</a>, avec une autre interface.
</p>

<p align="center">
  <img alt="macOS Apple Silicon" src="https://img.shields.io/badge/macOS-Apple%20Silicon-3450d1?style=flat-square">
  <img alt="Linux x86_64" src="https://img.shields.io/badge/Linux-x86__64-3450d1?style=flat-square">
  <img alt="Basé sur Helium" src="https://img.shields.io/badge/base-Helium-555e8a?style=flat-square">
  <img alt="Chromium 157" src="https://img.shields.io/badge/Chromium-157-555e8a?style=flat-square">
  <img alt="Licence GPL-3.0" src="https://img.shields.io/badge/licence-GPL--3.0-555e8a?style=flat-square">
  <img alt="État : projet personnel" src="https://img.shields.io/badge/%C3%A9tat-projet%20personnel-b5651d?style=flat-square">
</p>

<p align="center">
  <a href="#à-savoir-avant">À savoir avant</a> ·
  <a href="#fonctionnalités">Fonctionnalités</a> ·
  <a href="#installer">Installer</a> ·
  <a href="#mise-à-jour-automatique">Mise à jour</a> ·
  <a href="#fonctionnement">Fonctionnement</a> ·
  <a href="#compiler-soi-même">Compiler</a> ·
  <a href="#feuille-de-route">Feuille de route</a> ·
  <a href="#crédits-et-licences">Crédits</a>
</p>

> **Fork non officiel.** Bluelium n'est ni affilié à imputnet ni soutenu par
> l'équipe de Helium. Un problème dans Bluelium se signale ici, pas sur le
> dépôt de Helium.

## En bref

Bluelium est un fork de [Helium](https://github.com/imputnet/helium), lui-même
basé sur ungoogled-chromium et Chromium. Il tourne sur macOS (Apple Silicon)
et Linux.

Le moteur et la protection de la vie privée sont ceux de Helium. Bluelium
change l'interface : thèmes, barre d'outils, panneau IA, mode Nuit, nouvel
onglet, animations.

L'image en haut de page est un schéma, pas une capture. Captures à venir.

## À savoir avant

- **C'est un projet personnel.** Une seule personne, pas d'équipe, pas de
  support, pas de garantie.
- **Il est écrit en grande partie avec des agents IA.** Le code, les rapports
  de `docs/` et ce README. Je dirige, je relis et je teste à l'usage.
- **Tout n'est pas terminé.** Le tableau des fonctionnalités indique ce qui
  est utilisé au quotidien et ce qui est encore en réglage.
- **Sur Mac, l'application est signée ad hoc**, sans notarisation Apple. Il
  faut l'ouvrir par clic droit → Ouvrir la première fois.
- **Pas de version Windows.**
- **Les mises à jour suivent celles de Helium**, avec le délai d'un build.

Pour un navigateur stable, suivi par une équipe, mieux vaut installer
[Helium](https://github.com/imputnet/helium). Bluelium s'adresse à ceux qui
veulent essayer cette interface, ou regarder comment le fork est construit.

## Fonctionnalités

- ✅ compilé et utilisé
- 🚧 en cours de réglage, ou pas encore reconstruit sur cette plateforme
- — sans objet

Les ajouts des derniers jours ont été compilés et sont utilisés sur macOS.
**L'auto-build Linux ne les a pas encore reconstruits** : ils ne sont pas dans
les releases Linux actuelles et n'ont pas été testés sous Linux.

| Fonctionnalité | macOS | Linux | Détails |
|---|:---:|:---:|---|
| **Thèmes Prism** | ✅ | ✅ | Prism par défaut, plus Ardoise, Ambre, Sauge, Lilas et Rose, en clair et en sombre. Modes Clair, Sombre, OLED, Nuit, Appareil. Onglets et barre plus compacts. |
| **Couleur de la page dans la barre** | 🚧 | 🚧 | Le cadre, les onglets et la barre prennent une teinte tirée de la page, en fondu. Pastilles de lisibilité sur les pages colorées, blanc et noir adaptés à l'apparence claire ou sombre. Les menus et panneaux gardent les couleurs du thème. Fonctionne, encore en réglage. |
| **Mode Nuit** | ✅ | 🚧 | Interface en rouge sur noir et filtre de lumière chaude sur les pages web. Raccourci <kbd>Alt</kbd>+<kbd>Maj</kbd>+<kbd>N</kbd>. L'ancien convertisseur de pages a été retiré. |
| **Panneau IA** | ✅ | ✅ | Claude, ChatGPT, Gemini et Le Chat dans le panneau latéral, avec la session du profil. Bouton épinglable dans la barre. |
| **Barre d'outils** | ✅ | ✅ | Icônes redessinées, bouclier avec le compteur du bloqueur, bouton Diviser avec les autres icônes, barre personnalisable. |
| **Nouvel onglet Shimmer** | ✅ | ✅ | [Shimmer Tab](https://github.com/dmitthedazed/shimmer-tab) intégré comme page interne : gestion d'onglets, sites les plus visités, onglets fermés récemment. |
| Shimmer : icônes et thème | ✅ | 🚧 | Icônes des sites via le cache du navigateur (l'option « Icônes pour tous les sites » fonctionne). Le thème suit celui de Bluelium. |
| **Panneau Personnaliser** | ✅ | 🚧 | Anciens réglages du nouvel onglet Helium/Chrome retirés, vignettes des thèmes corrigées. |
| **Vue partagée** (Diviser) | ✅ | ✅ | Les deux moitiés forment un seul onglet combiné. |
| **Animations** | 🚧 | 🚧 | Geste retour/suivant au trackpad : la page suit le doigt, pastille avec retour haptique, bande découverte à la couleur de la page. Changement d'onglet : indicateur glissant, fondu directionnel, couleur de barre synchronisée. En cours d'affinage. |
| **Bulle ⌘Q** | ✅ | — | « Maintenir ⌘Q pour quitter » redessinée : capsule en verre, touches dessinées, jauge d'appui. |
| Extensions du Chrome Web Store | ✅ | ✅ | Installation avec la confirmation habituelle, une fois les services d'extensions de Helium acceptés. |

Sur Mac, <kbd>Alt</kbd>+<kbd>Maj</kbd> correspond à <kbd>⌥</kbd><kbd>⇧</kbd>.

L'historique détaillé est dans [AVANCEMENT.md](AVANCEMENT.md). C'est un
journal de travail, pas toujours à jour.

### Limites connues

- macOS : les boutons de fenêtre ne sont pas parfaitement alignés avec les
  onglets. La police Instrument Sans n'est appliquée que sous Linux.
- Linux : Instrument Sans n'est pas embarquée, il faut l'installer
  ([`assets/InstrumentSans.ttf`](assets/InstrumentSans.ttf)).
- Le nom de travail « Glyphe » subsiste dans le code, les patchs et le dossier
  d'installation Linux.
- Claude Code ne détecte pas encore l'extension Claude installée dans
  Bluelium ([docs/connexion-ia.md](docs/connexion-ia.md)).
- Pas de suite de tests propre au projet. La vérification se fait à l'usage.

## Plateformes

| | macOS Apple Silicon | Linux x86_64 | Windows |
|---|---|---|:---:|
| Build | Local, sur le Mac de l'auteur | Automatique, chaque nuit | ❌ |
| État | Compilé, installé et utilisé | Releases publiées, sans les derniers ajouts | |
| Paquet | `.dmg` signé ad hoc, **pas encore publié** | `.tar.zst` + `.sha256` | |
| Mise à jour auto | Agent launchd | Minuteur systemd | |

## Installer

### macOS (Apple Silicon)

Aucun `.dmg` n'est encore publié sur GitHub. En attendant, il faut
[compiler](#compiler-soi-même). Une fois le `.dmg` disponible dans les
[releases](https://github.com/matthieuleconte1/bluelium/releases) :

1. Vérifier le `.sha256`, puis glisser **Bluelium.app** dans `~/Applications`.
2. Au premier lancement, clic droit → **Ouvrir**. Ou bien :

   ```sh
   xattr -dr com.apple.quarantine ~/Applications/Bluelium.app
   ```

Bluelium a sa propre identité et cohabite avec Helium : identifiant de bundle
`io.github.matthieuleconte1.bluelium`, profil dans
`~/Library/Application Support/Bluelium`, clé de trousseau « Bluelium Storage
Key ».

**Reprendre son profil Helium.** Helium et Bluelium fermés :

```sh
tools/migrate-helium-macos.sh
```

Le script copie onglets, favoris, historique, extensions et réglages, ainsi
que les mots de passe et les cookies (la clé du trousseau est recopiée, macOS
demande le mot de passe de session). Le profil Helium n'est pas modifié. Un
profil Bluelium existant est conservé dans `Bluelium.avant-migration`.

### Linux (x86_64)

#### AppImage

Télécharger `Bluelium-<version>-x86_64.AppImage` et son `.sha256` depuis les
[releases](https://github.com/matthieuleconte1/bluelium/releases/latest), vérifier
l'empreinte avec `sha256sum -c Bluelium-*.AppImage.sha256`, puis lancer :

```sh
chmod +x Bluelium-*.AppImage
./Bluelium-<version>-x86_64.AppImage
```

L'AppImage vérifie les mises à jour au lancement, au maximum toutes les 6 h,
en arrière-plan, sans outil de mise à jour externe. Elle télécharge la nouvelle
version avec `curl` ou `wget`, vérifie son SHA-256 et remplace son propre fichier
si celui-ci et son dossier sont accessibles en écriture. La version téléchargée
sera utilisée au prochain lancement. Journal :
`${XDG_CACHE_HOME:-~/.cache}/bluelium/appimage-update.log`.

Pour désactiver : lancer avec `BLUELIUM_NO_UPDATE=1`, ou créer le fichier
`~/.config/bluelium/no-appimage-update` (créer le dossier si nécessaire).

#### Archive tar.zst

Télécharger la dernière archive `bluelium-*.tar.zst` des
[releases](https://github.com/matthieuleconte1/bluelium/releases/latest),
vérifier son `.sha256`, puis :

```sh
mkdir -p ~/Applications && tar --zstd -xf bluelium-*.tar.zst -C ~/Applications
mv ~/Applications/bluelium-* ~/Applications/helium-glyphe
~/Applications/helium-glyphe/helium-wrapper --user-data-dir="$HOME/.config/helium-glyphe"
```

Le dossier `helium-glyphe` porte encore le nom de travail. Les scripts de mise
à jour s'appuient sur ce chemin.

Pour utiliser Bluelium sur un profil Helium existant,
`autobuild/switch-to-bluelium.sh` sauvegarde le profil et remplace l'entrée du
menu (`--revert` pour revenir à Helium).

## Mise à jour automatique

Pour les installations par archive (l'AppImage se met à jour seule),
à installer une fois depuis un clone du dépôt :

| | macOS | Linux |
|---|---|---|
| Installation | `autobuild/install-updater-macos.sh` | `autobuild/install-updater.sh` |
| Mécanisme | Agent launchd, toutes les 2 h | Minuteur systemd utilisateur, toutes les 2 h |
| État | `bluelium-update-macos --status` | `glyphe-update --status` |

Le script lit les releases GitHub, vérifie le SHA-256 et installe la nouvelle
version quand Bluelium est fermé. La version précédente est conservée à côté.
Sur macOS, il n'aura rien à installer tant qu'aucun `.dmg` n'est publié.

## Fonctionnement

Les modifications ne sont pas des patchs écrits à la main. Chacune est une
**spec** Python dans [`specs/`](specs/) : des fichiers à créer et des
remplacements de texte dans les sources de Chromium.
[`specs/SERIES`](specs/SERIES) fixe l'ordre et peut réserver une spec à
`linux` ou à `mac`.

À chaque build :

1. Récupération de la dernière version de Helium
   ([helium-linux](https://github.com/imputnet/helium-linux) ou
   [helium-macos](https://github.com/imputnet/helium-macos)).
2. Étapes de Helium : patchs, substitutions, traductions, ressources.
3. `tools/apply-series.py` applique les specs et régénère les `.patch`. Si une
   spec ne s'applique plus, le build s'arrête en la nommant.
4. Compilation, paquet, publication.

Sous Linux, une machine de build vérifie chaque nuit s'il existe une nouvelle
version de Helium ou un changement dans les specs. Si oui, elle reconstruit
tout et publie une release `v<version Helium>-g<commit>`. Sous macOS, le build
se lance à la main.

| Dossier | Contenu |
|---|---|
| `specs/` | Les specs, source de vérité |
| `patches/glyphe/` | Les `.patch` générés (peuvent être en retard sur les specs) |
| `tools/` | Application des specs, migration du profil, outils de mesure |
| `scripts/` | Scripts de build et de paquet |
| `autobuild/` | Auto-build Linux et mise à jour automatique |
| `docs/` | Rapports de travail |

## Compiler soi-même

Compiler Chromium demande plusieurs heures, beaucoup d'espace disque et de
mémoire.

<details>
<summary><b>macOS</b> (Apple Silicon, Xcode, 100 Go libres sur un volume APFS)</summary>

<br>

Prérequis, identiques à ceux de
[helium-macos](https://github.com/imputnet/helium-macos/blob/main/docs/building.md) :

```sh
brew install python@3.13 wget zstd coreutils readline
python3 -m pip install requests pillow
xcodebuild -downloadComponent MetalToolchain
```

Build :

```sh
scripts/build-macos.sh                          # arm64, dans ~/bluelium-build
PATCH_ONLY=1 scripts/build-macos.sh             # vérifie seulement que la série s'applique
SKIP_FETCH=1 PGO=false scripts/build-macos.sh   # recompile l'arbre existant, sans PGO
PUBLISH=1 scripts/build-macos.sh                # publie le .dmg sur GitHub
```

Le script prend la dernière version de helium-macos, applique ses étapes puis
la série Bluelium, compile et produit
`releases/bluelium-<version>-macos-arm64.dmg` avec son `.sha256`
(`scripts/package-macos.sh`).

| Variable | Effet | Défaut |
|---|---|---|
| `BLUELIUM_MAC_WORK` | Dossier de travail | `~/bluelium-build` |
| `HELIUM_TAG` | Version de helium-macos | La dernière publiée |
| `JOBS` | Tâches de compilation en parallèle | `8` |
| `PGO` | `false` désactive le profil PGO | `true` |
| `PATCH_ONLY=1` | S'arrête après la série Bluelium | |
| `SKIP_FETCH=1` | Garde les sources et relance la compilation | |
| `MIN_FREE_GB` | Espace libre minimal exigé | `100` |
| `PUBLISH=1` | Publie le `.dmg` sur GitHub | |
| `KEEP_GOING=1` | Continue malgré les erreurs | |

**Disque externe en exFAT.** exFAT ne gère pas les liens symboliques dont
Chromium a besoin. Il faut y créer une image APFS :

```sh
hdiutil create -size 200g -type SPARSEBUNDLE -fs APFS \
  -volname BlueliumBuild /Volumes/MonDisque/bluelium.sparsebundle
hdiutil attach /Volumes/MonDisque/bluelium.sparsebundle
BLUELIUM_MAC_WORK=/Volumes/BlueliumBuild scripts/build-macos.sh
```

**Mémoire.** Sur un Mac de 18 Go, `tools/ram-watch-macos.sh` surveille la
mémoire pendant le build et l'arrête avant que la machine se fige. Le build
reprend ensuite avec `SKIP_FETCH=1`.

</details>

<details>
<summary><b>Linux</b> (environ 250 Go de disque, 32 Go de RAM ou plus)</summary>

<br>

Il n'y a pas de script générique : `scripts/build-helium.sh`,
`scripts/dev-build.sh` et `autobuild/autobuild.sh` utilisent les chemins de ma
machine de build. Ils servent d'exemple.

1. Cloner [helium-linux](https://github.com/imputnet/helium-linux) et ajouter
   à son `downloads.ini` la section `[shimmer-tab]` de ce dépôt.
2. Suivre sa procédure jusqu'à la fin de la préparation des sources.
3. Appliquer la série Bluelium :

   ```sh
   python3 tools/apply-series.py <helium-linux>/build/src <ce dépôt> <dossier de sortie> linux
   ```

4. Reprendre la procédure de Helium pour la compilation.

Avec une machine de build accessible en SSH, `tools/sync-builder.sh` y
installe l'auto-build (`--now` le lance, `--patch-only` vérifie seulement que
la série s'applique). L'hôte se règle dans `~/.config/bluelium/builder.env`,
non versionné :

```sh
BLUELIUM_BUILDER=root@ma-machine-de-build
BLUELIUM_JUMP=root@rebond      # facultatif
```

Pour publier les releases, la machine de build lit `GH_TOKEN` dans
`/root/glyphe/github.env` (jeton limité à ce dépôt, droit « Contents: write »).

</details>

## Feuille de route

Sans dates.

- Publier le `.dmg` macOS sur GitHub.
- Reconstruire sous Linux avec les nouvelles specs.
- Affiner les animations et la couleur de la page dans la barre.
- Lecteur PDF : en réflexion, entre améliorer celui de Chromium et passer à
  PDF.js. Rien n'est décidé.
- Ajouter des captures d'écran.

## Crédits et licences

Bluelium est une couche fine au-dessus du travail d'autres projets.

- [Helium](https://github.com/imputnet/helium), avec
  [helium-linux](https://github.com/imputnet/helium-linux) et
  [helium-macos](https://github.com/imputnet/helium-macos), par imputnet.
  L'archive des sources Chromium vient aussi de leur dépôt
  [chromium-tarballs](https://github.com/imputnet/chromium-tarballs).
- **ungoogled-chromium**, sur lequel Helium s'appuie
  ([LICENSE.ungoogled_chromium](LICENSE.ungoogled_chromium), BSD).
- **Chromium**, sous ses propres licences.
- [Shimmer Tab](https://github.com/dmitthedazed/shimmer-tab) de dmitthedazed
  pour le nouvel onglet (GPL-3.0, téléchargé au moment du build).
- **Instrument Sans**, SIL Open Font License
  ([assets/OFL-InstrumentSans.txt](assets/OFL-InstrumentSans.txt)).
- [Material Symbols](https://github.com/google/material-design-icons/tree/master/variablefont)
  de Google pour les contours d'icônes, Apache 2.0
  ([détails](assets/icons/MATERIAL_SYMBOLS_SOURCE.md)).

Bluelium est distribué sous **GPL-3.0** ([LICENSE](LICENSE)), comme Helium.

Les noms et logos Helium, Claude, ChatGPT, Gemini et Le Chat appartiennent à
leurs propriétaires. Les icônes des assistants servent seulement à identifier
chaque service dans l'interface. Voir [NOTICE.md](NOTICE.md).
