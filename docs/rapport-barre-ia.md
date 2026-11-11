# Livraison — barre et panneau IA Glyphe

Build incrémental réussi sur CT 118, dernier passage : **4 min 11**.
Binaire installé par remplacement atomique :
`~/Applications/helium-glyphe/helium`, SHA-256
`845d76da96c701ff6b30646425bf3bfb5712a8cfa7da3cb7f2effdf868fc6545`.

Sauvegardes conservées : `helium.backup-20261111-before-toolbar-final`
(version concurrente `3dd06197cb52…`) et `helium.backup-20261111-before-pixel`.
Aucun commit effectué.

## Résultat visible

- Bloqueur → Diviser → Extensions → séparateur → IA → menu. Diviser garde son
  contrôleur natif ; il est placé dans le conteneur d’extensions avant le puzzle.
- Profil absent en navigation normale, conservé pour invité/incognito. La seconde
  mise à jour de visibilité par la préférence Chromium ne le réaffiche plus.
- IA : cercle à l’accent du thème et logo blanc lorsque le panneau est ouvert.
  La source de l’état est le surlignage natif d’ancrage, distinct de l’indicateur
  d’engagement des commandes. L’image du modèle ne peut plus écraser la teinte.
- Icônes menu, puzzle, division, signet et bouclier issues de Material Symbols
  Rounded, graisse 350 / taille optique 20. Compteur réel d’uBlock, sans valeur
  « 14 » simulée. Les panneaux des quatre assistants restent présents.

## Mesures natives

Captures Spectacle sous KDE/KWin : 1472 × 942. Rectangle client de comparaison :
x=16, y=10, 1440 × 900. Mesures et assertions par PIL.

| Élément | Début de session | Livraison | Référence HTML |
|---|---:|---:|---:|
| Adresse : y / hauteur | 41 / 30 | 41 / 30 | 41 / 30 |
| Début de page y | 78 | 78 | 78 |
| Panneau x / largeur | 996 / 440 | 994 / 440 | 994 / 440 |
| Origine d’en-tête y | 73 | 78 | 78 |
| Séparateur sous l’en-tête y | 121 | 126 | 126 |
| Déplacement des favicons à la sélection | 0 px, validation historique | **0 px**, nouvelle capture | 0 px |

Les quatre boîtes de favicons sont identiques avant et après sélection :
`[14,14,27,27]`, `[261,14,274,27]`, `[508,14,521,27]`,
`[755,14,768,27]` (bornes inclusives, donc 14 × 14).

Avant la dernière correction, Diviser se trouvait à gauche de l’adresse
(`assistant-after.png`, capture intermédiaire) et le profil réapparaissait.
La livraison corrige ces deux points. L’état IA rempli est visible dans
`audit-assistant-open.png` ; la couleur capturée varie d’un niveau par canal
par rapport à #3450d1, ce qui est conservé dans les données de mesure.

Les captures finales et les données sont dans `specs/reference/validation/` :
`audit-tab-a.png`, `audit-tab-b.png`, `audit-assistant-open.png`,
`audit-pixels.json`, `measurements.json`, `ai-layout-pixel-build.log`.

## Travaux concurrents préservés

Le build installé **inclut `page-color-fade`** (couleur mémorisée, fondu 240 ms),
`window-corners`, `newtab-button`, `split-tab`, les onglets de 240 px et la
suppression de bordure du conteneur d’extensions. Les onglets de 176 × 30 de
la planche d’origine ne sont donc plus la cible pour leurs dimensions.

## Connexions et limites

Le binaire final passe les tests réels Native Messaging : hôtes Chrome et
Chromium accessibles, origine non autorisée refusée (`native-messaging-final.json`).
Le ping de l’hôte Claude Code depuis l’extension officielle a répondu `pong`
(`claude-native-ping.json`) ; un nouvel essai a expiré, sans modification du
connecteur. Le compte Claude Code est connecté en mode officiel. La vérification
complète `/chrome` (**Status**, **Extension**) est reportée à la fin à la demande
utilisateur ; aucune connexion complète n’est revendiquée.

L’installation de Claude 1.0.106 via le Web Store a été vérifiée dans un profil
jetable, avec les services d’extensions Helium activés. Les extensions ont depuis
été installées dans le profil habituel par l’utilisateur. Le manifeste OpenAI
`com.openai.codexextension` reste absent ; connexion ChatGPT/Codex non validée.
Voir `docs/connexion-ia.md` pour les étapes restantes.

Le contenu des quatre WebViews est celui des sites officiels ; le transcript
statique du HTML n’est pas reproduit. Le « + » pour assistants personnalisés,
le pied du mock et le tracking CSS exact restent absents. La correspondance
à 100 % de toute la planche n’est donc pas annoncée.

La génération des patchs sur l’arbre de développement a été effectuée. La
reconstruction de la série sur un Helium vierge reste le chantier séparé déjà
signalé dans `AVANCEMENT.md` ; elle n’est pas validée par ce build incrémental.
