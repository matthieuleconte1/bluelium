"""Bluelium : logo du navigateur en haut à gauche des onglets ouvrant le menu « ⋯ ».

- Onglets horizontaux (HorizontalTabStripRegionViewOld et New) : le logo de
  Bluelium est le premier élément à gauche de la bande d'onglets (après les
  feux tricolores sur macOS grâce à HasLeadingButtons()).
- Onglets verticaux (VerticalTabStripRegionView) : le logo est tout en haut de
  la bande verticale, au-dessus des onglets, aligné avec les favicons en mode
  étendu et centré en mode replié.
- Un clic (ou Alt+F / Alt+E / ShowAppMenu / activation clavier) ouvre le même
  menu d'application (AppMenu / ActionAppMenu), ancré sous le logo.
- Le bouton « ⋯ » reste à droite de la barre, avec une icône Bluelium : trois
  points ronds horizontaux (bluelium_more.icon). S'il est masqué dans
  Personnaliser, les ancres de bulles (GetAnchor / IsDrawn) et le focus
  clavier (Focus / HasFocus) basculent vers le logo actif.
- Les alertes et mises à jour (linux_update_spec.py, Sparkle / UpgradeDetector,
  GlobalError, HeliumServicesUpdate) sont reportées directement sur le logo par
  une pastille colorée selon la sévérité, avec mise à jour de l'info-bulle et
  du nom accessible.
- Aucun logo dans les fenêtres PWA, popup ou plein écran sans bande d'onglets.
"""

BROWSER_LOGO_H = 'chrome/browser/ui/views/frame/browser_logo_menu_button.h'
BROWSER_LOGO_CC = 'chrome/browser/ui/views/frame/browser_logo_menu_button.cc'

