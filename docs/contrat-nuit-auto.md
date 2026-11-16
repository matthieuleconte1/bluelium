# Nuit automatique : contrat du panneau Personnaliser Bluelium

Spec backend : `specs/red_night_schedule_spec.py`, après `prism-ui` et les
specs de personnalisation existantes. Placer `night_schedule_ui_spec.py` après
`red-night-schedule.patch` dans `specs/SERIES`. Aucun contrôle dans Settings.

Sources de l'élément du sélecteur et de l'interrupteur Couleur de la page :

- `ui/webui/resources/cr_components/customize_color_scheme_mode/customize_color_scheme_mode.ts`
- `ui/webui/resources/cr_components/customize_color_scheme_mode/customize_color_scheme_mode.html.ts`
- sa feuille `customize_color_scheme_mode.css` dans le même dossier.

Le frontend ajoute ses propriétés Lit et son listener avant l'appel existant
`this.browserProxy_.handler.initializeColorSchemeMode()`, puis retire le
listener dans `disconnectedCallback`, comme pour `setFollowPageColor`.

```ts
this.browserProxy_.callbackRouter.setRedNightSchedule.addListener(
    (enabled: boolean, startMinutes: number, endMinutes: number) => { /* état */ });
this.browserProxy_.handler.setRedNightSchedule(enabled, startMinutes, endMinutes);
```

Le handler et le client Mojo ont tous deux
`SetRedNightSchedule(bool enabled, int32 start_minutes, int32 end_minutes)`.
Le client renvoie l'état à l'initialisation et à chaque changement des trois
prefs, y compris venant d'une autre fenêtre. Un appel invalide (minutes hors
0..1439) ne change rien et renvoie l'état retenu. Envoyer les trois valeurs à
chaque modification ; les écritures sont coalescées avant évaluation.

Prefs de profil : `glyphe.red_night.auto.enabled` (false),
`glyphe.red_night.auto.start` (1260), `glyphe.red_night.auto.end` (420).
L'heure est locale. Début inclus, fin exclue ; la plage peut passer minuit.
Début = fin signifie plage vide. Le réglage des horaires ou l'activation
recalcule le mode. Désactiver l'automatisation conserve le mode courant.
Un changement manuel de `glyphe.red_night.enabled` est conservé jusqu'à la
prochaine borne. Une relance du navigateur réévalue la plage. Veille : contrôle
immédiat au réveil ; horloge, fuseau, heure d'été/hiver : contrôle sous 1 s.

## État OLED / Nuit pour les contrôles désactivés

Le sélecteur reçoit déjà `setColorSchemeMode` avec les valeurs Mojo
`ColorSchemeMode.kOled` (3) et `ColorSchemeMode.kRedNight` (4), Nuit prioritaire.
Utiliser son état `currentMode_.value` existant (et `glypheMode_` dans la spec UI) pour griser l'interrupteur.
Ne pas déduire ces modes de la couleur de fond ni du mode sombre système.

La grille utilise `ui/webui/resources/cr_components/theme_color_picker/`
et son parent `chrome/browser/resources/side_panel/customize_chrome/appearance.ts`.
Le frontend relaie l'état du sélecteur par l'événement `glyphe-mode-change`
(implémenté dans `night_schedule_ui_spec.py`). Aucun champ supplémentaire dans
`theme_color_picker.mojom::Theme` n'est nécessaire. Les deux prefs OLED/Nuit
peuvent être vraies ; Nuit reste prioritaire dans le mode affiché.
