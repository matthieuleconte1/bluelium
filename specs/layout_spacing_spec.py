# Native desktop spacing measured from the Onglet IA reference board.
# Applied AFTER prism-ui; unlike CSS, Chromium tab bounds include extensions.
NEW_FILES = {}
LC = 'chrome/browser/ui/layout_constants.cc'
TS = 'chrome/browser/ui/tabs/tab_style.cc'
HS = 'chrome/browser/ui/views/tabs/common/horizontal_tab_style_views.cc'
EDITS = [
  # A 176px painted tab has two invisible 4px extensions: 184px bounds.
  (TS, 'constexpr int kSeparatorHorizontalMargin = 5;',
       'constexpr int kSeparatorHorizontalMargin = 3;  // Glyphe: 7px between inactive tabs'),
  (TS, 'constexpr int kTabHorizontalPadding = 2;',
       'constexpr int kTabHorizontalPadding = 10;  // Glyphe: 10px inside painted edge'),
  (TS, 'int TabStyle::GetBottomCornerRadius() const {\n  return 8;\n}',
       'int TabStyle::GetBottomCornerRadius() const {\n  return 4;  // Glyphe: invisible extension, not the painted 8px radius\n}'),
  # The old paint path subtracted the top padding twice, painting only 27px.
  (HS, '      tab_height -= GetLayoutConstant(LayoutConstant::kTabStripPadding) * scale;\n',
       '      // Glyphe: 30px painted height; top padding is outside this height.\n'),
  # Onglet IA: tabs y=5.5..35.5, URL y=41..71, content y=78.
  (LC, '      // Glyphe : rangée de 36 px, 1 px au-dessus, 5 px avant la page.\n'
       '      return gfx::Insets::TLBR(base - 2, base - 1, base + 2, base - 1);',
       '      // Glyphe Onglet IA: URL y=41, h=30; page y=78.\n'
       '      return gfx::Insets::TLBR(base + 3, base + 5, base + 3, base + 5);'),
  ('chrome/browser/ui/views/frame/horizontal_tab_strip_region_view.cc',
       'gfx::Insets::TLBR(0, tab_strip_left_margin.value_or(0), 0,\n'
       '                        tab_strip_right_margin.value_or(0))',
       'gfx::Insets::TLBR(0, tab_strip_left_margin.value_or(0) - 1, 0,  // Glyphe : 1er onglet à 4 px du bord\n'
       '                        tab_strip_right_margin.value_or(0))'),
  ('chrome/browser/ui/views/chrome_typography.cc',
       '      int desired_font_size = is_touch_ui ? 15 : 14;',
       '      int desired_font_size = is_touch_ui ? 15 : 13;  // Glyphe HTML'),
]