NEW_FILES = {
    'chrome/app/vector_icons/bluelium_more.icon': '''// Bluelium : menu « ⋯ », trois points ronds horizontaux.
CANVAS_DIMENSIONS, 20,
CIRCLE, 4.5, 10, 1.75,
CIRCLE, 10, 10, 1.75,
CIRCLE, 15.5, 10, 1.75
''',
    BROWSER_LOGO_H: '''// Copyright 2026 The Bluelium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef CHROME_BROWSER_UI_VIEWS_FRAME_BROWSER_LOGO_MENU_BUTTON_H_
#define CHROME_BROWSER_UI_VIEWS_FRAME_BROWSER_LOGO_MENU_BUTTON_H_

#include "base/callback_list.h"
#include "base/memory/raw_ptr.h"
#include "chrome/browser/ui/toolbar/app_menu_icon_controller.h"
#include "ui/base/metadata/metadata_header_macros.h"
#include "ui/gfx/geometry/rect.h"
#include "ui/gfx/geometry/size.h"
#include "ui/gfx/image/image_skia.h"
#include "ui/gfx/animation/slide_animation.h"
#include "ui/views/controls/button/label_button.h"

class BrowserView;

namespace views {
class MenuButtonController;
}  // namespace views

// Bluelium : bouton portant le logo produit en haut à gauche de la bande
// d'onglets (horizontale ou verticale) et ouvrant le menu de l'application.
class BrowserLogoMenuButton : public views::LabelButton {
  METADATA_HEADER(BrowserLogoMenuButton, views::LabelButton)

 public:
  static gfx::Size GetButtonSize();

  explicit BrowserLogoMenuButton(BrowserView* browser_view);
  BrowserLogoMenuButton(const BrowserLogoMenuButton&) = delete;
  BrowserLogoMenuButton& operator=(const BrowserLogoMenuButton&) = delete;
  ~BrowserLogoMenuButton() override;

  views::MenuButtonController* menu_button_controller() const {
    return menu_button_controller_;
  }

  // Ouvre le menu comme si l'utilisateur activait le bouton au clavier.
  void ActivateMenu();

  // Reporte la sévérité (mise à jour disponible, erreur) sous forme de
  // pastille colorée et met à jour l'info-bulle et le nom accessible.
  void SetTypeAndSeverity(
      AppMenuIconController::TypeAndSeverity type_and_severity);

  // Bluelium : séparateur peint par le bouton, à droite (onglets
  // horizontaux) ou dessous (onglets verticaux).
  enum class SeparatorSide { kNone, kTrailing, kBottom };
  void SetSeparatorSide(SeparatorSide side);
  // Onglets verticaux : logo centré (bande repliée) ou aligné à gauche.
  void SetIconCentered(bool centered);
  // Zone carrée du logo (survol, ancrage du menu), hors séparateur.
  gfx::Rect GetIconBounds() const;

  // views::LabelButton / views::View :
  gfx::Size CalculatePreferredSize(
      const views::SizeBounds& available_size) const override;
  views::ProposedLayout CalculateProposedLayout(
      const views::SizeBounds& size_bounds) const override;
  gfx::Rect GetAnchorBoundsInScreen() const override;
  void AddedToWidget() override;
  void RemovedFromWidget() override;
  void OnThemeChanged() override;
  bool HandleAccessibleAction(const ui::AXActionData& action_data) override;
  void StateChanged(ButtonState old_state) override;
  void PaintButtonContents(gfx::Canvas* canvas) override;

  // views::AnimationDelegateViews (hérité de views::Button) :
  void AnimationProgressed(const gfx::Animation* animation) override;
  void AnimationEnded(const gfx::Animation* animation) override;

 private:
  void ButtonPressed(const ui::Event& event);
  void UpdateInkDrop();
  void UpdateLogoImage();
  void UpdateAccessibleAndTooltip();

  raw_ptr<BrowserView> browser_view_ = nullptr;
  raw_ptr<views::MenuButtonController> menu_button_controller_ = nullptr;
  AppMenuIconController::TypeAndSeverity type_and_severity_{
      AppMenuIconController::IconType::kNone,
      AppMenuIconController::Severity::kNone};
  base::CallbackListSubscription paint_as_active_subscription_;

  // Bluelium : rendu et animation du logo.
  SeparatorSide separator_side_ = SeparatorSide::kNone;
  bool icon_centered_ = false;
  SkColor logo_color_ = SK_ColorTRANSPARENT;
  SkColor separator_color_ = SK_ColorTRANSPARENT;
  SkColor pill_fill_color_ = SK_ColorTRANSPARENT;
  SkColor pill_border_color_ = SK_ColorTRANSPARENT;
  std::optional<SkColor> badge_color_;
  SkColor ring_color_ = SK_ColorTRANSPARENT;
  gfx::SlideAnimation hover_animation_{this};
  gfx::SlideAnimation press_animation_{this};
};

#endif  // CHROME_BROWSER_UI_VIEWS_FRAME_BROWSER_LOGO_MENU_BUTTON_H_
''',
    BROWSER_LOGO_CC: '''// Copyright 2026 The Bluelium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "chrome/browser/ui/views/frame/browser_logo_menu_button.h"

#include <memory>
#include <optional>
#include <utility>

#include "base/functional/bind.h"
#include "cc/paint/paint_flags.h"
#include "chrome/browser/ui/color/chrome_color_id.h"
#include "chrome/browser/ui/layout_constants.h"
#include "chrome/browser/ui/views/frame/browser_view.h"
#include "chrome/browser/ui/views/frame/toolbar_button_provider.h"
#include "chrome/browser/ui/views/toolbar/app_menu_control.h"
#include "chrome/browser/ui/views/toolbar/toolbar_ink_drop_util.h"
#include "chrome/grit/theme_resources.h"
#include "skia/ext/image_operations.h"
#include "third_party/skia/include/core/SkPath.h"
#include "third_party/skia/include/core/SkPathBuilder.h"
#include "third_party/skia/include/core/SkRRect.h"
#include "ui/accessibility/ax_action_data.h"
#include "ui/accessibility/ax_enums.mojom.h"
#include "ui/base/metadata/metadata_impl_macros.h"
#include "ui/base/models/image_model.h"
#include "ui/base/resource/resource_bundle.h"
#include "ui/color/color_id.h"
#include "ui/color/color_provider.h"
#include "ui/compositor/layer.h"
#include "ui/events/event.h"
#include "ui/gfx/canvas.h"
#include "ui/gfx/color_utils.h"
#include "ui/gfx/scoped_canvas.h"
#include "ui/gfx/animation/tween.h"
#include "ui/gfx/geometry/insets.h"
#include "ui/gfx/geometry/point_f.h"
#include "ui/gfx/geometry/skia_conversions.h"
#include "ui/gfx/image/canvas_image_source.h"
#include "ui/gfx/image/image_skia_operations.h"
#include "ui/views/accessibility/view_accessibility.h"
#include "ui/views/animation/ink_drop.h"
#include "ui/views/controls/button/menu_button_controller.h"
#include "ui/views/controls/focus_ring.h"
#include "ui/views/controls/highlight_path_generator.h"
#include "ui/views/controls/menu/menu_runner.h"
#include "ui/views/layout/proposed_layout.h"
#include "ui/views/widget/widget.h"

namespace {

constexpr int kLogoIconSize = 18;
constexpr int kLogoCanvasSize = 22;
constexpr int kLogoCornerRadius = 8;

class LogoButtonHighlightPathGenerator : public views::HighlightPathGenerator {
 public:
  SkPath GetHighlightPath(const views::View* view) override {
    const gfx::Rect rect(
        static_cast<const BrowserLogoMenuButton*>(view)->GetIconBounds());
    return SkPath::RRect(SkRRect::MakeRectXY(
        gfx::RectToSkRect(rect), kLogoCornerRadius, kLogoCornerRadius));
  }
};

// Bluelium : astérisque de la DA (planche « Mode compact »), en aplat de la
// couleur des boutons de la bande d'onglets, sans fond. Tracé 256 x 256,
// centré sur l'origine pour tourner sur lui-même.
SkPath BlueliumAsteriskPath(float size) {
  static constexpr float kPoints[][2] = {
      {152.62f, 237.85f}, {128.f, 256.f},      {103.38f, 237.85f},
      {114.568f, 151.248f}, {45.05f, 204.22f}, {17.f, 192.f},
      {20.425f, 161.635f}, {101.128f, 128.f},  {20.425f, 94.365f},
      {17.f, 64.f},        {45.05f, 51.78f},   {114.568f, 104.752f},
      {103.38f, 18.15f},   {128.f, 0.f},       {152.62f, 18.15f},
      {141.432f, 104.752f}, {210.95f, 51.78f}, {239.f, 64.f},
      {235.575f, 94.365f}, {154.872f, 128.f},  {235.575f, 161.635f},
      {239.f, 192.f},      {210.95f, 204.22f}, {141.432f, 151.248f}};
  const float scale = size / 256.f;
  SkPathBuilder builder;
  bool first = true;
  for (const auto& point : kPoints) {
    const SkPoint p = SkPoint::Make((point[0] - 128.f) * scale,
                                    (point[1] - 128.f) * scale);
    if (first) {
      builder.moveTo(p);
      first = false;
    } else {
      builder.lineTo(p);
    }
  }
  builder.close();
  return builder.detach();
}

// Survol : l'astérisque tourne d'une branche (60°, il retombe sur sa forme)
// en grossissant un peu ; il se déroule à la sortie. Appui : il se tasse.
constexpr base::TimeDelta kHoverDuration = base::Milliseconds(420);
constexpr base::TimeDelta kPressDuration = base::Milliseconds(140);
constexpr float kHoverRotationDegrees = 60.f;
constexpr float kHoverScale = 0.10f;
constexpr float kPressScale = 0.12f;
// Pastille façon Ladybird : astérisque + chevron à l'accent, fond et contour
// tirés du cadre. 42 x 26 px dans une zone de 44 x 30.
constexpr int kPillWidth = 42;
constexpr int kPillHeight = 26;
constexpr float kPillRadius = 8.f;
constexpr int kPillLeftPadding = 6;
constexpr int kChevronGap = 5;
constexpr float kChevronHalfWidth = 3.5f;
constexpr float kChevronHoverDrop = 1.5f;
// Séparateur : trait de 1 px, 16 px de long, à 8 px de la pastille ; avec la
// marge droite (2 px) et le retrait de l'onglet (3 px), à 9 px de l'onglet.
constexpr int kSeparatorGapBefore = 8;
constexpr int kSeparatorGapAfter = 4;
constexpr int kSeparatorGap = kSeparatorGapAfter;
constexpr int kSeparatorLength = 16;
constexpr int kSeparatorExtent = kSeparatorGapBefore + 1 + kSeparatorGapAfter;

}  // namespace

// static
gfx::Size BrowserLogoMenuButton::GetButtonSize() {
  const int height = GetLayoutConstant(LayoutConstant::kLocationBarHeight);
  return gfx::Size(kPillWidth + 2, height);
}

BrowserLogoMenuButton::BrowserLogoMenuButton(BrowserView* browser_view)
    : views::LabelButton(PressedCallback()),
      browser_view_(browser_view) {
  hover_animation_.SetSlideDuration(kHoverDuration);
  hover_animation_.SetTweenType(gfx::Tween::FAST_OUT_SLOW_IN);
  press_animation_.SetSlideDuration(kPressDuration);
  press_animation_.SetTweenType(gfx::Tween::EASE_OUT);
  auto menu_button_controller = std::make_unique<views::MenuButtonController>(
      this,
      base::BindRepeating(&BrowserLogoMenuButton::ButtonPressed,
                          base::Unretained(this)),
      std::make_unique<views::Button::DefaultButtonControllerDelegate>(this));
  menu_button_controller_ = menu_button_controller.get();
  SetButtonController(std::move(menu_button_controller));

  SetHorizontalAlignment(gfx::ALIGN_CENTER);
  SetImageCentered(false);
  SetFocusBehavior(FocusBehavior::ACCESSIBLE_ONLY);
  GetViewAccessibility().SetHasPopup(ax::mojom::HasPopup::kMenu);

  views::FocusRing::Get(this)->SetColorId(kColorNewTabButtonFocusRing);
  // Bluelium : pas d'effet d'encre. Peint au-dessus du logo, il l'assombrit
  // au survol et le recouvre pendant que le menu est ouvert ; l'animation de
  // l'astérisque sert de retour visuel.
  views::InkDrop::Get(this)->SetMode(views::InkDropHost::InkDropMode::OFF);
  views::HighlightPathGenerator::Install(
      this, std::make_unique<LogoButtonHighlightPathGenerator>());

  SetPaintToLayer();
  layer()->SetFillsBoundsOpaquely(false);

  UpdateAccessibleAndTooltip();
  UpdateLogoImage();
}

BrowserLogoMenuButton::~BrowserLogoMenuButton() = default;

void BrowserLogoMenuButton::ActivateMenu() {
  menu_button_controller_->Activate(nullptr);
}

void BrowserLogoMenuButton::SetTypeAndSeverity(
    AppMenuIconController::TypeAndSeverity type_and_severity) {
  if (type_and_severity_ == type_and_severity) {
    return;
  }
  type_and_severity_ = type_and_severity;
  UpdateAccessibleAndTooltip();
  UpdateLogoImage();
}

gfx::Size BrowserLogoMenuButton::CalculatePreferredSize(
    const views::SizeBounds& available_size) const {
  gfx::Size size = GetButtonSize();
  if (separator_side_ == SeparatorSide::kTrailing) {
    size.Enlarge(kSeparatorExtent, 0);
  } else if (separator_side_ == SeparatorSide::kBottom) {
    size.Enlarge(0, kSeparatorExtent);
  }
  const gfx::Insets insets = GetInsets();
  size.Enlarge(insets.width(), insets.height());
  return size;
}

views::ProposedLayout BrowserLogoMenuButton::CalculateProposedLayout(
    const views::SizeBounds& size_bounds) const {
  views::ProposedLayout layout =
      views::LabelButton::CalculateProposedLayout(size_bounds);
  // Bluelium : centrer le logo sur la zone de survol (marges Fitts exclues),
  // comme pour le bouton « + » dans newtab_button_spec.py.
  if (!size_bounds.height().is_bounded()) {
    return layout;
  }
  const gfx::Insets insets = GetInsets();
  const int content_height = size_bounds.height().value() - insets.height();
  const views::View* const image = image_container_view();
  for (auto& child : layout.child_layouts) {
    if (child.child_view.get() == image) {
      child.bounds.set_y(insets.top() +
                         (content_height - child.bounds.height()) / 2);
    }
  }
  return layout;
}

gfx::Rect BrowserLogoMenuButton::GetAnchorBoundsInScreen() const {
  gfx::Rect bounds = GetIconBounds();
  ConvertRectToScreen(this, &bounds);
  return bounds;
}

void BrowserLogoMenuButton::AddedToWidget() {
  paint_as_active_subscription_ =
      GetWidget()->RegisterPaintAsActiveChangedCallback(base::BindRepeating(
          &BrowserLogoMenuButton::UpdateLogoImage, base::Unretained(this)));
  UpdateInkDrop();
  UpdateLogoImage();
}

void BrowserLogoMenuButton::RemovedFromWidget() {
  paint_as_active_subscription_ = {};
}

void BrowserLogoMenuButton::OnThemeChanged() {
  views::LabelButton::OnThemeChanged();
  UpdateInkDrop();
  UpdateLogoImage();
}

bool BrowserLogoMenuButton::HandleAccessibleAction(
    const ui::AXActionData& action_data) {
  if (action_data.action == ax::mojom::Action::kExpand) {
    if (browser_view_) {
      browser_view_->ShowAppMenuFromLogo(this, views::MenuRunner::NO_FLAGS);
    }
    return true;
  }
  if (action_data.action == ax::mojom::Action::kCollapse) {
    if (browser_view_) {
      if (auto* provider = browser_view_->toolbar_button_provider()) {
        if (auto* control = provider->GetAppMenuControl();
            control && control->IsMenuShowing()) {
          control->CloseMenu();
        }
      }
    }
    return true;
  }
  return views::LabelButton::HandleAccessibleAction(action_data);
}

void BrowserLogoMenuButton::ButtonPressed(const ui::Event& event) {
  if (!browser_view_) {
    return;
  }
  const int run_types = event.IsKeyEvent()
                            ? (views::MenuRunner::SHOULD_SHOW_MNEMONICS |
                               views::MenuRunner::INVOKED_FROM_KEYBOARD)
                            : views::MenuRunner::NO_FLAGS;
  browser_view_->ShowAppMenuFromLogo(this, run_types);
}

void BrowserLogoMenuButton::UpdateInkDrop() {
  if (!GetColorProvider() || !GetWidget() || GetWidget()->IsClosed()) {
    return;
  }
  // Bluelium : effet d'encre désactivé (voir le constructeur).
}

void BrowserLogoMenuButton::UpdateLogoImage() {
  std::optional<SkColor> badge_color;
  SkColor ring_color = SK_ColorTRANSPARENT;
  SkColor logo_color = SK_ColorTRANSPARENT;

  if (const ui::ColorProvider* color_provider = GetColorProvider()) {
    const bool active = !GetWidget() || GetWidget()->ShouldPaintAsActive();
    ring_color = color_provider->GetColor(active ? ui::kColorFrameActive
                                                 : ui::kColorFrameInactive);
    // Bluelium : accent du thème (comme le logo de Ladybird).
    logo_color = color_provider->GetColor(ui::kColorSysPrimary);
    const SkColor frame = color_provider->GetColor(
        active ? ui::kColorFrameActive : ui::kColorFrameInactive);
    const SkColor ink = color_provider->GetColor(
        active ? kColorTabForegroundActiveFrameActive
               : kColorTabForegroundActiveFrameInactive);
    pill_fill_color_ = color_utils::AlphaBlend(ink, frame, SkAlpha{0x10});
    pill_border_color_ = color_utils::AlphaBlend(ink, frame, SkAlpha{0x30});
    separator_color_ = color_provider->GetColor(
        active ? kColorTabDividerFrameActive : kColorTabDividerFrameInactive);
    switch (type_and_severity_.severity) {
      case AppMenuIconController::Severity::kNone:
        break;
      case AppMenuIconController::Severity::kLow:
        badge_color = color_provider->GetColor(ui::kColorAlertLowSeverity);
        break;
      case AppMenuIconController::Severity::kMedium:
        badge_color =
            color_provider->GetColor(ui::kColorAlertMediumSeverityIcon);
        break;
      case AppMenuIconController::Severity::kHigh:
        badge_color = color_provider->GetColor(ui::kColorAlertHighSeverity);
        break;
    }
  }

  logo_color_ = logo_color;
  badge_color_ = badge_color;
  ring_color_ = ring_color;
  SchedulePaint();
}

void BrowserLogoMenuButton::SetSeparatorSide(SeparatorSide side) {
  if (separator_side_ == side) {
    return;
  }
  separator_side_ = side;
  PreferredSizeChanged();
  SchedulePaint();
}

void BrowserLogoMenuButton::SetIconCentered(bool centered) {
  if (icon_centered_ == centered) {
    return;
  }
  icon_centered_ = centered;
  SchedulePaint();
}

gfx::Rect BrowserLogoMenuButton::GetIconBounds() const {
  const gfx::Rect contents = GetContentsBounds();
  const gfx::Size area = GetButtonSize();
  int x = contents.x() + 1;
  int y = contents.y() + (area.height() - kPillHeight) / 2;
  if (separator_side_ == SeparatorSide::kBottom) {
    if (icon_centered_) {
      x = contents.x() + (contents.width() - kPillWidth) / 2;
    }
  } else {
    y = contents.y() + (contents.height() - kPillHeight) / 2;
  }
  return gfx::Rect(x, y, kPillWidth, kPillHeight);
}

void BrowserLogoMenuButton::StateChanged(ButtonState old_state) {
  views::LabelButton::StateChanged(old_state);
  const bool animate = gfx::Animation::ShouldRenderRichAnimation();
  hover_animation_.SetSlideDuration(animate ? kHoverDuration
                                            : base::TimeDelta());
  press_animation_.SetSlideDuration(animate ? kPressDuration
                                            : base::TimeDelta());
  const ButtonState state = GetState();
  if (state == STATE_HOVERED || state == STATE_PRESSED) {
    hover_animation_.Show();
  } else {
    hover_animation_.Hide();
  }
  if (state == STATE_PRESSED) {
    press_animation_.Show();
  } else {
    press_animation_.Hide();
  }
}

void BrowserLogoMenuButton::AnimationProgressed(
    const gfx::Animation* animation) {
  views::LabelButton::AnimationProgressed(animation);
  SchedulePaint();
}

void BrowserLogoMenuButton::AnimationEnded(const gfx::Animation* animation) {
  views::LabelButton::AnimationEnded(animation);
  SchedulePaint();
}

void BrowserLogoMenuButton::PaintButtonContents(gfx::Canvas* canvas) {
  const gfx::Rect icon = GetIconBounds();

  // Séparateur entre le logo et les onglets.
  if (separator_side_ == SeparatorSide::kTrailing) {
    canvas->FillRect(gfx::Rect(icon.right() + kSeparatorGapBefore,
                               icon.CenterPoint().y() - kSeparatorLength / 2,
                               1, kSeparatorLength),
                     separator_color_);
  } else if (separator_side_ == SeparatorSide::kBottom) {
    const gfx::Rect contents = GetContentsBounds();
    canvas->FillRect(gfx::Rect(contents.x() + 4, icon.bottom() + kSeparatorGap,
                               std::max(0, contents.width() - 8), 1),
                     separator_color_);
  }

  const double hover = hover_animation_.GetCurrentValue();
  const double press = press_animation_.GetCurrentValue();

  // Pastille : fond et contour légèrement plus clairs que le cadre.
  {
    const gfx::RectF pill(icon);
    cc::PaintFlags fill;
    fill.setAntiAlias(true);
    fill.setColor(pill_fill_color_);
    canvas->DrawRoundRect(pill, kPillRadius, fill);
    cc::PaintFlags stroke;
    stroke.setAntiAlias(true);
    stroke.setStyle(cc::PaintFlags::kStroke_Style);
    stroke.setStrokeWidth(1.f);
    stroke.setColor(pill_border_color_);
    gfx::RectF stroke_rect = pill;
    stroke_rect.Inset(0.5f);
    canvas->DrawRoundRect(stroke_rect, kPillRadius - 0.5f, stroke);
  }

  // Astérisque animé, à l'accent.
  const gfx::PointF logo_center(icon.x() + kPillLeftPadding + kLogoIconSize / 2.f,
                                icon.y() + icon.height() / 2.f);
  const float scale = 1.f + kHoverScale * hover - kPressScale * press;
  cc::PaintFlags logo_flags;
  logo_flags.setAntiAlias(true);
  logo_flags.setStyle(cc::PaintFlags::kFill_Style);
  logo_flags.setColor(logo_color_);
  {
    gfx::ScopedCanvas scoped(canvas);
    canvas->sk_canvas()->translate(logo_center.x(), logo_center.y());
    canvas->sk_canvas()->rotate(kHoverRotationDegrees * hover);
    canvas->sk_canvas()->scale(scale, scale);
    canvas->DrawPath(BlueliumAsteriskPath(kLogoIconSize), logo_flags);
  }

  // Chevron : descend d'un cran au survol, se retourne menu ouvert.
  {
    const float cx = icon.x() + kPillLeftPadding + kLogoIconSize + kChevronGap +
                     kChevronHalfWidth;
    const float cy = icon.y() + icon.height() / 2.f + kChevronHoverDrop * hover;
    gfx::ScopedCanvas scoped(canvas);
    canvas->sk_canvas()->translate(cx, cy);
    canvas->sk_canvas()->rotate(180.f * press);
    SkPathBuilder chevron;
    chevron.moveTo(-kChevronHalfWidth, -1.75f);
    chevron.lineTo(0.f, 1.75f);
    chevron.lineTo(kChevronHalfWidth, -1.75f);
    cc::PaintFlags chevron_flags;
    chevron_flags.setAntiAlias(true);
    chevron_flags.setStyle(cc::PaintFlags::kStroke_Style);
    chevron_flags.setStrokeWidth(1.75f);
    chevron_flags.setStrokeCap(cc::PaintFlags::kRound_Cap);
    chevron_flags.setStrokeJoin(cc::PaintFlags::kRound_Join);
    chevron_flags.setColor(logo_color_);
    canvas->DrawPath(chevron.detach(), chevron_flags);
  }

  // Pastille de mise à jour, fixe, en haut à droite du logo.
  if (badge_color_.has_value()) {
    const gfx::PointF badge(logo_center.x() + kLogoIconSize / 2.f - 1.f,
                            logo_center.y() - kLogoIconSize / 2.f + 1.f);
    cc::PaintFlags ring_flags;
    ring_flags.setAntiAlias(true);
    ring_flags.setColor(ring_color_);
    canvas->DrawCircle(badge, 4.0f, ring_flags);
    cc::PaintFlags dot_flags;
    dot_flags.setAntiAlias(true);
    dot_flags.setColor(*badge_color_);
    canvas->DrawCircle(badge, 3.0f, dot_flags);
  }
}

void BrowserLogoMenuButton::UpdateAccessibleAndTooltip() {
  if (type_and_severity_.severity == AppMenuIconController::Severity::kNone) {
    GetViewAccessibility().SetName(u"Menu Bluelium");
    SetTooltipText(u"Menu Bluelium");
  } else {
    GetViewAccessibility().SetName(
        AppMenuIconController::GetIconAccessibleName(type_and_severity_.type));
    SetTooltipText(AppMenuIconController::GetIconTooltip(
        type_and_severity_.type, type_and_severity_.severity));
  }
}

BEGIN_METADATA(BrowserLogoMenuButton)
END_METADATA
''',
}

