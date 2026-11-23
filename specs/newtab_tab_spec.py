"""Bluelium : titre localisé et icône neutre pour l'onglet du nouvel onglet.

Deux corrections pour l'onglet du nouvel onglet (Shimmer) :
1. Titre : third_party/shimmer/index.html figeait <title>New Tab</title> en
   anglais, qui écrasait le titre initial de SearchTabHelper dès le chargement.
   GlypheShimmerUI expose désormais IDS_NEW_TAB_TITLE sous la clé « title » et
   index.html utilise <title>$i18n{title}</title> : l'onglet affiche « Nouvel
   onglet » en français et suit la langue de l'interface dans toutes les
   locales Chromium.
2. Favicon : NewTabPageUI renvoyait IDR_NTP_FAVICON (l'astérisque Bluelium),
   en doublon avec d'autres éléments de l'interface. TabUIHelper::GetFavicon()
   renvoie pour chrome://newtab et chrome://new-tab-page l'icône vectorielle
   Material kHomeIcon aux couleurs de l'onglet (kColorToolbarButtonIcon), ce
   qui reste propre même si l'onglet est épinglé ou en barre verticale repliée.
"""

SHIMMER_UI = 'chrome/browser/ui/webui/new_tab_page/glyphe_shimmer_ui.cc'
SHIMMER_HTML = 'third_party/shimmer/index.html'
TAB_UI_HELPER = 'chrome/browser/ui/tab_ui_helper.cc'
UI_BUILD = 'chrome/browser/ui/BUILD.gn'

NEW_FILES = {}

EDITS = [
    # 1. Titre localisé via IDS_NEW_TAB_TITLE et remplacement $i18n{title}.
    (SHIMMER_UI,
     '#include "chrome/common/webui_url_constants.h"\n',
     '#include "chrome/common/webui_url_constants.h"\n'
     '#include "components/strings/grit/components_strings.h"\n'),
    (SHIMMER_UI,
     '  source->SetDefaultResource(IDR_SHIMMER_INDEX_HTML);\n',
     '  // Bluelium : titre localisé du nouvel onglet ($i18n{title}).\n'
     '  source->AddLocalizedString("title", IDS_NEW_TAB_TITLE);\n'
     '  source->SetDefaultResource(IDR_SHIMMER_INDEX_HTML);\n'),
    (SHIMMER_HTML,
     '        <title>New Tab</title>\n',
     '        <!-- Bluelium : titre localisé par WebUIDataSource -->\n'
     '        <title>$i18n{title}</title>\n'),

    # 2. Icône vectorielle discrète (maison) pour le nouvel onglet.
    (UI_BUILD,
     '    deps = [\n'
     '      "//chrome/app:generated_resources",\n'
     '      "//chrome/browser/favicon",\n',
     '    deps = [\n'
     '      "//chrome/app:generated_resources",\n'
     '      "//chrome/app/vector_icons",  # Bluelium : icône du nouvel onglet.\n'
     '      "//chrome/browser/favicon",\n'),
    (TAB_UI_HELPER,
     '#include "chrome/grit/generated_resources.h"\n',
     '#include "chrome/app/vector_icons/vector_icons.h"\n'
     '#include "chrome/grit/generated_resources.h"\n'),
    (TAB_UI_HELPER,
     '#include "ui/gfx/image/image_skia.h"\n',
     '#include "ui/gfx/favicon_size.h"\n'
     '#include "ui/gfx/image/image_skia.h"\n'),
    (TAB_UI_HELPER,
     '  // When the page provides no favicon of its own, use the tab-background-aware\n',
     '  // Bluelium : icône vectorielle neutre (maison) pour le nouvel onglet,\n'
     '  // au lieu de l\'astérisque produit qui fait doublon dans l\'interface.\n'
     '  const GURL& visible_url = web_contents()->GetVisibleURL();\n'
     '  if (visible_url.SchemeIs(content::kChromeUIScheme) &&\n'
     '      (visible_url.host() == chrome::kChromeUINewTabHost ||\n'
     '       visible_url.host() == chrome::kChromeUINewTabPageHost)) {\n'
     '    retained_favicon_ = gfx::Image();\n'
     '    return ui::ImageModel::FromVectorIcon(\n'
     '        kHomeIcon, kColorToolbarButtonIcon, gfx::kFaviconSize);\n'
     '  }\n'
     '\n'
     '  // When the page provides no favicon of its own, use the tab-background-aware\n'),
]
