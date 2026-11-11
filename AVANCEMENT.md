# Avancement — Helium Glyphe

Mis à jour le 11 novembre 2026.

## Fait

### Barre d’outils, panneau IA et connecteurs (11 novembre, soirée)
- **Livraison installée et mesurée** : SHA `845d76da96c7…`, dernier build
  incrémental **4 min 11**. Rapport : `docs/rapport-barre-ia.md` ; sauvegarde
  du build concurrent `3dd06197cb52…` dans `helium.backup-20261111-before-toolbar-final`.
- Contours Material Symbols Rounded extraits aux axes de la maquette (350,
  opsz 20) : menu, extensions, signet, bouclier et Diviser. Compteur uBlock
  réel à côté du bouclier ; popup et moteur de blocage conservés.
- Ordre natif corrigé : adresse → bloqueur → Diviser → Extensions →
  séparateur → IA → menu. Le bouton Diviser est placé dans le conteneur
  d’extensions, avant son bouton principal ; profil masqué en navigation
  normale, conservé en invité/incognito.
- État IA réellement lié à l’ouverture du panneau (anchor highlight), et non
  à l’indicateur de commande engagé : cercle à l’accent du thème et logo blanc
  quand il est ouvert, logo monochrome et cercle discret au repos. La teinte
  est réappliquée après l’image du modèle, qui l’écrasait.
- Panneau de 440 px, en-tête de 48 px et segments de 28 px ; retrait latéral
  corrigé de 2 px, recouvrement vertical supprimé. Les quatre sites restent
  de vraies WebViews du profil. Le « + » personnalisable reste à faire ; la
  conversation statique du HTML n’est pas substituée aux services distants.
- Native Messaging : Helium prenait déjà en charge les dossiers Chrome et
  les chemins système ; ajout du dossier Chromium utilisateur sous XDG.
  Test sur binaire réel : réponses des hôtes Chrome et Chromium, refus d’une
  origine non autorisée. L’extension Claude officielle obtient aussi `pong`
  de l’hôte Claude Code installé par l’utilisateur.
- Web Store : installation réelle de Claude 1.0.106 dans le profil jetable,
  avec confirmation native. Il faut avoir validé les services d’extensions
  Helium : `--no-first-run` ne vaut pas consentement. Aucun choix du profil
  utilisateur n’a été modifié par ce test. Voir `docs/connexion-ia.md`.
- Captures Spectacle et mesures PIL : `specs/reference/validation/audit-*`,
  `measurements.json`, `native-messaging-final.json`, `claude-native-ping.json`.
  `page-color-fade`, `window-corners`, `newtab-button`, `split-tab`, la bordure
  retirée et les onglets de 240 px des autres sessions sont conservés.
- Les patchs ont été régénérés sur l’arbre de développement. La reconstruction
  de la série sur un Helium vierge reste le chantier distinct indiqué plus bas.

### Correction des espacements (retour utilisateur)
- Référence verticale : planche **Onglet IA**, et non Fenêtre. Adresse à y=41,
  contenu à y=78 ; espace visible de 6 px entre l’onglet actif et le champ.
- Retrait du calcul d’écart selon la sélection et des modifications de la
  gestion de sélection : les onglets ne sautent plus horizontalement.
- Build réussi (4 min 39), installé par remplacement atomique du binaire.
- Vérifié : coordonnées des quatre favicons identiques avant/après sélection,
  zone de page 1428 × 816, barre avec 14 onglets. Captures et mesures dans
  `specs/reference/validation/`.

### Infrastructure
- **Conteneur de build CT 118** (Proxmox) : Debian 13, dépendances du Dockerfile
  officiel installées sans Docker, sccache et ccache.
- **Premier build complet réussi** : Helium 0.21.2.1 / Chromium 157.0.8103.50 en
  2 h 07 (1 h 55 de compilation, 57 504 étapes, 32 jobs).
- **PGO activé par défaut** dans `build-helium.sh` (`PGO=false` pour le couper).
  Le profil Linux est déjà dans les sources.