FRAME_BUILD = 'chrome/browser/ui/views/frame/BUILD.gn'
TOOLBAR_BUILD = 'chrome/browser/ui/views/toolbar/BUILD.gn'
TSRV_H = 'chrome/browser/ui/views/frame/tab_strip_region_view.h'
HTSRV_H = 'chrome/browser/ui/views/frame/horizontal_tab_strip_region_view.h'
HTSRV_CC = 'chrome/browser/ui/views/frame/horizontal_tab_strip_region_view.cc'
VTSRV_H = 'chrome/browser/ui/views/frame/vertical_tab_strip_region_view.h'
VTSRV_CC = 'chrome/browser/ui/views/frame/vertical_tab_strip_region_view.cc'
BV_H = 'chrome/browser/ui/views/frame/browser_view.h'
BV_CC = 'chrome/browser/ui/views/frame/browser_view.cc'
AMB_H = 'chrome/browser/ui/views/frame/app_menu_button.h'
AMB_CC = 'chrome/browser/ui/views/frame/app_menu_button.cc'
AM_H = 'chrome/browser/ui/views/toolbar/app_menu.h'
AM_CC = 'chrome/browser/ui/views/toolbar/app_menu.cc'
AAM_H = 'chrome/browser/ui/views/app_menu/action_app_menu.h'
AAM_CC = 'chrome/browser/ui/views/app_menu/action_app_menu.cc'
BAMB_H = 'chrome/browser/ui/views/toolbar/browser_app_menu_button.h'
BAMB_CC = 'chrome/browser/ui/views/toolbar/browser_app_menu_button.cc'
TV_H = 'chrome/browser/ui/views/toolbar/toolbar_view.h'
PREFS = 'chrome/browser/ui/browser_ui_prefs.cc'

