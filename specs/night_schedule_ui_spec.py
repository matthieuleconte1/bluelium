"""Bluelium : panneau Personnaliser — Nuit automatique, et options grisées en
OLED et en Nuit (maquette validée le 16 nov. 2026).

- Bloc « Nuit automatique » (interrupteur + plage De/À) dans l'élément du
  sélecteur de mode. En Nuit, il passe juste sous le sélecteur ; dans les
  autres modes, il suit l'interrupteur « Couleur de la page dans la barre ».
- En OLED et en Nuit, « Couleur de la page dans la barre » et la grille des
  thèmes sont grisés et inertes, avec une note qui dit pourquoi.
- La grille des thèmes est dans <customize-chrome-appearance> : le sélecteur
  de mode émet `glyphe-mode-change` (composé) et l'apparence l'écoute sur le
  document.

Backend (red_night_schedule_spec.py, placé avant dans SERIES) : prefs
glyphe.red_night.auto.{enabled,start,end} et, dans le mojom
customize_color_scheme_mode, `SetRedNightSchedule(bool, int32, int32)` côté
handler et côté client. Les ancres ci-dessous sont le texte produit par
prism_ui_spec.py et customize_panel_spec.py.
"""

CSM = 'ui/webui/resources/cr_components/customize_color_scheme_mode/'
APP = 'chrome/browser/resources/side_panel/customize_chrome/'