- **`dev-build.sh`** : build incrémental sans PGO ni effacement de `out/`
  (≈ 10 min par patch, dont ≈ 5 min d'édition des liens).
- **Outils** : `apply_spec.py` (génère les patchs), `shot.mjs` (captures
  avant/après), empaquetage vers `~/Applications/helium-glyphe` sur le PC.

### Maquette (canvas Claude)
Fenêtre (deux rangées serrées, séparateurs d'onglets, fondu au débordement),
mode compact une ligne, barre de commande, vue divisée, nouvel onglet façon
Shimmer, thème sombre, mode nuit rouge, versions KDE Plasma et macOS (curseur de
transparence), liste des features avec leur statut.

### Patchs (dans l'ordre de `patches/series`)

| Patch | Ce qu'il fait | État |
|---|---|---|
| `shimmer-tab-component` | Shimmer Tab 1.3.0 empaqueté en extension composant (comme uBlock), ID fixe `jjnlkggdiemlbkiipdpjfpcpfhkpcico` | ✅ Testé (headless) — remplacé par `shimmer-native-ntp` |
| `red-night-converter` | Pref `glyphe.red_night.enabled`, commande + raccourci Alt+Maj+N | ✅ Compilé — sa partie filtre est retirée par `red-night-dom-converter` |
| `red-night-ui-palette` | Interface en noir pur et rouge : jetons système `kColorSys*` réécrits juste après le mixer système, cadre/onglets/barre forcés | ✅ Compilé, à valider à l'écran |
| `assistant-side-panel` | Entrées de panneau latéral Claude et ChatGPT (vraie vue web, session du profil, 440 px), actions épinglables avec favicon en masque monochrome teinté `kColorIcon`, Alt+Maj+C / Alt+Maj+G | ✅ Compilé, à valider |
| `tab-strip-fade` | Fondu en dégradé au lieu des ombres quand les onglets débordent (barre défilante, `chrome://flags#tab-strip-unification`) | ✅ Compilé, à valider |
| `shortcut-labels` | Libellés des commandes Glyphe : sans eux, les raccourcis personnalisables de Chromium 157 retiraient Alt+Maj+N/C/G | ✅ Compilé |
| `red-night-dom-converter` | Vrai convertisseur de pages : script `glyphe_night.js` injecté par un tab helper natif dans un monde isolé de chaque cadre ; supprime le filtre de calque et le mode sombre forcé de Blink | ✅ Compilé, à valider |
| `shimmer-native-ntp` | Shimmer servi comme page interne `chrome://new-tab-page` (WebUI) au lieu d'une extension : plus de changement de favicon ; `localStorage` sans `chrome.storage` ; CSP ouverte pour svgl.app et Open-Meteo ; nuit rouge appliquée au nouvel onglet | ✅ Compilé, s'affiche (headless) |
| `prism-ui` | DA de la maquette. **Thèmes Glyphe** dans l'onglet Personnaliser à la place des couleurs de Helium (pastille grise retirée, pipette conservée) : Prism (défaut, aussi pour les profils restés sur le gris et après réinitialisation), Ardoise, Ambre, Sauge, Lilas, Rose, chacun en clair et sombre. Sélecteur de mode Clair · Sombre · **OLED** · **Nuit** · Appareil. Interrupteur **« Couleur de la page dans la barre »** (`glyphe.follow_page_color`) : cadre, onglets et barre à la couleur de la page active (theme-color, sinon fond). **Espacements** de la maquette, **Instrument Sans** 13 px, lissage en niveaux de gris | ✅ Compilé, vérifié sur capture |
| `assistant-tabs` | **Onglet IA** (maquette « Onglet IA ») : un seul bouton épinglé au logo du dernier assistant, panneau de 440 px sans en-tête Chromium avec Claude · ChatGPT · Gemini · Le Chat en onglets et une vue web par assistant gardée en vie ; Alt+Maj+C / Alt+Maj+G ouvrent Claude / ChatGPT, pref `glyphe.assistant.current` | ✅ Compilé, vérifié sur capture |
| `layout-spacing` | Espacements natifs mesurés dans le HTML joint : aplats initiaux 176 × 30 (240 × 33 après les ajustements concurrents), favicon 14 px, positions horizontales stables à la sélection, espacement vertical de la planche Onglet IA, outils et adresse, police 13 px, commandes de fenêtre | ✅ Compilé, installé ; mesures IA et stabilité à la sélection vérifiées |

| `native-messaging` | Dossier Chromium utilisateur XDG en secours des dossiers Helium/Chrome ; politique et origines conservées | ✅ Transport Chrome/Chromium et refus d’origine testés |
| `toolbar-glyphe` | Contours natifs menu, extension et Diviser issus de Material Symbols Rounded | ✅ Compilé et capturé |
| `reference-finishing` | Signet au lieu de l’étoile, Diviser épinglé par défaut, boutons circulaires et séparateur | ✅ Compilé et capturé |
| `webstore-install` | Sources CRX HTTPS officielles Google autorisées, confirmation et validation conservées | ✅ Installation Claude testée avec services Helium actifs |
| `blocker-toolbar` | Bouclier monochrome + compteur uBlock réel ; bordure de conteneur retirée par l’autre session | ✅ Compilé et capturé |
| `assistant-button-style` | Repos/actif IA, cercle accent et logo blanc, survol/focus circulaires | ✅ Capture de l’état ouvert vérifiée |
| `page-color-fade` | Couleur mémorisée et fondu de 240 ms (autre session) | ✅ Conservé dans le build installé |
| `window-corners` | Coins natifs arrondis (autre session) | ✅ Conservé |
| `newtab-button` | « + » centré (autre session) | ✅ Conservé |
| `split-tab` | Paire combinée de 400 px, segment actif teinté (autre session) | ✅ Conservé |
| `toolbar-final-layout` | Ordre bloqueur/Diviser/Extensions, profil normal masqué, origine du panneau y=78 | ✅ Build et mesures natives |

### Convertisseur nuit rouge (`specs/glyphe_night.js`)
Règles de l'Atelier Glyphe appliquées au DOM et au CSS :
- règles CSS lisibles réécrites (fond, texte, bordures, SVG), dégradés et ombres retirés ;
- passe sur les styles calculés pour l'inline et les feuilles d'autres origines ;
- fonds → noir (légère trace rouge pour l'élévation), texte → rouge dont
  l'intensité suit le contraste d'origine, aplats colorés (boutons, badges) →
  rouge plein + texte noir, bordures → trait rouge ;
- images et vidéos → monochrome rouge assombri par un filtre SVG `feColorMatrix` ;
- sélection et `<mark>` en rouge plein ;
- `MutationObserver` pour le contenu ajouté ; feuilles adoptées (non bloquées par la CSP) ;
- testé sur Wikipédia, GitHub et Hacker News : 60 à 230 ms par page.

## En cours

- Build incrémental du 11 nov. (13 h 24) dans `~/Applications/helium-glyphe` :
  convertisseur avec pseudo-éléments et icônes à masque, Claude/ChatGPT épinglés
  par défaut. À valider à l'écran.

## À faire

### Corrections et finitions
- [ ] Nuit rouge : filtre rouge de secours sur ce que le convertisseur DOM ne
      touche pas (contenu dessiné en JS : `<canvas>`, WebGL, sous-cadres, etc.).
- [ ] Nuit rouge : page d'accueil dédiée (nouvel onglet custom en mode nuit).
- [x] Shimmer : le favicon changeait à l'ouverture d'un nouvel onglet. Cause :
      l'édition qui retirait `<link rel="icon">` remplaçait par une chaîne vide,
      qu'`apply_spec.py` considérait toujours comme déjà appliquée. Remplacée par
      un commentaire ; `apply_spec.py` refuse désormais les remplacements vides.
- [x] Nouvel onglet : l'extension Shimmer était encore chargée (édition
      `AddShimmerTab()` ignorée pour la même raison) et imposait son icône ;
      retirée, l'onglet garde l'icône d'origine. `apply_spec.py` refuse aussi
      un remplacement contenu dans son motif.
- [ ] Onglet IA : panneau arrondi (calque arrondi par ContentParentView), fond
      et segment actif à la couleur de l'onglet actif. À valider à l'écran.
- [ ] Onglets tracés en 33 px (au lieu de 30), même centre y=20,5, barre
      d'adresse inchangée. À valider à l'écran.
- [x] Bouton IA : logo monochrome (`kColorToolbarButtonIcon`) comme les autres
      icônes, pastille plus marquée quand le panneau est ouvert.
- [x] Mode nuit (convertisseur DOM) validé à l'écran : « bien mieux ».
- [ ] Valider à l'écran : panneau assistant, fondu des onglets.
- [x] Convertisseur : pseudo-éléments (`::before` / `::after`) via règles générées
      partagées, icônes à masque (`mask-image`) en trait rouge, dégradés cachés
      dans le raccourci `background`. Wikipédia propre (≈ 235 ms).
- [ ] Convertisseur : sous-cadres d'autres origines, sites très lourds.
- [ ] Shimmer : icônes des raccourcis vides (GitHub, YouTube, Helium) en headless — CSP svgl.app ou réseau ?
- [ ] Shimmer : thème Glyphe (à préciser : « nouveau futur thème »), raccourcis
      Claude / ChatGPT, favicons via `chrome://favicon2`, moteur de recherche du navigateur.
- [x] Épingler Claude et ChatGPT par défaut dans la barre d'outils (liste par
      défaut de `kPinnedActions` ; un profil existant déjà modifié garde sa liste).
- [ ] Bascule automatique du mode nuit à heure fixe.
- [ ] Fusionner `red-night-converter` + `red-night-dom-converter` en un seul patch propre.
- [ ] Corriger l'icône ChatGPT dans le patch assistant si besoin (SVG nettoyé).
- [x] Couleur de la page dans la barre : patch `page-color-fade` (couleur
      mémorisée, fondu 240 ms, attente de 120 ms au chargement). Plus de
      rectangles de l'ancienne couleur ; validé à l'écran (« nickel »),
      installé le 11 nov. (sauvegarde `helium.backup-20261111-before-page-color`).

- [ ] À valider à l'écran (build du 11 nov. au soir, sauvegarde
      `helium.backup-20261111-before-split`) :
      « + » centré sur son survol (LabelButton ignorait les marges verticales) ;
      traits fins autour des extensions supprimés (bordure de survol de
      `ToolbarIconContainerView`) ; onglets de 240 px ; **onglet combiné de la
      vue divisée** (`split-tab`, spec `split_tab_spec.py`) : une pastille,
      segment actif teinté, icône `vertical_split` à la jonction.
