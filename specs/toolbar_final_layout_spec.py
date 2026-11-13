"""Bluelium : bloqueur, Diviser, puis le groupe intact des extensions.

uBlock garde sa vue, son modèle et son contrôleur natifs ; seul son parent
visuel change. Diviser reste un enfant direct de ToolbarView, avec sa pref
kPinSplitTabButton, indépendamment des actions épinglées du panneau IA.
"""
NEW_FILES = {}
P = 'chrome/browser/ui/views/toolbar/toolbar_view.cc'
E = 'chrome/browser/ui/views/extensions/extensions_toolbar_desktop.cc'
EH = 'chrome/browser/ui/views/extensions/extensions_toolbar_desktop.h'

EDITS = [
 (P, '    avatar_->SetVisible(show_avatar_button_.GetValue());',
  '    avatar_->SetVisible(show_avatar_button_.GetValue());  // Bluelium : caché par défaut (pref)'),
 (P, 'void ToolbarView::OnShowAvatarButtonChanged() {\n  avatar_->SetVisible(show_avatar_button_.GetValue());\n}',
  'void ToolbarView::OnShowAvatarButtonChanged() {\n  // Bluelium : réglable dans Personnaliser > Barre d\'outils.\n  avatar_->SetVisible(!browser_->GetProfile()->IsRegularProfile() ||\n                     show_avatar_button_.GetValue());\n}'),
 (P, '''  if (!features::IsWebUISplitTabsButtonEnabled()) {
    split_tabs_ =
        AddChildView(std::make_unique<SplitTabsToolbarButton>(browser_));
  }
''',
  '  // Bluelium : Diviser est créé après l\'adresse, hors des extensions.\n'),
 (P, '''  if (extensions_container) {
    extensions_container_ = AddChildView(std::move(extensions_container));
''',
  '''  // Bluelium : bloqueur, Diviser, puis le groupe intact des extensions.
  // Le contrôleur natif conserve le compteur, la popup et l'épinglage.
  if (extensions_container) {
    auto* blocker_host = AddChildView(
        std::make_unique<views::FlexLayoutView>());
    extensions_container->SetBlueliumBlockerHost(blocker_host);
  }
  if (!features::IsWebUISplitTabsButtonEnabled()) {
    split_tabs_ =
        AddChildView(std::make_unique<SplitTabsToolbarButton>(browser_));
  }

  if (extensions_container) {
    extensions_container_ = AddChildView(std::move(extensions_container));
'''),
 (P, 'ToolbarView::~ToolbarView() {\n',
  '''ToolbarView::~ToolbarView() {
  // Bluelium : rendre le bouclier à son contrôleur avant les enfants.
  if (extensions_container_) {
    extensions_container_->SetBlueliumBlockerHost(nullptr);
  }
'''),
 # Bluelium : aligner le panneau sur la même origine que la page.
 ('chrome/browser/ui/views/side_panel/side_panel.cc',
  '      -kOverlapFromToolbar,\n',
  '      1 - kOverlapFromToolbar,  // Bluelium : même y que la page\n'),

 # Bluelium : uBlock reste une seule action native, dans un hôte frère de la
 # zone Extensions. Les autres fenêtres gardent leur conteneur habituel.
 (EH, '  void CreateActions();\n',
  '''  void CreateActions();

  // Bluelium : hôte du bouclier dans la barre ; nullptr le réintègre.
  void SetBlueliumBlockerHost(views::View* host);
'''),
 (EH, '  ToolbarIcons icons_;\n',
  '''  ToolbarIcons icons_;

  // Bluelium : détaché par ToolbarView avant la destruction des enfants.
  raw_ptr<views::View> bluelium_blocker_host_ = nullptr;
'''),
 (E, 'namespace {\n',
  '''namespace {

// Bluelium : identifiant du composant uBlock fourni par Helium.
constexpr char kBlueliumBlockerActionId[] = "blockjmkbacgjkknlgpkjjiijinjdanf";
'''),
 (E, '  action_hover_card_controller_.reset();\n',
  '''  action_hover_card_controller_.reset();
  // Bluelium : détruire le bouclier avec son modèle et ses observateurs.
  SetBlueliumBlockerHost(nullptr);
'''),
 (E, 'void ExtensionsToolbarDesktop::ReorderAllChildViews() {\n',
  '''// Bluelium : déplacer la vue existante, sans dupliquer l'action uBlock.
void ExtensionsToolbarDesktop::SetBlueliumBlockerHost(
    views::View* host) {
  if (bluelium_blocker_host_ == host) {
    return;
  }
  ToolbarActionView* blocker = GetViewForId(kBlueliumBlockerActionId);
  bluelium_blocker_host_ = host;
  if (blocker) {
    auto owned_blocker = blocker->parent()->RemoveChildViewT(blocker);
    views::View* target = host ? host : this;
    target->AddChildView(std::move(owned_blocker));
  }
  ReorderAllChildViews();
}

void ExtensionsToolbarDesktop::ReorderAllChildViews() {
'''),
 (E, '''  for (size_t i = 0; i < pinned_action_ids.size(); ++i) {
    ReorderChildView(GetViewForId(pinned_action_ids[i]), i);
  }
  if (drop_info_.get()) {
    ReorderChildView(GetViewForId(drop_info_->action_id), drop_info_->index);
  }
''',
  '''  // Bluelium : le bouclier a son propre hôte, hors de ce réordonnancement.
  size_t child_index = 0;
  size_t drop_index = 0;
  for (size_t i = 0; i < pinned_action_ids.size(); ++i) {
    auto* view = GetViewForId(pinned_action_ids[i]);
    if (view->parent() != this) {
      continue;
    }
    ReorderChildView(view, child_index++);
    if (drop_info_ && i < drop_info_->index) {
      ++drop_index;
    }
  }
  if (drop_info_) {
    ReorderChildView(GetViewForId(drop_info_->action_id), drop_index);
  }
'''),
 (E, '  icons_.insert({action_id, AddChildView(std::move(icon))});\n',
  '''  // Bluelium : gérer aussi le chargement tardif ou le rechargement uBlock.
  views::View* host =
      bluelium_blocker_host_ && action_id == kBlueliumBlockerActionId
          ? bluelium_blocker_host_.get()
          : this;
  icons_.insert({action_id, host->AddChildView(std::move(icon))});
'''),
 (E, '    RemoveChildViewT(action_view);\n',
  '''    // Bluelium : le bouclier peut appartenir à son hôte séparé.
    action_view->parent()->RemoveChildViewT(action_view);
'''),
 (E, '''  if (must_show || (ToolbarActionsModel::CanShowActionsInToolbar(*browser_) &&
                    model_->IsActionPinned(extension_id))) {
    GetAnimatingLayoutManager()->FadeIn(action_view);
  } else {
    GetAnimatingLayoutManager()->FadeOut(action_view);
  }
''',
  '''  // Bluelium : le bouclier séparé ne dépend plus du layout des extensions.
  const bool visible =
      must_show || (ToolbarActionsModel::CanShowActionsInToolbar(*browser_) &&
                    model_->IsActionPinned(extension_id));
  if (action_view->parent() != this) {
    action_view->SetVisible(visible);
  } else if (visible) {
    GetAnimatingLayoutManager()->FadeIn(action_view);
  } else {
    GetAnimatingLayoutManager()->FadeOut(action_view);
  }
'''),
 (E, '  return toolbar_view_model_->IsActionDraggable(it->first);\n',
  '''  // Bluelium : le bouclier garde sa place avant Diviser.
  return sender->parent() == this &&
         toolbar_view_model_->IsActionDraggable(it->first);
'''),
 (E, '  const size_t visible_icons = toolbar_view_model_->GetPinnedActionIds().size();\n',
  '''  // Bluelium : les indices du modèle incluent encore le bouclier séparé.
  const auto& pinned_ids = toolbar_view_model_->GetPinnedActionIds();
  std::vector<size_t> model_indices;
  for (size_t i = 0; i < pinned_ids.size(); ++i) {
    if (GetViewForId(pinned_ids[i])->parent() == this) {
      model_indices.push_back(i);
    }
  }
  const size_t visible_icons = model_indices.size();
'''),
 (E, '  before_icon = std::min(before_icon_unclamped, visible_icons);\n',
  '''  before_icon = std::min(before_icon_unclamped, visible_icons);
  // Bluelium : reconvertir la position visuelle en indice du modèle natif.
  before_icon = before_icon < model_indices.size()
                    ? model_indices[before_icon]
                    : pinned_ids.size();
'''),
]
