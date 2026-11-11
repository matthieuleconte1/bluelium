# Arrangement final de la barre, après les finitions concurrentes.
NEW_FILES = {}
P = 'chrome/browser/ui/views/toolbar/toolbar_view.cc'
EDITS = [
 (P, '    avatar_->SetVisible(show_avatar_button_.GetValue());',
  '    avatar_->SetVisible(false);  // Glyphe : profil normal absent du HTML'),
 (P, 'void ToolbarView::OnShowAvatarButtonChanged() {\n  avatar_->SetVisible(show_avatar_button_.GetValue());\n}',
  'void ToolbarView::OnShowAvatarButtonChanged() {\n  avatar_->SetVisible(!browser_->GetProfile()->IsRegularProfile());\n}'),
 (P, '    extensions_toolbar_coordinator_ =\n        std::make_unique<ExtensionsToolbarCoordinator>(extensions_container_);',
  '    extensions_toolbar_coordinator_ =\n        std::make_unique<ExtensionsToolbarCoordinator>(extensions_container_);\n'
  '    // Glyphe : bloqueur, Diviser, Extensions ; conserver le contrôleur\n'
  '    // natif et placer Diviser avant le bouton principal du conteneur.\n'
  '    if (split_tabs_) {\n'
  '      auto glyphe_split = RemoveChildViewT(split_tabs_.get());\n'
  '      const size_t index = extensions_container_->GetIndexOf(\n'
  '          extensions_container_->main_item()).value();\n'
  '      extensions_container_->AddChildViewAt(std::move(glyphe_split), index);\n'
  '    }'),
]

# Le bord de contenu Chromium occupe déjà un pixel : aligner le panneau sur
# la même origine y=78 que la page, au lieu de y=77.
EDITS += [
 ('chrome/browser/ui/views/side_panel/side_panel.cc',
  '      -kOverlapFromToolbar,\n', '      1 - kOverlapFromToolbar,  // Glyphe : même y que la page\n'),
]