- [ ] `prism-ui.patch` ne contient pas `kTabWidth` (176 puis 240) : à régénérer.

### Auto-build et releases GitHub (Bluelium)
- [x] Dépôt public https://github.com/matthieuleconte1/bluelium (GPL-3.0,
      NOTICE pour les marques, adresses de build hors dépôt dans
      `~/.config/bluelium/builder.env`).
- [x] Cause de l'échec du 11 nov. : la série était appliquée avant la
      substitution des domaines et des noms de Helium, alors que les specs sont
      écrites sur l'arbre final. Désormais `tools/apply-series.py` applique
      `specs/SERIES` après toutes les étapes de Helium et régénère les patchs
      (dans `/root/glyphe/releases/patches-<version>/`).
- [x] La machine de build prend la série sur GitHub (main) : un commit qui
      touche `specs/`, `patches/` ou `downloads.ini` déclenche un build la nuit
      suivante, comme une nouvelle version de Helium. Release `v<helium>-g<commit>`
      publiée avec le jeton de `/root/glyphe/github.env`.
- [x] `glyphe-update` (PC) lit la dernière release GitHub, vérifie le SHA-256,
      installe quand Bluelium est fermé.
- [x] La série (22 patchs) s'applique sur un Helium 0.21.2.1 neuf
      (`tools/sync-builder.sh --patch-only`, 12 nov.). Patchs régénérés recopiés :
      seuls `prism-ui` (thèmes, largeur des onglets) et `layout-spacing` différaient.
