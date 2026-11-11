# Helium Glyphe — panneau assistant Claude / ChatGPT.
# Deux entrées de panneau latéral qui chargent claude.ai et chatgpt.com dans une
# vraie vue web (session du profil), deux actions épinglables dans la barre
# d'outils avec la favicon du site en masque monochrome (couleur kColorIcon,
# donc adaptée au thème), raccourcis Alt+Maj+C et Alt+Maj+G.
from pathlib import Path

ICONS = Path(__file__).resolve().parent.parent / 'assets/icons'
if not ICONS.is_dir():
  ICONS = Path(__file__).with_name('icons')


def c_array(name, data):
  body = ', '.join(f'0x{b:02x}' for b in data)
  return f'constexpr uint8_t {name}[] = {{{body}}};\n'


icons_inc = ('// Généré depuis les favicons de claude.ai et chatgpt.com (16 px, alpha).\n'
             + c_array('kClaudePng', (ICONS / 'claude_16.png').read_bytes())
             + c_array('kClaudePng2x', (ICONS / 'claude_32.png').read_bytes())
             + c_array('kChatGptPng', (ICONS / 'chatgpt_16.png').read_bytes())
             + c_array('kChatGptPng2x', (ICONS / 'chatgpt_32.png').read_bytes()))

NEW_FILES = {
  'chrome/browser/ui/views/side_panel/glyphe_assistant_icons.inc': icons_inc,
  'chrome/browser/ui/views/side_panel/glyphe_assistant.h': '''// Helium Glyphe — panneau assistant Claude / ChatGPT.
#ifndef CHROME_BROWSER_UI_VIEWS_SIDE_PANEL_GLYPHE_ASSISTANT_H_
#define CHROME_BROWSER_UI_VIEWS_SIDE_PANEL_GLYPHE_ASSISTANT_H_

#include "chrome/browser/ui/side_panel/side_panel_entry_id.h"
#include "ui/base/models/image_model.h"

class BrowserWindowInterface;
class SidePanelRegistry;

namespace glyphe {

// Enregistre les entrées Claude et ChatGPT dans le registre de la fenêtre.
void RegisterAssistantEntries(BrowserWindowInterface* browser,
                              SidePanelRegistry* registry);

// Favicon du site en masque monochrome, teintée avec kColorIcon.
ui::ImageModel AssistantIcon(SidePanelEntryId id);

}  // namespace glyphe

#endif  // CHROME_BROWSER_UI_VIEWS_SIDE_PANEL_GLYPHE_ASSISTANT_H_
''',
  'chrome/browser/ui/views/side_panel/glyphe_assistant.cc': '''// Helium Glyphe — panneau assistant Claude / ChatGPT.
#include "chrome/browser/ui/views/side_panel/glyphe_assistant.h"

#include <cstdint>
#include <memory>

#include "base/containers/span.h"
#include "base/functional/bind.h"
#include "chrome/browser/profiles/profile.h"
#include "chrome/browser/ui/browser_window/public/browser_window_interface.h"
#include "chrome/browser/ui/side_panel/side_panel_entry.h"
#include "chrome/browser/ui/side_panel/side_panel_entry_scope.h"
#include "chrome/browser/ui/side_panel/side_panel_registry.h"
#include "ui/color/color_id.h"
#include "ui/color/color_provider.h"
#include "ui/gfx/image/image.h"
#include "ui/gfx/image/image_skia.h"
#include "ui/gfx/image/image_skia_operations.h"
#include "ui/gfx/image/image_skia_rep.h"
#include "ui/views/controls/webview/webview.h"
#include "url/gurl.h"

namespace glyphe {

namespace {

#include "chrome/browser/ui/views/side_panel/glyphe_assistant_icons.inc"

constexpr int kAssistantPanelWidth = 440;

const char* UrlFor(SidePanelEntryId id) {
  return id == SidePanelEntryId::kGlypheClaude ? "https://claude.ai/new"
                                               : "https://chatgpt.com/";
}

std::unique_ptr<views::View> CreateAssistantView(SidePanelEntryId id,
                                                 SidePanelEntryScope& scope) {
  auto web_view = std::make_unique<views::WebView>(
      scope.GetBrowserWindowInterface().GetProfile());
  web_view->LoadInitialURL(GURL(UrlFor(id)));
  return web_view;
}

gfx::ImageSkia LoadIcon(SidePanelEntryId id) {
  const bool claude = id == SidePanelEntryId::kGlypheClaude;
  gfx::ImageSkia image =
      gfx::Image::CreateFrom1xPNGBytes(
          claude ? base::span<const uint8_t>(kClaudePng)
                 : base::span<const uint8_t>(kChatGptPng))
          .AsImageSkia();
  gfx::ImageSkia image_2x =
      gfx::Image::CreateFrom1xPNGBytes(
          claude ? base::span<const uint8_t>(kClaudePng2x)
                 : base::span<const uint8_t>(kChatGptPng2x))
          .AsImageSkia();
  if (!image_2x.isNull()) {
    image.AddRepresentation(
        gfx::ImageSkiaRep(image_2x.GetRepresentation(1.0f).GetBitmap(), 2.0f));
  }
  return image;
}

}  // namespace

void RegisterAssistantEntries(BrowserWindowInterface* browser,
                              SidePanelRegistry* registry) {
  for (SidePanelEntryId id :
       {SidePanelEntryId::kGlypheClaude, SidePanelEntryId::kGlypheChatGPT}) {
    registry->Register(std::make_unique<SidePanelEntry>(
        SidePanelEntry::Key(id), base::BindRepeating(&CreateAssistantView, id),
        base::BindRepeating([]() { return kAssistantPanelWidth; })));
  }
}

ui::ImageModel AssistantIcon(SidePanelEntryId id) {
  return ui::ImageModel::FromImageGenerator(
      base::BindRepeating(
          [](gfx::ImageSkia image, const ui::ColorProvider* provider) {
            return gfx::ImageSkiaOperations::CreateColorMask(
                image, provider->GetColor(ui::kColorIcon));
          },
          LoadIcon(id)),
      gfx::Size(16, 16));
}

}  // namespace glyphe
''',
}

