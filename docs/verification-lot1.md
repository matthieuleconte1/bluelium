# Vérification du lot 1 — 16 novembre 2026

Branche `lot1-backend`, créée avant modification. `AVANCEMENT.md` appartient au
travail parallèle de Claude ; il n'est ni restauré, ni indexé, ni commité.
Aucun stash, reset, push, publication ou accès aux profils/trousseaux réels.

## Sources et méthode

Le volume était initialement absent. Une première vérification a utilisé des
sources partielles téléchargées de Chromium **157.0.8103.50**, les patchs Helium
macOS **0.21.2.1** et les ressources publiées (onboarding **202610161403**).
Cette étape n'était pas un build Chromium complet.

Le volume APFS a ensuite été monté par l'utilisateur :

- `BLUELIUM_MAC_WORK=/Volumes/BlueliumBuild` ;
- image : `/Volumes/Medock/bluelium.sparsebundle` ;
- sources : `/Volumes/BlueliumBuild/helium-macos/build/src` ;
- sortie existante : `out/Default`.

Les sept specs du lot ont été appliquées dans l'ordre de SERIES sur cet arbre
réel avec `tools/apply_spec.py`. Une première passe a aussi utilisé
`tools/apply-series.py` avec une SERIES temporaire limitée au lot pour ne pas
réappliquer le patch figé Shimmer sur un arbre déjà préparé. La dernière passe
porte sur les versions définitives des sept specs :

1. `red_night_schedule_spec.py` ;
2. `night_schedule_ui_spec.py` (Claude) ;
3. `macos_traffic_lights_spec.py` (mac seulement) ;
4. `helium_import_spec.py` ;
5. `helium_import_ui_spec.py` (Claude) ;
6. `dark_outline_spec.py` ;
7. `native_messaging_compat_spec.py`.

Résultats : **7/7 appliquées**, puis réappliquées ; empreintes SHA-256
identiques pour les **34 fichiers** concernés. Les ancres de prefs de mes specs
Nuit/import ont été séparées pour éviter une duplication à la réapplication.
Aucune modification d'ancre ou de contenu dans les specs frontend de Claude.

Les sources réelles sauvegardées avant le lot ont ensuite été copiées dans un
arbre temporaire minimal. Rejeu des sept specs dans l'ordre, génération des sept
`patches/glyphe/*.patch` par l'outil, puis rejeu séparé de ces patchs avec `patch` :
**7/7 OK**, résultat identique aux 34 fichiers de l'arbre macOS réel. Cela vérifie
aussi les contextes des patchs générés. Les patchs n'ont pas été écrits à la main.
Les fichiers temporaires et journaux sont sous `/tmp/bluelium-lot1`.

## Résultat par tâche

| Tâche | Vérifié ici | Reste à vérifier après compilation |
|---|---|---|
| Nuit automatique | Prefs, cycle de vie par profil, Mojo bidirectionnel, application et idempotence des specs backend/frontend | Horaires, changement manuel, plusieurs fenêtres, veille et changements d'heure/fuseau en fonctionnement |
| Feux macOS | Ancres Cocoa et réservations plein écran appliquées, centre géométrique y=20 | Alignement visuel normal/plein écran, macOS avant/après 26 |
| Bienvenue/import | Handler et UI appliqués, AppRun valide avec `sh -n`, contrat documenté | Détection réelle et import des favoris/historique/extensions sur profils jetables, annulation/erreurs |
| Connecteurs IA | Sources des détecteurs installés inspectées ; fallback Chromium macOS appliqué ; six tests Python isolés passent | Transport avec le nouveau binaire, connexion aux comptes et détection externe de bout en bout |
| Trait fin | Spec commune appliquée sur l'arbre réel ; code basé sur cc::PaintFlags et l'adaptateur SkDashPathEffect de Chromium | Rendu OLED/Nuit, changement de mode, focus/survol, DPI/Retina, onglets groupés/épinglés/séparés |

`py_compile` passe pour les sept specs et les deux scripts Python.
`python3 tools/test-native-messaging.py` : **6 tests passent**, uniquement dans
des dossiers jetables. Le frontend d'import a été signalé par Claude comme
validé avec svelte-check (0 erreur), Vite build et polyfill en dev ; ces tests
frontend n'ont pas été relancés par l'agent backend.

**Aucune compilation lancée**, conformément à la dernière instruction. Aucun test
à l'exécution ni test visuel de ce lot. Le binaire existant ne contient donc pas
ces nouveaux changements. La préparation de l'arbre n'établit pas la validité de
compilation C++/Mojo/GN, ni le fonctionnement Linux.

Le code « Trait fin » s'applique aux onglets horizontaux classiques du fork
(`HorizontalTabStyleViews`), et ne revendique pas une refonte des onglets verticaux
ou d'une autre implémentation expérimentale. Le contour actif est peint directement
dans ces deux modes, sans le remplissage animé de la pastille ; les autres modes
conservent leur rendu et leur animation existants. Les feux Cocoa ne reçoivent
aucune couleur de la palette Nuit/OLED.

## Contrats et limites fonctionnelles

- `docs/contrat-nuit-auto.md` : messages Mojo et sources du panneau Personnaliser,
  événement frontend de grisage ; aucune exposition à chrome://settings.
- `docs/contrat-bienvenue.md` : messages WebUI, masques des données, états et
  fichiers Svelte. L'import en ligne porte sur favoris, historique et extensions ;
  la migration intégrale macOS avec sessions/cookies/mots de passe reste l'outil
  hors ligne distinct. L'AppImage ne copie plus implicitement Helium.
- `docs/connexion-ia.md` : chemins macOS/Linux, critères des clients, installation
  des manifestes et limites de leur détection externe. Le fallback et les liens
  ne font pas apparaître Bluelium dans une liste de navigateurs codée dans Claude
  Code ou ChatGPT.