- [ ] Premier build complet PGO lancé le 12 nov. dans la nuit : vérifier la
      release sur GitHub, puis `autobuild/switch-to-bluelium.sh` (Helium fermé).
- Outils : `tools/respec.py` (met à jour l'arbre quand une spec déjà
  appliquée change) ; `apply_spec.py` refuse les remplacements vides ou
  contenus dans leur motif.

### Connecteurs IA (priorité basse)
- [ ] Vérification utilisateur `/chrome` reportée en dernier : après redémarrage
      de Helium et `claude --chrome`, relever les lignes **Status** et
      **Extension**. Ne bloque pas la livraison des corrections de barre.
      Le compte est connecté (`claude.ai`, firstParty) et le ping natif de
      l’extension officielle réussit ; la détection complète reste à vérifier.
- [ ] **Claude Code ne détecte pas l'extension Claude** dans Helium Glyphe
      (profil `--user-data-dir=~/.config/helium-glyphe`), alors que l'extension
      (`fcoeoabgfenejglbffodgkkbkcdhcgfn`) est installée et que `/chrome` a écrit
      `com.anthropic.claude_code_browser_extension.json` dans
      `~/.config/{google-chrome,chromium}/NativeMessagingHosts`. Piste : Claude
      Code cherche peut-être l'extension dans les profils de Chrome/Chromium ou un
      processus `chrome`, pas seulement via le connecteur. À diagnostiquer.
