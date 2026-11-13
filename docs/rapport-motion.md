# Animations natives Bluelium

`motion_spec.py` est commune Linux/macOS ; `motion_tuning_spec.py`, réservée
à macOS dans `specs/SERIES`, affine le geste après elle et avant
`macos-identity`. Aucun patch généré n'a été modifié.

## Geste macOS : continuité jusqu'à la destination

- `HistorySwiper` garde les seuils tactiles natifs et transmet distance et
  vitesse en DIP/s. La vitesse vient des deltas non inertiels horodatés,
  filtrés (35 % précédent / 65 % courant) ; elle retombe à zéro après une
  pause de 80 ms au relâchement. La dérivée de la résistance convertit cette
  vitesse en vitesse visible, au lieu d'appliquer la vitesse brute du doigt.
- `ChromeRenderWidgetHostViewMacDelegate::viewThatWantsHistoryOverlay` vise
  désormais `WebContents::GetNativeView()` : le conteneur Cocoa stable,
  contrairement à `GetContentNativeView()` qui désigne le RWHV remplaçable.
  Le délégué observe le WebContents et remet au repos le fondu du RWHV.
- `HistoryOverlayController` possède toute la translation du geste, de son
  suivi à l'arrivée. Course douce plafonnée à 96 DIP (24 sans historique),
  pastille qui se remplit à l'accent au seuil, haptique conservé. La bande
  découverte utilise `WebContents::GetBackgroundColor()` si disponible, puis
  le fond du calque ou de la fenêtre ; ombre limitée au bord. Aucun voile
  sombre, aucun fondu de la page et aucune impulsion de grossissement.
- La navigation démarre **au relâchement**. La page poursuit sa course vers
  au plus 160 DIP (18 % de la largeur), sans reculer si le geste dépasse ce
  montant. Elle reste décalée pendant le chargement. Il n'y a plus de
  `restorePageAnimated:NO` avant de lancer la navigation.
- Un `WebContentsObserver` suit l'identifiant de la navigation principale.
  Après son commit, `RenderFrameHost::InsertVisualStateCallback` attend la
  soumission d'une image au compositeur. BFCache et historique du même
  document suivent ce chemin. Une fois ce signal reçu **et** la poursuite
  terminée, le conteneur rejoint le centre en 180 ms. La destination arrive
  depuis le décalage courant ; elle ne repart pas du côté opposé.
- La poursuite et l'annulation durent 150–280 ms. La pente initiale de la
  Bézier `.2,y,.2,1` est issue de la vitesse visible et bornée à 0–4 ; les
  deux coordonnées y restent entre 0 et 1, sans rebond ni dépassement.
  L'arrivée commence à vitesse nulle après l'arrêt de la poursuite.
- Après 2 s sans signal de rendu, retour doux sur la page courante. Ce
  garde-fou couvre aussi téléchargements, absence de callback et moteur
  bloqué ; il ne coupe pas une arrivée déjà commencée.

## Un propriétaire, nettoyage et cas limites

Le calque du conteneur porte `blueliumHistoryActive` pendant la présentation.
`BrowserView::DidFinishNavigation`, `StartBlueliumContentMotion` et
`TickBlueliumContentMotion` consultent cet état sur macOS : le fondu générique
ne s'ajoute pas au geste. Clavier et boutons conservent leur transition
40 DIP / 200 ms, hors geste ; les changements d'onglet restent à 12 DIP / 120 ms.

Le changement d'onglet annule explicitement le contrôleur de l'ancien contenu.
Un nouveau geste restaure et libère son prédécesseur avant de capturer sa
transformation originale. Les callbacks tardifs d'un contrôleur terminé sont
sans effet. Le contrôleur survit au changement de RWHV grâce aux blocs de fin,
indépendamment de la durée de vie du swiper/délégué ; les références vers le
WebContents observé et le propriétaire Cocoa ne créent pas de cycle.

Sont également traités : navigation concurrente, navigation refusée/annulée,
WebContents détruit ou masqué, fenêtre fermée, entrée/sortie de plein écran et
activation de « Réduire les animations » pendant le geste. Le nettoyage retire
les observateurs, invalide les callbacks de rendu, restaure la transformation
originale et enlève le marqueur. Sans historique : résistance et pastille à
50 %, aucun armement, aucun haptique de seuil ni navigation. Le plein écran
HTML/vidéo refuse le geste dès son départ ; le plein écran de fenêtre macOS
reste utilisable. Le mode réduit ne translate pas et navigue immédiatement.
La Magic Mouse partage observation, validation et nettoyage ; sa vitesse
reste celle du suivi AppKit, sans estimation supplémentaire.