NEW_FILES = {}
EDITS = [
  # --- Sélecteur de mode : état ---
  (CSM + 'customize_color_scheme_mode.ts',
   '      followPageColor_: {type: Boolean, state: true},\n',
   '      followPageColor_: {type: Boolean, state: true},\n'
   '      // Bluelium : mode courant et Nuit automatique.\n'
   '      glypheMode_: {type: Number, state: true},\n'
   '      autoNight_: {type: Boolean, state: true},\n'
   '      autoStart_: {type: Number, state: true},\n'
   '      autoEnd_: {type: Number, state: true},\n'
   '      pickerOpen_: {type: String, state: true},\n'),
  (CSM + 'customize_color_scheme_mode.ts',
   '  private setFollowPageColorListenerId_: number|null = null;\n',
   '  private setFollowPageColorListenerId_: number|null = null;\n'
   '  // Bluelium : OLED et Nuit ont leurs propres couleurs.\n'
   '  protected accessor glypheMode_: number = -1;\n'
   '  protected accessor autoNight_: boolean = false;\n'
   '  protected accessor autoStart_: number = 21 * 60;\n'
   '  protected accessor autoEnd_: number = 7 * 60;\n'
   '  // Bluelium : heure réglée à la souris (le clavier du panneau est pris\n'
   '  // par les raccourcis du navigateur).\n'
   '  protected accessor pickerOpen_: string = \'\';\n'
   '  protected readonly hours_: number[] =\n'
   '      Array.from({length: 24}, (_, i) => i);\n'
   '  protected readonly minutes_: number[] =\n'
   '      Array.from({length: 12}, (_, i) => i * 5);\n'
   '  private glypheListenerIds_: number[] = [];\n'),
  (CSM + 'customize_color_scheme_mode.ts',
   '              this.followPageColor_ = enabled;\n'
   '            });\n'
   '    this.browserProxy_.handler.initializeColorSchemeMode();\n',
   '              this.followPageColor_ = enabled;\n'
   '            });\n'
   '    // Bluelium : suivre le mode (grisage) et la plage de la Nuit auto.\n'
   '    this.glypheListenerIds_ = [\n'
   '      this.browserProxy_.callbackRouter.setColorSchemeMode.addListener(\n'
   '          (mode: ColorSchemeMode) => {\n'
   '            this.glypheMode_ = mode;\n'
   '            this.fire(\'glyphe-mode-change\',\n'
   '                      {locked: this.isGlypheLocked_()});\n'
   '          }),\n'
   '      this.browserProxy_.callbackRouter.setRedNightSchedule.addListener(\n'
   '          (enabled: boolean, start: number, end: number) => {\n'
   '            this.autoNight_ = enabled;\n'
   '            this.autoStart_ = start;\n'
   '            this.autoEnd_ = end;\n'
   '          }),\n'
   '    ];\n'
   '    this.browserProxy_.handler.initializeColorSchemeMode();\n'),
  (CSM + 'customize_color_scheme_mode.ts',
   '      this.setFollowPageColorListenerId_ = null;\n'
   '    }\n',
   '      this.setFollowPageColorListenerId_ = null;\n'
   '    }\n'
   '    // Bluelium\n'
   '    for (const id of this.glypheListenerIds_) {\n'
   '      this.browserProxy_.callbackRouter.removeListener(id);\n'
   '    }\n'
   '    this.glypheListenerIds_ = [];\n'),
  (CSM + 'customize_color_scheme_mode.ts',
   '  protected onFollowPageColorChange_(e: CustomEvent<boolean>) {\n',
   '  // Bluelium : OLED et Nuit imposent leurs couleurs.\n'
   '  protected isGlypheLocked_(): boolean {\n'
   '    return this.glypheMode_ === ColorSchemeMode.kOled ||\n'
   '        this.glypheMode_ === ColorSchemeMode.kRedNight;\n'
   '  }\n\n'
   '  protected isNight_(): boolean {\n'
   '    return this.glypheMode_ === ColorSchemeMode.kRedNight;\n'
   '  }\n\n'
   '  protected formatMinutes_(minutes: number): string {\n'
   '    const h = Math.floor(minutes / 60) % 24;\n'
   '    const m = minutes % 60;\n'
   '    return `${String(h).padStart(2, \'0\')}:${String(m).padStart(2, \'0\')}`;\n'
   '  }\n\n'
   '  protected pad_(n: number): string {\n'
   '    return String(n).padStart(2, \'0\');\n'
   '  }\n\n'
   '  protected pickedMinutes_(): number {\n'
   '    return this.pickerOpen_ === \'end\' ? this.autoEnd_ : this.autoStart_;\n'
   '  }\n\n'
   '  private setPicked_(minutes: number) {\n'
   '    if (this.pickerOpen_ === \'end\') {\n'
   '      this.autoEnd_ = minutes;\n'
   '    } else {\n'
   '      this.autoStart_ = minutes;\n'
   '    }\n'
   '    this.sendSchedule_();\n'
   '  }\n\n'
   '  private sendSchedule_() {\n'
   '    this.browserProxy_.handler.setRedNightSchedule(\n'
   '        this.autoNight_, this.autoStart_, this.autoEnd_);\n'
   '  }\n\n'
   '  protected onAutoNightChange_(e: CustomEvent<boolean>) {\n'
   '    this.autoNight_ = e.detail;\n'
   '    this.sendSchedule_();\n'
   '  }\n\n'
   '  protected onTimeChipClick_(e: Event) {\n'
   '    const which = (e.currentTarget as HTMLElement).dataset[\'which\'] || \'\';\n'
   '    this.pickerOpen_ = this.pickerOpen_ === which ? \'\' : which;\n'
   '  }\n\n'
   '  protected onHourClick_(e: Event) {\n'
   '    const hour = Number((e.currentTarget as HTMLElement).dataset[\'value\']);\n'
   '    this.setPicked_(hour * 60 + this.pickedMinutes_() % 60);\n'
   '  }\n\n'
   '  protected onMinuteClick_(e: Event) {\n'
   '    const minute = Number((e.currentTarget as HTMLElement).dataset[\'value\']);\n'
   '    this.setPicked_(Math.floor(this.pickedMinutes_() / 60) * 60 + minute);\n'
   '    this.pickerOpen_ = \'\';\n'
   '  }\n\n'
   '  protected onFollowPageColorChange_(e: CustomEvent<boolean>) {\n'),

  # --- Sélecteur de mode : rendu ---
  (CSM + 'customize_color_scheme_mode.html.ts',
   '</segmented-button>\n'
   '<div id="glypheFollowPage">\n'
   '  <span id="glypheFollowPageLabel">Couleur de la page dans la barre</span>\n'
   '  <cr-toggle ?checked="${this.followPageColor_}"\n'
   '      aria-labelledby="glypheFollowPageLabel"\n'
   '      @change="${this.onFollowPageColorChange_}"></cr-toggle>\n'
   '</div>`;\n',
   '</segmented-button>\n'
   '<!-- Bluelium : Nuit automatique ; options grisées en OLED et en Nuit. -->\n'
   '<div id="glypheExtras" ?night="${this.isNight_()}">\n'
   '  <div id="glypheFollowPage" ?locked="${this.isGlypheLocked_()}"\n'
   '      ?inert="${this.isGlypheLocked_()}">\n'
   '    <span id="glypheFollowPageLabel">Couleur de la page dans la barre</span>\n'
   '    <cr-toggle ?checked="${this.followPageColor_}"\n'
   '        ?disabled="${this.isGlypheLocked_()}"\n'
   '        aria-labelledby="glypheFollowPageLabel"\n'
   '        @change="${this.onFollowPageColorChange_}"></cr-toggle>\n'
   '  </div>\n'
   '  <div id="glypheSchedule">\n'
   '    <div class="glyphe-row">\n'
   '      <div class="glyphe-text">\n'
   '        <span id="glypheAutoLabel">Nuit automatique</span>\n'
   '        <span class="glyphe-sub">${this.autoNight_ && !this.isNight_() ?\n'
   '            `${this.formatMinutes_(this.autoStart_)} – '
   '${this.formatMinutes_(this.autoEnd_)}` :\n'
   '            \'Bascule chaque jour aux heures choisies\'}</span>\n'
   '      </div>\n'
   '      <cr-toggle ?checked="${this.autoNight_}"\n'
   '          aria-labelledby="glypheAutoLabel"\n'
   '          @change="${this.onAutoNightChange_}"></cr-toggle>\n'
   '    </div>\n'
   '    <div id="glypheTimes" ?hidden="${!this.autoNight_ || !this.isNight_()}">\n'
   '      <span>De</span>\n'
   '      <button class="glyphe-time" data-which="start"\n'
   '          ?open="${this.pickerOpen_ === \'start\'}"\n'
   '          aria-expanded="${this.pickerOpen_ === \'start\'}"\n'
   '          @click="${this.onTimeChipClick_}">\n'
   '        ${this.formatMinutes_(this.autoStart_)}</button>\n'
   '      <span>à</span>\n'
   '      <button class="glyphe-time" data-which="end"\n'
   '          ?open="${this.pickerOpen_ === \'end\'}"\n'
   '          aria-expanded="${this.pickerOpen_ === \'end\'}"\n'
   '          @click="${this.onTimeChipClick_}">\n'
   '        ${this.formatMinutes_(this.autoEnd_)}</button>\n'
   '    </div>\n'
   '    <div id="glyphePicker"\n'
   '        ?hidden="${!this.pickerOpen_ || !this.autoNight_ || !this.isNight_()}">\n'
   '      <span class="glyphe-picker-title">Heure</span>\n'
   '      <div class="glyphe-grid">\n'
   '        ${this.hours_.map(h => html`<button class="glyphe-cell"\n'
   '            data-value="${h}"\n'
   '            ?selected="${Math.floor(this.pickedMinutes_() / 60) === h}"\n'
   '            @click="${this.onHourClick_}">${this.pad_(h)}</button>`)}\n'
   '      </div>\n'
   '      <span class="glyphe-picker-title">Minutes</span>\n'
   '      <div class="glyphe-grid">\n'
   '        ${this.minutes_.map(m => html`<button class="glyphe-cell"\n'
   '            data-value="${m}"\n'
   '            ?selected="${this.pickedMinutes_() % 60 === m}"\n'
   '            @click="${this.onMinuteClick_}">${this.pad_(m)}</button>`)}\n'
   '      </div>\n'
   '    </div>\n'
   '  </div>\n'
   '</div>`;\n'),

  # --- Sélecteur de mode : styles ---
  (CSM + 'customize_color_scheme_mode.css',
   '#glypheFollowPage {\n',
   '/* Bluelium : Nuit automatique et options grisées. */\n'
   '#glypheExtras {\n'
   '  display: flex;\n'
   '  flex-direction: column;\n'
   '}\n\n'
   '#glypheExtras[night] #glypheSchedule {\n'
   '  border-bottom: 1px solid var(--cr-separator-color);\n'
   '  border-top: 0;\n'
   '  margin-top: 4px;\n'
   '  order: -1;\n'
   '  padding-bottom: 12px;\n'
   '}\n\n'
   '#glypheFollowPage[locked] {\n'
   '  opacity: 0.38;\n'
   '}\n\n'
   '#glypheSchedule {\n'
   '  border-top: 1px solid var(--cr-separator-color);\n'
   '  margin-top: 14px;\n'
   '  padding-top: 2px;\n'
   '}\n\n'
   '.glyphe-row {\n'
   '  align-items: center;\n'
   '  display: flex;\n'
   '  gap: 12px;\n'
   '  justify-content: space-between;\n'
   '  margin-top: 12px;\n'
   '}\n\n'
   '.glyphe-text {\n'
   '  color: var(--cr-primary-text-color);\n'
   '  display: flex;\n'
   '  flex-direction: column;\n'
   '  font-size: 13px;\n'
   '  gap: 2px;\n'
   '}\n\n'
   '.glyphe-sub {\n'
   '  color: var(--cr-secondary-text-color);\n'
   '  font-size: 11.5px;\n'
   '}\n\n'
   '#glypheTimes {\n'
   '  align-items: center;\n'
   '  color: var(--cr-secondary-text-color);\n'
   '  display: flex;\n'
   '  font-size: 13px;\n'
   '  gap: 8px;\n'
   '  margin-top: 10px;\n'
   '}\n\n'
   '#glypheTimes[hidden] {\n'
   '  display: none;\n'
   '}\n\n'
   '.glyphe-time,\n'
   '.glyphe-cell {\n'
   '  background: transparent;\n'
   '  border: 1px solid var(--cr-separator-color);\n'
   '  border-radius: 9px;\n'
   '  color: var(--cr-primary-text-color);\n'
   '  cursor: pointer;\n'
   '  font: 500 13px ui-monospace, Menlo, monospace;\n'
   '  padding: 5px 10px;\n'
   '}\n\n'
   '.glyphe-time:hover,\n'
   '.glyphe-cell:hover {\n'
   '  border-color: var(--cr-primary-text-color);\n'
   '}\n\n'
   '.glyphe-time[open] {\n'
   '  border-style: dashed;\n'
   '  border-color: var(--cr-primary-text-color);\n'
   '}\n\n'
   '#glyphePicker {\n'
   '  border: 1px dashed var(--cr-separator-color);\n'
   '  border-radius: 12px;\n'
   '  display: flex;\n'
   '  flex-direction: column;\n'
   '  gap: 6px;\n'
   '  margin-top: 10px;\n'
   '  padding: 10px;\n'
   '}\n\n'
   '#glyphePicker[hidden] {\n'
   '  display: none;\n'
   '}\n\n'
   '.glyphe-picker-title {\n'
   '  color: var(--cr-secondary-text-color);\n'
   '  font-size: 11.5px;\n'
   '}\n\n'
   '.glyphe-grid {\n'
   '  display: grid;\n'
   '  gap: 4px;\n'
   '  grid-template-columns: repeat(6, 1fr);\n'
   '}\n\n'
   '.glyphe-cell {\n'
   '  padding: 4px 0;\n'
   '}\n\n'
   '.glyphe-cell[selected] {\n'
   '  background: var(--cr-primary-text-color);\n'
   '  border-color: var(--cr-primary-text-color);\n'
   '  color: var(--cr-card-background-color, #000);\n'
   '}\n\n'
   '.glyphe-time:focus-visible,\n'
   '.glyphe-cell:focus-visible {\n'
   '  outline: 2px solid var(--cr-focus-outline-color);\n'
   '  outline-offset: 1px;\n'
   '}\n\n'
   '#glypheFollowPage {\n'),

  # --- Apparence : grille des thèmes grisée en OLED et en Nuit ---
  (APP + 'appearance.ts',
   '      showManagedDialog_: {type: Boolean},\n    };\n',
   '      showManagedDialog_: {type: Boolean},\n'
   '      glypheLocked_: {type: Boolean, state: true},\n    };\n'),
  (APP + 'appearance.ts',
   '  protected accessor showManagedDialog_: boolean = false;\n',
   '  protected accessor showManagedDialog_: boolean = false;\n'
   '  // Bluelium : thèmes inactifs en OLED et en Nuit.\n'
   '  protected accessor glypheLocked_: boolean = false;\n'
   '  private onGlypheModeChange_ = (e: Event) => {\n'
   '    this.glypheLocked_ =\n'
   '        (e as CustomEvent<{locked: boolean}>).detail?.locked === true;\n'
   '  };\n'),
  (APP + 'appearance.ts',
   '    // Bluelium : aucune souscription aux réglages ou à la gestion de la NTP.\n'
   '    this.apiProxy_.handler.updateTheme();\n',
   '    // Bluelium : aucune souscription aux réglages ou à la gestion de la NTP.\n'
   '    document.addEventListener(\n'
   '        \'glyphe-mode-change\', this.onGlypheModeChange_);\n'
   '    this.apiProxy_.handler.updateTheme();\n'),
  (APP + 'appearance.ts',
   '      assert(this.apiProxy_.callbackRouter.removeListener(id));\n'
   '    }\n'
   '    this.listenerIds_ = [];\n'
   '  }\n',
   '      assert(this.apiProxy_.callbackRouter.removeListener(id));\n'
   '    }\n'
   '    this.listenerIds_ = [];\n'
   '    // Bluelium\n'
   '    document.removeEventListener(\n'
   '        \'glyphe-mode-change\', this.onGlypheModeChange_);\n'
   '  }\n'),
  (APP + 'appearance.html.ts',
   '<cr-theme-color-picker id="chromeColors" tabindex="-1"\n'
   '    ?hidden="${!this.showColorPicker_}">',
   '<cr-theme-color-picker id="chromeColors" tabindex="-1"\n'
   '    ?hidden="${!this.showColorPicker_}"\n'
   '    ?inert="${this.glypheLocked_}"\n'
   '    style="${this.glypheLocked_ ? \'opacity: 0.38\' : \'\'}">'),
  # --- Couleur de la page dans la barre : coupée en OLED comme en Nuit ---
  ('chrome/browser/ui/views/frame/browser_widget.cc',
   '#include "ui/color/glyphe_red_night.h"\n',
   '#include "ui/color/glyphe_red_night.h"\n'
   '#include "ui/color/glyphe_prism.h"  // Bluelium : IsGlypheOled\n'),
  ('chrome/browser/ui/views/frame/browser_widget.cc',
   '  else if (glyphe_shown_page_color_ && !ui::IsGlypheRedNight()) {\n',
   '  else if (glyphe_shown_page_color_ && !ui::IsGlypheRedNight() &&\n'
   '           !ui::IsGlypheOled()) {\n'),
  ('chrome/browser/ui/views/frame/browser_widget.cc',
   '      !ui::IsGlypheRedNight() &&\n'
   '      !web_app::AppBrowserController::From(browser_view_->browser()) &&\n',
   '      !ui::IsGlypheRedNight() && !ui::IsGlypheOled() &&\n'
   '      !web_app::AppBrowserController::From(browser_view_->browser()) &&\n'),
]