- [ ] ChatGPT/Codex : extension installée, connecteur `com.openai.codexextension`
      absent (créé par le plugin Chrome de l'appli ChatGPT, qui cherche aussi un
      processus `chrome`). Non prioritaire.

### Features de la liste (voir le canvas)
- [ ] Onglets horizontaux sur le cadre, page en retrait, barre d'adresse dans la page (moyen).
- [ ] Sites épinglés en boutons ronds (moyen).
- [ ] Archivage automatique des onglets inactifs depuis 12 h (moyen).
- [ ] Barre de commande : recherche d'onglets + actions dans l'omnibox (moyen).
- [ ] Vue divisée : activer et styliser la vue côte à côte native (facile).
- [ ] Accent personnalisable (facile). Pages internes en Prism : couleurs faites par `prism-ui`, reste la typo des pages WebUI.
- [ ] Empaqueter Instrument Sans avec le navigateur (aujourd'hui installée dans `~/.local/share/fonts`, copie dans `assets/`).
- [ ] Onglet IA : bouton « + » pour ajouter un assistant, pied « session du profil · raccourci ».
- [ ] Fusionner `assistant-side-panel` + `assistant-tabs` en un seul patch.
- [ ] Interface ludique en option (maquette « Test : interface ludique »).
- [ ] Transparence du cadre avec curseur + flou KWin (lourd ; X11 : `_KDE_NET_WM_BLUR_BEHIND_REGION`, Wayland : protocole de flou KDE).
- [ ] Teinte et dégradé du cadre (moyen).
- [ ] Mode compact une ligne en option (moyen).
- [ ] Import depuis Arc (macOS/Windows), code de configuration, CLI pour agents (moyen).
- [ ] Jeu hors ligne, aperçu de lien, canal Nightly compilé chaque soir sur le CT 118 (facile).
- [ ] Compteur du bloqueur dans la barre d'adresse (facile).

### Build et diffusion
- [ ] Build complet PGO avec tous les patchs, puis `scripts/package.sh` (AppImage + tarball).
- [ ] Version macOS sur le M3 Pro (disque NVMe externe, Xcode sur le disque, `-j 8`).
- [ ] Commit initial de ce dépôt.
