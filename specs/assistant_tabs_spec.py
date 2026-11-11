# Helium Glyphe — onglet IA (maquette « Onglet IA »).
# Remplace les deux entrées Claude / ChatGPT de assistant-side-panel par une
# seule : un bouton dans la barre d'outils, au logo du dernier assistant
# utilisé, ouvre un panneau de 440 px sans en-tête Chromium. En haut, un groupe
# segmenté Claude · ChatGPT · Gemini · Le Chat et un bouton de fermeture ;
# dessous, une vraie vue web par assistant (session du profil), gardée en vie
# quand on change d'onglet. Pref de profil glyphe.assistant.current.
# Raccourcis : Alt+Maj+C ouvre Claude, Alt+Maj+G ChatGPT (bascule si déjà
# affiché) ; la commande « Ouvrir l'onglet IA » rouvre le dernier.
import runpy
from pathlib import Path

ICONS = Path(__file__).resolve().parent.parent / 'assets/icons'
if not ICONS.is_dir():
  ICONS = Path(__file__).with_name('icons')
OLD = runpy.run_path(str(Path(__file__).with_name('assistant_spec.py')))['NEW_FILES']
SP = 'chrome/browser/ui/views/side_panel/'


def c_array(name, data):
  body = ', '.join(f'0x{b:02x}' for b in data)
  return f'constexpr uint8_t {name}[] = {{{body}}};\n'


logos_inc = ('// Masques des logos (16 et 32 px, alpha seulement).\n'
             + c_array('kClaudePng', (ICONS / 'claude_16.png').read_bytes())
             + c_array('kClaudePng2x', (ICONS / 'claude_32.png').read_bytes())
             + c_array('kChatGptPng', (ICONS / 'chatgpt_16.png').read_bytes())
             + c_array('kChatGptPng2x', (ICONS / 'chatgpt_32.png').read_bytes())
             + c_array('kGeminiPng', (ICONS / 'gemini_16.png').read_bytes())
             + c_array('kGeminiPng2x', (ICONS / 'gemini_32.png').read_bytes())
             + c_array('kLeChatPng', (ICONS / 'mistral_16.png').read_bytes())
             + c_array('kLeChatPng2x', (ICONS / 'mistral_32.png').read_bytes()))

NEW_H = '''// Helium Glyphe — onglet IA : Claude, ChatGPT, Gemini et Le Chat.
#ifndef CHROME_BROWSER_UI_VIEWS_SIDE_PANEL_GLYPHE_ASSISTANT_H_
#define CHROME_BROWSER_UI_VIEWS_SIDE_PANEL_GLYPHE_ASSISTANT_H_

#include "ui/base/models/image_model.h"

class BrowserWindowInterface;
class Profile;
class SidePanelRegistry;

namespace glyphe {

// 0 Claude, 1 ChatGPT, 2 Gemini, 3 Le Chat.
inline constexpr int kAssistantCount = 4;

// Enregistre l’entrée « Onglet IA » dans le registre de la fenêtre.
void RegisterAssistantEntries(BrowserWindowInterface* browser,
                              SidePanelRegistry* registry);

// Logo de l’assistant en masque monochrome, teinté avec kColorIcon.
ui::ImageModel AssistantIcon(int index);

// Assistant affiché en dernier (pref glyphe.assistant.current).
int CurrentAssistant(Profile* profile);

// Ouvre l’onglet IA sur l’assistant `index` (-1 : le dernier), ou le ferme
// s’il l’affiche déjà.
void ToggleAssistant(BrowserWindowInterface* browser, int index);

}  // namespace glyphe

#endif  // CHROME_BROWSER_UI_VIEWS_SIDE_PANEL_GLYPHE_ASSISTANT_H_
'''

