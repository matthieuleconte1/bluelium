"""Bluelium : regrouper les extensions épinglées et le bouton puzzle en pastille.

Les icônes d'extensions épinglées et le bouton « puzzle » (menu des extensions)
partagent une pastille arrondie (rayon Prism 10 px, fond teinté dérivé des
couleurs du thème, sans couleur codée en dur), séparée des autres boutons de la
barre par une marge. Le bouclier du bloqueur (uBlock), déplacé dans son propre
hôte par toolbar_final_layout_spec.py, reste hors de la pastille.

S'applique après toolbar_final_layout_spec.py, page_color_contrast_spec.py et
dark_outline_spec.py.
"""

NEW_FILES = {}

BUILD = 'chrome/browser/ui/views/extensions/BUILD.gn'
EH = 'chrome/browser/ui/views/extensions/extensions_toolbar_desktop.h'
E = 'chrome/browser/ui/views/extensions/extensions_toolbar_desktop.cc'
TB = 'chrome/browser/ui/views/toolbar/toolbar_view.cc'

EDITS = [
    (BUILD,
     '    "//chrome/browser/user_education",\n'
     '    "//ui/base/dragdrop/mojom",\n'
     '  ]\n'
     '}\n',
     '    "//cc/paint",\n'
     '    "//chrome/browser/ui/color:color_headers",\n'
     '    "//chrome/browser/user_education",\n'
     '    "//ui/base/dragdrop/mojom",\n'
     '    "//ui/color",\n'
     '    "//ui/gfx",\n'
     '    "//ui/gfx/geometry",\n'
     '  ]\n'
     '}\n'),
    (EH,
     '  void OnMouseExited(const ui::MouseEvent& event) override;\n'
     '  void OnMouseMoved(const ui::MouseEvent& event) override;\n',
     '  void OnMouseExited(const ui::MouseEvent& event) override;\n'
     '  void OnMouseMoved(const ui::MouseEvent& event) override;\n'
     '  // Bluelium : pastille de groupe des extensions, rafraîchie au thème.\n'
     '  void OnThemeChanged() override;\n'
     '  void OnPaintBackground(gfx::Canvas* canvas) override;\n'),
    (E,
     '#include "chrome/browser/ui/views/extensions/extensions_toolbar_desktop.h"\n',
     '#include "chrome/browser/ui/views/extensions/extensions_toolbar_desktop.h"\n'
     '#include "cc/paint/paint_flags.h"\n'
     '#include "chrome/browser/ui/color/chrome_color_id.h"\n'
     '#include "ui/color/bluelium_dark_outline.h"\n'
     '#include "ui/color/color_provider.h"\n'
     '#include "ui/gfx/canvas.h"\n'
     '#include "ui/gfx/color_utils.h"\n'
     '#include "ui/gfx/geometry/rect_f.h"\n'
     '#include <algorithm>\n'),
    (E,
     '// Bluelium : identifiant du composant uBlock fourni par Helium.\n'
     'constexpr char kBlueliumBlockerActionId[] = "blockjmkbacgjkknlgpkjjiijinjdanf";\n',
     '// Bluelium : identifiant du composant uBlock fourni par Helium.\n'
     'constexpr char kBlueliumBlockerActionId[] = "blockjmkbacgjkknlgpkjjiijinjdanf";\n'
     '// Bluelium : géométrie de la pastille des extensions (rayon Prism 10 px).\n'
     'constexpr int kBlueliumGroupHorizontalPadding = 3;\n'
     'constexpr float kBlueliumGroupCornerRadius = 10.0f;\n'),
    (E,
     '  GetTargetLayoutManager()->SetDefault(views::kMarginsKey,\n'
     '                                       gfx::Insets::VH(0, 2));\n',
     '  // Bluelium : marge intérieure compacte pour encadrer la pastille.\n'
     '  GetTargetLayoutManager()\n'
     '      ->SetInteriorMargin(\n'
     '          gfx::Insets::VH(0, kBlueliumGroupHorizontalPadding))\n'
     '      .SetDefault(views::kMarginsKey, gfx::Insets::VH(0, 2));\n'),
    (E,
     '  const int offset_into_icon_area = GetMirroredXInView(event.x());\n',
     '  // Bluelium : tenir compte de la marge intérieure gauche de la pastille.\n'
     '  const int offset_into_icon_area =\n'
     '      GetMirroredXInView(event.x()) - kBlueliumGroupHorizontalPadding;\n'),
    (E,
     'void ExtensionsToolbarDesktop::OnMouseMoved(const ui::MouseEvent& event) {\n',
     'void ExtensionsToolbarDesktop::OnThemeChanged() {\n'
     '  ToolbarIconContainerView::OnThemeChanged();\n'
     '  SchedulePaint();\n'
     '}\n\n'
     'void ExtensionsToolbarDesktop::OnPaintBackground(gfx::Canvas* canvas) {\n'
     '  ToolbarIconContainerView::OnPaintBackground(canvas);\n'
     '  const gfx::Rect bounds = GetLocalBounds();\n'
     '  if (bounds.IsEmpty()) {\n'
     '    return;\n'
     '  }\n'
     '  const auto* colors = GetColorProvider();\n'
     '  if (!colors) {\n'
     '    return;\n'
     '  }\n'
     '  // Bluelium : pas de pastille autour du puzzle seul ; elle n\'apparaît\n'
     '  // qu\'à partir d\'une extension épinglée (visible dans la barre).\n'
     '  if (std::ranges::none_of(icons_, [](const auto& icon) {\n'
     '        return icon.second && icon.second->GetVisible();\n'
     '      })) {\n'
     '    return;\n'
     '  }\n'
     '  // Bluelium : pastille arrondie regroupant les extensions et le puzzle.\n'
     '  const SkColor page_bg =\n'
     '      colors->GetColor(kColorGlyphePageColorButtonBackground);\n'
     '  const bool has_page_box = SkColorGetA(page_bg) != SK_AlphaTRANSPARENT;\n'
     '  cc::PaintFlags flags;\n'
     '  flags.setAntiAlias(true);\n'
     '  flags.setStyle(cc::PaintFlags::kFill_Style);\n'
     '  if (ui::BlueliumDarkOutline() && !has_page_box) {\n'
     '    // Bluelium : OLED / Nuit (« Trait fin ») : fond discret + contour fin.\n'
     '    flags.setColor(color_utils::AlphaBlend(\n'
     '        colors->GetColor(kColorToolbarButtonIcon),\n'
     '        colors->GetColor(kColorToolbar), SkAlpha{0x10}));\n'
     '    canvas->DrawRoundRect(gfx::RectF(bounds), kBlueliumGroupCornerRadius,\n'
     '                          flags);\n'
     '    cc::PaintFlags stroke;\n'
     '    stroke.setAntiAlias(true);\n'
     '    stroke.setStyle(cc::PaintFlags::kStroke_Style);\n'
     '    stroke.setStrokeWidth(1.0f);\n'
     '    stroke.setColor(colors->GetColor(kColorToolbarSeparatorDefault));\n'
     '    gfx::RectF stroke_rect(bounds);\n'
     '    stroke_rect.Inset(0.5f);\n'
     '    canvas->DrawRoundRect(stroke_rect, kBlueliumGroupCornerRadius - 0.5f,\n'
     '                          stroke);\n'
     '    return;\n'
     '  }\n'
     '  flags.setColor(\n'
     '      has_page_box\n'
     '          ? page_bg\n'
     '          : color_utils::AlphaBlend(\n'
     '                colors->GetColor(kColorToolbarButtonIcon),\n'
     '                colors->GetColor(kColorToolbar), SkAlpha{0x14}));\n'
     '  canvas->DrawRoundRect(gfx::RectF(bounds), kBlueliumGroupCornerRadius, flags);\n'
     '}\n\n'
     'void ExtensionsToolbarDesktop::OnMouseMoved(const ui::MouseEvent& event) {\n'),
    (TB,
     '  if (extensions_container) {\n'
     '    extensions_container_ = AddChildView(std::move(extensions_container));\n'
     '    extensions_toolbar_coordinator_ =\n',
     '  if (extensions_container) {\n'
     '    extensions_container_ = AddChildView(std::move(extensions_container));\n'
     '    // Bluelium : séparer la pastille des extensions des autres boutons.\n'
     '    extensions_container_->SetProperty(views::kMarginsKey,\n'
     '                                       gfx::Insets::VH(0, 4));\n'
     '    extensions_toolbar_coordinator_ =\n'),
    # Bluelium : la pastille délimite déjà les extensions ; le séparateur
    # entre elles et le bouton IA (reference_finishing_spec.py) est en trop.
    (TB,
     '  glyphe_separator->SetColorId(kColorToolbarSeparatorDefault);\n',
     '  glyphe_separator->SetColorId(kColorToolbarSeparatorDefault);\n'
     '  glyphe_separator->SetVisible(false);  // Bluelium : épuration\n'),
]