## Captures d'historique : reportées

Inspection des sources Chromium 157 présentes sur le volume de build :

- `content/public/browser/back_forward_transition_animation_manager.cc` :
  `ShouldAnimateNavigationTransition` renvoie `false` hors Android.
- `content/public/browser/content_browser_client.cc` :
  `ShouldAnimateBackForwardTransitions` renvoie également `false` sur desktop.
- `content/browser/BUILD.gn` : les sources `NavigationEntryScreenshot`, cache,
  manager, configuration et utilitaires de capture appartiennent à Android.
- `content/browser/renderer_host/navigation_transitions/navigation_transition_utils.cc`
  utilise notamment `RenderWidgetHostViewAndroid`, le contexte raster Android
  et des buffers matériels Android.

Activer un flag `kBackForwardTransitions` ne suffit donc pas à disposer d'un
cache et d'une animation desktop. Porter cette chaîne avec budgets mémoire,
captures GPU, invalidation et surfaces protégées dépasse cette correction.
La bande couleur page est conservée ; aucune capture synchronisée AppKit
n'est ajoutée, notamment pour éviter des images vides de surfaces RemoteCocoa
ou de vidéos protégées.

## Linux et autres animations

Linux reste sur `OverscrollController` → `GestureNavSimple::Affordance`, sans
voile sombre, avec seuils natifs et restrictions CSS `overscroll-behavior`.
La spec commune et la série sont inchangées. La translation Aura est libérée
avant la navigation ; le comportement macOS décrit ici ne prétend pas résoudre
ce raccord Linux. Le fondu d'historique Linux reste à 24 DIP / 150 ms.

L'indicateur du TabStrip historique reste à 180 ms ; l'architecture
expérimentale TabStripUnification ne le reçoit pas. Le fondu de barre de
`page_color_fade_spec.py` est indépendant et n'a pas été modifié.

## Vérifications et intégration

Fichiers du dépôt modifiés par cette correction :
`specs/motion_tuning_spec.py`, `docs/rapport-motion.md`.
La spec produit des changements dans 11 fichiers Chromium : contrôleur Cocoa
et son en-tête/tests ; swiper et son en-tête ; délégué et son `BUILD.gn` ;
helper natif `.h/.mm` ; `browser_view.cc` ; `bluelium_motion.h`.

- Compilation Python via `compile(...)` de toutes les specs : réussie.
- Copie temporaire de 21 fichiers Chromium ; inversion des anciennes EDITS
  de motion-tuning puis de motion ; application de motion puis de la nouvelle
  motion-tuning. Les 71 ancres de motion et 29 de tuning ont été contrôlées
  individuellement, chacune unique.
- Deux applications de la nouvelle tuning via `tools/apply_spec.py` : SHA-256
  identiques des sources et du patch temporaire régénéré. Les familles de
  courbes ont aussi été échantillonnées : bornes et monotonie vérifiées.
- Tests Cocoa ajoutés : absence de navigation sans historique, navigation
  immédiate avec décalage conservé, annulation et succession de propriétaires.
  Les tests existants de mouvement réduit sont conservés.
- Relecture des déclarations, callbacks faibles, ARC, dépendances GN et
  barrières de plateforme. Les modifications communes de `browser_view.cc`
  gardent les appels Cocoa sous `BUILDFLAG(IS_MAC)`.

**Aucun build ni test C++/Objective-C++ exécuté**, aucun test visuel,
aucun commit/push, aucune écriture dans `/Volumes/BlueliumBuild`.
`InsertVisualStateCallback` garantit une image soumise, pas sa présentation
physique à l'écran ; ce raccord, le BFCache, les changements de processus,
les vues divisées, la vidéo et la durée réelle restent à valider après
compilation, avec Computer Use dans Helium. L'intégrateur doit aussi vérifier
le découpage du conteneur Cocoa lorsqu'il est translaté. Au-delà du garde-fou
réseau de 2 s, la page courante est volontairement remise au repos.