NEW_CC = '''// Helium Glyphe — onglet IA : Claude, ChatGPT, Gemini et Le Chat.
#include "chrome/browser/ui/views/side_panel/glyphe_assistant.h"

#include <array>
#include <cstdint>
#include <memory>

#include "base/containers/span.h"
#include "base/functional/bind.h"
#include "base/memory/raw_ptr.h"
#include "chrome/browser/profiles/profile.h"
#include "chrome/browser/ui/actions/chrome_action_id.h"
#include "chrome/browser/ui/browser_actions.h"  // nogncheck
#include "chrome/browser/ui/browser_window/public/browser_window_interface.h"
#include "chrome/browser/ui/side_panel/side_panel_entry.h"
#include "chrome/browser/ui/side_panel/side_panel_entry_id.h"
#include "chrome/browser/ui/side_panel/side_panel_entry_key.h"
#include "chrome/browser/ui/side_panel/side_panel_entry_scope.h"
#include "chrome/browser/ui/side_panel/side_panel_registry.h"
#include "chrome/browser/ui/side_panel/side_panel_ui.h"
#include "chrome/common/pref_names.h"
#include "components/prefs/pref_change_registrar.h"
#include "components/prefs/pref_service.h"
#include "components/vector_icons/vector_icons.h"
#include "ui/accessibility/ax_enums.mojom.h"\n#include "ui/actions/actions.h"
#include "ui/base/metadata/metadata_header_macros.h"
#include "ui/base/metadata/metadata_impl_macros.h"
#include "ui/color/color_id.h"
#include "ui/color/color_provider.h"
#include "ui/gfx/geometry/insets.h"
#include "ui/gfx/image/image.h"
#include "ui/gfx/image/image_skia.h"
#include "ui/gfx/image/image_skia_operations.h"
#include "ui/gfx/image/image_skia_rep.h"
#include "ui/views/accessibility/view_accessibility.h"
#include "ui/views/background.h"
#include "ui/views/border.h"
#include "ui/views/controls/button/image_button.h"
#include "ui/views/controls/button/image_button_factory.h"
#include "ui/views/controls/button/label_button.h"
#include "ui/views/controls/separator.h"
#include "ui/views/controls/webview/webview.h"
#include "ui/views/layout/box_layout.h"
#include "ui/views/view.h"
#include "url/gurl.h"

namespace glyphe {

namespace {

#include "chrome/browser/ui/views/side_panel/glyphe_assistant_logos.inc"

constexpr int kAssistantPanelWidth = 440;

struct AssistantInfo {
  const char16_t* name;
  const char* url;
  base::span<const uint8_t> png;
  base::span<const uint8_t> png_2x;
};

AssistantInfo GetInfo(int index) {
  switch (index) {
    case 1:
      return {u"ChatGPT", "https://chatgpt.com/", kChatGptPng, kChatGptPng2x};
    case 2:
      return {u"Gemini", "https://gemini.google.com/app", kGeminiPng,
              kGeminiPng2x};
    case 3:
      return {u"Le Chat", "https://chat.mistral.ai/chat", kLeChatPng,
              kLeChatPng2x};
    default:
      return {u"Claude", "https://claude.ai/new", kClaudePng, kClaudePng2x};
  }
}

int ClampIndex(int index) {
  return index >= 0 && index < kAssistantCount ? index : 0;
}

gfx::ImageSkia LoadLogo(int index) {
  const AssistantInfo info = GetInfo(index);
  gfx::ImageSkia image =
      gfx::Image::CreateFrom1xPNGBytes(info.png).AsImageSkia();
  gfx::ImageSkia image_2x =
      gfx::Image::CreateFrom1xPNGBytes(info.png_2x).AsImageSkia();
  if (!image_2x.isNull()) {
    image.AddRepresentation(
        gfx::ImageSkiaRep(image_2x.GetRepresentation(1.0f).GetBitmap(), 2.0f));
  }
  return image;
}

// Le bouton de la barre d’outils porte le logo du dernier assistant.
void UpdateToolbarAction(BrowserWindowInterface* browser, int index) {
  BrowserActions* browser_actions = BrowserActions::From(browser);
  if (!browser_actions) {
    return;
  }
  actions::ActionItem* item = actions::ActionManager::Get().FindAction(
      kActionSidePanelShowGlypheAssistant,
      browser_actions->root_action_item());
  if (!item) {
    return;
  }
  item->SetImage(AssistantIcon(index));
  item->SetTooltipText(std::u16string(u"Onglet IA · ") + GetInfo(index).name);
}

// Panneau : groupe segmenté + fermeture en haut, vues web dessous.
class AssistantView : public views::View {
  METADATA_HEADER(AssistantView, views::View)

 public:
  explicit AssistantView(BrowserWindowInterface* browser)
      : browser_(browser), profile_(browser->GetProfile()) {
    auto* layout = SetLayoutManager(std::make_unique<views::BoxLayout>(
        views::BoxLayout::Orientation::kVertical));

    // En-tête de 48 px.
    auto* header = AddChildView(std::make_unique<views::View>());
    auto* header_layout =
        header->SetLayoutManager(std::make_unique<views::BoxLayout>(
            views::BoxLayout::Orientation::kHorizontal,
            gfx::Insets::TLBR(7, 10, 7, 9), 4));
    header_layout->set_cross_axis_alignment(
        views::BoxLayout::CrossAxisAlignment::kCenter);

    auto* group = header->AddChildView(std::make_unique<views::View>());
    group->SetLayoutManager(std::make_unique<views::BoxLayout>(
        views::BoxLayout::Orientation::kHorizontal, gfx::Insets(3), 2));
    group->SetBackground(
        views::CreateRoundedRectBackground(ui::kColorSysNeutralContainer, 10));
    group->GetViewAccessibility().SetRole(ax::mojom::Role::kGroup);
    group->GetViewAccessibility().SetName(std::u16string(u"Assistant"));

    for (int i = 0; i < kAssistantCount; ++i) {
      auto button = std::make_unique<views::LabelButton>(
          base::BindRepeating(&AssistantView::OnPicked, base::Unretained(this),
                              i),
          GetInfo(i).name);
      button->SetHorizontalAlignment(gfx::ALIGN_CENTER);
      button->SetBorder(views::CreateEmptyBorder(gfx::Insets::VH(0, 12)));
      button->SetMinSize(gfx::Size(0, 28));
      buttons_[i] = group->AddChildView(std::move(button));
    }

    auto* spacer = header->AddChildView(std::make_unique<views::View>());
    header_layout->SetFlexForView(spacer, 1);

    auto* close = header->AddChildView(
        views::CreateVectorImageButtonWithNativeTheme(
            base::BindRepeating(&AssistantView::OnClose,
                                base::Unretained(this)),
            vector_icons::kCloseIcon, 16));
    close->SetTooltipText(u"Fermer l’onglet IA");
    close->GetViewAccessibility().SetName(std::u16string(u"Fermer l’onglet IA"));
    close->SetPreferredSize(gfx::Size(30, 30));

    AddChildView(std::make_unique<views::Separator>());

    body_ = AddChildView(std::make_unique<views::View>());
    body_->SetUseDefaultFillLayout(true);
    layout->SetFlexForView(body_, 1);

    registrar_.Init(profile_->GetPrefs());
    registrar_.Add(prefs::kGlypheAssistantCurrent,
                   base::BindRepeating(&AssistantView::Sync,
                                       base::Unretained(this)));
    Sync();
  }

 private:
  void Sync() {
    const int current = CurrentAssistant(profile_);
    if (!web_views_[current]) {
      auto web_view = std::make_unique<views::WebView>(profile_);
      web_view->LoadInitialURL(GURL(GetInfo(current).url));
      web_views_[current] = body_->AddChildView(std::move(web_view));
    }
    for (int i = 0; i < kAssistantCount; ++i) {
      if (web_views_[i]) {
        web_views_[i]->SetVisible(i == current);
      }
      const bool on = i == current;
      buttons_[i]->SetBackground(
          on ? views::CreateRoundedRectBackground(ui::kColorSysBase, 8)
             : nullptr);
      buttons_[i]->SetEnabledTextColors(
          on ? ui::kColorSysOnSurface : ui::kColorSysOnSurfaceSecondary);
    }
    InvalidateLayout();
  }

  void OnPicked(int index) {
    profile_->GetPrefs()->SetInteger(prefs::kGlypheAssistantCurrent, index);
    UpdateToolbarAction(browser_, index);
  }

  void OnClose() { SidePanelUI::From(browser_)->Close(); }

  raw_ptr<BrowserWindowInterface> browser_;
  raw_ptr<Profile> profile_;
  std::array<raw_ptr<views::LabelButton>, kAssistantCount> buttons_ = {};
  std::array<raw_ptr<views::WebView>, kAssistantCount> web_views_ = {};
  raw_ptr<views::View> body_ = nullptr;
  PrefChangeRegistrar registrar_;
};

BEGIN_METADATA(AssistantView)
END_METADATA

std::unique_ptr<views::View> CreateAssistantView(SidePanelEntryScope& scope) {
  return std::make_unique<AssistantView>(&scope.GetBrowserWindowInterface());
}

}  // namespace

void RegisterAssistantEntries(BrowserWindowInterface* browser,
                              SidePanelRegistry* registry) {
  auto entry = std::make_unique<SidePanelEntry>(
      SidePanelEntry::Key(SidePanelEntryId::kGlypheAssistant),
      base::BindRepeating(&CreateAssistantView),
      base::BindRepeating([]() { return kAssistantPanelWidth; }));
  // L’en-tête est dans la vue (groupe segmenté et fermeture).
  entry->set_should_show_header(false);
  registry->Register(std::move(entry));
}

ui::ImageModel AssistantIcon(int index) {
  return ui::ImageModel::FromImageGenerator(
      base::BindRepeating(
          [](gfx::ImageSkia image, const ui::ColorProvider* provider) {
            return gfx::ImageSkiaOperations::CreateColorMask(
                image, provider->GetColor(ui::kColorIcon));
          },
          LoadLogo(ClampIndex(index))),
      gfx::Size(16, 16));
}

int CurrentAssistant(Profile* profile) {
  return ClampIndex(
      profile->GetPrefs()->GetInteger(prefs::kGlypheAssistantCurrent));
}

void ToggleAssistant(BrowserWindowInterface* browser, int index) {
  SidePanelUI* side_panel = SidePanelUI::From(browser);
  if (!side_panel) {
    return;
  }
  Profile* profile = browser->GetProfile();
  const int target = index < 0 ? CurrentAssistant(profile) : ClampIndex(index);
  const SidePanelEntryKey key(SidePanelEntryId::kGlypheAssistant);
  if (side_panel->IsSidePanelEntryShowing(key) &&
      CurrentAssistant(profile) == target) {
    side_panel->Close();
    return;
  }
  profile->GetPrefs()->SetInteger(prefs::kGlypheAssistantCurrent, target);
  UpdateToolbarAction(browser, target);
  side_panel->Show(key, SidePanelOpenTrigger::kToolbarButton);
}

}  // namespace glyphe
'''