# A 14px destination must still sample the complete source bitmap.
EDITS += [
  ('chrome/browser/ui/views/tabs/tab.cc',
   '  // indicator, but visually it will be smaller at kFaviconSize wide.\n  gfx::Rect favicon_bounds(\n      start,\n      contents_rect.y() + Center(contents_rect.height(), gfx::kFaviconSize),\n      0, 0);\n  if (showing_icon_) {\n    if (center_icon_) {\n      // When centering the favicon, the favicon is allowed to escape the normal\n      // contents rect.\n      favicon_bounds.set_x(Center(width(), gfx::kFaviconSize));\n    } else {\n      MaybeAdjustLeftForPinnedTab(&favicon_bounds, gfx::kFaviconSize);\n    }\n    icon_->ResizeDiscardIndicatorRadiusForWidth(\n        width() - 2 * tab_style()->GetBottomCornerRadius());\n',
   '  // indicator, but visually it will be smaller at kFaviconSize wide.\n  gfx::Rect favicon_bounds(\n      start,\n      contents_rect.y() + Center(contents_rect.height(), 16 /* Glyphe favicon */),\n      0, 0);\n  if (showing_icon_) {\n    if (center_icon_) {\n      // When centering the favicon, the favicon is allowed to escape the normal\n      // contents rect.\n      favicon_bounds.set_x(Center(width(), 16 /* Glyphe favicon */));\n    } else {\n      MaybeAdjustLeftForPinnedTab(&favicon_bounds, 16 /* Glyphe favicon */);\n    }\n    icon_->ResizeDiscardIndicatorRadiusForWidth(\n        width() - 2 * tab_style()->GetBottomCornerRadius());\n'),
  ('chrome/browser/ui/views/tabs/tab.cc',
   '      // indicator), but rather the normal favicon width which is what it will\n      // look like.\n      const int after_favicon =\n          favicon_bounds.x() + icon_->GetInsets().left() + gfx::kFaviconSize +\n          GetLayoutConstant(LayoutConstant::kTabPreTitlePadding);\n      title_left = std::max(title_left, after_favicon);\n    }\n',
   '      // indicator), but rather the normal favicon width which is what it will\n      // look like.\n      const int after_favicon =\n          favicon_bounds.x() + icon_->GetInsets().left() + 16 /* Glyphe favicon */ +\n          GetLayoutConstant(LayoutConstant::kTabPreTitlePadding);\n      title_left = std::max(title_left, after_favicon);\n    }\n'),
  ('chrome/browser/ui/views/tabs/tab.cc',
   '  int available_width = GetContentsBounds().width();\n\n  const bool touch_ui = ui::TouchUiController::Get()->touch_ui();\n  const int favicon_width = gfx::kFaviconSize;\n  const int alert_icon_width =\n      alert_indicator_button_->GetPreferredSize().width();\n  // In case of touch optimized UI, the close button has an extra padding on the\n',
   '  int available_width = GetContentsBounds().width();\n\n  const bool touch_ui = ui::TouchUiController::Get()->touch_ui();\n  const int favicon_width = 16 /* Glyphe favicon */;\n  const int alert_icon_width =\n      alert_indicator_button_->GetPreferredSize().width();\n  // In case of touch optimized UI, the close button has an extra padding on the\n'),
  ('chrome/browser/ui/views/tabs/tab/tab_icon.cc',
   '  // elements will anchor to the center of the favicon.\n  SetBorder(views::CreateEmptyBorder(kAttentionIndicatorRadius));\n\n  const int preferred_width = gfx::kFaviconSize + GetInsets().width();\n  SetPreferredSize(gfx::Size(preferred_width, preferred_width));\n\n  // Initial state (before any data) should not be animating.\n',
   '  // elements will anchor to the center of the favicon.\n  SetBorder(views::CreateEmptyBorder(kAttentionIndicatorRadius));\n\n  const int preferred_width = 16 /* Glyphe favicon */ + GetInsets().width();\n  SetPreferredSize(gfx::Size(preferred_width, preferred_width));\n\n  // Initial state (before any data) should not be animating.\n'),
  ('chrome/browser/ui/views/tabs/tab/tab_icon.cc',
   "  }\n\n  gfx::Rect icon_bounds(\n      GetMirroredXWithWidthInView(contents_bounds.x(), gfx::kFaviconSize),\n      contents_bounds.y() +\n          static_cast<int>(contents_bounds.height() * hiding_fraction_),\n      std::min(gfx::kFaviconSize, contents_bounds.width()),\n      std::min(gfx::kFaviconSize, contents_bounds.height()));\n\n  // Don't paint the attention indicator during the loading animation.\n  if (!GetShowingLoadingAnimation() && GetShowingAttentionIndicator() &&\n",
   "  }\n\n  gfx::Rect icon_bounds(\n      GetMirroredXWithWidthInView(contents_bounds.x(), 16 /* Glyphe favicon */),\n      contents_bounds.y() +\n          static_cast<int>(contents_bounds.height() * hiding_fraction_),\n      std::min(16 /* Glyphe favicon */, contents_bounds.width()),\n      std::min(16 /* Glyphe favicon */, contents_bounds.height()));\n\n  // Don't paint the attention indicator during the loading animation.\n  if (!GetShowingLoadingAnimation() && GetShowingAttentionIndicator() &&\n"),
  ('chrome/browser/ui/views/tabs/tab/tab_icon.cc',
   '  TRACE_EVENT0("views", "TabIcon::PaintAttentionIndicatorAndIcon");\n\n  gfx::Point circle_center(\n      bounds.x() + (base::i18n::IsRTL() ? 0 : gfx::kFaviconSize),\n      bounds.y() + gfx::kFaviconSize);\n\n  // The attention indicator consists of two parts:\n  // . a clear (totally transparent) part over the bottom right (or left in rtl)\n',
   '  TRACE_EVENT0("views", "TabIcon::PaintAttentionIndicatorAndIcon");\n\n  gfx::Point circle_center(\n      bounds.x() + (base::i18n::IsRTL() ? 0 : 16 /* Glyphe favicon */),\n      bounds.y() + 16 /* Glyphe favicon */);\n\n  // The attention indicator consists of two parts:\n  // . a clear (totally transparent) part over the bottom right (or left in rtl)\n'),
  ('chrome/browser/ui/views/tabs/tab/tab_icon.cc',
   '  // . a circle in the bottom right (or left in rtl) of the favicon.\n  if (!icon.isNull()) {\n    canvas->SaveLayerAlpha(0xff);\n    canvas->DrawImageInt(icon, 0, 0, bounds.width(), bounds.height(),\n                         bounds.x(), bounds.y(), bounds.width(),\n                         bounds.height(), false);\n    cc::PaintFlags clear_flags;\n',
   '  // . a circle in the bottom right (or left in rtl) of the favicon.\n  if (!icon.isNull()) {\n    canvas->SaveLayerAlpha(0xff);\n    canvas->DrawImageInt(icon, 0, 0, icon.width(), icon.height(),\n                         bounds.x(), bounds.y(), bounds.width(),\n                         bounds.height(), false);\n    cc::PaintFlags clear_flags;\n'),
  ('chrome/browser/ui/views/tabs/tab/tab_icon.cc',
   '  color_matrix.getRowMajor(matrix_data);\n  flags.setColorFilter(cc::ColorFilter::MakeMatrix(matrix_data));\n\n  canvas->DrawImageInt(icon, 0, 0, bounds.width(), bounds.height(), bounds.x(),\n                       bounds.y(), bounds.width(), bounds.height(),\n                       /*filter=*/true, flags);\n\n',
   '  color_matrix.getRowMajor(matrix_data);\n  flags.setColorFilter(cc::ColorFilter::MakeMatrix(matrix_data));\n\n  canvas->DrawImageInt(icon, 0, 0, icon.width(), icon.height(), bounds.x(),\n                       bounds.y(), bounds.width(), bounds.height(),\n                       /*filter=*/true, flags);\n\n'),
  ('chrome/browser/ui/views/tabs/tab/tab_icon.cc',
   '    // stroke + an additional dp to create some visual separation.\n    const float kInitialFaviconInsetDp = 1 + kLoadingAnimationStrokeWidthDp;\n    const float kInitialFaviconDiameterDp =\n        gfx::kFaviconSize - 2 * kInitialFaviconInsetDp +\n        (was_discard_indicator_shown_ ? 2 * increased_discard_indicator_radius_\n                                      : 0);\n    // This a full outset circle of the favicon square. The animation ends with\n    // the entire favicon shown.\n    const float kFinalFaviconDiameterDp = sqrt(2) * gfx::kFaviconSize;\n\n    SkScalar diameter = kInitialFaviconDiameterDp;\n    if (was_discard_indicator_shown_ ||\n',
   '    // stroke + an additional dp to create some visual separation.\n    const float kInitialFaviconInsetDp = 1 + kLoadingAnimationStrokeWidthDp;\n    const float kInitialFaviconDiameterDp =\n        16 /* Glyphe favicon */ - 2 * kInitialFaviconInsetDp +\n        (was_discard_indicator_shown_ ? 2 * increased_discard_indicator_radius_\n                                      : 0);\n    // This a full outset circle of the favicon square. The animation ends with\n    // the entire favicon shown.\n    const float kFinalFaviconDiameterDp = sqrt(2) * 16 /* Glyphe favicon */;\n\n    SkScalar diameter = kInitialFaviconDiameterDp;\n    if (was_discard_indicator_shown_ ||\n'),
  ('chrome/browser/ui/views/tabs/tab/tab_icon.cc',
   '    // This scales and offsets painting so that the drawn favicon is downscaled\n    // to fit in the cropping area.\n    const float offset =\n        (gfx::kFaviconSize -\n         std::min(diameter, SkFloatToScalar(gfx::kFaviconSize))) /\n        2;\n    const float scale = std::min(diameter, SkFloatToScalar(gfx::kFaviconSize)) /\n                        gfx::kFaviconSize;\n    // Translating to/from bounds offset is done to scale around the center\n    // point. This fixes RTL issues where bounds.x() is non-zero. See\n    // https://crbug.com/40730696\n',
   '    // This scales and offsets painting so that the drawn favicon is downscaled\n    // to fit in the cropping area.\n    const float offset =\n        (16 /* Glyphe favicon */ -\n         std::min(diameter, SkFloatToScalar(16 /* Glyphe favicon */))) /\n        2;\n    const float scale = std::min(diameter, SkFloatToScalar(16 /* Glyphe favicon */)) /\n                        16 /* Glyphe favicon */;\n    // Translating to/from bounds offset is done to scale around the center\n    // point. This fixes RTL issues where bounds.x() is non-zero. See\n    // https://crbug.com/40730696\n'),
  ('chrome/browser/ui/views/tabs/tab/tab_icon.cc',
   '    canvas->Translate(gfx::Vector2d(-bounds.x(), -bounds.y()));\n  }\n\n  canvas->DrawImageInt(icon, 0, 0, bounds.width(), bounds.height(), bounds.x(),\n                       bounds.y(), bounds.width(), bounds.height(),\n                       /*filter=*/true);\n}\n',
   '    canvas->Translate(gfx::Vector2d(-bounds.x(), -bounds.y()));\n  }\n\n  canvas->DrawImageInt(icon, 0, 0, icon.width(), icon.height(), bounds.x(),\n                       bounds.y(), bounds.width(), bounds.height(),\n                       /*filter=*/true);\n}\n'),
]

