# Bluelium : règles du projet

Consignes pour toute personne ou tout agent (Claude, Codex…) qui travaille sur
ce dépôt. Le fonctionnement technique est décrit dans le README.

## Avant chaque release : la page du patch note

Toute release (macOS `scripts/package-macos.sh` avec `PUBLISH=1`, ou Linux via
l'auto-build qui publie depuis `main`) doit avoir sa page de notes de version.

- **Où :** `docs/patch-notes/<version>.html`, par exemple
  `docs/patch-notes/0.22.5.1-glycine.html`. La couleur de la série :
  `python3 tools/couleur.py` (une fois la série commitée).
- **Modèle :** partir de `docs/patch-notes/modele.html`, dont la DA est validée.
  Garder sa structure : en-tête (version, date, base Helium/Chromium, une
  phrase de résumé), une à trois nouveautés majeures avec leur démo
  interactive, « Également » en cartes d'une ligne, versions précédentes
  repliables. Pas d'effets décoratifs (confettis, fonds animés) : l'effet vient
  des démos.
- **Ton :** pro et court. Pas de détail technique, pas de liste exhaustive de
  commits. Indiquer la plateforme de chaque nouveauté (macOS, Linux).
- **Contenu vrai :** ne décrire que ce qui est dans la release et a été vu
  marcher. Ce qui n'a pas été testé n'y figure pas.
- **Quand :** la page est commitée avec les changements, avant de publier. Pour
  Linux, l'auto-build publie `main` chaque nuit : la page doit être dans le même
  push que les changements.

- **Validation :** montrer la page à Matthieu (aperçu ou artifact) et attendre
  son accord avant de publier. Pas de publication sans ce feu vert.

Une release sans sa page de patch note n'est pas prête.