# Ajustements mesurés sur la planche Onglet IA (11 novembre 2026).
# Les quatre segments de la référence ne contiennent pas de logos.
NEW_CC = NEW_CC.replace('#include "ui/views/controls/separator.h"',
    '#include "ui/views/controls/separator.h"\n#include "ui/views/controls/label.h"\n#include "ui/gfx/font_list.h"')
NEW_CC = NEW_CC.replace('    // En-tête de 48 px.',
    '    SetBackground(views::CreateSolidBackground(ui::kColorSysBase));\n    // En-tête de 48 px.')
NEW_CC = NEW_CC.replace('    auto* group = header->AddChildView',
    '    header->SetPreferredSize(gfx::Size(440, 48));\n\n    auto* group = header->AddChildView')
NEW_CC = NEW_CC.replace('ui::kColorSysNeutralContainer, 10',
    'ui::kColorSysSurfaceVariant, 10')
NEW_CC = NEW_CC.replace('// Panneau : groupe segmenté + fermeture en haut, vues web dessous.',
    'class AssistantButton : public views::LabelButton {\n'
    '  METADATA_HEADER(AssistantButton, views::LabelButton)\n'
    ' public:\n'
    '  AssistantButton(PressedCallback callback, std::u16string_view text)\n'
    '      : LabelButton(std::move(callback), text) {\n'
    '    label()->SetFontList(gfx::FontList("Instrument Sans, Medium 13px"));\n'
    '  }\n'
    '};\n\n'
    'BEGIN_METADATA(AssistantButton)\nEND_METADATA\n\n'
    '// Panneau : groupe segmenté + fermeture en haut, vues web dessous.')
