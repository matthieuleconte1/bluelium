# Mode nuit — filtre de lumière chaude

Specs préparées le 13 novembre 2026 ; compilation et contrôle visuel à faire
par l'agent d'intégration.

Fichiers modifiés : `specs/red_night_spec.py`, `specs/red_night_ui_spec.py`,
`specs/prism_ui_spec.py`, `specs/shortcut_labels_spec.py`,
`specs/shimmer_native_spec.py`, `specs/SERIES`, `README.md`, `AVANCEMENT.md`
et ce rapport. Fichiers supprimés : `specs/red_night_dom_spec.py` et
`specs/glyphe_night.js`.

Le convertisseur est supprimé : `glyphe_night.js`,
`red_night_dom_spec.py`, son entrée dans `specs/SERIES`, ainsi que l'édition
de `shimmer_native_spec.py` qui étendait l'injection au nouvel onglet. Aucun
script, tab helper, monde isolé ou changement DOM/CSS n'est généré désormais.
La seule modification de Shimmer retire cette dépendance au helper supprimé.

`red_night_spec.py` conserve la pref `glyphe.red_night.enabled`, la commande,
Alt+Maj+N et le sélecteur Nuit existant. La matrice diagonale appliquée au
calque de `ContentsWebView` conserve R et l'alpha, multiplie G par 0,85 et B
par 0,65. Le blanc devient ambre clair, le noir reste noir et les couleurs
restent distinctes. Aucun mode sombre Blink n'est activé. La désactivation
retire la matrice ; chaque vue de contenu observe la pref et la relit quand
un onglet lui est affecté. Cela couvre également les vues divisées et les
nouveaux onglets. Un onglet masqué reçoit l'état courant lorsqu'il est affiché.

Le calque parent existe déjà sur les deux plateformes. Sous Linux,
`NativeViewHostAura::AttachNativeView()` rattache le calque natif au holder
avec `NativeViewHostManagesLayers` (activé par défaut). Si ce flag est
désactivé, le filtre utilise directement le calque natif Aura. Sur macOS,
`WebContentsViewMac::ViewsHostableAttach()` appelle `SetParentUiLayer()` sur
ses vues ; `BrowserCompositorMac::TransitionToState()` ajoute sa surface au
calque du holder. `RenderWidgetHostViewMac::SetParentUiLayer()` désactive alors
l'affichage Cocoa séparé. Le filtre agit donc sur la surface web, sans modifier
les calques de la barre. `ui::Layer::Clone()` conserve la matrice lors d'une
recréation du calque.

`red_night_ui_spec.py` conserve les points d'intégration attendus par Prism :
`IsGlypheRedNight()` retourne faux (ancienne palette rouge désactivée), et
`AddGlypheRedNightMixer()` est neutre. L'état réel du filtre reste dans la pref
du profil. Les changements dans `prism_ui_spec.py` remplacent les ancres du
convertisseur et dissocient OLED du mode nuit. La logique de couleur de page
et `page_color_fade_spec.py` ne sont pas modifiés.

Validation effectuée : compilation Python en mémoire de chaque spec ; inversion
exacte de l'ancienne série depuis les fichiers de l'arbre macOS en lecture seule,
puis application stricte de la nouvelle série aux variantes Linux et macOS.
Chaque texte « ancien » apparaît exactement une fois à son étape ; plus aucune
référence au helper d'injection dans le résultat. `git diff --check` passe.
Aucun fichier du volume de build, patch généré, commit ou push n'a été modifié.

Pour intégrer, repartir d'un état Helium avant les anciennes specs Bluelium,
ou inverser l'ancienne série avant de rejouer la nouvelle. Réappliquer seulement
les nouvelles specs sur l'arbre déjà patché ne supprime pas les anciennes
injections ; `respec.py` seul ne suffit pas lorsque des éditions sont retirées.
Régénérer les patchs avec la nouvelle série, sans réintroduire l'ancien
`red-night-dom-converter.patch`.

Restent à vérifier sur les binaires Linux/macOS : compilation C++, bascule
immédiate, navigation entre processus, onglets restaurés, nouvel onglet,
vue divisée et vidéo plein écran. Le rendu GPU/HDR et les overlays vidéo
requièrent un essai réel ; tester aussi le secours Linux avec
`NativeViewHostManagesLayers` désactivé.
