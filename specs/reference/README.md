# Référence de mise en page Glyphe

`Helium — DA Glyphe.html` est la pièce jointe originale du 11 novembre 2026,
conservée sans modification. La planche **Onglet IA** sert de référence aux
espacements verticaux, conformément au retour utilisateur.

Mesures calculées dans la planche à 1440 × 900 pixels CSS et à 100 % :

| Élément | Mesure CSS |
|---|---|
| Onglets | y = 5,5 ; hauteur 30 ; largeur 176 |
| Bas des onglets | y = 35,5 |
| Champ d’adresse et outils | x = 108 pour le champ ; y = 41 ; hauteur 30 |
| Espace onglets / champ | 5,5 |
| Page | x = 6 ; y = 78 ; marge basse 6 ; rayon 10 |
| Zone de page sans panneau IA | 1428 × 816 |
| Favicons | 14 × 14 ; écart au titre 8 |
| Police des onglets et du champ | Instrument Sans Medium, 13 |

Les deux rangées du HTML font respectivement **38** et **40** pixels, car leur
padding s’ajoute à la hauteur déclarée (`content-box`). La planche Fenêtre
utilise une autre construction, plus serrée : elle ne sert plus de référence
pour l’espacement vertical.

Le patch `layout-spacing` vient après `prism-ui` et `assistant-tabs`.
Les positions horizontales des onglets restent fixes quand la sélection change.
Le séparateur peut disparaître à côté de l’onglet actif, mais l’espace demeure.
Le calcul variable des écarts et les modifications de la gestion de sélection
ont été retirés après le signalement d’onglets qui sautaient de position.

## Limites

La barre comporte désormais le compteur réel d'uBlock, Diviser, Extensions,
le séparateur, IA et le menu. Le profil est masqué en navigation normale,
conservé en invité/incognito. Les contours du menu, des extensions, du bouclier,
du signet et de Diviser sont issus de Material Symbols Rounded (350 / opsz 20).
Le bouton IA suit l'état d'ouverture natif : accent du thème + logo blanc. Le rendu des icônes et le
tracking CSS de -0,16px peuvent différer du moteur de texte natif.

Comparer une fenêtre restaurée à 100 %, en retirant l’ombre KWin. En mode
maximisé, certaines cibles de clic restent étendues jusqu’au bord de l’écran.

Validation native et build réussis ; binaire installé dans `~/Applications/helium-glyphe`.
Captures, mesures et journal du build dans `validation/`.

## Validation complémentaire du 11 novembre au soir

Les captures `audit-*` comparent une fenêtre restaurée à 1440 × 900, après
retrait de l'ombre native (rectangle x=16, y=10, 1440 × 900 dans les PNG
Spectacle de 1472 × 942). La capture `assistant-before.png` est le point de
départ de cette session ; les fichiers historiques `native-*top.png` concernent
la validation d'espacement précédente. Les nouveaux onglets de 240 px et leurs
favicons de 14 px sont conservés, conformément aux corrections concurrentes
acceptées ; la largeur 176 px du HTML n'est donc plus la cible de ce build.

La conversation dessinée dans le HTML n'est pas une conversation réellement
connectée : les quatre WebViews conservent les sites officiels et leurs sessions.
Le contenu de ces sites dépend de la connexion au compte et de leurs évolutions.
Le bouton « + » pour assistants personnalisés et le pied du mock HTML restent absents dans le panneau courant. Le tracking CSS
de -0,01em n'est pas reproduit par les Labels natifs. Aucune correspondance
à 100 % de la page distante n'est revendiquée.