NEW_CC = NEW_CC.replace('std::make_unique<views::LabelButton>(',
                        'std::make_unique<AssistantButton>(')
NEW_CC = NEW_CC.replace('ui::kColorSysOnSurfaceSecondary);',
    'ui::kColorSysOnSurfaceVariant);')
# Pas de pied de page (retour du 11 nov.) : le panneau s’arrête à la vue web.
NEW_CC = NEW_CC.replace('#include "base/containers/span.h"',
    '#include "base/containers/span.h"\n#include "base/strings/utf_string_conversions.h"')

# Planche Onglet IA (retour du 11 nov.) : fond de l’onglet actif comme la
# planche (aside = onglet actif = segment actif) et coins arrondis. Le panneau
# peint dans un calque : ContentParentView arrondit alors ses coins comme ceux
# de la page (sinon le fond plein recouvrait l’arrondi).
for _old, _new in [
    ('    SetBackground(views::CreateSolidBackground(ui::kColorSysBase));\n',
     '    SetPaintToLayer();\n'
     '    layer()->SetFillsBoundsOpaquely(false);\n'
     '    SetBackground(\n'
     '        views::CreateSolidBackground(kColorTabBackgroundActiveFrameActive));\n'),
    ('views::CreateRoundedRectBackground(ui::kColorSysBase, 8)',
     'views::CreateRoundedRectBackground(\n'
     '                 kColorTabBackgroundActiveFrameActive, 8)'),
    ('#include "chrome/common/pref_names.h"\n',
     '#include "chrome/browser/ui/color/chrome_color_id.h"\n'
     '#include "chrome/common/pref_names.h"\n'),
    ('#include "ui/color/color_provider.h"\n',
     '#include "ui/color/color_provider.h"\n#include "ui/compositor/layer.h"\n'),
]:
  assert NEW_CC.count(_old) == 1, _old
  NEW_CC = NEW_CC.replace(_old, _new)