# Tab children are centered in the painted 30px region starting at y=3,
# rather than the full 33px hit target (which includes the top padding).
EDITS += [
  (HS, '          0, 0, GetLayoutConstant(LayoutConstant::kTabstripToolbarOverlap), 0) +',
       '          3, 0, GetLayoutConstant(LayoutConstant::kTabstripToolbarOverlap), 0) +'),
  ('chrome/browser/ui/views/tabs/tab.cc',
       '    const gfx::Rect title_bounds(title_left, GetLocalBounds().y(), title_width,\n'
       '                                 GetLocalBounds().height());',
       '    const gfx::Rect title_bounds(title_left, GetLocalBounds().y() + 3, title_width,\n'
       '                                 GetLocalBounds().height() - 3);'),
]

# Linux window controls share the HTML's 30px buttons, 2px gaps and 8px inset.
# Preserve native window/app dialogs and the platform shadow/resize borders.
FL = 'chrome/browser/ui/views/frame/opaque_browser_frame_view_layout.cc'
EDITS += [
  (FL, '  const int button_width = views::GetCaptionButtonWidth();',
       '  const int button_width = delegate_->IsTabStripVisible()\n'
       '                               ? 30 : views::GetCaptionButtonWidth();'),
  (FL, '    const int height =\n'
       '        delegate_->GetTopAreaHeight() - FrameEdgeInsets(false).top();',
       '    const int height = delegate_->IsTabStripVisible()\n'
       '                           ? 30\n'
       '                           : delegate_->GetTopAreaHeight() - FrameEdgeInsets(false).top();'),
  (FL, '  available_space_trailing_x_ = host->width() - top_area_padding.trailing;\n',
       '  available_space_trailing_x_ = host->width() - top_area_padding.trailing -\n'
       '                                (delegate_->IsTabStripVisible() ? 8 : 0);\n'),
  (FL, '          GetWindowCaptionSpacing(button_id, true, !placed_trailing_button_);',
       '          GetWindowCaptionSpacing(button_id, true, !placed_trailing_button_) +\n'
       '          (delegate_->IsTabStripVisible() && placed_trailing_button_ ? 2 : 0);'),
  ('chrome/browser/ui/views/frame/browser_frame_view_layout_linux.cc',
       '  return FrameEdgeInsets(restored).top();',
       '  return FrameEdgeInsets(restored).top() +\n'
       '         (delegate_->IsTabStripVisible() ? 3 : 0);'),
]

