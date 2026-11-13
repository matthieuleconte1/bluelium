"""Bluelium : le bouton IA reste épinglé, même après un import de données.

L'IA n'était ajoutée qu'à la valeur par défaut de kPinnedActions : un import
(ou une synchronisation) qui remplace la liste la faisait disparaître. Le
modèle l'ajoute maintenant à la liste lue, sauf si l'utilisateur l'a lui-même
désépinglée (pref glyphe.assistant.unpinned, remise à faux s'il la réépingle).
"""

M = 'chrome/browser/ui/toolbar/pinned_toolbar/pinned_toolbar_actions_model.cc'

NEW_FILES = {}

EDITS = [
  ('chrome/common/pref_names.h',
   'inline constexpr char kGlypheAssistantCurrent[] = "glyphe.assistant.current";\n',
   'inline constexpr char kGlypheAssistantCurrent[] = "glyphe.assistant.current";\n'
   '// Bluelium : vrai si l\'utilisateur a désépinglé le bouton IA.\n'
   'inline constexpr char kGlypheAssistantUnpinned[] = "glyphe.assistant.unpinned";\n'),
  ('chrome/browser/ui/prefs/prefs_tab_helper.cc',
   '  registry->RegisterIntegerPref(prefs::kGlypheAssistantCurrent, 0);\n',
   '  registry->RegisterIntegerPref(prefs::kGlypheAssistantCurrent, 0);\n'
   '  registry->RegisterBooleanPref(prefs::kGlypheAssistantUnpinned, false);\n'),
  (M,
   '#include <iterator>\n',
   '#include <algorithm>\n#include <iterator>\n'),
  (M,
   '      pinned_action_ids_.push_back(id.value());\n'
   '    }\n'
   '  }\n'
   '\n'
   '  for (Observer& observer : observers_) {\n'
   '    observer.OnActionsChanged();\n'
   '  }\n',
   '      pinned_action_ids_.push_back(id.value());\n'
   '    }\n'
   '  }\n'
   '\n'
   '  // Bluelium : bouton IA toujours épinglé (un import peut remplacer la\n'
   '  // liste), sauf si l\'utilisateur l\'a retiré lui-même.\n'
   '  if (!pref_service_->GetBoolean(prefs::kGlypheAssistantUnpinned) &&\n'
   '      !std::ranges::contains(pinned_action_ids_,\n'
   '                             kActionSidePanelShowGlypheAssistant)) {\n'
   '    pinned_action_ids_.push_back(kActionSidePanelShowGlypheAssistant);\n'
   '  }\n'
   '\n'
   '  for (Observer& observer : observers_) {\n'
   '    observer.OnActionsChanged();\n'
   '  }\n'),
  (M,
   'void PinnedToolbarActionsModel::PinAction(actions::ActionId action_id) {\n',
   'void PinnedToolbarActionsModel::PinAction(actions::ActionId action_id) {\n'
   '  if (action_id == kActionSidePanelShowGlypheAssistant) {\n'
   '    pref_service_->SetBoolean(prefs::kGlypheAssistantUnpinned, false);\n'
   '  }\n'),
  (M,
   'void PinnedToolbarActionsModel::UnpinAction(actions::ActionId action_id) {\n',
   'void PinnedToolbarActionsModel::UnpinAction(actions::ActionId action_id) {\n'
   '  if (action_id == kActionSidePanelShowGlypheAssistant) {\n'
   '    // Avant UpdatePref : UpdatePinnedActionIds() ne doit pas la rajouter.\n'
   '    pref_service_->SetBoolean(prefs::kGlypheAssistantUnpinned, true);\n'
   '  }\n'),
]