# Finitions de reference_finishing intégrées ici (elles remplaçaient tout le
# fichier, ce qui cassait la série dès que ce fichier changeait) : fond teinté
# du groupe et trait fin sous l’en-tête, recalculés au changement de thème.
for _old, _new in [
    ('#include "ui/gfx/font_list.h"\n',
     '#include "ui/gfx/font_list.h"\n#include "ui/gfx/color_utils.h"\n'),
    ('    auto* group = header->AddChildView(std::make_unique<views::View>());\n',
     '    group_ = header->AddChildView(std::make_unique<views::View>());\n'
     '    auto* group = group_.get();\n'),
    ('    AddChildView(std::make_unique<views::Separator>());\n',
     '    separator_ = AddChildView(std::make_unique<views::View>());\n'
     '    separator_->SetPreferredSize(gfx::Size(440, 1));\n'),
    (' private:\n  void Sync() {',
     '  void OnThemeChanged() override {\n'
     '    views::View::OnThemeChanged();\n'
     '    const auto* colors = GetColorProvider();\n'
     '    // Teinte : l’accent en clair, le texte en sombre (l’accent y manque\n'
     '    // de contraste), comme les états du thème Prism.\n'
     '    const SkColor panel =\n'
     '        colors->GetColor(kColorTabBackgroundActiveFrameActive);\n'
     '    const bool dark = color_utils::IsDark(panel);\n'
     '    const SkColor tint = colors->GetColor(\n'
     '        dark ? ui::kColorSysOnSurface : ui::kColorSysPrimary);\n'
     '    group_->SetBackground(views::CreateRoundedRectBackground(\n'
     '        color_utils::AlphaBlend(tint, panel,\n'
     '                                static_cast<SkAlpha>(dark ? 0x24 : 0x14)),\n'
     '        10));\n'
     '    separator_->SetBackground(views::CreateSolidBackground(\n'
     '        SkColorSetA(tint, dark ? 0x26 : 0x1a)));\n'
     '  }\n\n'
     ' private:\n  void Sync() {'),
    ('  std::array<raw_ptr<views::WebView>, kAssistantCount> web_views_ = {};\n',
     '  std::array<raw_ptr<views::WebView>, kAssistantCount> web_views_ = {};\n'
     '  raw_ptr<views::View> group_ = nullptr;\n'
     '  raw_ptr<views::View> separator_ = nullptr;\n'),
]:
  assert NEW_CC.count(_old) == 1, _old
  NEW_CC = NEW_CC.replace(_old, _new)

NEW_FILES = {
  SP + 'glyphe_assistant_logos.inc': logos_inc,
}