# The native client already has a 1px frame border. Five additional pixels
# give the HTML's six pixels from the actual window edge, including the bottom.
EDITS += [
  ('chrome/browser/ui/views/frame/multi_contents_view.h',
   '  static constexpr int kSplitViewContentInset = 6;  // Glyphe : page en retrait\n',
   '  static constexpr int kSplitViewContentInset = 5;  // Glyphe: 1px native border + 5px = 6px\n'),
]

# Center the new-tab controls on the painted tab row (y=3..33).
EDITS += [
  ('chrome/browser/ui/views/frame/horizontal_tab_strip_region_view.cc',
   'void HorizontalTabStripRegionViewOld::UpdateButtonBorders() {\n  const int extra_vertical_space =\n      GetLayoutConstant(LayoutConstant::kTabStripHeight) -\n      GetLayoutConstant(LayoutConstant::kTabstripToolbarOverlap) -\n      NewTabButton::kButtonSize.height();\n  const int top_inset = extra_vertical_space / 2;',
   'void HorizontalTabStripRegionViewOld::UpdateButtonBorders() {\n  const int extra_vertical_space =\n      GetLayoutConstant(LayoutConstant::kTabStripHeight) -\n      GetLayoutConstant(LayoutConstant::kTabstripToolbarOverlap) -\n      NewTabButton::kButtonSize.height();\n  const int top_inset = extra_vertical_space / 2 + 1;  // Glyphe : centré sur les onglets (y=20)'),
  ('chrome/browser/ui/views/frame/horizontal_tab_strip_region_view.cc',
   'void HorizontalTabStripRegionViewNew::UpdateButtonBorders() {\n  const int extra_vertical_space =\n      GetLayoutConstant(LayoutConstant::kTabStripHeight) -\n      GetLayoutConstant(LayoutConstant::kTabstripToolbarOverlap) -\n      TabStripControlButton::kButtonSize.height();\n  const int top_inset = extra_vertical_space / 2;',
   'void HorizontalTabStripRegionViewNew::UpdateButtonBorders() {\n  const int extra_vertical_space =\n      GetLayoutConstant(LayoutConstant::kTabStripHeight) -\n      GetLayoutConstant(LayoutConstant::kTabstripToolbarOverlap) -\n      TabStripControlButton::kButtonSize.height();\n  const int top_inset = extra_vertical_space / 2 + 1;  // Glyphe : centré sur les onglets (y=20)'),
]

