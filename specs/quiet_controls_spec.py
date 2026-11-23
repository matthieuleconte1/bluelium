"""Bluelium : retour et avance masqués quand ils ne servent pas.

Épuration de la barre (revue du 23 nov.) : les flèches grisées d'un onglet
neuf sont du bruit. Retour n'est visible que s'il y a une page précédente (et
que la pref « Afficher le bouton Retour » est active) ; Avance seulement s'il
y a une page suivante. Simple masquage, sans animation de largeur : la barre
d'adresse se décale d'un bouton quand une flèche apparaît.

Inchangés : raccourcis clavier (Alt+← / Alt+→), geste de retour au trackpad,
menu d'historique au clic long ou au clic droit quand la flèche est visible.
L'état vient des commandes IDC_BACK / IDC_FORWARD, comme le grisé d'origine.
"""

TV = 'chrome/browser/ui/views/toolbar/toolbar_view.cc'

NEW_FILES = {}

EDITS = [
  # État initial : à la création de la barre, la fenêtre peut déjà avoir un
  # onglet sans historique.
  (TV,
   '  back_->SetVisible(show_back_button_.GetValue());\n'
   '\n'
   '  show_reload_button_.Init(\n',
   '  // Bluelium : retour et avance n\'apparaissent que s\'ils servent.\n'
   '  back_->SetEnabled(chrome::IsCommandEnabled(browser_, IDC_BACK));\n'
   '  forward_->SetEnabled(chrome::IsCommandEnabled(browser_, IDC_FORWARD));\n'
   '  back_->SetVisible(show_back_button_.GetValue() && back_->GetEnabled());\n'
   '  forward_->SetVisible(show_forward_button_.GetValue() && forward_->GetEnabled());\n'
   '\n'
   '  show_reload_button_.Init(\n'),
  # Pref « Afficher le bouton Retour » : ne pas réafficher une flèche inutile.
  (TV,
   'void ToolbarView::OnShowBackButtonChanged() {\n'
   '  back_->SetVisible(show_back_button_.GetValue());\n',
   'void ToolbarView::OnShowBackButtonChanged() {\n'
   '  // Bluelium : visible seulement s\'il y a une page précédente.\n'
   '  back_->SetVisible(show_back_button_.GetValue() && back_->GetEnabled());\n'),
  # Changement d'état des commandes (navigation, changement d'onglet).
  (TV,
   '  if (it != kButtons.end()) {\n'
   '    (*it)->SetEnabled(enabled);\n'
   '  }\n'
   '}\n',
   '  if (it != kButtons.end()) {\n'
   '    (*it)->SetEnabled(enabled);\n'
   '  }\n'
   '  // Bluelium : retour et avance masqués quand ils sont inactifs.\n'
   '  if (id == IDC_BACK && back_) {\n'
   '    back_->SetVisible(enabled && show_back_button_.GetValue());\n'
   '    InvalidateLayout();\n'
   '  } else if (id == IDC_FORWARD && forward_) {\n'
   '    forward_->SetVisible(enabled && show_forward_button_.GetValue());\n'
   '    InvalidateLayout();\n'
   '  }\n'
   '}\n'),
  # Pref « Afficher le bouton Avance » : même règle.
  (TV,
   '  } else {\n'
   '    forward_->SetVisible(visible);\n'
   '  }\n',
   '  } else {\n'
   '    // Bluelium : visible seulement s\'il y a une page suivante.\n'
   '    forward_->SetVisible(visible && forward_->GetEnabled());\n'
   '  }\n'),
]