OLD_ACTIONS = (
  '  // Helium Glyphe : assistants épinglables dans la barre d’outils.\n'
  '  for (const auto& [glyphe_id, glyphe_action, glyphe_name] :\n'
  '       {std::tuple(SidePanelEntryId::kGlypheClaude,\n'
  '                   kActionSidePanelShowGlypheClaude, u"Claude"),\n'
  '        std::tuple(SidePanelEntryId::kGlypheChatGPT,\n'
  '                   kActionSidePanelShowGlypheChatGPT, u"ChatGPT")}) {\n'
  '    root_action_item_->AddChild(\n'
  '        actions::ActionItem::Builder(\n'
  '            CreateToggleSidePanelActionCallback(SidePanelEntryKey(glyphe_id),\n'
  '                                                bwi))\n'
  '            .SetActionId(glyphe_action)\n'
  '            .SetText(glyphe_name)\n'
  '            .SetTooltipText(glyphe_name)\n'
  '            .SetImage(glyphe::AssistantIcon(glyphe_id))\n'
  '            .SetProperty(actions::kActionItemPinnableKey,\n'
  '                         std::underlying_type_t<actions::ActionPinnableState>(\n'
  '                             actions::ActionPinnableState::kPinnable))\n'
  '            .Build());\n'
  '  }\n')

NEW_ACTIONS = (
  '  // Helium Glyphe : bouton unique de l’onglet IA, au logo du dernier\n'
  '  // assistant utilisé.\n'
  '  {\n'
  '    const int glyphe_assistant = glyphe::CurrentAssistant(profile);\n'
  '    root_action_item_->AddChild(\n'
  '        actions::ActionItem::Builder(\n'
  '            CreateToggleSidePanelActionCallback(\n'
  '                SidePanelEntryKey(SidePanelEntryId::kGlypheAssistant), bwi))\n'
  '            .SetActionId(kActionSidePanelShowGlypheAssistant)\n'
  '            .SetText(u"Onglet IA")\n'
  '            .SetTooltipText(u"Onglet IA")\n'
  '            .SetImage(glyphe::AssistantIcon(glyphe_assistant))\n'
  '            .SetProperty(actions::kActionItemPinnableKey,\n'
  '                         std::underlying_type_t<actions::ActionPinnableState>(\n'
  '                             actions::ActionPinnableState::kPinnable))\n'
  '            .Build());\n'
  '  }\n')

