"""Helium Glyphe : couleur de la page dans la barre, sans artefact et en fondu.

Avant : BrowserWidget::GetColorProviderKey lisait la couleur de la page active
à chaque appel, donc à chaque dessin. Les zones redessinées seules (animation
de chargement des onglets, bouton recharger) prenaient la nouvelle couleur
pendant que le reste du cadre gardait l’ancienne : rectangles de mauvaise
couleur dans la barre.

Après : la fenêtre garde la couleur affichée et ne la change qu’avec
ThemeChanged(), qui redessine tout. Le passage d’une couleur à l’autre se fait
en fondu (240 ms, ease-in-out, ~30 i/s). Les changements de couleur pendant un
chargement (fond blanc puis couleur du site) sont regroupés : 120 ms de calme
avant le fondu. Changement d’onglet : fondu immédiat. Les fournisseurs de
couleurs créés pour les teintes intermédiaires sont libérés à la fin du fondu
(le cache de ColorProviderManager n’a pas de limite).

Se place après prism-ui (reprend son code de clé de couleurs).
"""

BW = 'chrome/browser/ui/views/frame/browser_widget'
CWV = 'chrome/browser/ui/views/frame/contents_web_view'
CPM = 'ui/color/color_provider_manager'

NEW_FILES = {}

EDITS = [
  # --- ColorProviderManager : retrait ciblé d’entrées du cache. ---
  (CPM + '.h',
   '#include "base/functional/callback.h"\n',
   '#include "base/functional/callback.h"\n'
   '#include "base/functional/function_ref.h"\n'),
  (CPM + '.h',
   '  // Clears the ColorProviders stored in `color_providers_`.\n'
   '  void ResetColorProviderCache();\n',
   '  // Clears the ColorProviders stored in `color_providers_`.\n'
   '  void ResetColorProviderCache();\n\n'
   '  // Helium Glyphe : retire du cache les fournisseurs dont la clé vérifie\n'
   '  // `pred` (teintes intermédiaires du fondu de la barre).\n'
   '  void EraseColorProvidersIf(\n'
   '      base::FunctionRef<bool(const ColorProviderKey&)> pred);\n'),
  (CPM + '.cc',
   'ColorProvider* ColorProviderManager::GetColorProviderFor(ColorProviderKey key) {\n',
   'void ColorProviderManager::EraseColorProvidersIf(\n'
   '    base::FunctionRef<bool(const ColorProviderKey&)> pred) {\n'
   '  base::EraseIf(color_providers_,\n'
   '                [&](const auto& entry) { return pred(entry.first); });\n'
   '}\n\n'
   'ColorProvider* ColorProviderManager::GetColorProviderFor(ColorProviderKey key) {\n'),

  # --- BrowserWidget : couleur affichée stable + fondu. ---
  (BW + '.h',
   '#include "base/memory/raw_ptr.h"\n',
   '#include "base/memory/raw_ptr.h"\n'
   '#include "base/time/time.h"\n'
   '#include "base/timer/timer.h"\n'
   '#include "third_party/skia/include/core/SkColor.h"\n'),
  (BW + '.h',
   '  TabDragKind tab_drag_kind() const { return tab_drag_kind_; }\n',
   '  TabDragKind tab_drag_kind() const { return tab_drag_kind_; }\n\n'
   '  // Helium Glyphe : relit la couleur de la page active et passe en fondu\n'
   '  // à la nouvelle couleur de la barre. `immediate` saute l’attente de\n'
   '  // stabilisation (changement d’onglet, option basculée).\n'
   '  void UpdateGlyphePageColor(bool immediate);\n'),
  (BW + '.h',
   '  raw_ptr<BrowserView> browser_view_;\n',
   '  raw_ptr<BrowserView> browser_view_;\n\n'
   '  // Helium Glyphe : fondu de la couleur de page.\n'
   '  void StartGlyphePageColorFade();\n'
   '  void StepGlyphePageColorFade();\n'
   '  void FinishGlyphePageColorFade();\n'
   '  // Couleur lue par GetColorProviderKey. Ne change qu’avec ThemeChanged(),\n'
   '  // jamais entre deux dessins partiels.\n'
   '  std::optional<SkColor> glyphe_shown_page_color_;\n'
   '  std::optional<SkColor> glyphe_target_page_color_;\n'
   '  SkColor glyphe_fade_from_ = SK_ColorTRANSPARENT;\n'
   '  base::TimeTicks glyphe_fade_start_;\n'
   '  std::vector<SkColor> glyphe_fade_steps_;\n'
   '  base::OneShotTimer glyphe_settle_timer_;\n'
   '  base::RepeatingTimer glyphe_fade_timer_;\n'),
  (BW + '.h',
   '#include <optional>\n',
   '#include <optional>\n#include <vector>\n'),

  (BW + '.cc',
   '  // Helium Glyphe : couleur de la page active dans la barre du haut\n'
   '  // (champ réservé aux applis web, libre pour une fenêtre normale).\n'
   '  else if (!ui::IsGlypheRedNight() &&\n'
   '           profile->GetPrefs()->GetBoolean(prefs::kGlypheFollowPageColor)) {\n'
   '    if (content::WebContents* contents =\n'
   '            browser_view_->GetActiveWebContents()) {\n'
   '      std::optional<SkColor> page = contents->GetThemeColor();\n'
   '      if (!page || SkColorGetA(*page) == SK_AlphaTRANSPARENT) {\n'
   '        page = contents->GetBackgroundColor();\n'
   '      }\n'
   '      // theme-color souvent semi-transparente (YouTube) : rendue opaque.\n'
   '      if (page && SkColorGetA(*page) != SK_AlphaTRANSPARENT) {\n'
   '        key.app_background_color = SkColorSetA(*page, SK_AlphaOPAQUE);\n'
   '      }\n'
   '    }\n'
   '  }\n',
   '  // Helium Glyphe : couleur de la page active dans la barre du haut\n'
   '  // (champ réservé aux applis web, libre pour une fenêtre normale).\n'
   '  // Valeur mémorisée, mise à jour par UpdateGlyphePageColor() avec un\n'
   '  // ThemeChanged() : la lire en direct ici colorait seulement les zones\n'
   '  // redessinées.\n'
   '  else if (glyphe_shown_page_color_ && !ui::IsGlypheRedNight()) {\n'
   '    key.app_background_color = *glyphe_shown_page_color_;\n'
   '  }\n'),
  (BW + '.cc',
   '#include "ui/color/glyphe_red_night.h"\n',
   '#include "ui/color/glyphe_red_night.h"\n'
   '#include <algorithm>\n'
   '#include "ui/color/color_provider_manager.h"\n'
   '#include "ui/gfx/animation/tween.h"\n'
   '#include "ui/gfx/color_utils.h"\n'),
  (BW + '.cc',
   'void BrowserWidget::OnMenuClosed() {\n',
   'void BrowserWidget::UpdateGlyphePageColor(bool immediate) {\n'
   '  if (!browser_view_) {\n'
   '    return;\n'
   '  }\n'
   '  Profile* profile = browser_view_->browser()->GetProfile();\n'
   '  const bool follow =\n'
   '      !ui::IsGlypheRedNight() &&\n'
   '      !web_app::AppBrowserController::From(browser_view_->browser()) &&\n'
   '      profile->GetPrefs()->GetBoolean(prefs::kGlypheFollowPageColor);\n'
   '  std::optional<SkColor> target;\n'
   '  // Nouvel onglet : couleurs du thème, comme Shimmer qui les suit.\n'
   '  content::WebContents* active = browser_view_->GetActiveWebContents();\n'
   '  const bool new_tab_page =\n'
   '      active && active->GetVisibleURL().SchemeIs("chrome") &&\n'
   '      (active->GetVisibleURL().host() == "new-tab-page" ||\n'
   '       active->GetVisibleURL().host() == "newtab");\n'
   '  if (follow && !new_tab_page) {\n'
   '    content::WebContents* contents = active;\n'
   '    std::optional<SkColor> page;\n'
   '    if (contents) {\n'
   '      page = contents->GetThemeColor();\n'
   '      if (!page || SkColorGetA(*page) == SK_AlphaTRANSPARENT) {\n'
   '        page = contents->GetBackgroundColor();\n'
   '      }\n'
   '    }\n'
   '    if (!page || SkColorGetA(*page) == SK_AlphaTRANSPARENT) {\n'
   '      // Couleur pas encore connue (chargement) : on garde la précédente\n'
   '      // plutôt que de repasser par le thème.\n'
   '      if (glyphe_target_page_color_) {\n'
   '        return;\n'
   '      }\n'
   '    } else {\n'
   '      // theme-color souvent semi-transparente (YouTube) : rendue opaque.\n'
   '      target = SkColorSetA(*page, SK_AlphaOPAQUE);\n'
   '    }\n'
   '  }\n'
   '  if (target == glyphe_target_page_color_) {\n'
   '    if (immediate && glyphe_settle_timer_.IsRunning()) {\n'
   '      glyphe_settle_timer_.Stop();\n'
   '      StartGlyphePageColorFade();\n'
   '    }\n'
   '    return;\n'
   '  }\n'
   '  glyphe_target_page_color_ = target;\n'
   '  if (immediate || !target || !glyphe_shown_page_color_) {\n'
   '    glyphe_settle_timer_.Stop();\n'
   '    StartGlyphePageColorFade();\n'
   '    return;\n'
   '  }\n'
   '  // Pendant un chargement la couleur change plusieurs fois de suite (fond\n'
   '  // blanc, puis celui du site) : on attend qu’elle se stabilise.\n'
   '  glyphe_settle_timer_.Start(\n'
   '      FROM_HERE, base::Milliseconds(120),\n'
   '      base::BindOnce(&BrowserWidget::StartGlyphePageColorFade,\n'
   '                     base::Unretained(this)));\n'
   '}\n\n'
   'void BrowserWidget::StartGlyphePageColorFade() {\n'
   '  if (!glyphe_target_page_color_ || !glyphe_shown_page_color_ ||\n'
   '      *glyphe_target_page_color_ == *glyphe_shown_page_color_) {\n'
   '    // Activation, désactivation ou rien à animer : passage direct.\n'
   '    glyphe_fade_timer_.Stop();\n'
   '    FinishGlyphePageColorFade();\n'
   '    return;\n'
   '  }\n'
   '  glyphe_fade_from_ = *glyphe_shown_page_color_;\n'
   '  glyphe_fade_start_ = base::TimeTicks::Now();\n'
   '  glyphe_fade_timer_.Start(\n'
   '      FROM_HERE, base::Milliseconds(33),\n'
   '      base::BindRepeating(&BrowserWidget::StepGlyphePageColorFade,\n'
   '                          base::Unretained(this)));\n'
   '  StepGlyphePageColorFade();\n'
   '}\n\n'
   'void BrowserWidget::StepGlyphePageColorFade() {\n'
   '  constexpr base::TimeDelta kDuration = base::Milliseconds(240);\n'
   '  const double t = std::clamp(\n'
   '      (base::TimeTicks::Now() - glyphe_fade_start_) / kDuration, 0.0, 1.0);\n'
   '  if (t >= 1.0 || !glyphe_target_page_color_) {\n'
   '    glyphe_fade_timer_.Stop();\n'
   '    FinishGlyphePageColorFade();\n'
   '    return;\n'
   '  }\n'
   '  const float eased = static_cast<float>(\n'
   '      gfx::Tween::CalculateValue(gfx::Tween::EASE_IN_OUT, t));\n'
   '  const SkColor color = color_utils::AlphaBlend(\n'
   '      *glyphe_target_page_color_, glyphe_fade_from_, eased);\n'
   '  if (glyphe_shown_page_color_ == color) {\n'
   '    return;\n'
   '  }\n'
   '  glyphe_shown_page_color_ = color;\n'
   '  glyphe_fade_steps_.push_back(color);\n'
   '  ThemeChanged();\n'
   '}\n\n'
   'void BrowserWidget::FinishGlyphePageColorFade() {\n'
   '  const bool changed = glyphe_shown_page_color_ != glyphe_target_page_color_;\n'
   '  glyphe_shown_page_color_ = glyphe_target_page_color_;\n'
   '  if (changed) {\n'
   '    ThemeChanged();\n'
   '  }\n'
   '  if (glyphe_fade_steps_.empty()) {\n'
   '    return;\n'
   '  }\n'
   '  // Les teintes intermédiaires ne resservent pas : le cache des\n'
   '  // fournisseurs de couleurs n’a pas de limite, on les libère.\n'
   '  std::vector<SkColor> steps;\n'
   '  steps.swap(glyphe_fade_steps_);\n'
   '  const std::optional<SkColor> keep = glyphe_shown_page_color_;\n'
   '  ui::ColorProviderManager::Get().EraseColorProvidersIf(\n'
   '      [&](const ui::ColorProviderKey& key) {\n'
   '        return !key.app_controller && key.app_background_color &&\n'
   '               key.app_background_color != keep &&\n'
   '               std::ranges::contains(steps, *key.app_background_color);\n'
   '      });\n'
   '}\n\n'
   'void BrowserWidget::OnMenuClosed() {\n'),

  # --- ContentsWebView : délègue à la fenêtre. ---
  (CWV + '.cc',
   'void ContentsWebView::UpdateGlyphePageColor() {\n'
   '  // La clé de couleurs de la fenêtre lit la couleur de la page active\n'
   '  // (BrowserWidget::GetColorProviderKey) : il suffit de la recalculer\n'
   '  // quand cette couleur change.\n'
   '  if (!GetWidget() || !glyphe_pref_registrar_.prefs()) {\n'
   '    return;\n'
   '  }\n'
   '  const bool follow = glyphe_pref_registrar_.prefs()->GetBoolean(\n'
   '      prefs::kGlypheFollowPageColor);\n'
   '  std::optional<SkColor> color;\n'
   '  if (follow && web_contents()) {\n'
   '    color = web_contents()->GetThemeColor();\n'
   '    if (!color) {\n'
   '      color = web_contents()->GetBackgroundColor();\n'
   '    }\n'
   '  }\n'
   '  if (follow == glyphe_follow_page_ && color == glyphe_page_color_) {\n'
   '    return;\n'
   '  }\n'
   '  glyphe_follow_page_ = follow;\n'
   '  glyphe_page_color_ = color;\n'
   '  GetWidget()->ThemeChanged();\n'
   '}\n\n'
   'void ContentsWebView::DidChangeThemeColor() {\n'
   '  UpdateGlyphePageColor();\n'
   '}\n\n'
   'void ContentsWebView::OnBackgroundColorChanged() {\n'
   '  UpdateGlyphePageColor();\n'
   '}\n',
   'void ContentsWebView::UpdateGlyphePageColor() {\n'
   '  UpdateGlyphePageColorFor(/*immediate=*/true);\n'
   '}\n\n'
   'void ContentsWebView::UpdateGlyphePageColorFor(bool immediate) {\n'
   '  // La fenêtre garde la couleur affichée et gère le fondu.\n'
   '  views::Widget* widget = GetWidget();\n'
   '  if (!widget) {\n'
   '    return;\n'
   '  }\n'
   '  BrowserView* browser_view =\n'
   '      BrowserView::GetBrowserViewForNativeWindow(widget->GetNativeWindow());\n'
   '  if (browser_view && browser_view->browser_widget()) {\n'
   '    browser_view->browser_widget()->UpdateGlyphePageColor(immediate);\n'
   '  }\n'
   '}\n\n'
   'void ContentsWebView::DidChangeThemeColor() {\n'
   '  UpdateGlyphePageColorFor(/*immediate=*/false);\n'
   '}\n\n'
   'void ContentsWebView::OnBackgroundColorChanged() {\n'
   '  UpdateGlyphePageColorFor(/*immediate=*/false);\n'
   '}\n'),
  (CWV + '.cc',
   '      ui::NativeTheme::GetInstanceForNativeUi()->NotifyOnNativeThemeUpdated();\n'
   '    }\n',
   '      ui::NativeTheme::GetInstanceForNativeUi()->NotifyOnNativeThemeUpdated();\n'
   '      UpdateGlyphePageColor();\n'
   '    }\n'),
  (CWV + '.cc',
   '#include "chrome/browser/ui/views/frame/contents_web_view.h"\n',
   '#include "chrome/browser/ui/views/frame/contents_web_view.h"\n\n'
   '#include "chrome/browser/ui/views/frame/browser_view.h"\n'
   '#include "chrome/browser/ui/views/frame/browser_widget.h"\n'),
  (CWV + '.h',
   '  std::optional<SkColor> glyphe_page_color_;\n'
   '  bool glyphe_follow_page_ = false;\n',
   '  void UpdateGlyphePageColorFor(bool immediate);\n'),
]

# Zone libre de la barre d'onglets (après le « + ») restée à l'ancienne
# couleur : un changement de thème ne redessine que les vues qui le demandent,
# et ThemedBackground (fond de la région des onglets) ne le demandait pas.
# Onglets et boutons se redessinaient, pas le fond entre eux et les boutons
# de fenêtre.
EDITS += [
  ('chrome/browser/ui/views/frame/themed_background.h',
   '  void Paint(gfx::Canvas* canvas, views::View* view) const override;\n',
   '  void Paint(gfx::Canvas* canvas, views::View* view) const override;\n'
   '  // Glyphe : redessin à chaque changement de couleurs (couleur de page).\n'
   '  void OnViewThemeChanged(views::View* view) override;\n'),
  ('chrome/browser/ui/views/frame/themed_background.cc',
   'void ThemedBackground::Paint(gfx::Canvas* canvas, views::View* view) const {\n',
   'void ThemedBackground::OnViewThemeChanged(views::View* view) {\n'
   '  views::Background::OnViewThemeChanged(view);\n'
   '  view->SchedulePaint();\n'
   '}\n\n'
   'void ThemedBackground::Paint(gfx::Canvas* canvas, views::View* view) const {\n'),
]