EDITS = [
  ('chrome/browser/ui/side_panel/side_panel_entry_id.h',
   '  V(kContextualTasks, kActionSidePanelShowContextualTasks, "ContextualTasks") \\\n',
   '  V(kContextualTasks, kActionSidePanelShowContextualTasks, "ContextualTasks") \\\n'
   '  V(kGlypheClaude, kActionSidePanelShowGlypheClaude, "GlypheClaude")          \\\n'
   '  V(kGlypheChatGPT, kActionSidePanelShowGlypheChatGPT, "GlypheChatGPT")       \\\n'),

  ('chrome/browser/ui/actions/chrome_action_id.h',
   '  E(kActionSidePanelShowBookmarks, IDC_SHOW_BOOKMARK_SIDE_PANEL) \\\n',
   '  E(kActionSidePanelShowBookmarks, IDC_SHOW_BOOKMARK_SIDE_PANEL) \\\n'
   '  E(kActionSidePanelShowGlypheClaude, IDC_GLYPHE_ASSISTANT_CLAUDE) \\\n'
   '  E(kActionSidePanelShowGlypheChatGPT, IDC_GLYPHE_ASSISTANT_CHATGPT) \\\n'),

  ('chrome/app/chrome_command_ids.h',
   '#define IDC_GLYPHE_TOGGLE_RED_NIGHT     34092\n',
   '#define IDC_GLYPHE_TOGGLE_RED_NIGHT     34092\n'
   '#define IDC_GLYPHE_ASSISTANT_CLAUDE     34093\n'
   '#define IDC_GLYPHE_ASSISTANT_CHATGPT    34094\n'),

  ('chrome/browser/ui/accelerator_table.cc',
   '     IDC_GLYPHE_TOGGLE_RED_NIGHT},\n',
   '     IDC_GLYPHE_TOGGLE_RED_NIGHT},\n'
   '    {ui::VKEY_C, ui::EF_SHIFT_DOWN | ui::EF_ALT_DOWN,\n'
   '     IDC_GLYPHE_ASSISTANT_CLAUDE},\n'
   '    {ui::VKEY_G, ui::EF_SHIFT_DOWN | ui::EF_ALT_DOWN,\n'
   '     IDC_GLYPHE_ASSISTANT_CHATGPT},\n'),

  ('chrome/browser/ui/browser_command_controller.cc',
   '    case IDC_SHOW_BOOKMARK_SIDE_PANEL:\n',
   '    case IDC_GLYPHE_ASSISTANT_CLAUDE:\n'
   '      SidePanelUI::From(browser_)->Toggle(\n'
   '          SidePanelEntryKey(SidePanelEntryId::kGlypheClaude),\n'
   '          SidePanelOpenTrigger::kToolbarButton);\n'
   '      break;\n'
   '    case IDC_GLYPHE_ASSISTANT_CHATGPT:\n'
   '      SidePanelUI::From(browser_)->Toggle(\n'
   '          SidePanelEntryKey(SidePanelEntryId::kGlypheChatGPT),\n'
   '          SidePanelOpenTrigger::kToolbarButton);\n'
   '      break;\n'
   '    case IDC_SHOW_BOOKMARK_SIDE_PANEL:\n'),
  ('chrome/browser/ui/browser_command_controller.cc',
   '  command_updater_->UpdateCommandEnabled(IDC_SHOW_BOOKMARK_SIDE_PANEL, true);\n',
   '  command_updater_->UpdateCommandEnabled(IDC_SHOW_BOOKMARK_SIDE_PANEL, true);\n'
   '  command_updater_->UpdateCommandEnabled(IDC_GLYPHE_ASSISTANT_CLAUDE, true);\n'
   '  command_updater_->UpdateCommandEnabled(IDC_GLYPHE_ASSISTANT_CHATGPT, true);\n'),

  ('chrome/browser/ui/views/side_panel/side_panel_helper.cc',
   '#include "chrome/browser/ui/views/side_panel/comments/comments_side_panel_coordinator.h"\n',
   '#include "chrome/browser/ui/views/side_panel/comments/comments_side_panel_coordinator.h"\n'
   '#include "chrome/browser/ui/views/side_panel/glyphe_assistant.h"\n'),
  ('chrome/browser/ui/views/side_panel/side_panel_helper.cc',
   '  BookmarksSidePanelCoordinator::From(browser)->CreateAndRegisterEntry(\n'
   '      window_registry);\n',
   '  BookmarksSidePanelCoordinator::From(browser)->CreateAndRegisterEntry(\n'
   '      window_registry);\n\n'
   '  // Helium Glyphe : assistants Claude et ChatGPT.\n'
   '  glyphe::RegisterAssistantEntries(browser, window_registry);\n'),

  ('chrome/browser/ui/views/side_panel/BUILD.gn',
   '    "side_panel_helper.cc",\n',
   '    "side_panel_helper.cc",\n'
   '    "glyphe_assistant.cc",\n'
   '    "glyphe_assistant.h",\n'),

  ('chrome/browser/ui/browser_actions.cc',
   'void BrowserActions::InitializeSidePanelActions() {\n'
   '  Profile* const profile = base::to_address(profile_);\n'
   '  BrowserWindowInterface* const bwi = base::to_address(bwi_);\n',
   'void BrowserActions::InitializeSidePanelActions() {\n'
   '  Profile* const profile = base::to_address(profile_);\n'
   '  BrowserWindowInterface* const bwi = base::to_address(bwi_);\n\n'
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
   '  }\n'),
  ('chrome/browser/ui/browser_actions.cc',
   '#include "chrome/browser/ui/browser_actions.h"\n',
   '#include "chrome/browser/ui/browser_actions.h"\n\n#include <tuple>\n\n'
   '#include "chrome/browser/ui/views/side_panel/glyphe_assistant.h"  // nogncheck\n'),
  # Claude et ChatGPT épinglés par défaut (nouveaux profils, ou liste jamais
  # modifiée par l'utilisateur).
  ('chrome/browser/ui/toolbar/toolbar_pref_names.cc',
   '  registry->RegisterListPref(prefs::kPinnedActions,\n',
   '  for (actions::ActionId glyphe_action :\n'
   '       {kActionSidePanelShowGlypheClaude, kActionSidePanelShowGlypheChatGPT}) {\n'
   '    const std::optional<std::string>& glyphe_name =\n'
   '        actions::ActionIdMap::ActionIdToString(glyphe_action);\n'
   '    if (glyphe_name.has_value()) {\n'
   '      default_pinned_actions.Append(glyphe_name.value());\n'
   '    }\n'
   '  }\n\n'
   '  registry->RegisterListPref(prefs::kPinnedActions,\n'),
]
