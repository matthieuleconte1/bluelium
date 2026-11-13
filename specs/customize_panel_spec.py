"""Bluelium : Personnaliser ne règle plus la NTP Chromium remplacée par Shimmer.

Conserve couleurs, modes, thèmes installés, barre d’outils et extensions.
Retire outils NTP, raccourcis, cartes, pied, fonds locaux/collections et recherche
de fonds, ainsi que leurs routes, abonnements et appels depuis ce panneau.
Les ressources et interfaces Mojo Chromium restent disponibles pour les autres
consommateurs ; aucun fichier de Shimmer n’est modifié.
"""

NEW_FILES = {}

EDITS = [
  ('chrome/browser/resources/side_panel/customize_chrome/app.html.ts',
   '''      <customize-chrome-appearance @edit-theme-click="${this.onEditThemeClick_}"
          @wallpaper-search-click="${this.onWallpaperSearchClick_}"
          id="appearanceElement">''',
   '''      <!-- Bluelium : couleurs du navigateur ; Shimmer règle sa propre NTP. -->
      <customize-chrome-appearance id="appearanceElement">'''),
  ('chrome/browser/resources/side_panel/customize_chrome/app.html.ts',
   '''    ${this.ntpNextFeaturesEnabled_ && this.ntpNextDisablementEnabled_ &&
            this.aimPolicyEnabled_ && this.isSourceTabFirstPartyNtp_() ?
        html`
      <hr class="sp-cards-separator">
      <div id="tools" class="section sp-card">
        <sp-heading hide-back-button>
          <h2 slot="heading">$i18n{toolsHeader}</h2>
        </sp-heading>
        <customize-chrome-tools></customize-chrome-tools>
      </div>
    ` : ''}
    ${this.isSourceTabFirstPartyNtp_() ? html`
      <hr class="sp-cards-separator">
      <div id="shortcuts" class="section sp-card">
        <customize-chrome-shortcuts></customize-chrome-shortcuts>
      </div>
    ` : ''}
    ${(this.modulesEnabled_ && this.isSourceTabFirstPartyNtp_()) ? html`
      <hr class="sp-cards-separator">
      <div id="modules" class="section sp-card">
        <sp-heading hide-back-button>
          <h2 slot="heading">$i18n{cardsHeader}</h2>
        </sp-heading>
        <customize-chrome-cards></customize-chrome-cards>
      </div>
    ` : ''}
''',
   '''    <!-- Bluelium : outils, raccourcis et cartes de la NTP retirés. -->
'''),
  ('chrome/browser/resources/side_panel/customize_chrome/app.html.ts',
   '''    ${this.showFooter_ ? html`
      <hr class="sp-cards-separator">
      <div id="footer" class="section sp-card">
        <sp-heading hide-back-button>
          <h2 slot="heading">$i18n{footerHeader}</h2>
        </sp-heading>
        <customize-chrome-footer></customize-chrome-footer>
      </div>
    ` : ''}
  </div>
  ${this.showEditTheme_ ? html`
    <customize-chrome-categories @back-click="${this.onBackClick_}"
        @collection-select="${this.onCollectionSelect_}" page-name="categories"
        id="categoriesPage" @local-image-upload="${this.onLocalImageUpload_}"
        @wallpaper-search-select="${this.onWallpaperSearchSelect_}">
    </customize-chrome-categories>
  ` : ''}
  ${this.showEditTheme_ ? html`
    <customize-chrome-themes @back-click="${this.onBackClick_}"
        page-name="themes" id="themesPage"
        .selectedCollection="${this.selectedCollection_}">
    </customize-chrome-themes>
  ` : ''}
  ${this.wallpaperSearchEnabled_ && this.showEditTheme_ ? html`
    <customize-chrome-wallpaper-search @back-click="${this.onBackClick_}"
        page-name="wallpaper-search" id="wallpaperSearchPage">
    </customize-chrome-wallpaper-search>
  ` : ''}
''',
   '''    <!-- Bluelium : pied de NTP et pages de fonds d’écran retirés. -->
  </div>
'''),
  ('chrome/browser/resources/side_panel/customize_chrome/app.html.ts',
   '''    <hr class="sp-cards-separator">
    ${this.toolbarCustomizationEnabled_ ? html`
      <cr-button''',
   '''    ${this.toolbarCustomizationEnabled_ ? html`
      <hr class="sp-cards-separator">
      <cr-button'''),
  ('chrome/browser/resources/side_panel/customize_chrome/app.ts',
   '''import './appearance.js';
import './cards.js';
import './categories.js';
import './customize_toolbar/toolbar.js';
import './footer.js';
import './tools.js';
import './shortcuts.js';
import './themes.js';
import './wallpaper_search/wallpaper_search.js';''',
   '''// Bluelium : aucun composant de réglage de l’ancienne NTP n’est instancié.
import './appearance.js';
import './customize_toolbar/toolbar.js';'''),
  ('chrome/browser/resources/side_panel/customize_chrome/app.ts',
   "import {assert, assertNotReached, assertNotReachedCase} from 'chrome://resources/js/assert.js';",
   "import {assert, assertNotReached} from 'chrome://resources/js/assert.js';"),
  ('chrome/browser/resources/side_panel/customize_chrome/app.ts',
   '''import type {PropertyValues} from 'chrome://resources/lit/v3_0/lit.rollup.js';
''',
   '''// Bluelium : plus de propriétés dérivées du pied de NTP.
'''),
  ('chrome/browser/resources/side_panel/customize_chrome/app.ts',
   '''import type {CategoriesElement} from './categories.js';
import type {BackgroundCollection, ManagementNoticeState} from './customize_chrome.mojom-webui.js';
import {ChromeWebStoreCategory, ChromeWebStoreCollection, CustomizeChromeSection, NewTabPageType} from './customize_chrome.mojom-webui.js';
import {CustomizeChromeApiProxy} from './customize_chrome_api_proxy.js';
import type {ThemesElement} from './themes.js';

const SECTION_TO_SELECTOR = {
  [CustomizeChromeSection.kUnspecified]: '',
  [CustomizeChromeSection.kAppearance]: '#appearance',
  [CustomizeChromeSection.kShortcuts]: '#shortcuts',
  [CustomizeChromeSection.kModules]: '#modules',
  [CustomizeChromeSection.kFooter]: '#footer',
};

const CHANGE_CHROME_THEME_BUTTON_ELEMENT_ID =
    'CustomizeChromeUI::kChangeChromeThemeButtonElementId';

''',
   '''import {ChromeWebStoreCategory, ChromeWebStoreCollection, CustomizeChromeSection} from './customize_chrome.mojom-webui.js';
import {CustomizeChromeApiProxy} from './customize_chrome_api_proxy.js';

// Bluelium : les anciennes destinations NTP sont ignorées par le routeur.
'''),
  ('chrome/browser/resources/side_panel/customize_chrome/app.ts',
   '''  OVERVIEW = 'overview',
  CATEGORIES = 'categories',
  THEMES = 'themes',
  TOOLBAR = 'toolbar',
  WALLPAPER_SEARCH = 'wallpaper-search',
''',
   '''  // Bluelium : seules les pages du navigateur restent dans ce panneau.
  OVERVIEW = 'overview',
  TOOLBAR = 'toolbar',
'''),
  ('chrome/browser/resources/side_panel/customize_chrome/app.ts',
   '''  static override get properties() {
    return {
      page_: {type: String},
      modulesEnabled_: {type: Boolean},
      selectedCollection_: {type: Object},
      extensionPolicyEnabled_: {type: Boolean},
      extensionsCardEnabled_: {type: Boolean},
      ntpNextFeaturesEnabled_: {type: Boolean},
      ntpNextDisablementEnabled_: {type: Boolean},
      aimPolicyEnabled_: {type: Boolean},
      footerEnabled_: {type: Boolean},
      wallpaperSearchEnabled_: {type: Boolean},
      newTabPageType_: {type: Number},
      showEditTheme_: {type: Boolean},
      showFooter_: {type: Boolean},
      showFooterForManagedBrowser_: {type: Boolean},
      toolbarCustomizationEnabled_: {type: Boolean},
    };
  }

  protected accessor page_: CustomizeChromePage = CustomizeChromePage.OVERVIEW;
  protected accessor modulesEnabled_: boolean =
      loadTimeData.getBoolean('modulesEnabled');
  protected accessor selectedCollection_: BackgroundCollection|null = null;
  protected accessor extensionsCardEnabled_: boolean =
      loadTimeData.getBoolean('extensionsCardEnabled');
  protected accessor ntpNextFeaturesEnabled_: boolean =
      loadTimeData.getBoolean('ntpNextFeaturesEnabled');
  protected accessor ntpNextDisablementEnabled_: boolean =
      loadTimeData.getBoolean('ntpNextDisablementEnabled');
  protected accessor extensionPolicyEnabled_: boolean = false;
  protected accessor aimPolicyEnabled_: boolean =
      loadTimeData.getBoolean('aimPolicyEnabled');
  protected accessor footerEnabled_: boolean =
      loadTimeData.getBoolean('footerEnabled');
  protected accessor wallpaperSearchEnabled_: boolean =
      loadTimeData.getBoolean('wallpaperSearchEnabled');
  protected accessor newTabPageType_: NewTabPageType =
      NewTabPageType.kFirstPartyWebUI;
  protected accessor showEditTheme_: boolean = true;
  protected accessor showFooter_: boolean = false;
  protected accessor showFooterForManagedBrowser_: boolean = false;
  protected accessor toolbarCustomizationEnabled_: boolean =
      loadTimeData.getBoolean('toolbarCustomizationEnabled');

''',
   '''  static override get properties() {
    return {
      page_: {type: String},
      extensionsCardEnabled_: {type: Boolean},
      toolbarCustomizationEnabled_: {type: Boolean},
    };
  }

  // Bluelium : les réglages NTP appartiennent à Shimmer, pas à ce panneau.
  protected accessor page_: CustomizeChromePage = CustomizeChromePage.OVERVIEW;
  protected accessor extensionsCardEnabled_: boolean =
      loadTimeData.getBoolean('extensionsCardEnabled');
  protected accessor toolbarCustomizationEnabled_: boolean =
      loadTimeData.getBoolean('toolbarCustomizationEnabled');

'''),
  ('chrome/browser/resources/side_panel/customize_chrome/app.ts',
   '''    this.listenerIds_ = [
      this.apiProxy_.callbackRouter.scrollToSection.addListener(
          this.onScrollToSection_.bind(this)),
      this.apiProxy_.callbackRouter.setThemeEditable.addListener(
          this.onSetThemeEditable_.bind(this)),
      this.apiProxy_.callbackRouter.setFooterSettings.addListener(
          this.onSetFooterSettings_.bind(this)),
    ];

    this.apiProxy_.handler.updateAttachedTabState();
    this.apiProxy_.handler.updateFooterSettings();

''',
   '''    // Bluelium : écouter uniquement la navigation vers les réglages conservés.
    this.listenerIds_ = [
      this.apiProxy_.callbackRouter.scrollToSection.addListener(
          this.onScrollToSection_.bind(this)),
    ];

'''),
  ('chrome/browser/resources/side_panel/customize_chrome/app.ts',
   '''  override willUpdate(changedProperties: PropertyValues<this>) {
    super.willUpdate(changedProperties);

    const changedPrivateProperties =
        changedProperties as Map<PropertyKey, unknown>;
    if (changedPrivateProperties.has('footerEnabled_') ||
        changedPrivateProperties.has('newTabPageType_') ||
        changedPrivateProperties.has('showFooterForManagedBrowser_') ||
        changedPrivateProperties.has('extensionPolicyEnabled_')) {
      this.showFooter_ = this.computeShowFooter_();
    }
  }

  override firstUpdated() {
    ColorChangeUpdater.forDocument().start();
    this.registerHelpBubble(
        CHANGE_CHROME_THEME_BUTTON_ELEMENT_ID,
        ['#appearanceElement', '#editThemeButton']);
  }

  private onScrollToSection_(section: CustomizeChromeSection) {
    if (section === CustomizeChromeSection.kWallpaperSearch) {
      this.onWallpaperSearchSelect_();
      return;
    }

    if (section === CustomizeChromeSection.kToolbar) {
      this.openToolbarCustomizationPage();
      chrome.metricsPrivate.recordUserAction(
          'Actions.CustomizeToolbarSidePanel' +
          '.OpenedFromOutsideCustomizeChrome');
      return;
    }

    const selector = SECTION_TO_SELECTOR[section];
    const element = this.shadowRoot.querySelector(selector);
    if (!element) {
      return;
    }

    this.page_ = CustomizeChromePage.OVERVIEW;
    element.scrollIntoView({behavior: 'auto'});
  }

  private onSetThemeEditable_(isThemeEditable: boolean) {
    this.showEditTheme_ = isThemeEditable;
  }

  private onSetFooterSettings_(
      _: boolean, extensionPolicyEnabled: boolean,
      managementNoticeState: ManagementNoticeState) {
    // The footer section should be shown for managed browsers if
    // the management notice is shown or if it is disabled by
    // the user and can be toggled back on.
    this.showFooterForManagedBrowser_ = managementNoticeState.canBeShown;
    this.extensionPolicyEnabled_ = extensionPolicyEnabled;
  }


  protected computeShowFooter_(): boolean {
    return this.footerEnabled_ &&
        ((this.extensionPolicyEnabled_ &&
          this.newTabPageType_ === NewTabPageType.kExtension) ||
         this.showFooterForManagedBrowser_);
  }

  protected isSourceTabFirstPartyNtp_(): boolean {
    return this.newTabPageType_ === NewTabPageType.kFirstPartyWebUI;
  }

  protected async onBackClick_() {
    switch (this.page_) {
      case CustomizeChromePage.CATEGORIES:
      case CustomizeChromePage.TOOLBAR:
        this.page_ = CustomizeChromePage.OVERVIEW;
        await this.updateComplete;
        this.$.appearanceElement.focusOnThemeButton();
        break;
      case CustomizeChromePage.THEMES:
      case CustomizeChromePage.WALLPAPER_SEARCH:
        this.page_ = CustomizeChromePage.CATEGORIES;
        await this.updateComplete;
        this.shadowRoot.querySelector<CategoriesElement>(
                           '#categoriesPage')!.focusOnBackButton();
        break;
      case CustomizeChromePage.OVERVIEW:
        assertNotReached();
      default:
        assertNotReachedCase(this.page_);
    }
  }

  protected async onEditThemeClick_() {
    this.page_ = CustomizeChromePage.CATEGORIES;
    await this.updateComplete;
    this.shadowRoot.querySelector<CategoriesElement>(
                       '#categoriesPage')!.focusOnBackButton();
  }

  protected async onCollectionSelect_(
      event: CustomEvent<BackgroundCollection>) {
    this.selectedCollection_ = event.detail;
    this.page_ = CustomizeChromePage.THEMES;
    await this.updateComplete;
    this.shadowRoot.querySelector<ThemesElement>(
                       '#themesPage')!.focusOnBackButton();
  }

  protected async onLocalImageUpload_() {
    this.page_ = CustomizeChromePage.OVERVIEW;
    await this.updateComplete;
    this.$.appearanceElement.focusOnThemeButton();
  }

  protected onWallpaperSearchClick_() {
    this.onWallpaperSearchSelect_();
  }

  protected onWallpaperSearchSelect_() {
    this.page_ = CustomizeChromePage.WALLPAPER_SEARCH;
    const page =
        this.shadowRoot.querySelector('customize-chrome-wallpaper-search');
    assert(page);
    page.focusOnBackButton();
  }

''',
   '''  override firstUpdated() {
    ColorChangeUpdater.forDocument().start();
  }

  private onScrollToSection_(section: CustomizeChromeSection) {
    if (section === CustomizeChromeSection.kToolbar) {
      this.openToolbarCustomizationPage();
      chrome.metricsPrivate.recordUserAction(
          'Actions.CustomizeToolbarSidePanel' +
          '.OpenedFromOutsideCustomizeChrome');
      return;
    }

    // Bluelium : ignorer aussi les liens externes vers les sections NTP retirées.
    if (section !== CustomizeChromeSection.kAppearance) {
      return;
    }
    this.page_ = CustomizeChromePage.OVERVIEW;
    void this.updateComplete.then(() => {
      this.shadowRoot.querySelector('#appearance')!.scrollIntoView(
          {behavior: 'auto'});
    });
  }

  protected async onBackClick_() {
    if (this.page_ !== CustomizeChromePage.TOOLBAR) {
      assertNotReached();
    }
    this.page_ = CustomizeChromePage.OVERVIEW;
    await this.updateComplete;
    // Bluelium : le bouton de fond NTP n’existe plus ; cibler les couleurs.
    this.$.appearanceElement.focusOnThemeButton();
  }

'''),
  ('chrome/browser/resources/side_panel/customize_chrome/appearance.html.ts',
   '''<customize-chrome-theme-snapshot id="themeSnapshot" role="button" tabindex="0"
    @keydown="${this.onThemeSnapshotKeydown_}"
    @edit-theme-click="${this.onEditThemeClick_}"
    hidden>
</customize-chrome-theme-snapshot>
''',
   '''<!-- Bluelium : pas d’aperçu ni d’édition du fond de l’ancienne NTP. -->
'''),
  ('chrome/browser/resources/side_panel/customize_chrome/appearance.html.ts',
   '''<div id="editButtonsContainer" ?hidden="${!this.showEditTheme_ && !this.showClassicChromeButton_}">
  <hr class="sp-hr">
  <cr-button id="editThemeButton"
      ?hidden="${!this.showEditTheme_}"
      @click="${this.onUploadedImageButtonClick_}">
    <div id="editThemeIcon" class="cr-icon edit-theme-icon" slot="prefix-icon"
        ?hidden="${this.wallpaperSearchButtonEnabled_}"></div>
    $i18n{changeWallpaper}
  </cr-button>
''',
   '''<!-- Bluelium : conserver la réinitialisation des thèmes du navigateur. -->
<div id="editButtonsContainer" ?hidden="${!this.showClassicChromeButton_}">
  <hr class="sp-hr">
'''),
  ('chrome/browser/resources/side_panel/customize_chrome/appearance.html.ts',
   '<cr-theme-color-picker id="chromeColors" ?hidden="${!this.showColorPicker_}">',
   '''<cr-theme-color-picker id="chromeColors" tabindex="-1"
    ?hidden="${!this.showColorPicker_}">'''),
  ('chrome/browser/resources/side_panel/customize_chrome/appearance.ts',
   '''import './theme_snapshot.js';
''',
   '''// Bluelium : aucun aperçu de la NTP Chromium à charger.
'''),
  ('chrome/browser/resources/side_panel/customize_chrome/appearance.ts',
   '''import {NewTabPageType} from './customize_chrome.mojom-webui.js';
''',
   '''// Bluelium : le type de NTP ne conditionne plus les couleurs du navigateur.
'''),
  ('chrome/browser/resources/side_panel/customize_chrome/appearance.ts',
   '''    editThemeButton: HTMLButtonElement,
    themeSnapshot: HTMLElement,
''',
   '''    // Bluelium : seules les commandes de thème du navigateur sont conservées.
'''),
  ('chrome/browser/resources/side_panel/customize_chrome/appearance.ts',
   '''  static override get properties() {
    return {
      theme_: {type: Object},
      editThemeButtonText_: {type: String},

      thirdPartyThemeId_: {
        type: String,
        reflect: true,
      },

      thirdPartyThemeName_: {
        type: String,
        reflect: true,
      },

      showBottomDivider_: {type: Boolean},
      showClassicChromeButton_: {type: Boolean},
      showColorPicker_: {type: Boolean},
      showDeviceThemeToggle_: {type: Boolean},
      showThemeSnapshot_: {type: Boolean},
      showUploadedImageButton_: {type: Boolean},
      showSearchedImageButton_: {type: Boolean},
      showManagedButton_: {type: Boolean},
      showManagedDialog_: {type: Boolean},
      showEditTheme_: {type: Boolean},
      managedByName_: {type: String},
      managedByDesc_: {type: String},
      newTabPageType_: {type: Number},

      wallpaperSearchButtonEnabled_: {
        type: Boolean,
        reflect: true,
      },

      wallpaperSearchEnabled_: {type: Boolean},
      footerEnabled_: {type: Boolean},
    };
  }

  protected accessor theme_: Theme|undefined;
  protected accessor editThemeButtonText_: string = '';
  protected accessor thirdPartyThemeId_: string|null = null;
  protected accessor thirdPartyThemeName_: string|null = null;
  protected accessor showBottomDivider_: boolean = false;
  protected accessor showClassicChromeButton_: boolean = false;
  protected accessor showColorPicker_: boolean = false;
  protected accessor showDeviceThemeToggle_: boolean = false;
  protected accessor showThemeSnapshot_: boolean = false;
  protected accessor showUploadedImageButton_: boolean = false;
  protected accessor showSearchedImageButton_: boolean = false;
  protected accessor showManagedButton_: boolean = false;
  protected accessor showManagedDialog_: boolean = false;
  protected accessor wallpaperSearchButtonEnabled_: boolean =
      loadTimeData.getBoolean('wallpaperSearchButtonEnabled');
  private accessor wallpaperSearchEnabled_: boolean =
      loadTimeData.getBoolean('wallpaperSearchEnabled');
  private accessor footerEnabled_: boolean =
      loadTimeData.getBoolean('footerEnabled');
  protected accessor newTabPageType_: NewTabPageType =
      NewTabPageType.kFirstPartyWebUI;
  protected accessor showEditTheme_: boolean = true;
  protected accessor managedByName_: string = '';
  protected accessor managedByDesc_: string = '';
''',
   '''  static override get properties() {
    return {
      theme_: {type: Object},
      thirdPartyThemeId_: {type: String, reflect: true},
      thirdPartyThemeName_: {type: String, reflect: true},
      showClassicChromeButton_: {type: Boolean},
      showColorPicker_: {type: Boolean},
      showDeviceThemeToggle_: {type: Boolean},
      showManagedDialog_: {type: Boolean},
    };
  }

  // Bluelium : ne conserver que l’état des thèmes du navigateur.
  protected accessor theme_: Theme|undefined;
  protected accessor thirdPartyThemeId_: string|null = null;
  protected accessor thirdPartyThemeName_: string|null = null;
  protected accessor showClassicChromeButton_: boolean = false;
  protected accessor showColorPicker_: boolean = false;
  protected accessor showDeviceThemeToggle_: boolean = false;
  protected accessor showManagedDialog_: boolean = false;
'''),
  ('chrome/browser/resources/side_panel/customize_chrome/appearance.ts',
   '''      this.apiProxy_.callbackRouter.setThemeEditable.addListener(
          isThemeEditable => {
            this.showEditTheme_ = isThemeEditable;
          }),
      this.apiProxy_.callbackRouter.ntpManagedByNameUpdated.addListener(
          (name, description) => {
            this.managedByName_ = name;
            this.managedByDesc_ = description;
          }),
    ];

    this.apiProxy_.handler.updateTheme();
    this.apiProxy_.handler.updateAttachedTabState();
    this.apiProxy_.handler.updateNtpManagedByName();
  }

''',
   '''    ];

    // Bluelium : aucune souscription aux réglages ou à la gestion de la NTP.
    this.apiProxy_.handler.updateTheme();
  }

'''),
  ('chrome/browser/resources/side_panel/customize_chrome/appearance.ts',
   '''    const changedPrivateProperties =
        changedProperties as Map<PropertyKey, unknown>;

    this.editThemeButtonText_ = this.computeEditThemeButtonText_();

    if (changedPrivateProperties.has('theme_') ||
        changedPrivateProperties.has('newTabPageType_')) {
      this.thirdPartyThemeId_ = this.computeThirdPartyThemeId_();
      this.thirdPartyThemeName_ = this.computeThirdPartyThemeName_();
      this.showClassicChromeButton_ = this.computeShowClassicChromeButton_();
      this.showColorPicker_ = this.computeShowColorPicker_();
      this.showDeviceThemeToggle_ = this.computeShowDeviceThemeToggle_();
      this.showThemeSnapshot_ = this.computeShowThemeSnapshot_();
      this.showUploadedImageButton_ = this.computeShowUploadedImageButton_();
      this.showSearchedImageButton_ = this.computeShowSearchedImageButton_();
    }

    if (changedPrivateProperties.has('newTabPageType_') ||
        changedPrivateProperties.has('managedByName_') ||
        changedPrivateProperties.has('managedByDesc_')) {
      this.showManagedButton_ = this.computeShowManagedButton_();
    }

    this.showBottomDivider_ = this.computeShowBottomDivider_();

''',
   '''    const changedPrivateProperties =
        changedProperties as Map<PropertyKey, unknown>;

    // Bluelium : seules les données de thème font évoluer cette apparence.
    if (changedPrivateProperties.has('theme_')) {
      this.thirdPartyThemeId_ = this.computeThirdPartyThemeId_();
      this.thirdPartyThemeName_ = this.computeThirdPartyThemeName_();
      this.showClassicChromeButton_ = this.computeShowClassicChromeButton_();
      this.showColorPicker_ = this.computeShowColorPicker_();
      this.showDeviceThemeToggle_ = this.computeShowDeviceThemeToggle_();
    }

'''),
  ('chrome/browser/resources/side_panel/customize_chrome/appearance.ts',
   '''  focusOnThemeButton() {
    this.$.editThemeButton.focus();
  }

  private computeEditThemeButtonText_(): string {
    return this.i18n(
        this.wallpaperSearchButtonEnabled_ ? 'categoriesHeader' :
                                             'changeTheme');
  }

''',
   '''  focusOnThemeButton() {
    // Bluelium : restaurer le focus sans viser l’ancien bouton de fond NTP.
    if (this.showColorPicker_) {
      this.$.chromeColors.focus();
    } else {
      this.$.thirdPartyThemeLinkButton.focus();
    }
  }

'''),
  ('chrome/browser/resources/side_panel/customize_chrome/appearance.ts',
   '''  private computeShowBottomDivider_(): boolean {
    return this.showClassicChromeButton_ || this.showDeviceThemeToggle_;
  }

  private computeShowClassicChromeButton_(): boolean {
    if (this.footerEnabled_) {
      return !!(
          this.theme_ && this.theme_.backgroundImage &&
          (this.newTabPageType_ === NewTabPageType.kFirstPartyWebUI ||
           this.newTabPageType_ === NewTabPageType.kThirdPartyWebUI));
    }
    return !!(
        this.theme_ &&
        (this.theme_.backgroundImage || this.theme_.thirdPartyThemeInfo));
  }

''',
   '''  private computeShowClassicChromeButton_(): boolean {
    // Bluelium : réinitialiser un thème installé, sans exposer le fond NTP.
    return !!this.theme_?.thirdPartyThemeInfo;
  }

'''),
  ('chrome/browser/resources/side_panel/customize_chrome/appearance.ts',
   '''  private computeShowThemeSnapshot_(): boolean {
    return !!this.theme_ && !this.theme_.thirdPartyThemeInfo &&
        (!(this.theme_.backgroundImage &&
           this.theme_.backgroundImage.isUploadedImage)) &&
        // TODO(crbug.com/404247286) Enable snapshots for extension NTP with 1P
        // theme.
        this.newTabPageType_ === NewTabPageType.kFirstPartyWebUI;
  }

  private computeShowUploadedImageButton_(): boolean {
    return !!(
        this.theme_ && this.theme_.backgroundImage &&
        this.theme_.backgroundImage.isUploadedImage &&
        !this.theme_.backgroundImage.localBackgroundId);
  }

  private computeShowSearchedImageButton_(): boolean {
    return !!(
        this.theme_ && this.theme_.backgroundImage &&
        this.theme_.backgroundImage.localBackgroundId);
  }

  private computeShowManagedButton_(): boolean {
    return this.newTabPageType_ !== NewTabPageType.kFirstPartyWebUI &&
        !!this.managedByName_;
  }

  protected onThemeSnapshotKeydown_(e: KeyboardEvent) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      this.onEditThemeClick_();
    }
  }

  protected onEditThemeClick_() {
    recordCustomizeChromeAction(CustomizeChromeAction.EDIT_THEME_CLICKED);
    if (this.handleClickForManagedThemes_()) {
      return;
    }
    this.dispatchEvent(new Event('edit-theme-click'));
  }

  protected onWallpaperSearchClick_() {
    recordCustomizeChromeAction(
        CustomizeChromeAction.WALLPAPER_SEARCH_APPEARANCE_BUTTON_CLICKED);
    if (this.handleClickForManagedThemes_()) {
      return;
    }
    this.dispatchEvent(new Event('wallpaper-search-click'));
  }

''',
   '''  // Bluelium : navigation et édition des fonds NTP retirées.
'''),
  ('chrome/browser/resources/side_panel/customize_chrome/appearance.ts',
   '''  protected onUploadedImageButtonClick_() {
    this.apiProxy_.handler.chooseLocalCustomBackground();
  }

  protected onSearchedImageButtonClick_() {
    if (this.wallpaperSearchEnabled_) {
      this.dispatchEvent(new CustomEvent('wallpaper-search-click'));
    } else {
      this.dispatchEvent(new Event('edit-theme-click'));
    }
  }

''',
   '''  // Bluelium : l’import de fond et la recherche d’images appartiennent à Shimmer.
'''),
  ('chrome/browser/resources/side_panel/customize_chrome/appearance.ts',
   '''      // If the classicChrome button has focus, change focus to editTheme
      // button, since the button is disappearing.
''',
   '''      // Bluelium : restaurer le focus sur les couleurs après réinitialisation.
'''),
  ('chrome/browser/resources/side_panel/customize_chrome/appearance.ts',
   '''  protected onNewTabPageManageByButtonClick_() {
    this.apiProxy_.handler.openNtpManagedByPage();
  }

''',
   '''  // Bluelium : pas de lien de gestion de l’ancienne NTP.
'''),
  ('chrome/browser/ui/webui/side_panel/customize_chrome/customize_chrome_ui.cc',
   '''#if BUILDFLAG(IS_ANDROID)
  const bool wallpaper_search_enabled = false;
#else
  const bool wallpaper_search_enabled =
      customize_chrome::IsWallpaperSearchEnabledForProfile(profile_);
  if (wallpaper_search_enabled) {
    wallpaper_search_background_manager_ =
        std::make_unique<WallpaperSearchBackgroundManager>(profile_);
    wallpaper_search_string_map_ = WallpaperSearchStringMap::Create();
  }
#endif
''',
   '''  // Bluelium : Shimmer gère les fonds ; ne pas initialiser leur recherche NTP.
  const bool wallpaper_search_enabled = false;
'''),
  ('chrome/browser/ui/webui/side_panel/customize_chrome/customize_chrome_ui.cc',
   '''  source->AddBoolean(
      "modulesEnabled",
      ntp::HasModulesEnabled(module_id_details_,
                             IdentityManagerFactory::GetForProfile(profile_)));''',
   '''  // Bluelium : les cartes Chromium ne configurent pas Shimmer.
  source->AddBoolean("modulesEnabled", false);'''),
  ('chrome/browser/ui/webui/side_panel/customize_chrome/customize_chrome_ui.cc',
   '''  source->AddBoolean("footerEnabled",
                     base::FeatureList::IsEnabled(ntp_features::kNtpFooter));''',
   '''  // Bluelium : le pied de la NTP Chromium n’est pas utilisé par Shimmer.
  source->AddBoolean("footerEnabled", false);'''),
]