EDITS = [
  (SP + 'glyphe_assistant.h', OLD[SP + 'glyphe_assistant.h'], NEW_H),
  (SP + 'glyphe_assistant.cc', OLD[SP + 'glyphe_assistant.cc'], NEW_CC),

  ('chrome/browser/ui/side_panel/side_panel_entry_id.h',
   '  V(kGlypheChatGPT, kActionSidePanelShowGlypheChatGPT, "GlypheChatGPT")       \\\n',
   '  V(kGlypheChatGPT, kActionSidePanelShowGlypheChatGPT, "GlypheChatGPT")       \\\n'
   '  V(kGlypheAssistant, kActionSidePanelShowGlypheAssistant, "GlypheAssistant") \\\n'),
  ('chrome/browser/ui/actions/chrome_action_id.h',
   '  E(kActionSidePanelShowGlypheChatGPT, IDC_GLYPHE_ASSISTANT_CHATGPT) \\\n',
   '  E(kActionSidePanelShowGlypheChatGPT, IDC_GLYPHE_ASSISTANT_CHATGPT) \\\n'
   '  E(kActionSidePanelShowGlypheAssistant, IDC_GLYPHE_ASSISTANT) \\\n'),
  ('chrome/app/chrome_command_ids.h',
   '#define IDC_GLYPHE_ASSISTANT_CHATGPT    34094\n',
   '#define IDC_GLYPHE_ASSISTANT_CHATGPT    34094\n'
   '#define IDC_GLYPHE_ASSISTANT           34096\n'),

  ('chrome/common/pref_names.h',
   'inline constexpr char kGlypheRedNightEnabled[] = "glyphe.red_night.enabled";\n',
   'inline constexpr char kGlypheRedNightEnabled[] = "glyphe.red_night.enabled";\n'
   '// Helium Glyphe : assistant affiché dans l’onglet IA (0 Claude, 1 ChatGPT,\n'
   '// 2 Gemini, 3 Le Chat).\n'
   'inline constexpr char kGlypheAssistantCurrent[] = "glyphe.assistant.current";\n'),
  ('chrome/browser/ui/prefs/prefs_tab_helper.cc',
   '  registry->RegisterBooleanPref(prefs::kGlypheRedNightEnabled, false);\n',
   '  registry->RegisterBooleanPref(prefs::kGlypheRedNightEnabled, false);\n'
   '  registry->RegisterIntegerPref(prefs::kGlypheAssistantCurrent, 0);\n'),

  ('chrome/browser/ui/browser_command_controller.cc',
   '    case IDC_GLYPHE_ASSISTANT_CLAUDE:\n'
   '      SidePanelUI::From(browser_)->Toggle(\n'
   '          SidePanelEntryKey(SidePanelEntryId::kGlypheClaude),\n'
   '          SidePanelOpenTrigger::kToolbarButton);\n'
   '      break;\n'
   '    case IDC_GLYPHE_ASSISTANT_CHATGPT:\n'
   '      SidePanelUI::From(browser_)->Toggle(\n'
   '          SidePanelEntryKey(SidePanelEntryId::kGlypheChatGPT),\n'
   '          SidePanelOpenTrigger::kToolbarButton);\n'
   '      break;\n',
   '    case IDC_GLYPHE_ASSISTANT:\n'
   '      glyphe::ToggleAssistant(browser_, -1);\n'
   '      break;\n'
   '    case IDC_GLYPHE_ASSISTANT_CLAUDE:\n'
   '      glyphe::ToggleAssistant(browser_, 0);\n'
   '      break;\n'
   '    case IDC_GLYPHE_ASSISTANT_CHATGPT:\n'
   '      glyphe::ToggleAssistant(browser_, 1);\n'
   '      break;\n'),
  ('chrome/browser/ui/browser_command_controller.cc',
   '  command_updater_->UpdateCommandEnabled(IDC_GLYPHE_ASSISTANT_CHATGPT, true);\n',
   '  command_updater_->UpdateCommandEnabled(IDC_GLYPHE_ASSISTANT_CHATGPT, true);\n'
   '  command_updater_->UpdateCommandEnabled(IDC_GLYPHE_ASSISTANT, true);\n'),
  ('chrome/browser/ui/browser_command_controller.cc',
   '#include "chrome/browser/ui/browser_command_controller.h"\n',
   '#include "chrome/browser/ui/browser_command_controller.h"\n\n'
   '#include "chrome/browser/ui/views/side_panel/glyphe_assistant.h"  // nogncheck\n'),

  ('chrome/browser/ui/browser_shortcuts/browser_shortcut_metadata.cc',
   '    case IDC_GLYPHE_ASSISTANT_CLAUDE:\n'
   '      return Label(IDS_WILDCARD, u"Ouvrir Claude dans le panneau latéral");\n'
   '    case IDC_GLYPHE_ASSISTANT_CHATGPT:\n'
   '      return Label(IDS_WILDCARD, u"Ouvrir ChatGPT dans le panneau latéral");\n',
   '    case IDC_GLYPHE_ASSISTANT:\n'
   '      return Label(IDS_WILDCARD, u"Ouvrir l’onglet IA");\n'
   '    case IDC_GLYPHE_ASSISTANT_CLAUDE:\n'
   '      return Label(IDS_WILDCARD, u"Onglet IA : Claude");\n'
   '    case IDC_GLYPHE_ASSISTANT_CHATGPT:\n'
   '      return Label(IDS_WILDCARD, u"Onglet IA : ChatGPT");\n'),

  ('chrome/browser/ui/browser_actions.cc', OLD_ACTIONS, NEW_ACTIONS),
  ('chrome/browser/ui/toolbar/toolbar_pref_names.cc',
   '       {kActionSidePanelShowGlypheClaude, kActionSidePanelShowGlypheChatGPT}) {\n',
   '       {kActionSidePanelShowGlypheAssistant}) {\n'),

  (SP + 'BUILD.gn',
   '    "glyphe_assistant.cc",\n    "glyphe_assistant.h",\n',
   '    "glyphe_assistant.cc",\n    "glyphe_assistant.h",\n    "glyphe_assistant_logos.inc",\n'),
]