EDITS += [
  # Separators follow the same y=18 center as the icons and tab titles.
  (HS, '      aligned_bounds.y() + extra_vertical_space / 2 + separator_margin.top(),',
       '      aligned_bounds.y() + extra_vertical_space / 2 + separator_margin.top() +\n'
       '          2 * scale,  // Glyphe: center on the painted tab row'),
  # The HTML has separators only BETWEEN tabs, not before the + button.
  (HS, '  const TabStyleViewDelegate* const adjacent_tab =\n'
       '      delegate_->GetAdjacentTab(leading);\n',
       '  const TabStyleViewDelegate* const adjacent_tab =\n'
       '      delegate_->GetAdjacentTab(leading);\n'
       '  if (!adjacent_tab) {\n'
       '    return 0.0f;  // Glyphe: no separator at the ends of the strip.\n'
       '  }\n'),
]


# Selection never changes horizontal geometry: use a fixed gap for every tab.
# The IA board's content-box rows are 38px + 40px, including their padding.
EDITS += [
  (LC, '    case LayoutConstant::kTabHeight:\n      return 30;  // Glyphe\n',
       '    case LayoutConstant::kTabHeight:\n      return 35;  // Glyphe IA: 38px strip including 3px padding\n'),
  (HS, '    float tab_height = GetLayoutConstant(LayoutConstant::kTabHeight) * scale;',
       '    float tab_height = 32 * scale;  // Bluelium : 32 px, le trait de groupe passe dessous'),
  (HS, '    float top = aligned_bounds.y() +\n'
       '                GetLayoutConstant(LayoutConstant::kTabStripPadding) * scale;',
       '    float top = aligned_bounds.y() + 4.0f * scale;  // Glyphe : 4 px au-dessus, 4 px avant l’adresse'),
]
