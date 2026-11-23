"""Bluelium : épurer le bouclier du bloqueur et le bouton IA dans la barre.

1. Bouclier uBlock :
   - Ne montrer le compteur que lorsqu'il est strictement supérieur à 0 ;
     sinon, afficher le bouclier seul dans un bouton rond 30x30 (sans réserver
     la place du chiffre), tout en préservant le nom accessible du bouton.
   - Masquer complètement le bouclier et son hôte sur les pages internes
     (chrome://, bluelium://, helium://, chrome-untrusted://, devtools://,
     chrome-error://, chrome-native://, about:*, nouvel onglet Shimmer, pages
     d'erreur et onglets sans URL), et le réafficher sur les pages web, au
     changement d'onglet comme à la navigation.

2. Bouton IA (panneau assistant) :
   - Retirer le fond circulaire plein au repos : icône seule comme les autres
     boutons de la barre, en conservant le survol/appui normal, la pastille de
     lisibilité sur page colorée (page_color_contrast_spec.py), le fond accent
     quand le panneau est ouvert, et le style trait fin en OLED/Nuit
     (dark_outline_spec.py).
"""

NEW_FILES = {}

EAVM_CC = 'chrome/browser/ui/extensions/extension_action_view_model.cc'
TAV_CC = 'chrome/browser/ui/views/toolbar/toolbar_action_view.cc'
EXT_BUILD = 'chrome/browser/ui/views/extensions/BUILD.gn'
ETD_H = 'chrome/browser/ui/views/extensions/extensions_toolbar_desktop.h'
ETD_CC = 'chrome/browser/ui/views/extensions/extensions_toolbar_desktop.cc'
PATB_CC = 'chrome/browser/ui/views/toolbar/pinned_action_toolbar_button.cc'