EDITS = [
    # 1. Bouton « ⋯ » stylisé : trois points ronds horizontaux.
    ('chrome/app/vector_icons/BUILD.gn',
     '    "more_vert.icon",\n',
     '    "more_vert.icon",\n'
     '    "bluelium_more.icon",\n'),
    (BAMB_CC,
     '      : features::IsRoundedIconsEnabled() ? kMoreVertIcon\n'
     '                                          : kBrowserToolsChromeRefreshOldIcon;\n',
     '      : features::IsRoundedIconsEnabled() ? kMoreVertIcon\n'
     '                                          : kBrowserToolsChromeRefreshOldIcon;\n'
     '  // Bluelium : trois points ronds horizontaux, en tactile comme à la souris.\n'
     '  const gfx::VectorIcon& bluelium_icon = kBlueliumMoreIcon;\n'),
    (BAMB_CC,
     '        ui::ImageModel::FromVectorIcon(icon, icon_color, icon_size);\n',
     '        ui::ImageModel::FromVectorIcon(bluelium_icon, icon_color, icon_size);\n'),

    # 2. AppMenu et ActionAppMenu : accepter une position d'ancrage (kTopLeft
    #    sous le logo à gauche, kTopRight par défaut).
    (AM_H,
     '#include "ui/views/controls/menu/menu_delegate.h"\n',
     '#include "ui/views/controls/menu/menu_delegate.h"\n'
     '#include "ui/views/controls/menu/menu_types.h"\n'),
    (AM_H,
     '  void RunMenu(\n'
     '      views::MenuButtonController* host,\n'
     '      ui::mojom::MenuSourceType source_type = ui::mojom::MenuSourceType::kNone);\n'
     '\n'
     '  // Shows the menu with an anchor in the parent widget given its bounds.\n'
     '  void RunMenu(\n'
     '      views::Widget* parent,\n'
     '      const gfx::Rect& anchor_screen_bounds,\n'
     '      ui::mojom::MenuSourceType source_type = ui::mojom::MenuSourceType::kNone);\n',
     '  // Bluelium : position d\'ancrage configurable (kTopLeft sous le logo).\n'
     '  void RunMenu(\n'
     '      views::MenuButtonController* host,\n'
     '      ui::mojom::MenuSourceType source_type = ui::mojom::MenuSourceType::kNone,\n'
     '      views::MenuAnchorPosition anchor_position =\n'
     '          views::MenuAnchorPosition::kTopRight);\n'
     '\n'
     '  // Shows the menu with an anchor in the parent widget given its bounds.\n'
     '  void RunMenu(\n'
     '      views::Widget* parent,\n'
     '      const gfx::Rect& anchor_screen_bounds,\n'
     '      ui::mojom::MenuSourceType source_type = ui::mojom::MenuSourceType::kNone,\n'
     '      views::MenuAnchorPosition anchor_position =\n'
     '          views::MenuAnchorPosition::kTopRight);\n'),
    (AM_CC,
     'void AppMenu::RunMenu(views::MenuButtonController* host,\n'
     '                      ui::mojom::MenuSourceType source_type) {\n'
     '  base::RecordAction(UserMetricsAction("ShowAppMenu"));\n'
     '  UMA_HISTOGRAM_ENUMERATION("WrenchMenu.MenuAction", MENU_ACTION_MENU_OPENED,\n'
     '                            LIMIT_MENU_ACTION);\n'
     '\n'
     '  menu_runner_->RunMenuAt(host->button()->GetWidget(), host,\n'
     '                          host->button()->GetAnchorBoundsInScreen(),\n'
     '                          views::MenuAnchorPosition::kTopRight, source_type,\n'
     '                          /*native_view_for_gestures=*/gfx::NativeView(),\n'
     '                          /*corners=*/std::nullopt,\n'
     '                          "Chrome.AppMenu.MenuHostInitToNextFramePresented");\n'
     '}\n'
     '\n'
     'void AppMenu::RunMenu(views::Widget* parent,\n'
     '                      const gfx::Rect& anchor_screen_bounds,\n'
     '                      ui::mojom::MenuSourceType source_type) {\n'
     '  base::RecordAction(UserMetricsAction("ShowAppMenu"));\n'
     '  UMA_HISTOGRAM_ENUMERATION("WrenchMenu.MenuAction", MENU_ACTION_MENU_OPENED,\n'
     '                            LIMIT_MENU_ACTION);\n'
     '\n'
     '  menu_runner_->RunMenuAt(parent, nullptr, anchor_screen_bounds,\n'
     '                          views::MenuAnchorPosition::kTopRight, source_type,\n'
     '                          /*native_view_for_gestures=*/gfx::NativeView(),\n'
     '                          /*corners=*/std::nullopt,\n'
     '                          "Chrome.AppMenu.MenuHostInitToNextFramePresented");\n'
     '}\n',
     'void AppMenu::RunMenu(views::MenuButtonController* host,\n'
     '                      ui::mojom::MenuSourceType source_type,\n'
     '                      views::MenuAnchorPosition anchor_position) {\n'
     '  base::RecordAction(UserMetricsAction("ShowAppMenu"));\n'
     '  UMA_HISTOGRAM_ENUMERATION("WrenchMenu.MenuAction", MENU_ACTION_MENU_OPENED,\n'
     '                            LIMIT_MENU_ACTION);\n'
     '\n'
     '  menu_runner_->RunMenuAt(host->button()->GetWidget(), host,\n'
     '                          host->button()->GetAnchorBoundsInScreen(),\n'
     '                          anchor_position, source_type,\n'
     '                          /*native_view_for_gestures=*/gfx::NativeView(),\n'
     '                          /*corners=*/std::nullopt,\n'
     '                          "Chrome.AppMenu.MenuHostInitToNextFramePresented");\n'
     '}\n'
     '\n'
     'void AppMenu::RunMenu(views::Widget* parent,\n'
     '                      const gfx::Rect& anchor_screen_bounds,\n'
     '                      ui::mojom::MenuSourceType source_type,\n'
     '                      views::MenuAnchorPosition anchor_position) {\n'
     '  base::RecordAction(UserMetricsAction("ShowAppMenu"));\n'
     '  UMA_HISTOGRAM_ENUMERATION("WrenchMenu.MenuAction", MENU_ACTION_MENU_OPENED,\n'
     '                            LIMIT_MENU_ACTION);\n'
     '\n'
     '  menu_runner_->RunMenuAt(parent, nullptr, anchor_screen_bounds,\n'
     '                          anchor_position, source_type,\n'
     '                          /*native_view_for_gestures=*/gfx::NativeView(),\n'
     '                          /*corners=*/std::nullopt,\n'
     '                          "Chrome.AppMenu.MenuHostInitToNextFramePresented");\n'
     '}\n'),

    (AAM_H,
     '#include "ui/views/controls/menu/menu_delegate.h"\n',
     '#include "ui/views/controls/menu/menu_delegate.h"\n'
     '#include "ui/views/controls/menu/menu_types.h"\n'),
    (AAM_H,
     '  void RunMenu(views::MenuButtonController* host, int run_types);\n'
     '  void RunMenu(\n'
     '      views::Widget* parent,\n'
     '      const gfx::Rect& anchor_screen_bounds,\n'
     '      int run_types,\n'
     '      ui::mojom::MenuSourceType source_type = ui::mojom::MenuSourceType::kNone);\n',
     '  // Bluelium : position d\'ancrage configurable (kTopLeft sous le logo).\n'
     '  void RunMenu(views::MenuButtonController* host,\n'
     '               int run_types,\n'
     '               views::MenuAnchorPosition anchor_position =\n'
     '                   views::MenuAnchorPosition::kTopRight);\n'
     '  void RunMenu(\n'
     '      views::Widget* parent,\n'
     '      const gfx::Rect& anchor_screen_bounds,\n'
     '      int run_types,\n'
     '      ui::mojom::MenuSourceType source_type = ui::mojom::MenuSourceType::kNone,\n'
     '      views::MenuAnchorPosition anchor_position =\n'
     '          views::MenuAnchorPosition::kTopRight);\n'),
    (AAM_H,
     '  void RunMenu(views::Widget* parent,\n'
     '               views::MenuButtonController* host,\n'
     '               const gfx::Rect& anchor_screen_bounds,\n'
     '               int run_types,\n'
     '               ui::mojom::MenuSourceType source_type);\n',
     '  void RunMenu(views::Widget* parent,\n'
     '               views::MenuButtonController* host,\n'
     '               const gfx::Rect& anchor_screen_bounds,\n'
     '               int run_types,\n'
     '               ui::mojom::MenuSourceType source_type,\n'
     '               views::MenuAnchorPosition anchor_position);\n'),
    (AAM_CC,
     'void ActionAppMenu::RunMenu(views::MenuButtonController* host, int run_types) {\n'
     '  RunMenu(host->button()->GetWidget(), host,\n'
     '          host->button()->GetAnchorBoundsInScreen(), run_types,\n'
     '          ui::mojom::MenuSourceType::kNone);\n'
     '}\n'
     '\n'
     'void ActionAppMenu::RunMenu(views::Widget* parent,\n'
     '                            const gfx::Rect& anchor_screen_bounds,\n'
     '                            int run_types,\n'
     '                            ui::mojom::MenuSourceType source_type) {\n'
     '  RunMenu(parent, nullptr, anchor_screen_bounds, run_types, source_type);\n'
     '}\n'
     '\n'
     'void ActionAppMenu::RunMenu(views::Widget* parent,\n'
     '                            views::MenuButtonController* host,\n'
     '                            const gfx::Rect& anchor_screen_bounds,\n'
     '                            int run_types,\n'
     '                            ui::mojom::MenuSourceType source_type) {\n',
     'void ActionAppMenu::RunMenu(views::MenuButtonController* host,\n'
     '                            int run_types,\n'
     '                            views::MenuAnchorPosition anchor_position) {\n'
     '  RunMenu(host->button()->GetWidget(), host,\n'
     '          host->button()->GetAnchorBoundsInScreen(), run_types,\n'
     '          ui::mojom::MenuSourceType::kNone, anchor_position);\n'
     '}\n'
     '\n'
     'void ActionAppMenu::RunMenu(views::Widget* parent,\n'
     '                            const gfx::Rect& anchor_screen_bounds,\n'
     '                            int run_types,\n'
     '                            ui::mojom::MenuSourceType source_type,\n'
     '                            views::MenuAnchorPosition anchor_position) {\n'
     '  RunMenu(parent, nullptr, anchor_screen_bounds, run_types, source_type,\n'
     '          anchor_position);\n'
     '}\n'
     '\n'
     'void ActionAppMenu::RunMenu(views::Widget* parent,\n'
     '                            views::MenuButtonController* host,\n'
     '                            const gfx::Rect& anchor_screen_bounds,\n'
     '                            int run_types,\n'
     '                            ui::mojom::MenuSourceType source_type,\n'
     '                            views::MenuAnchorPosition anchor_position) {\n'),
    (AAM_CC,
     '  menu_runner_->RunMenuAt(parent, host, anchor_screen_bounds,\n'
     '                          views::MenuAnchorPosition::kTopRight, source_type,\n',
     '  menu_runner_->RunMenuAt(parent, host, anchor_screen_bounds,\n'
     '                          anchor_position, source_type,\n'),

    # 3. AppMenuButton : permettre l'ouverture du menu ancrée sur un autre
    #    MenuButtonController (le bouton logo), avec repli sur le widget si
    #    aucun bouton n'est dessiné (plein écran / mode dynamique 1 onglet).
    (AMB_H,
     '#include "ui/base/metadata/metadata_header_macros.h"\n',
     '#include "ui/base/metadata/metadata_header_macros.h"\n'
     '#include "ui/views/controls/menu/menu_types.h"\n'),
    (AMB_H,
     '  void RunMenu(std::unique_ptr<AppMenuModel> menu_model,\n'
     '               BrowserWindowInterface* browser,\n'
     '               int run_flags);\n'
     '  // Not using an AppMenuModel because the new Block Style menu hierarchy\n'
     '  // is managed by the Actions framework.\n'
     '  void RunActionMenu(BrowserWindowInterface* browser_window_interface,\n'
     '                     int run_flags);\n',
     '  // Bluelium : ancre facultative (logo) et position du menu.\n'
     '  void RunMenu(std::unique_ptr<AppMenuModel> menu_model,\n'
     '               BrowserWindowInterface* browser,\n'
     '               int run_flags,\n'
     '               views::MenuButtonController* anchor_host = nullptr,\n'
     '               views::MenuAnchorPosition anchor_position =\n'
     '                   views::MenuAnchorPosition::kTopRight);\n'
     '  // Not using an AppMenuModel because the new Block Style menu hierarchy\n'
     '  // is managed by the Actions framework.\n'
     '  void RunActionMenu(BrowserWindowInterface* browser_window_interface,\n'
     '                     int run_flags,\n'
     '                     views::MenuButtonController* anchor_host = nullptr,\n'
     '                     views::MenuAnchorPosition anchor_position =\n'
     '                         views::MenuAnchorPosition::kTopRight);\n'),
    (AMB_CC,
     '#include "ui/views/view_class_properties.h"\n',
     '#include "ui/views/view_class_properties.h"\n'
     '#include "ui/views/widget/widget.h"\n'),
    (AMB_CC,
     'void AppMenuButton::RunMenu(std::unique_ptr<AppMenuModel> menu_model,\n'
     '                            BrowserWindowInterface* browser,\n'
     '                            int run_flags) {\n'
     '  // |menu_| must be reset before |menu_model_| is destroyed, as per the comment\n'
     '  // in the class declaration.\n'
     '  menu_.reset();\n'
     '  menu_model_ = std::move(menu_model);\n'
     '  highlighter_.MaybeHighlight(browser, this, menu_model_.get());\n'
     '  menu_model_->Init();\n'
     '\n'
     '  menu_ = std::make_unique<AppMenu>(\n'
     '      browser, menu_model_.get(), run_flags,\n'
     '      base::BindRepeating(&AppMenuButton::OnMenuClosed,\n'
     '                          weak_ptr_factory_.GetWeakPtr()));\n'
     '  menu_->RunMenu(menu_button_controller_);\n'
     '\n'
     '  observer_list_.Notify(&AppMenuButtonObserver::AppMenuShown);\n'
     '}\n'
     '\n'
     'void AppMenuButton::RunActionMenu(\n'
     '    BrowserWindowInterface* browser_window_interface,\n'
     '    int run_flags) {\n'
     '  action_menu_.reset();\n'
     '\n'
     '  action_menu_ = std::make_unique<ActionAppMenu>(\n'
     '      browser_window_interface,\n'
     '      base::BindRepeating(&AppMenuButton::OnMenuClosed,\n'
     '                          weak_ptr_factory_.GetWeakPtr()));\n'
     '  action_menu_->RunMenu(menu_button_controller_, run_flags);\n'
     '\n'
     '  observer_list_.Notify(&AppMenuButtonObserver::AppMenuShown);\n'
     '}\n',
     'void AppMenuButton::RunMenu(std::unique_ptr<AppMenuModel> menu_model,\n'
     '                            BrowserWindowInterface* browser,\n'
     '                            int run_flags,\n'
     '                            views::MenuButtonController* anchor_host,\n'
     '                            views::MenuAnchorPosition anchor_position) {\n'
     '  // |menu_| must be reset before |menu_model_| is destroyed, as per the comment\n'
     '  // in the class declaration.\n'
     '  menu_.reset();\n'
     '  menu_model_ = std::move(menu_model);\n'
     '  highlighter_.MaybeHighlight(browser, this, menu_model_.get());\n'
     '  menu_model_->Init();\n'
     '\n'
     '  menu_ = std::make_unique<AppMenu>(\n'
     '      browser, menu_model_.get(), run_flags,\n'
     '      base::BindRepeating(&AppMenuButton::OnMenuClosed,\n'
     '                          weak_ptr_factory_.GetWeakPtr()));\n'
     '  // Bluelium : ancrer sur le logo si fourni, sinon sur le bouton ou la fenêtre.\n'
     '  views::MenuButtonController* host =\n'
     '      anchor_host ? anchor_host : menu_button_controller_.get();\n'
     '  if (host && host->button() && host->button()->IsDrawn()) {\n'
     '    menu_->RunMenu(host, ui::mojom::MenuSourceType::kNone, anchor_position);\n'
     '  } else if (views::Widget* widget = GetWidget()) {\n'
     '    const gfx::Rect anchor_bounds(\n'
     '        widget->GetClientAreaBoundsInScreen().origin(), gfx::Size());\n'
     '    menu_->RunMenu(widget, anchor_bounds, ui::mojom::MenuSourceType::kNone,\n'
     '                   views::MenuAnchorPosition::kTopLeft);\n'
     '  }\n'
     '\n'
     '  observer_list_.Notify(&AppMenuButtonObserver::AppMenuShown);\n'
     '}\n'
     '\n'
     'void AppMenuButton::RunActionMenu(\n'
     '    BrowserWindowInterface* browser_window_interface,\n'
     '    int run_flags,\n'
     '    views::MenuButtonController* anchor_host,\n'
     '    views::MenuAnchorPosition anchor_position) {\n'
     '  action_menu_.reset();\n'
     '\n'
     '  action_menu_ = std::make_unique<ActionAppMenu>(\n'
     '      browser_window_interface,\n'
     '      base::BindRepeating(&AppMenuButton::OnMenuClosed,\n'
     '                          weak_ptr_factory_.GetWeakPtr()));\n'
     '  views::MenuButtonController* host =\n'
     '      anchor_host ? anchor_host : menu_button_controller_.get();\n'
     '  if (host && host->button() && host->button()->IsDrawn()) {\n'
     '    action_menu_->RunMenu(host, run_flags, anchor_position);\n'
     '  } else if (views::Widget* widget = GetWidget()) {\n'
     '    const gfx::Rect anchor_bounds(\n'
     '        widget->GetClientAreaBoundsInScreen().origin(), gfx::Size());\n'
     '    action_menu_->RunMenu(widget, anchor_bounds, run_flags,\n'
     '                          ui::mojom::MenuSourceType::kNone,\n'
     '                          views::MenuAnchorPosition::kTopLeft);\n'
     '  }\n'
     '\n'
     '  observer_list_.Notify(&AppMenuButtonObserver::AppMenuShown);\n'
     '}\n'),

    # 4. TabStripRegionView : exposer le bouton logo aux régions d'onglets.
    (TSRV_H,
     'class TabDragContext;\n',
     'class BrowserLogoMenuButton;\n'
     'class TabDragContext;\n'),
    (TSRV_H,
     '  // -- Locks --\n'
     '  virtual std::unique_ptr<ExpandOnHoverLock> GetExpandOnHoverLock(\n'
     '      ExpandOnHoverLockType lock_type) = 0;\n',
     '  // -- Locks --\n'
     '  virtual std::unique_ptr<ExpandOnHoverLock> GetExpandOnHoverLock(\n'
     '      ExpandOnHoverLockType lock_type) = 0;\n'
     '\n'
     '  // Bluelium : bouton logo ouvrant le menu d\'application, si présent.\n'
     '  virtual BrowserLogoMenuButton* GetLogoMenuButton() { return nullptr; }\n'),

    # 5. HorizontalTabStripRegionView (Old et New) : ajouter le logo en premier
    #    élément à gauche (après les feux tricolores sur macOS).
    (HTSRV_H,
     'class NewTabButton;\n',
     'class BrowserLogoMenuButton;\n'
     'class NewTabButton;\n'),
    (HTSRV_H,
     '  void OnGlassFrameEligibilityChanged(bool is_eligible) override;\n'
     '\n'
     '  bool HasLeadingButtons() const;\n',
     '  void OnGlassFrameEligibilityChanged(bool is_eligible) override;\n'
     '\n'
     '  bool HasLeadingButtons() const;\n'
     '  BrowserLogoMenuButton* GetLogoMenuButton() override {\n'
     '    return logo_menu_button_;\n'
     '  }\n'),
    (HTSRV_H,
     '  raw_ptr<TabStripScrollContainer> tab_strip_scroll_container_ = nullptr;\n'
     '  raw_ptr<TabStripComboButton> combo_button_ = nullptr;\n'
     '  raw_ptr<views::Button> new_tab_button_ = nullptr;\n',
     '  raw_ptr<TabStripScrollContainer> tab_strip_scroll_container_ = nullptr;\n'
     '  raw_ptr<TabStripComboButton> combo_button_ = nullptr;\n'
     '  raw_ptr<BrowserLogoMenuButton> logo_menu_button_ = nullptr;\n'
     '  raw_ptr<views::Button> new_tab_button_ = nullptr;\n'),
    (HTSRV_H,
     '  bool HasLeadingButtons() const;\n'
     '  TabStripComboButton* combo_button() { return combo_button_; }\n',
     '  bool HasLeadingButtons() const;\n'
     '  BrowserLogoMenuButton* GetLogoMenuButton() override {\n'
     '    return logo_menu_button_;\n'
     '  }\n'
     '  TabStripComboButton* combo_button() { return combo_button_; }\n'),
    (HTSRV_H,
     '  raw_ptr<views::View> reserved_grab_handle_space_ = nullptr;\n'
     '  raw_ptr<TabStripComboButton> combo_button_ = nullptr;\n'
     '  raw_ptr<views::Button> new_tab_button_ = nullptr;\n',
     '  raw_ptr<views::View> reserved_grab_handle_space_ = nullptr;\n'
     '  raw_ptr<TabStripComboButton> combo_button_ = nullptr;\n'
     '  raw_ptr<BrowserLogoMenuButton> logo_menu_button_ = nullptr;\n'
     '  raw_ptr<views::Button> new_tab_button_ = nullptr;\n'),
    (HTSRV_CC,
     '#include "chrome/browser/ui/views/frame/browser_view.h"\n',
     '#include "chrome/browser/ui/views/frame/browser_logo_menu_button.h"\n'
     '#include "chrome/browser/ui/views/frame/browser_view.h"\n'),
    # HorizontalTabStripRegionViewOld : création en position 0 avant tab_strip_.
    (HTSRV_CC,
     '  tab_strip_ = AddChildView(CreateTabStrip(this, browser_view));\n',
     '  // Bluelium : logo cliquable ouvrant le menu, à gauche des onglets.\n'
     '  if (browser &&\n'
     '      browser->GetType() == BrowserWindowInterface::Type::TYPE_NORMAL) {\n'
     '    logo_menu_button_ =\n'
     '        AddChildView(std::make_unique<BrowserLogoMenuButton>(browser_view));\n'
     '    logo_menu_button_->SetProperty(\n'
     '        views::kMarginsKey,\n'
     '        gfx::Insets::TLBR(0, GetLayoutConstant(LayoutConstant::kTabStripPadding) + 1,\n'
     '                          0, 2));\n'
     '    logo_menu_button_->SetSeparatorSide(\n'
     '        BrowserLogoMenuButton::SeparatorSide::kTrailing);\n'
     '  }\n'
     '\n'
     '  tab_strip_ = AddChildView(CreateTabStrip(this, browser_view));\n'),
    (HTSRV_CC,
     'HorizontalTabStripRegionViewOld::~HorizontalTabStripRegionViewOld() {\n'
     '  // These objects have pointers to TabStripController, which is also destoroyed\n'
     '  // by this class. Remove child views that hold raw_ptr to TabStripController.\n'
     '  if (tab_strip_action_container_) {\n'
     '    RemoveChildViewT(std::exchange(tab_strip_action_container_, nullptr));\n'
     '  }\n'
     '  if (combo_button_) {\n'
     '    RemoveChildViewT(std::exchange(combo_button_, nullptr));\n'
     '  }\n'
     '  if (new_tab_button_) {\n'
     '    RemoveChildViewT(std::exchange(new_tab_button_, nullptr));\n'
     '  }\n'
     '}\n',
     'HorizontalTabStripRegionViewOld::~HorizontalTabStripRegionViewOld() {\n'
     '  // These objects have pointers to TabStripController, which is also destoroyed\n'
     '  // by this class. Remove child views that hold raw_ptr to TabStripController.\n'
     '  if (tab_strip_action_container_) {\n'
     '    RemoveChildViewT(std::exchange(tab_strip_action_container_, nullptr));\n'
     '  }\n'
     '  if (combo_button_) {\n'
     '    RemoveChildViewT(std::exchange(combo_button_, nullptr));\n'
     '  }\n'
     '  if (logo_menu_button_) {\n'
     '    RemoveChildViewT(std::exchange(logo_menu_button_, nullptr));\n'
     '  }\n'
     '  if (new_tab_button_) {\n'
     '    RemoveChildViewT(std::exchange(new_tab_button_, nullptr));\n'
     '  }\n'
     '}\n'),
    (HTSRV_CC,
     'HorizontalTabStripRegionViewNew::~HorizontalTabStripRegionViewNew() {\n'
     '  if (tab_strip_action_container_) {\n'
     '    RemoveChildViewT(std::exchange(tab_strip_action_container_, nullptr));\n'
     '  }\n'
     '  if (combo_button_) {\n'
     '    RemoveChildViewT(std::exchange(combo_button_, nullptr));\n'
     '  }\n'
     '  if (new_tab_button_) {\n'
     '    RemoveChildViewT(std::exchange(new_tab_button_, nullptr));\n'
     '  }\n'
     '}\n',
     'HorizontalTabStripRegionViewNew::~HorizontalTabStripRegionViewNew() {\n'
     '  if (tab_strip_action_container_) {\n'
     '    RemoveChildViewT(std::exchange(tab_strip_action_container_, nullptr));\n'
     '  }\n'
     '  if (combo_button_) {\n'
     '    RemoveChildViewT(std::exchange(combo_button_, nullptr));\n'
     '  }\n'
     '  if (logo_menu_button_) {\n'
     '    RemoveChildViewT(std::exchange(logo_menu_button_, nullptr));\n'
     '  }\n'
     '  if (new_tab_button_) {\n'
     '    RemoveChildViewT(std::exchange(new_tab_button_, nullptr));\n'
     '  }\n'
     '}\n'),
    (HTSRV_CC,
     'bool HorizontalTabStripRegionViewOld::IsPositionInWindowCaption(\n'
     '    const gfx::Point& point) {\n'
     '  if (new_tab_button_ && IsHitInView(new_tab_button_, point)) {\n'
     '    return false;\n'
     '  }\n',
     'bool HorizontalTabStripRegionViewOld::IsPositionInWindowCaption(\n'
     '    const gfx::Point& point) {\n'
     '  if (logo_menu_button_ && logo_menu_button_->GetVisible() &&\n'
     '      IsHitInView(logo_menu_button_, point)) {\n'
     '    return false;\n'
     '  }\n'
     '\n'
     '  if (new_tab_button_ && IsHitInView(new_tab_button_, point)) {\n'
     '    return false;\n'
     '  }\n'),
    (HTSRV_CC,
     '  if (tab_strip_) {\n'
     '    children.emplace_back(tab_strip_.get());\n'
     '  }\n'
     '\n'
     '  if (new_tab_button_) {\n',
     '  if (tab_strip_) {\n'
     '    children.emplace_back(tab_strip_.get());\n'
     '  }\n'
     '\n'
     '  if (logo_menu_button_) {\n'
     '    children.emplace_back(logo_menu_button_.get());\n'
     '  }\n'
     '\n'
     '  if (new_tab_button_) {\n'),
    (HTSRV_CC,
     'bool HorizontalTabStripRegionViewOld::HasLeadingButtons() const {\n'
     '  if (combo_button_ && combo_button_->GetVisible() &&\n',
     'bool HorizontalTabStripRegionViewOld::HasLeadingButtons() const {\n'
     '  if (logo_menu_button_ && logo_menu_button_->GetVisible()) {\n'
     '    return true;\n'
     '  }\n'
     '  if (combo_button_ && combo_button_->GetVisible() &&\n'),
    (HTSRV_CC,
     '  if (new_tab_button_) {\n'
     '    UpdateBorderInsetsIfNeeded(new_tab_button_, border_insets);\n'
     '  }\n',
     '  if (logo_menu_button_) {\n'
     '    UpdateBorderInsetsIfNeeded(logo_menu_button_, border_insets);\n'
     '  }\n'
     '  if (new_tab_button_) {\n'
     '    UpdateBorderInsetsIfNeeded(new_tab_button_, border_insets);\n'
     '  }\n'),
    # HorizontalTabStripRegionViewNew : même logique (si kTabStripUnification).
    (HTSRV_CC,
     '  if (browser &&\n'
     '      (browser->GetType() == BrowserWindowInterface::Type::TYPE_NORMAL)) {\n'
     '    combo_button_ = AddChildView(std::make_unique<TabStripComboButton>(\n',
     '  if (browser &&\n'
     '      (browser->GetType() == BrowserWindowInterface::Type::TYPE_NORMAL)) {\n'
     '    // Bluelium : logo cliquable ouvrant le menu, à gauche des onglets.\n'
     '    logo_menu_button_ =\n'
     '        AddChildView(std::make_unique<BrowserLogoMenuButton>(browser_view));\n'
     '    logo_menu_button_->SetProperty(\n'
     '        views::kMarginsKey,\n'
     '        gfx::Insets::TLBR(0, GetLayoutConstant(LayoutConstant::kTabStripPadding) + 1,\n'
     '                          0, 2));\n'
     '    logo_menu_button_->SetSeparatorSide(\n'
     '        BrowserLogoMenuButton::SeparatorSide::kTrailing);\n'
     '\n'
     '    combo_button_ = AddChildView(std::make_unique<TabStripComboButton>(\n'),
    (HTSRV_CC,
     'bool HorizontalTabStripRegionViewNew::IsPositionInWindowCaption(\n'
     '    const gfx::Point& point) {\n'
     '  if (new_tab_button_ && IsHitInView(new_tab_button_, point)) {\n'
     '    return false;\n'
     '  }\n',
     'bool HorizontalTabStripRegionViewNew::IsPositionInWindowCaption(\n'
     '    const gfx::Point& point) {\n'
     '  if (logo_menu_button_ && logo_menu_button_->GetVisible() &&\n'
     '      IsHitInView(logo_menu_button_, point)) {\n'
     '    return false;\n'
     '  }\n'
     '  if (new_tab_button_ && IsHitInView(new_tab_button_, point)) {\n'
     '    return false;\n'
     '  }\n'),
    (HTSRV_CC,
     '  if (GetDragContext()) {\n'
     '    children.emplace_back(GetDragContext());\n'
     '  }\n'
     '  if (new_tab_button_) {\n',
     '  if (GetDragContext()) {\n'
     '    children.emplace_back(GetDragContext());\n'
     '  }\n'
     '  if (logo_menu_button_) {\n'
     '    children.emplace_back(logo_menu_button_.get());\n'
     '  }\n'
     '  if (new_tab_button_) {\n'),
    (HTSRV_CC,
     'bool HorizontalTabStripRegionViewNew::HasLeadingButtons() const {\n'
     '  if (combo_button_ && combo_button_->GetVisible() &&\n',
     'bool HorizontalTabStripRegionViewNew::HasLeadingButtons() const {\n'
     '  if (logo_menu_button_ && logo_menu_button_->GetVisible()) {\n'
     '    return true;\n'
     '  }\n'
     '  if (combo_button_ && combo_button_->GetVisible() &&\n'),
    (HTSRV_CC,
     '  const size_t index = combo_button_ ? 1 : 0;\n',
     '  const size_t index =\n'
     '      (logo_menu_button_ ? 1 : 0) + (combo_button_ ? 1 : 0);\n'),
    (HTSRV_CC,
     '  if (combo_button_) {\n'
     '    UpdateBorderInsetsIfNeeded(combo_button_, border_insets);\n'
     '  }\n'
     '}\n',
     '  if (logo_menu_button_) {\n'
     '    UpdateBorderInsetsIfNeeded(logo_menu_button_, border_insets);\n'
     '  }\n'
     '  if (combo_button_) {\n'
     '    UpdateBorderInsetsIfNeeded(combo_button_, border_insets);\n'
     '  }\n'
     '}\n'),

    # 6. VerticalTabStripRegionView : ajouter le logo tout en haut de la bande
    #    verticale (index 0 de content_area_view_, au-dessus des onglets).
    (VTSRV_H,
     'class BrowserView;\n',
     'class BrowserLogoMenuButton;\n'
     'class BrowserView;\n'),
    (VTSRV_H,
     '  bool IsPositionInWindowCaption(const gfx::Point& point) override;\n',
     '  bool IsPositionInWindowCaption(const gfx::Point& point) override;\n'
     '  BrowserLogoMenuButton* GetLogoMenuButton() override {\n'
     '    return logo_menu_button_;\n'
     '  }\n'),
    (VTSRV_H,
     '  raw_ptr<VerticalTabStripBottomContainer> bottom_button_container_ = nullptr;\n',
     '  raw_ptr<BrowserLogoMenuButton> logo_menu_button_ = nullptr;\n'
     '  raw_ptr<VerticalTabStripBottomContainer> bottom_button_container_ = nullptr;\n'),
    (VTSRV_CC,
     '#include "chrome/browser/ui/views/frame/browser_view.h"\n',
     '#include "chrome/browser/ui/views/frame/browser_logo_menu_button.h"\n'
     '#include "chrome/browser/ui/views/frame/browser_view.h"\n'),
    (VTSRV_CC,
     '  const int region_horizontal_padding =\n'
     '      GetLayoutConstant(LayoutConstant::kVerticalTabStripHorizontalPadding);\n'
     '\n'
     '  bottom_button_container_ = content_area_view_->AddChildView(\n',
     '  const int region_horizontal_padding =\n'
     '      GetLayoutConstant(LayoutConstant::kVerticalTabStripHorizontalPadding);\n'
     '\n'
     '  // Bluelium : logo cliquable ouvrant le menu, tout en haut des onglets verticaux.\n'
     '  if (browser_view->browser() &&\n'
     '      browser_view->browser()->GetType() ==\n'
     '          BrowserWindowInterface::Type::TYPE_NORMAL) {\n'
     '    logo_menu_button_ = content_area_view_->AddChildView(\n'
     '        std::make_unique<BrowserLogoMenuButton>(browser_view));\n'
     '    logo_menu_button_->SetProperty(\n'
     '        views::kMarginsKey,\n'
     '        gfx::Insets::TLBR(0, region_horizontal_padding,\n'
     '                          kBottomContainerGap,\n'
     '                          region_horizontal_padding));\n'
     '    // Bluelium : pleine largeur pour le séparateur sous le logo.\n'
     '    logo_menu_button_->SetSeparatorSide(\n'
     '        BrowserLogoMenuButton::SeparatorSide::kBottom);\n'
     '    logo_menu_button_->SetProperty(\n'
     '        views::kCrossAxisAlignmentKey, views::LayoutAlignment::kStretch);\n'
     '    logo_menu_button_->SetIconCentered(state_controller_->IsCollapsed());\n'
     '  }\n'
     '\n'
     '  bottom_button_container_ = content_area_view_->AddChildView(\n'),
    (VTSRV_CC,
     '  if (tab_strip_view()) {\n'
     '    tab_strip_view()->SetCollapsedState(collapsed);\n'
     '  }\n',
     '  if (logo_menu_button_) {\n'
     '    logo_menu_button_->SetIconCentered(collapsed);\n'
     '  }\n'
     '\n'
     '  if (tab_strip_view()) {\n'
     '    tab_strip_view()->SetCollapsedState(collapsed);\n'
     '  }\n'),

    # 7. BrowserView : exposer le logo actif, tous les logos (pour la pastille
    #    de mise à jour) et l'ouverture du menu depuis le logo.
    (BV_H,
     'class BrowserWindowInterface;\n',
     'class BrowserLogoMenuButton;\n'
     'class BrowserWindowInterface;\n'),
    (BV_H,
     '  // Returns either the Horizontal or Vertical TabStrip.\n'
     '  TabStripRegionView* tab_strip_view() const;\n',
     '  // Returns either the Horizontal or Vertical TabStrip.\n'
     '  TabStripRegionView* tab_strip_view() const;\n'
     '\n'
     '  // Bluelium : logo cliquable ouvrant le menu dans la bande d\'onglets.\n'
     '  BrowserLogoMenuButton* GetActiveLogoMenuButton() const;\n'
     '  std::vector<BrowserLogoMenuButton*> GetLogoMenuButtons() const;\n'
     '  void ShowAppMenuFromLogo(BrowserLogoMenuButton* logo_button, int run_types);\n'),
    (BV_CC,
     '#include "chrome/browser/ui/views/frame/browser_frame_view.h"\n',
     '#include "chrome/browser/ui/views/frame/browser_frame_view.h"\n'
     '#include "chrome/browser/ui/views/frame/browser_logo_menu_button.h"\n'),
    (BV_CC,
     'void BrowserView::ShowAppMenu() {\n'
     '  auto* control = ToolbarButtonProvider::From(browser_)->GetAppMenuControl();\n'
     '  if (!control) {\n'
     '    return;\n'
     '  }\n'
     '\n'
     '  // Keep the top-of-window views revealed as long as the app menu is visible.\n'
     '  std::unique_ptr<ImmersiveRevealedLock> revealed_lock =\n'
     '      ImmersiveModeController::From(browser())->GetRevealedLock(\n'
     '          ImmersiveModeController::ANIMATE_REVEAL_NO);\n'
     '\n'
     '  control->ShowMenu();\n'
     '}\n',
     'BrowserLogoMenuButton* BrowserView::GetActiveLogoMenuButton() const {\n'
     '  if (!ShouldDrawTabStrip()) {\n'
     '    return nullptr;\n'
     '  }\n'
     '  TabStripRegionView* region = tab_strip_view();\n'
     '  if (!region) {\n'
     '    return nullptr;\n'
     '  }\n'
     '  BrowserLogoMenuButton* button = region->GetLogoMenuButton();\n'
     '  return button && button->IsDrawn() ? button : nullptr;\n'
     '}\n'
     '\n'
     'std::vector<BrowserLogoMenuButton*> BrowserView::GetLogoMenuButtons() const {\n'
     '  std::vector<BrowserLogoMenuButton*> buttons;\n'
     '  if (horizontal_tab_strip_region_view_) {\n'
     '    if (auto* button = horizontal_tab_strip_region_view_->GetLogoMenuButton()) {\n'
     '      buttons.push_back(button);\n'
     '    }\n'
     '  }\n'
     '  if (vertical_tab_strip_region_view_) {\n'
     '    if (auto* button = vertical_tab_strip_region_view_->GetLogoMenuButton()) {\n'
     '      buttons.push_back(button);\n'
     '    }\n'
     '  }\n'
     '  return buttons;\n'
     '}\n'
     '\n'
     'void BrowserView::ShowAppMenuFromLogo(BrowserLogoMenuButton* logo_button,\n'
     '                                      int run_types) {\n'
     '  if (!toolbar_ || !toolbar_->app_menu_button()) {\n'
     '    return;\n'
     '  }\n'
     '  std::unique_ptr<ImmersiveRevealedLock> revealed_lock =\n'
     '      ImmersiveModeController::From(browser())->GetRevealedLock(\n'
     '          ImmersiveModeController::ANIMATE_REVEAL_NO);\n'
     '  toolbar_->app_menu_button()->ShowMenuFromLogo(logo_button, run_types);\n'
     '}\n'
     '\n'
     'void BrowserView::ShowAppMenu() {\n'
     '  auto* control = ToolbarButtonProvider::From(browser_)->GetAppMenuControl();\n'
     '  if (!control) {\n'
     '    return;\n'
     '  }\n'
     '\n'
     '  // Keep the top-of-window views revealed as long as the app menu is visible.\n'
     '  std::unique_ptr<ImmersiveRevealedLock> revealed_lock =\n'
     '      ImmersiveModeController::From(browser())->GetRevealedLock(\n'
     '          ImmersiveModeController::ANIMATE_REVEAL_NO);\n'
     '\n'
     '  control->ShowMenu();\n'
     '}\n'),

    # 8. ToolbarView : accesseurs browser_view() et app_menu_button().
    (TV_H,
     '  // Accessors.\n'
     '  BrowserWindowInterface* browser() const { return browser_; }\n',
     '  // Accessors.\n'
     '  BrowserWindowInterface* browser() const { return browser_; }\n'
     '  BrowserView* browser_view() const { return browser_view_; }\n'
     '  BrowserAppMenuButton* app_menu_button() const { return app_menu_button_; }\n'),

    # 9. BrowserAppMenuButton :
    #    - ShowMenuFromLogo() ancre le menu sous le logo (+ verrou expand-on-hover
    #      en onglets verticaux) ;
    #    - ShowMenu() / Alt+F / Alt+E / ShowAppMenu() activent le logo actif ;
    #    - GetAnchor() / IsDrawn() / HasFocus() / Focus() / GetFocusablePaneView()
    #      basculent vers le logo actif quand « ⋯ » est masqué ;
    #    - SetTypeAndSeverity() propage la sévérité (mise à jour, erreur) sur
    #      tous les boutons logo (bande horizontale et bande verticale).
    (BAMB_H,
     '#include "base/memory/raw_ptr.h"\n',
     '#include <memory>\n\n#include "base/memory/raw_ptr.h"\n'),
    (BAMB_H,
     'class ToolbarView;\n',
     'class BrowserLogoMenuButton;\n'
     'class ExpandOnHoverLock;\n'
     'class ToolbarView;\n'),
    (BAMB_H,
     '  // AppMenuControl:\n'
     '  void ShowMenuWithFlags(int run_types) override;\n',
     '  // Bluelium : ouvrir le menu ancré sous le bouton logo.\n'
     '  void ShowMenuFromLogo(BrowserLogoMenuButton* logo_button, int run_types);\n'
     '\n'
     '  // AppMenuControl:\n'
     '  views::BubbleAnchor GetAnchor() override;\n'
     '  bool IsDrawn() const override;\n'
     '  void ShowMenu() override;\n'
     '  void ShowMenuWithFlags(int run_types) override;\n'
     '  bool HasFocus() const override;\n'
     '  void Focus(views::AccessiblePaneView* pane) override;\n'
     '  views::View* GetFocusablePaneView() override;\n'),
    (BAMB_H,
     '  void ButtonPressed(const ui::Event& event);\n',
     '  BrowserLogoMenuButton* GetActiveLogoMenuButton() const;\n'
     '  void ShowMenuWithFlagsAndAnchor(int run_types,\n'
     '                                  views::MenuButtonController* anchor_host,\n'
     '                                  views::MenuAnchorPosition anchor_position);\n'
     '\n'
     '  void ButtonPressed(const ui::Event& event);\n'),
    (BAMB_H,
     '  user_education::FeaturePromoHandle promo_handle_;\n',
     '  user_education::FeaturePromoHandle promo_handle_;\n'
     '  std::unique_ptr<ExpandOnHoverLock> expand_on_hover_lock_;\n'),
    (BAMB_CC,
     '#include "chrome/browser/ui/views/toolbar/toolbar_view.h"\n',
     '#include "chrome/browser/ui/views/frame/browser_logo_menu_button.h"\n'
     '#include "chrome/browser/ui/views/frame/browser_view.h"\n'
     '#include "chrome/browser/ui/views/frame/tab_strip_region_view.h"\n'
     '#include "chrome/browser/ui/views/toolbar/toolbar_view.h"\n'
     '#include "ui/views/accessible_pane_view.h"\n'
     '#include "ui/views/controls/menu/menu_types.h"\n'),
    (BAMB_CC,
     'void BrowserAppMenuButton::SetTypeAndSeverity(\n'
     '    AppMenuIconController::TypeAndSeverity type_and_severity) {\n'
     '  type_and_severity_ = type_and_severity;\n'
     '  GetViewAccessibility().SetName(\n'
     '      AppMenuIconController::GetIconAccessibleName(type_and_severity_.type));\n'
     '  UpdateThemeBasedState();\n'
     '}\n'
     '\n'
     'void BrowserAppMenuButton::ShowMenuWithFlags(int run_types) {\n'
     '  if (IsMenuShowing()) {\n'
     '    return;\n'
     '  }\n'
     '\n'
     '#if BUILDFLAG(IS_CHROMEOS)\n'
     '  if (auto* input_method = GetInputMethod()) {\n'
     '    if (auto* controller = input_method->GetVirtualKeyboardController();\n'
     '        controller && controller->IsKeyboardVisible()) {\n'
     '      input_method->SetVirtualKeyboardVisibilityIfEnabled(false);\n'
     '    }\n'
     '  }\n'
     '#endif  // BUILDFLAG(IS_CHROMEOS)\n'
     '\n'
     '  BrowserWindowInterface* browser = toolbar_view_->browser();\n'
     '\n'
     '  if (base::FeatureList::IsEnabled(features::kAppMenuGlowUp)) {\n'
     '    RunActionMenu(browser, run_types);\n'
     '    return;\n'
     '  }\n'
     '\n'
     '  // Allow highlighting menu items when the menu was opened while\n'
     '  // certain tutorials are running.\n'
     '  AlertMenuItem alert_item =\n'
     '      AppMenuModel::GetAlertItemForRunningTutorial(browser);\n'
     '\n'
     '  RunMenu(std::make_unique<AppMenuModel>(\n'
     '              toolbar_view_, browser, toolbar_view_->app_menu_icon_controller(),\n'
     '              alert_item),\n'
     '          browser, run_types);\n'
     '}\n',
     'BrowserLogoMenuButton* BrowserAppMenuButton::GetActiveLogoMenuButton() const {\n'
     '  BrowserView* browser_view = toolbar_view_->browser_view();\n'
     '  return browser_view ? browser_view->GetActiveLogoMenuButton() : nullptr;\n'
     '}\n'
     '\n'
     'void BrowserAppMenuButton::SetTypeAndSeverity(\n'
     '    AppMenuIconController::TypeAndSeverity type_and_severity) {\n'
     '  type_and_severity_ = type_and_severity;\n'
     '  GetViewAccessibility().SetName(\n'
     '      AppMenuIconController::GetIconAccessibleName(type_and_severity_.type));\n'
     '  UpdateThemeBasedState();\n'
     '  // Bluelium : reporter la pastille de mise à jour / alerte sur le logo.\n'
     '  if (BrowserView* browser_view = toolbar_view_->browser_view()) {\n'
     '    for (BrowserLogoMenuButton* logo : browser_view->GetLogoMenuButtons()) {\n'
     '      logo->SetTypeAndSeverity(type_and_severity);\n'
     '    }\n'
     '  }\n'
     '}\n'
     '\n'
     'views::BubbleAnchor BrowserAppMenuButton::GetAnchor() {\n'
     '  if (views::View::IsDrawn()) {\n'
     '    return views::BubbleAnchor(this);\n'
     '  }\n'
     '  if (BrowserLogoMenuButton* logo = GetActiveLogoMenuButton()) {\n'
     '    return views::BubbleAnchor(logo);\n'
     '  }\n'
     '  return AppMenuButton::GetAnchor();\n'
     '}\n'
     '\n'
     'bool BrowserAppMenuButton::IsDrawn() const {\n'
     '  if (views::View::IsDrawn()) {\n'
     '    return true;\n'
     '  }\n'
     '  return GetActiveLogoMenuButton() != nullptr;\n'
     '}\n'
     '\n'
     'void BrowserAppMenuButton::ShowMenu() {\n'
     '  // Bluelium : Alt+F / Alt+E et ShowAppMenu ouvrent le menu sous le logo.\n'
     '  if (BrowserLogoMenuButton* logo = GetActiveLogoMenuButton()) {\n'
     '    logo->ActivateMenu();\n'
     '    return;\n'
     '  }\n'
     '  if (views::View::IsDrawn()) {\n'
     '    AppMenuButton::ShowMenu();\n'
     '    return;\n'
     '  }\n'
     '  ShowMenuWithFlags(views::MenuRunner::SHOULD_SHOW_MNEMONICS |\n'
     '                    views::MenuRunner::INVOKED_FROM_KEYBOARD);\n'
     '}\n'
     '\n'
     'void BrowserAppMenuButton::ShowMenuFromLogo(BrowserLogoMenuButton* logo_button,\n'
     '                                            int run_types) {\n'
     '  if (!logo_button || IsMenuShowing()) {\n'
     '    return;\n'
     '  }\n'
     '  BrowserView* browser_view = toolbar_view_->browser_view();\n'
     '  if (browser_view && browser_view->tab_strip_view()) {\n'
     '    expand_on_hover_lock_ =\n'
     '        browser_view->tab_strip_view()->GetExpandOnHoverLock(\n'
     '            ExpandOnHoverLockType::kKeepCurrentState);\n'
     '  }\n'
     '  const bool right_aligned_vertical =\n'
     '      browser_view && browser_view->ShouldDrawVerticalTabStrip() &&\n'
     '      browser_view->IsVerticalTabStripRightAligned();\n'
     '  const views::MenuAnchorPosition anchor_position =\n'
     '      right_aligned_vertical ? views::MenuAnchorPosition::kTopRight\n'
     '                             : views::MenuAnchorPosition::kTopLeft;\n'
     '  ShowMenuWithFlagsAndAnchor(run_types, logo_button->menu_button_controller(),\n'
     '                             anchor_position);\n'
     '}\n'
     '\n'
     'void BrowserAppMenuButton::ShowMenuWithFlags(int run_types) {\n'
     '  if (!views::View::IsDrawn()) {\n'
     '    if (BrowserLogoMenuButton* logo = GetActiveLogoMenuButton()) {\n'
     '      ShowMenuFromLogo(logo, run_types);\n'
     '      return;\n'
     '    }\n'
     '  }\n'
     '  ShowMenuWithFlagsAndAnchor(run_types, nullptr,\n'
     '                             views::MenuAnchorPosition::kTopRight);\n'
     '}\n'
     '\n'
     'void BrowserAppMenuButton::ShowMenuWithFlagsAndAnchor(\n'
     '    int run_types,\n'
     '    views::MenuButtonController* anchor_host,\n'
     '    views::MenuAnchorPosition anchor_position) {\n'
     '  if (IsMenuShowing()) {\n'
     '    return;\n'
     '  }\n'
     '\n'
     '#if BUILDFLAG(IS_CHROMEOS)\n'
     '  if (auto* input_method = GetInputMethod()) {\n'
     '    if (auto* controller = input_method->GetVirtualKeyboardController();\n'
     '        controller && controller->IsKeyboardVisible()) {\n'
     '      input_method->SetVirtualKeyboardVisibilityIfEnabled(false);\n'
     '    }\n'
     '  }\n'
     '#endif  // BUILDFLAG(IS_CHROMEOS)\n'
     '\n'
     '  BrowserWindowInterface* browser = toolbar_view_->browser();\n'
     '\n'
     '  if (base::FeatureList::IsEnabled(features::kAppMenuGlowUp)) {\n'
     '    RunActionMenu(browser, run_types, anchor_host, anchor_position);\n'
     '    return;\n'
     '  }\n'
     '\n'
     '  // Allow highlighting menu items when the menu was opened while\n'
     '  // certain tutorials are running.\n'
     '  AlertMenuItem alert_item =\n'
     '      AppMenuModel::GetAlertItemForRunningTutorial(browser);\n'
     '\n'
     '  RunMenu(std::make_unique<AppMenuModel>(\n'
     '              toolbar_view_, browser, toolbar_view_->app_menu_icon_controller(),\n'
     '              alert_item),\n'
     '          browser, run_types, anchor_host, anchor_position);\n'
     '}\n'
     '\n'
     'bool BrowserAppMenuButton::HasFocus() const {\n'
     '  if (views::View::HasFocus()) {\n'
     '    return true;\n'
     '  }\n'
     '  BrowserLogoMenuButton* logo = GetActiveLogoMenuButton();\n'
     '  return logo && logo->HasFocus();\n'
     '}\n'
     '\n'
     'void BrowserAppMenuButton::Focus(views::AccessiblePaneView* pane) {\n'
     '  if (views::View::IsDrawn()) {\n'
     '    AppMenuButton::Focus(pane);\n'
     '    return;\n'
     '  }\n'
     '  if (BrowserLogoMenuButton* logo = GetActiveLogoMenuButton()) {\n'
     '    if (BrowserView* browser_view = toolbar_view_->browser_view()) {\n'
     '      if (TabStripRegionView* region = browser_view->tab_strip_view()) {\n'
     '        region->SetPaneFocus(logo);\n'
     '        return;\n'
     '      }\n'
     '    }\n'
     '    logo->RequestFocus();\n'
     '    return;\n'
     '  }\n'
     '  AppMenuButton::Focus(pane);\n'
     '}\n'
     '\n'
     'views::View* BrowserAppMenuButton::GetFocusablePaneView() {\n'
     '  if (views::View::IsDrawn()) {\n'
     '    return this;\n'
     '  }\n'
     '  if (BrowserLogoMenuButton* logo = GetActiveLogoMenuButton()) {\n'
     '    return logo;\n'
     '  }\n'
     '  return this;\n'
     '}\n'),
    (BAMB_CC,
     '  AppMenuButton::OnMenuClosed();\n'
     '}\n',
     '  expand_on_hover_lock_.reset();\n'
     '  AppMenuButton::OnMenuClosed();\n'
     '}\n'),

    # 10. BUILD.gn : déclarer browser_logo_menu_button et câbler les dépendances.
    (FRAME_BUILD,
     'source_set("horizontal_tab_strip_region_view") {\n',
     'source_set("browser_logo_menu_button") {\n'
     '  public = [ "browser_logo_menu_button.h" ]\n'
     '  sources = [ "browser_logo_menu_button.cc" ]\n'
     '  public_deps = [\n'
     '    "//base",\n'
     '    "//chrome/browser/ui/toolbar",\n'
     '    "//ui/base/metadata",\n'
     '    "//ui/gfx",\n'
     '    "//ui/gfx/geometry",\n'
     '    "//ui/views",\n'
     '  ]\n'
     '  deps = [\n'
     '    ":browser_view_header",\n'
     '    ":toolbar_button_provider",\n'
     '    "//cc/paint",\n'
     '    "//chrome/app/theme:theme_resources",\n'
     '    "//chrome/browser/ui:layout_constants",\n'
     '    "//chrome/browser/ui/color:color_headers",\n'
     '    "//chrome/browser/ui/views/toolbar",\n'
     '    "//skia",\n'
     '    "//ui/accessibility",\n'
     '    "//ui/base",\n'
     '    "//ui/color",\n'
     '    "//ui/compositor",\n'
     '    "//ui/events",\n'
     '  ]\n'
     '}\n'
     '\n'
     'source_set("horizontal_tab_strip_region_view") {\n'),
    (FRAME_BUILD,
     'source_set("horizontal_tab_strip_region_view") {\n'
     '  public = [ "horizontal_tab_strip_region_view.h" ]\n'
     '  sources = [ "horizontal_tab_strip_region_view.cc" ]\n'
     '  public_deps = [\n'
     '    ":base_tab_strip_region_view",\n'
     '    ":frame",\n'
     '    "//base",\n'
     '    "//build:buildflag_header_h",\n'
     '    "//chrome/browser/ui/tabs",\n'
     '    "//chrome/browser/ui/views/tabs:tab_strip",\n'
     '    "//chrome/common:buildflags",\n'
     '    "//components/tabs:public",\n'
     '    "//ui/base",\n'
     '    "//ui/base/metadata",\n'
     '    "//ui/views",\n'
     '  ]\n'
     '  deps = [\n'
     '    ":browser_view_header",\n',
     'source_set("horizontal_tab_strip_region_view") {\n'
     '  public = [ "horizontal_tab_strip_region_view.h" ]\n'
     '  sources = [ "horizontal_tab_strip_region_view.cc" ]\n'
     '  public_deps = [\n'
     '    ":base_tab_strip_region_view",\n'
     '    ":frame",\n'
     '    "//base",\n'
     '    "//build:buildflag_header_h",\n'
     '    "//chrome/browser/ui/tabs",\n'
     '    "//chrome/browser/ui/views/tabs:tab_strip",\n'
     '    "//chrome/common:buildflags",\n'
     '    "//components/tabs:public",\n'
     '    "//ui/base",\n'
     '    "//ui/base/metadata",\n'
     '    "//ui/views",\n'
     '  ]\n'
     '  deps = [\n'
     '    ":browser_logo_menu_button",\n'
     '    ":browser_view_header",\n'),
    (FRAME_BUILD,
     'source_set("vertical_tab_strip_region_view") {\n'
     '  public = [ "vertical_tab_strip_region_view.h" ]\n'
     '  sources = [ "vertical_tab_strip_region_view.cc" ]\n'
     '  public_deps = [\n'
     '    ":base_tab_strip_region_view",\n'
     '    "//base",\n'
     '    "//chrome/browser/ui/animation",\n'
     '    "//chrome/browser/ui/omnibox",\n'
     '    "//chrome/browser/ui/tabs",\n'
     '    "//chrome/browser/ui/views/tabs/common",\n'
     '    "//chrome/browser/ui/views/tabs/hovercard",\n'
     '    "//chrome/browser/ui/views/tabs/organizer:organizer_panel_host",\n'
     '    "//chrome/browser/ui/views/tabs/shared",\n'
     '    "//chrome/browser/ui/views/tabs/vertical",\n'
     '    "//components/tabs:public",\n'
     '    "//ui/base",\n'
     '    "//ui/base/metadata",\n'
     '    "//ui/events",\n'
     '    "//ui/gfx/geometry",\n'
     '    "//ui/views",\n'
     '  ]\n'
     '  deps = [\n'
     '    ":browser_view_header",\n',
     'source_set("vertical_tab_strip_region_view") {\n'
     '  public = [ "vertical_tab_strip_region_view.h" ]\n'
     '  sources = [ "vertical_tab_strip_region_view.cc" ]\n'
     '  public_deps = [\n'
     '    ":base_tab_strip_region_view",\n'
     '    "//base",\n'
     '    "//chrome/browser/ui/animation",\n'
     '    "//chrome/browser/ui/omnibox",\n'
     '    "//chrome/browser/ui/tabs",\n'
     '    "//chrome/browser/ui/views/tabs/common",\n'
     '    "//chrome/browser/ui/views/tabs/hovercard",\n'
     '    "//chrome/browser/ui/views/tabs/organizer:organizer_panel_host",\n'
     '    "//chrome/browser/ui/views/tabs/shared",\n'
     '    "//chrome/browser/ui/views/tabs/vertical",\n'
     '    "//components/tabs:public",\n'
     '    "//ui/base",\n'
     '    "//ui/base/metadata",\n'
     '    "//ui/events",\n'
     '    "//ui/gfx/geometry",\n'
     '    "//ui/views",\n'
     '  ]\n'
     '  deps = [\n'
     '    ":browser_logo_menu_button",\n'
     '    ":browser_view_header",\n'),
    (FRAME_BUILD,
     'source_set("app_menu_button") {\n'
     '  public = [ "app_menu_button.h" ]\n'
     '  public_deps = [\n'
     '    "//base",\n'
     '    "//chrome/browser/ui/views/toolbar:app_menu_control",\n'
     '    "//chrome/browser/ui/views/toolbar:toolbar_button",\n'
     '    "//ui/base/metadata",\n'
     '  ]\n'
     '}\n',
     'source_set("app_menu_button") {\n'
     '  public = [ "app_menu_button.h" ]\n'
     '  public_deps = [\n'
     '    "//base",\n'
     '    "//chrome/browser/ui/views/toolbar:app_menu_control",\n'
     '    "//chrome/browser/ui/views/toolbar:toolbar_button",\n'
     '    "//ui/base/metadata",\n'
     '    "//ui/views",\n'
     '  ]\n'
     '}\n'),
    (FRAME_BUILD,
     '  deps = [\n'
     '    ":app_menu_button",\n'
     '    ":browser_frame_view",\n',
     '  deps = [\n'
     '    ":app_menu_button",\n'
     '    ":browser_frame_view",\n'
     '    ":browser_logo_menu_button",\n'),
    (TOOLBAR_BUILD,
     '    "//chrome/browser/ui/views/frame:browser_frame_view",\n'
     '    "//chrome/browser/ui/views/frame:browser_view_header",\n',
     '    "//chrome/browser/ui/views/frame:browser_frame_view",\n'
     '    "//chrome/browser/ui/views/frame:browser_logo_menu_button",\n'
     '    "//chrome/browser/ui/views/frame:browser_view_header",\n'
     '    "//chrome/browser/ui/views/frame:frame",\n'),
]
