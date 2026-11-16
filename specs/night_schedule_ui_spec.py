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
   '      autoEnd_: {type: Number, state: true},\n'),
  (CSM + 'customize_color_scheme_mode.ts',
   '  private setFollowPageColorListenerId_: number|null = null;\n',
   '  private setFollowPageColorListenerId_: number|null = null;\n'
   '  // Bluelium : OLED et Nuit ont leurs propres couleurs.\n'
   '  protected accessor glypheMode_: number = -1;\n'
   '  protected accessor autoNight_: boolean = false;\n'
   '  protected accessor autoStart_: number = 21 * 60;\n'
   '  protected accessor autoEnd_: number = 7 * 60;\n'
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
   '            this.dispatchEvent(new CustomEvent(\'glyphe-mode-change\', {\n'
   '              bubbles: true,\n'
   '              composed: true,\n'
   '              detail: {locked: this.isGlypheLocked_()},\n'
   '            }));\n'
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
   '  private parseTime_(value: string, fallback: number): number {\n'
   '    const match = /^(\\d{1,2}):(\\d{2})/.exec(value);\n'
   '    if (!match) {\n'
   '      return fallback;\n'
   '    }\n'
   '    const minutes = Number(match[1]) * 60 + Number(match[2]);\n'
   '    return minutes >= 0 && minutes < 24 * 60 ? minutes : fallback;\n'
   '  }\n\n'
   '  private sendSchedule_() {\n'
   '    this.browserProxy_.handler.setRedNightSchedule(\n'
   '        this.autoNight_, this.autoStart_, this.autoEnd_);\n'
   '  }\n\n'
   '  protected onAutoNightChange_(e: CustomEvent<boolean>) {\n'
   '    this.autoNight_ = e.detail;\n'
   '    this.sendSchedule_();\n'
   '  }\n\n'
   '  protected onAutoStartChange_(e: Event) {\n'
   '    this.autoStart_ = this.parseTime_(\n'
   '        (e.target as HTMLInputElement).value, this.autoStart_);\n'
   '    this.sendSchedule_();\n'
   '  }\n\n'
   '  protected onAutoEndChange_(e: Event) {\n'
   '    this.autoEnd_ = this.parseTime_(\n'
   '        (e.target as HTMLInputElement).value, this.autoEnd_);\n'
   '    this.sendSchedule_();\n'
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
   '      <label for="glypheStart">De</label>\n'
   '      <input id="glypheStart" type="time" step="300"\n'
   '          .value="${this.formatMinutes_(this.autoStart_)}"\n'
   '          @change="${this.onAutoStartChange_}">\n'
   '      <label for="glypheEnd">à</label>\n'
   '      <input id="glypheEnd" type="time" step="300"\n'
   '          .value="${this.formatMinutes_(this.autoEnd_)}"\n'
   '          @change="${this.onAutoEndChange_}">\n'
   '    </div>\n'
   '  </div>\n'
   '  <p id="glypheLockNote" ?hidden="${!this.isGlypheLocked_()}">\n'
   '    ${this.isNight_() ? \'Le mode Nuit\' : \'Le mode OLED\'} a ses propres\n'
   '    couleurs. Thèmes et couleur de la page reviennent en Clair, Sombre et\n'
   '    Appareil.\n'
   '  </p>\n'
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
   '#glypheTimes input {\n'
   '  background: var(--color-sys-surface-container-lowest, transparent);\n'
   '  border: 1px solid var(--cr-separator-color);\n'
   '  border-radius: 9px;\n'
   '  color: var(--cr-primary-text-color);\n'
   '  color-scheme: inherit;\n'
   '  font: 500 13px ui-monospace, "SF Mono", Menlo, monospace;\n'
   '  padding: 5px 8px;\n'
   '}\n\n'
   '#glypheTimes input:focus-visible {\n'
   '  outline: 2px solid var(--cr-focus-outline-color);\n'
   '  outline-offset: 1px;\n'
   '}\n\n'
   '#glypheLockNote {\n'
   '  color: var(--cr-secondary-text-color);\n'
   '  font-size: 11.5px;\n'
   '  line-height: 1.4;\n'
   '  margin: 12px 0 0;\n'
   '}\n\n'
   '#glypheLockNote[hidden] {\n'
   '  display: none;\n'
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
   '        !!(e as CustomEvent<{locked: boolean}>).detail?.locked;\n'
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
]
