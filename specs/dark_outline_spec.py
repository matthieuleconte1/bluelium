"""Bluelium : variante A « Trait fin », uniquement en OLED et en Nuit.
Les pointillés utilisent cc::PathEffect::MakeDash, adaptateur sérialisable de
SkDashPathEffect pour cc::PaintFlags dans Chromium 157 (pas un SkPathEffect brut).
"""
NEW_FILES = {
'ui/color/bluelium_dark_outline.h': r'''// Bluelium : couleurs communes du trait fin, sans modifier les autres modes.
#ifndef UI_COLOR_BLUELIUM_DARK_OUTLINE_H_
#define UI_COLOR_BLUELIUM_DARK_OUTLINE_H_
#include "ui/color/glyphe_prism.h"
#include "ui/color/glyphe_red_night.h"
namespace ui {
inline bool BlueliumDarkOutline() {
  return IsGlypheRedNight() || IsGlypheOled();
}
inline SkColor BlueliumDarkOutlineAccent() {
  return IsGlypheRedNight() ? GlypheRedNightColor() : SkColorSetRGB(0xec, 0xec, 0xef);
}
inline SkColor BlueliumDarkOutlineTab() {
  return IsGlypheRedNight() ? GlypheRedNightColor() :
      SkColorSetA(BlueliumDarkOutlineAccent(), 0x8c);
}
inline SkColor BlueliumDarkOutlineDivider() {
  return IsGlypheRedNight() ? SkColorSetA(GlypheRedNightColor(), 0x52) :
      SkColorSetRGB(0x3a, 0x3a, 0x42);
}
}  // namespace ui
#endif  // UI_COLOR_BLUELIUM_DARK_OUTLINE_H_
''',
}
HS = 'chrome/browser/ui/views/tabs/common/horizontal_tab_style_views.cc'
TB = 'chrome/browser/ui/views/toolbar/toolbar_view.'
IA = 'chrome/browser/ui/views/toolbar/pinned_action_toolbar_button.'
LB = 'chrome/browser/ui/views/location_bar/location_bar_view.cc'
EDITS = [
 ('ui/color/BUILD.gn', '    "glyphe_prism.h",\n',
  '    "glyphe_prism.h",\n    "bluelium_dark_outline.h",\n'),
 (HS, '#include "chrome/browser/ui/views/tabs/common/horizontal_tab_style_views.h"\n',
  '#include "chrome/browser/ui/views/tabs/common/horizontal_tab_style_views.h"\n'
  '#include "ui/color/bluelium_dark_outline.h"\n'
  '#include "cc/paint/path_effect.h"\n'),
 (HS, '  std::optional<SkColor> group_color = delegate_->GetGroupColor();\n\n'
  '  PaintTabBackgroundFill(canvas, hovered, fill_id);\n',
  '  // Bluelium : pas de remplissage, de survol peint ni de contour Chromium doublé.\n'
  '  if (ui::BlueliumDarkOutline()) {\n'
  '    if (delegate_->IsActive()) {\n'
  '      const SkPath path = GetPath(TabStyle::PathType::kBorder,\n'
  '          canvas->image_scale(), {.should_paint_extension = false});\n'
  '      gfx::ScopedCanvas scoped(canvas);\n'
  '      const float scale = canvas->UndoDeviceScaleFactor();\n'
  '      cc::PaintFlags flags;\n'
  '      flags.setAntiAlias(true);\n'
  '      flags.setStyle(cc::PaintFlags::kStroke_Style);\n'
  '      flags.setStrokeWidth(scale);\n'
  '      flags.setColor(ui::BlueliumDarkOutlineTab());\n'
  '      canvas->DrawPath(path, flags);\n'
  '    }\n'
  '    PaintSeparators(canvas);\n'
  '    return;\n'
  '  }\n'
  '  std::optional<SkColor> group_color = delegate_->GetGroupColor();\n\n'
  '  PaintTabBackgroundFill(canvas, hovered, fill_id);\n'),
 (HS, 'void HorizontalTabStyleViews::PaintBackgroundHover(gfx::Canvas* canvas,\n'
  '                                                   float scale) const {\n',
  'void HorizontalTabStyleViews::PaintBackgroundHover(gfx::Canvas* canvas,\n'
  '                                                   float scale) const {\n'
  '  if (ui::BlueliumDarkOutline()) {\n'
  '    return;  // Bluelium : la pastille reste sans remplissage au survol.\n'
  '  }\n'),
 (HS, 'void HorizontalTabStyleViews::PaintSeparators(gfx::Canvas* canvas) const {\n',
  'void HorizontalTabStyleViews::PaintSeparators(gfx::Canvas* canvas) const {\n'
  '  if (ui::BlueliumDarkOutline()) {\n'
  '    const auto* next = delegate_->GetAdjacentTab(false);\n'
  '    if (delegate_->IsActive() || !next || next->IsActive()) {\n'
  '      return;\n'
  '    }\n'
  '    // Bluelium : un seul trait par paire, du côté logique suivant (RTL compris).\n'
  '    gfx::ScopedCanvas scoped(canvas);\n'
  '    const float scale = canvas->UndoDeviceScaleFactor();\n'
  '    const auto bounds = GetSeparatorBounds(scale);\n'
  '    const float x = (base::i18n::IsRTL() ? bounds.leading : bounds.trailing).CenterPoint().x();\n'
  '    cc::PaintFlags flags;\n'
  '    flags.setAntiAlias(false);\n'
  '    flags.setStyle(cc::PaintFlags::kStroke_Style);\n'
  '    flags.setStrokeWidth(scale);\n'
  '    flags.setColor(ui::BlueliumDarkOutlineDivider());\n'
  '    const float intervals[] = {scale, scale};  // Bluelium : point 1 px, pas 2 px.\n'
  '    flags.setPathEffect(cc::PathEffect::MakeDash(intervals, 2, 0));\n'
  '    canvas->DrawLine(gfx::PointF(x, 13 * scale), gfx::PointF(x, 27 * scale), flags);\n'
  '    return;\n'
  '  }\n'),
 (LB, '#include "chrome/browser/ui/views/location_bar/location_bar_view.h"\n',
  '#include "chrome/browser/ui/views/location_bar/location_bar_view.h"\n'
  '#include "ui/color/bluelium_dark_outline.h"\n'),
 (LB, '  if (is_popup_mode_) {\n'
  '    SetBackground(views::CreateSolidBackground(background_color_));\n',
  '  if (ui::BlueliumDarkOutline() && !is_popup_mode_) {\n'
  '    background_color_ = SK_ColorTRANSPARENT;  // Bluelium : champ sans aplat.\n'
  '    border_color = ui::BlueliumDarkOutlineDivider();\n'
  '  }\n'
  '  if (is_popup_mode_) {\n'
  '    SetBackground(views::CreateSolidBackground(background_color_));\n'),
 (TB + 'h', '  void OnThemeChanged() override;\n',
  '  void OnThemeChanged() override;\n'
  '  void OnPaint(gfx::Canvas* canvas) override;  // Bluelium : trait sous les onglets\n'),
 (TB + 'cc', '#include "chrome/browser/ui/views/toolbar/toolbar_view.h"\n',
  '#include "chrome/browser/ui/views/toolbar/toolbar_view.h"\n'
  '#include "ui/color/bluelium_dark_outline.h"\n'
  '#include "cc/paint/paint_flags.h"\n'
  '#include "cc/paint/path_effect.h"\n'
  '#include "ui/gfx/canvas.h"\n'),
 (TB + 'cc', 'void ToolbarView::OnThemeChanged() {\n',
  'void ToolbarView::OnPaint(gfx::Canvas* canvas) {\n'
  '  views::AccessiblePaneView::OnPaint(canvas);\n'
  '  if (ui::BlueliumDarkOutline() && browser_view_->ShouldDrawTabStrip()) {\n'
  '    cc::PaintFlags flags;\n'
  '    flags.setColor(ui::BlueliumDarkOutlineDivider());\n'
  '    flags.setStyle(cc::PaintFlags::kStroke_Style);\n'
  '    flags.setStrokeWidth(1.f);\n'
  '    const float intervals[] = {1.f, 1.f};\n'
  '    flags.setPathEffect(cc::PathEffect::MakeDash(intervals, 2, 0));\n'
  '    canvas->DrawLine(gfx::PointF(0, 0.5f), gfx::PointF(width(), 0.5f), flags);\n'
  '  }\n'
  '}\n\n'
  'void ToolbarView::OnThemeChanged() {\n'),
 (IA + 'h', '  void UpdateColorsAndInsets() override;\n',
  '  void UpdateColorsAndInsets() override;\n'
  '  void OnPaintBackground(gfx::Canvas* canvas) override;  // Bluelium : anneau IA\n'),
 (IA + 'cc', '#include "ui/color/glyphe_prism.h"',
  '#include "ui/color/glyphe_prism.h"\n'
  '#include "ui/color/bluelium_dark_outline.h"\n'
  '#include "cc/paint/paint_flags.h"\n'
  '#include "ui/gfx/canvas.h"\n#include <algorithm>'),
 (IA + 'cc', '  const SkColor icon = glyphe_active\n'
  '                           ? on_seed\n'
  '                           : colors->GetColor(kColorToolbarButtonIcon);\n',
  '  const SkColor icon = ui::BlueliumDarkOutline() ? ui::BlueliumDarkOutlineAccent() :\n'
  '      glyphe_active ? on_seed : colors->GetColor(kColorToolbarButtonIcon);\n'),
 (IA + 'cc', '  SetBackground(views::CreateRoundedRectBackground(background, 15));\n',
  '  SetBackground(views::CreateRoundedRectBackground(\n'
  '      ui::BlueliumDarkOutline() && glyphe_active ? SK_ColorTRANSPARENT : background, 15));\n'),
 (IA + 'cc', 'void PinnedActionToolbarButton::UpdateIcon() {\n',
  'void PinnedActionToolbarButton::OnPaintBackground(gfx::Canvas* canvas) {\n'
  '  ToolbarButton::OnPaintBackground(canvas);\n'
  '  if (action_id_ == kActionSidePanelShowGlypheAssistant && IsActive() &&\n'
  '      ui::BlueliumDarkOutline()) {\n'
  '    cc::PaintFlags flags;\n'
  '    flags.setAntiAlias(true);\n'
  '    flags.setStyle(cc::PaintFlags::kStroke_Style);\n'
  '    flags.setStrokeWidth(1.f);\n'
  '    flags.setColor(ui::BlueliumDarkOutlineAccent());\n'
  '    canvas->DrawCircle(gfx::PointF(width() / 2.f, height() / 2.f),\n'
  '                       (std::min(width(), height()) - 1) / 2.f, flags);\n'
  '  }\n'
  '}\n\n'
  'void PinnedActionToolbarButton::UpdateIcon() {\n'),
 ('chrome/browser/ui/color/chrome_color_mixers.cc',
  '#include "ui/color/glyphe_prism.h"\n',
  '#include "ui/color/glyphe_prism.h"\n#include "ui/color/bluelium_dark_outline.h"\n'),
 ('chrome/browser/ui/color/chrome_color_mixers.cc',
  '  if (key.app_controller) {\n'
  '    key.app_controller->AddColorMixers(provider, key);\n',
  '  if (ui::BlueliumDarkOutline()) {\n'
  '    ui::ColorMixer& outline = provider->AddMixer();\n'
  '    // Bluelium : texte lisible dans la pastille vide et séparateurs solides.\n'
  '    outline[kColorTabForegroundActiveFrameActive] = {ui::BlueliumDarkOutlineAccent()};\n'
  '    outline[kColorTabForegroundActiveFrameInactive] = {ui::BlueliumDarkOutlineAccent()};\n'
  '    outline[kColorToolbarSeparatorDefault] = {ui::BlueliumDarkOutlineDivider()};\n'
  '    outline[kColorToolbarExtensionSeparatorEnabled] = {ui::BlueliumDarkOutlineDivider()};\n'
  '  }\n\n'
  '  if (key.app_controller) {\n'
  '    key.app_controller->AddColorMixers(provider, key);\n'),
]
