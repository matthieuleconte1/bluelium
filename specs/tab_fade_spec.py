# Helium Glyphe — onglets en fondu au débordement.
# Dans la barre d'onglets défilante (flag chrome://flags#tab-strip-unification),
# les ombres de débordement sont remplacées par un masque en dégradé : les
# onglets s'effacent sur les bords au lieu d'être recouverts par une ombre.

OLD = '''    scroll_view->SetCustomOverflowIndicator(
        views::OverflowIndicatorAlignment::kLeft,
        std::make_unique<HorizontalTabStripOverflowIndicatorView>(
            views::OverflowIndicatorAlignment::kLeft),
        HorizontalTabStripOverflowIndicatorView::kTotalThickness,
        /*fills_opaquely=*/false);

    scroll_view->SetCustomOverflowIndicator(
        views::OverflowIndicatorAlignment::kRight,
        std::make_unique<HorizontalTabStripOverflowIndicatorView>(
            views::OverflowIndicatorAlignment::kRight),
        HorizontalTabStripOverflowIndicatorView::kTotalThickness,
        /*fills_opaquely=*/false);
'''

NEW = '''    // Helium Glyphe : fondu sur les bords plutôt qu'une ombre.
    scroll_view->SetOverflowGradientMask(
        views::ScrollView::GradientDirection::kHorizontal);
'''

EDITS = [
  ('chrome/browser/ui/views/tabs/common/tab_strip_view.cc', OLD, NEW),
]