EDITS = [
    # -------------------------------------------------------------------------
    # 1. Compteur uBlock : chaîne vide si rien n'est bloqué (0 ou vide).
    # -------------------------------------------------------------------------
    (EAVM_CC,
     '#include <string>\n'
     '#include <utility>\n',
     '#include <string>\n'
     '#include <string_view>\n'
     '#include <utility>\n'),

    (EAVM_CC,
     '#include "base/strings/string_util.h"\n',
     '#include "base/strings/string_number_conversions.h"\n'
     '#include "base/strings/string_util.h"\n'),

    (EAVM_CC,
     'std::u16string ExtensionActionViewModel::GetGlypheBadgeText(\n'
     '    content::WebContents* web_contents) const {\n'
     '  if (!ExtensionIsValid() || !web_contents) {\n'
     '    return u"0";\n'
     '  }\n'
     '  const std::string text = extension_action_->GetDisplayBadgeText(\n'
     '      sessions::SessionTabHelper::IdForTab(web_contents).id());\n'
     '  return text.empty() ? u"0" : base::UTF8ToUTF16(text);\n'
     '}\n',
     'std::u16string ExtensionActionViewModel::GetGlypheBadgeText(\n'
     '    content::WebContents* web_contents) const {\n'
     '  // Bluelium : n\'afficher le compteur du bloqueur que s\'il est > 0.\n'
     '  if (!ExtensionIsValid() || !web_contents) {\n'
     '    return std::u16string();\n'
     '  }\n'
     '  const std::string text = extension_action_->GetDisplayBadgeText(\n'
     '      sessions::SessionTabHelper::IdForTab(web_contents).id());\n'
     '  const std::string_view trimmed =\n'
     '      base::TrimWhitespaceASCII(text, base::TRIM_ALL);\n'
     '  if (trimmed.empty()) {\n'
     '    return std::u16string();\n'
     '  }\n'
     '  int count = 0;\n'
     '  if (base::StringToInt(trimmed, &count) && count <= 0) {\n'
     '    return std::u16string();\n'
     '  }\n'
     '  return base::UTF8ToUTF16(trimmed);\n'
     '}\n'),

    # -------------------------------------------------------------------------
    # 2. Vue du bouclier : bouton rond 30x30 sans espace réservé quand vide.
    # -------------------------------------------------------------------------
    (TAV_CC,
     '  if (view_model_->GetId() == "blockjmkbacgjkknlgpkjjiijinjdanf") {\n'
     '    // ID fixe du composant uBlock de Helium : garder son popup et son moteur.\n'
     '    const auto* extension_model =\n'
     '        static_cast<ExtensionActionViewModel*>(view_model_.get());\n'
     '    SetText(extension_model->GetGlypheBadgeText(web_contents));\n'
     '    label()->SetFontList(gfx::FontList("Instrument Sans, 12px"));\n'
     '    SetEnabledTextColors(kColorToolbarButtonIcon);\n'
     '    SetImageLabelSpacing(4);\n'
     '    SetMinSize(gfx::Size(30, 30));\n'
     '    SetBorder(views::CreateEmptyBorder(gfx::Insets::TLBR(0, 7, 0, 9)));\n',
     '  if (view_model_->GetId() == "blockjmkbacgjkknlgpkjjiijinjdanf") {\n'
     '    // ID fixe du composant uBlock de Helium : garder son popup et son moteur.\n'
     '    // Bluelium : sans compteur (> 0), bouclier seul dans un bouton rond 30x30.\n'
     '    const auto* extension_model =\n'
     '        static_cast<ExtensionActionViewModel*>(view_model_.get());\n'
     '    const std::u16string badge =\n'
     '        extension_model->GetGlypheBadgeText(web_contents);\n'
     '    const bool has_badge = !badge.empty();\n'
     '    SetText(badge);\n'
     '    // Bluelium : LabelButton::SetText écrase le nom accessible ; le restaurer.\n'
     '    GetViewAccessibility().SetName(\n'
     '        view_model_->GetAccessibleName(web_contents));\n'
     '    label()->SetFontList(gfx::FontList("Instrument Sans, 12px"));\n'
     '    SetEnabledTextColors(kColorToolbarButtonIcon);\n'
     '    SetImageLabelSpacing(has_badge ? 4 : 0);\n'
     '    SetMinSize(gfx::Size(30, 30));\n'
     '    const gfx::Insets insets = has_badge ? gfx::Insets::TLBR(0, 7, 0, 9)\n'
     '                                         : gfx::Insets::TLBR(0, 6, 0, 6);\n'
     '    if (!GetBorder() || GetBorder()->GetInsets() != insets) {\n'
     '      SetBorder(views::CreateEmptyBorder(insets));\n'
     '    }\n'),

    # -------------------------------------------------------------------------
    # 3. Masquage complet du bouclier (et de son hôte) sur les pages internes.
    # -------------------------------------------------------------------------
    (EXT_BUILD,
     '    "//chrome/browser/user_education",\n'
     '    "//ui/base/dragdrop/mojom",\n'
     '    "//ui/color",\n'
     '    "//ui/gfx",\n'
     '    "//ui/gfx/geometry",\n'
     '  ]\n'
     '}\n',
     '    "//chrome/browser/user_education",\n'
     '    "//content/public/browser",\n'
     '    "//content/public/common",\n'
     '    "//ui/base/dragdrop/mojom",\n'
     '    "//ui/color",\n'
     '    "//ui/gfx",\n'
     '    "//ui/gfx/geometry",\n'
     '    "//url",\n'
     '  ]\n'
     '}\n'),

    (ETD_H,
     '  void UpdateIconVisibility(const std::string& extension_id);\n',
     '  void UpdateIconVisibility(const std::string& extension_id);\n'
     '\n'
     '  // Bluelium : visibilité du bouclier (masqué sur les pages internes).\n'
     '  bool ShouldShowBlueliumBlocker() const;\n'
     '  void UpdateBlueliumBlockerVisibility();\n'),

    (ETD_CC,
     '#include "content/public/browser/web_contents.h"\n',
     '#include "content/public/browser/render_frame_host.h"\n'
     '#include "content/public/browser/web_contents.h"\n'
     '#include "content/public/common/url_constants.h"\n'
     '#include "url/gurl.h"\n'
     '#include "url/url_constants.h"\n'),

    (ETD_CC,
     '// Bluelium : identifiant du composant uBlock fourni par Helium.\n'
     'constexpr char kBlueliumBlockerActionId[] = "blockjmkbacgjkknlgpkjjiijinjdanf";\n',
     '// Bluelium : identifiant du composant uBlock fourni par Helium.\n'
     'constexpr char kBlueliumBlockerActionId[] = "blockjmkbacgjkknlgpkjjiijinjdanf";\n'
     '\n'
     '// Bluelium : pages internes et pages d\'erreur où le bloqueur n\'agit pas.\n'
     'bool IsBlueliumInternalPage(content::WebContents* web_contents) {\n'
     '  if (!web_contents) {\n'
     '    return true;\n'
     '  }\n'
     '  const auto* main_frame = web_contents->GetPrimaryMainFrame();\n'
     '  if (main_frame && main_frame->IsErrorDocument()) {\n'
     '    return true;\n'
     '  }\n'
     '  const GURL& committed_url = web_contents->GetLastCommittedURL();\n'
     '  const GURL& page_url =\n'
     '      committed_url.is_empty() ? web_contents->GetVisibleURL() : committed_url;\n'
     '  if (page_url.is_empty()) {\n'
     '    return true;\n'
     '  }\n'
     '  return page_url.SchemeIs(content::kChromeUIScheme) ||\n'
     '         page_url.SchemeIs(content::kChromeUIUntrustedScheme) ||\n'
     '         page_url.SchemeIs(content::kChromeDevToolsScheme) ||\n'
     '         page_url.SchemeIs(content::kChromeErrorScheme) ||\n'
     '         page_url.SchemeIs(content::kChromeNativeScheme) ||\n'
     '         page_url.SchemeIs(content::kHeliumUIScheme) ||\n'
     '         page_url.SchemeIs("helium") ||\n'
     '         page_url.SchemeIs(url::kAboutScheme);\n'
     '}\n'),

    (ETD_CC,
     '  for (const auto& icon : icons_) {\n'
     '    icon.second->UpdateState();\n'
     '  }\n'
     '\n'
     '  if (close_side_panel_button_) {\n',
     '  for (const auto& icon : icons_) {\n'
     '    icon.second->UpdateState();\n'
     '  }\n'
     '  // Bluelium : masquer le bouclier sur les pages internes et erreurs.\n'
     '  UpdateBlueliumBlockerVisibility();\n'
     '\n'
     '  if (close_side_panel_button_) {\n'),

    (ETD_CC,
     '  // Bluelium : le bouclier séparé ne dépend plus du layout des extensions.\n'
     '  const bool visible =\n'
     '      must_show || (ToolbarActionsModel::CanShowActionsInToolbar(*browser_) &&\n'
     '                    model_->IsActionPinned(extension_id));\n'
     '  if (action_view->parent() != this) {\n'
     '    action_view->SetVisible(visible);\n',
     '  // Bluelium : le bouclier séparé ne dépend plus du layout des extensions.\n'
     '  const bool visible =\n'
     '      must_show || (ToolbarActionsModel::CanShowActionsInToolbar(*browser_) &&\n'
     '                    model_->IsActionPinned(extension_id));\n'
     '  if (action_view->parent() != this) {\n'
     '    UpdateBlueliumBlockerVisibility();\n'),

    (ETD_CC,
     '// Bluelium : déplacer la vue existante, sans dupliquer l\'action uBlock.\n'
     'void ExtensionsToolbarDesktop::SetBlueliumBlockerHost(\n'
     '    views::View* host) {\n'
     '  if (bluelium_blocker_host_ == host) {\n'
     '    return;\n'
     '  }\n'
     '  ToolbarActionView* blocker = GetViewForId(kBlueliumBlockerActionId);\n'
     '  bluelium_blocker_host_ = host;\n'
     '  if (blocker) {\n'
     '    auto owned_blocker = blocker->parent()->RemoveChildViewT(blocker);\n'
     '    views::View* target = host ? host : this;\n'
     '    target->AddChildView(std::move(owned_blocker));\n'
     '  }\n'
     '  ReorderAllChildViews();\n'
     '}\n',
     '// Bluelium : déterminer si le bouclier doit apparaître pour l\'onglet actif.\n'
     'bool ExtensionsToolbarDesktop::ShouldShowBlueliumBlocker() const {\n'
     '  if (ShouldForceVisibility(kBlueliumBlockerActionId)) {\n'
     '    return true;\n'
     '  }\n'
     '  if (!browser_ || !model_ ||\n'
     '      !ToolbarActionsModel::CanShowActionsInToolbar(*browser_) ||\n'
     '      !model_->IsActionPinned(kBlueliumBlockerActionId)) {\n'
     '    return false;\n'
     '  }\n'
     '  tabs::TabInterface* const tab = browser_->GetActiveTabInterface();\n'
     '  content::WebContents* const web_contents = tab ? tab->GetContents() : nullptr;\n'
     '  return !IsBlueliumInternalPage(web_contents);\n'
     '}\n'
     '\n'
     'void ExtensionsToolbarDesktop::UpdateBlueliumBlockerVisibility() {\n'
     '  ToolbarActionView* const blocker = GetViewForId(kBlueliumBlockerActionId);\n'
     '  const bool visible = blocker && ShouldShowBlueliumBlocker();\n'
     '  if (blocker && blocker->parent() != this) {\n'
     '    blocker->SetVisible(visible);\n'
     '  }\n'
     '  if (bluelium_blocker_host_) {\n'
     '    bluelium_blocker_host_->SetVisible(visible);\n'
     '  }\n'
     '}\n'
     '\n'
     '// Bluelium : déplacer la vue existante, sans dupliquer l\'action uBlock.\n'
     'void ExtensionsToolbarDesktop::SetBlueliumBlockerHost(\n'
     '    views::View* host) {\n'
     '  if (bluelium_blocker_host_ == host) {\n'
     '    return;\n'
     '  }\n'
     '  ToolbarActionView* blocker = GetViewForId(kBlueliumBlockerActionId);\n'
     '  bluelium_blocker_host_ = host;\n'
     '  if (blocker) {\n'
     '    auto owned_blocker = blocker->parent()->RemoveChildViewT(blocker);\n'
     '    views::View* target = host ? host : this;\n'
     '    target->AddChildView(std::move(owned_blocker));\n'
     '  }\n'
     '  if (host) {\n'
     '    UpdateBlueliumBlockerVisibility();\n'
     '  }\n'
     '  ReorderAllChildViews();\n'
     '}\n'),

    (ETD_CC,
     '  icons_.insert({action_id, host->AddChildView(std::move(icon))});\n'
     '}\n',
     '  icons_.insert({action_id, host->AddChildView(std::move(icon))});\n'
     '  // Bluelium : synchroniser le bouclier et son hôte dès sa création.\n'
     '  if (action_id == kBlueliumBlockerActionId && bluelium_blocker_host_) {\n'
     '    UpdateBlueliumBlockerVisibility();\n'
     '  }\n'
     '}\n'),

    (ETD_CC,
     '    // Bluelium : le bouclier peut appartenir à son hôte séparé.\n'
     '    action_view->parent()->RemoveChildViewT(action_view);\n'
     '    icons_.erase(action_id);\n'
     '  }\n',
     '    // Bluelium : le bouclier peut appartenir à son hôte séparé.\n'
     '    action_view->parent()->RemoveChildViewT(action_view);\n'
     '    icons_.erase(action_id);\n'
     '    if (action_id == kBlueliumBlockerActionId && bluelium_blocker_host_) {\n'
     '      bluelium_blocker_host_->SetVisible(false);\n'
     '    }\n'
     '  }\n'),

    # -------------------------------------------------------------------------
    # 4. Bouton IA : pas de fond circulaire au repos (icône seule).
    # -------------------------------------------------------------------------
    (PATB_CC,
     '  const SkColor page_background =\n'
     '      colors->GetColor(kColorGlyphePageColorButtonBackground);\n'
     '  // Bluelium : au repos, la même pastille lisible que les autres outils.\n'
     '  const SkColor background = glyphe_active ? seed\n'
     '      : SkColorGetA(page_background) != SK_AlphaTRANSPARENT\n'
     '          ? page_background\n'
     '          : color_utils::AlphaBlend(icon, colors->GetColor(kColorToolbar),\n'
     '                                    SkAlpha{0x14});\n'
     '  SetBackground(views::CreateRoundedRectBackground(\n'
     '      ui::BlueliumDarkOutline() && glyphe_active ? SK_ColorTRANSPARENT : background, 15));\n',
     '  const SkColor page_background =\n'
     '      colors->GetColor(kColorGlyphePageColorButtonBackground);\n'
     '  const bool has_page_background =\n'
     '      SkColorGetA(page_background) != SK_AlphaTRANSPARENT;\n'
     '  // Bluelium : au repos, icône seule sans fond rond (sauf pastille de\n'
     '  // lisibilité sur page colorée) ; panneau ouvert : accent ou anneau OLED/Nuit.\n'
     '  if (glyphe_active && !ui::BlueliumDarkOutline()) {\n'
     '    SetBackground(views::CreateRoundedRectBackground(seed, 15));\n'
     '  } else if (!glyphe_active && has_page_background) {\n'
     '    SetBackground(views::CreateRoundedRectBackground(page_background, 15));\n'
     '  } else {\n'
     '    SetBackground(nullptr);\n'
     '  }\n'),
]
