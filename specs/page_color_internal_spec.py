"""Bluelium : garder le thème sur les pages internes et les erreurs.

Après page-color-blend. Le fondu entre deux pages web garde sa courbe. Lors
d'un passage par le thème, l'alpha de la teinte représente le poids de la
palette de page sur les couleurs du thème, jusqu'à retrouver la clé de base.
"""

FRAME = 'chrome/browser/ui/views/frame/'
WIDGET = FRAME + 'browser_widget.cc'
VIEW = FRAME + 'browser_view.cc'
CHROME_MIXERS = 'chrome/browser/ui/color/chrome_color_mixers.cc'
PRISM = 'ui/color/glyphe_prism'

EDITS = [
    (WIDGET,
     '#include "content/public/browser/web_contents.h"\n',
     '#include "content/public/browser/render_frame_host.h"\n'
     '#include "content/public/browser/web_contents.h"\n'
     '#include "content/public/common/url_constants.h"\n'),
    (WIDGET,
     '#include "ui/views/widget/native_widget.h"\n',
     '#include "ui/views/widget/native_widget.h"\n'
     '#include "url/gurl.h"\n'
     '#include "url/url_constants.h"\n'),
    (WIDGET,
     'bool IsUsingLinuxSystemTheme(Profile* profile) {\n',
     '''bool UsesThemeForPage(content::WebContents& contents) {
  const auto* main_frame = contents.GetPrimaryMainFrame();
  if (main_frame && main_frame->IsErrorDocument()) {
    return true;
  }

  // Bluelium : l'URL visible peut déjà désigner une navigation en attente.
  // L'alias bluelium:// est normalement réécrit en chrome:// avant le commit.
  const GURL& committed_url = contents.GetLastCommittedURL();
  const GURL& page_url =
      committed_url.is_empty() ? contents.GetVisibleURL() : committed_url;
  return page_url.SchemeIs(content::kChromeUIScheme) ||
         page_url.SchemeIs(content::kChromeUIUntrustedScheme) ||
         page_url.SchemeIs(content::kChromeDevToolsScheme) ||
         page_url.SchemeIs(url::kAboutScheme) ||
         page_url.SchemeIs(content::kHeliumUIScheme);
}

bool IsUsingLinuxSystemTheme(Profile* profile) {
'''),
    (WIDGET,
     '''  std::optional<SkColor> target;
  // Nouvel onglet : couleurs du thème, comme Shimmer qui les suit.
  content::WebContents* active = browser_view_->GetActiveWebContents();
  const bool new_tab_page =
      active && active->GetVisibleURL().SchemeIs("chrome") &&
      (active->GetVisibleURL().host() == "new-tab-page" ||
       active->GetVisibleURL().host() == "newtab");
  if (follow && !new_tab_page) {
    content::WebContents* contents = active;
    std::optional<SkColor> page;
    if (contents) {
      page = contents->GetThemeColor();
      if (!page || SkColorGetA(*page) == SK_AlphaTRANSPARENT) {
        page = contents->GetBackgroundColor();
      }
    }
''',
     '''  std::optional<SkColor> target;
  content::WebContents* active = browser_view_->GetActiveWebContents();
  if (follow && active && !UsesThemeForPage(*active)) {
    std::optional<SkColor> page = active->GetThemeColor();
    if (!page || SkColorGetA(*page) == SK_AlphaTRANSPARENT) {
      page = active->GetBackgroundColor();
    }
'''),
    (WIDGET,
     '''  if (target == glyphe_target_page_color_) {
''',
     '''  if (!follow || !active) {
    glyphe_target_page_color_.reset();
    glyphe_settle_timer_.Stop();
    glyphe_fade_timer_.Stop();
    FinishGlyphePageColorFade();
    return;
  }
  if (target == glyphe_target_page_color_) {
'''),
    (WIDGET,
     '''  glyphe_target_page_color_ = target;
  if (immediate || !target || !glyphe_shown_page_color_) {
''',
     '''  const bool theme_transition = !target || !glyphe_target_page_color_;
  glyphe_target_page_color_ = target;
  if (immediate || theme_transition || !glyphe_shown_page_color_ ||
      SkColorGetA(*glyphe_shown_page_color_) != SK_AlphaOPAQUE) {
'''),
    (WIDGET,
     '''  // Pendant un chargement la couleur change plusieurs fois de suite (fond
  // blanc, puis celui du site) : on attend qu’elle se stabilise.
  glyphe_settle_timer_.Start(
''',
     '''  // Pendant un chargement la couleur change plusieurs fois de suite (fond
  // blanc, puis celui du site) : on attend qu’elle se stabilise.
  glyphe_fade_timer_.Stop();
  glyphe_settle_timer_.Start(
'''),
    (WIDGET,
     '''  if (!glyphe_target_page_color_ || !glyphe_shown_page_color_ ||
      *glyphe_target_page_color_ == *glyphe_shown_page_color_) {
    // Activation, désactivation ou rien à animer : passage direct.
    glyphe_fade_timer_.Stop();
    FinishGlyphePageColorFade();
    return;
  }
  glyphe_fade_from_ = *glyphe_shown_page_color_;
''',
     '''  if (glyphe_target_page_color_ == glyphe_shown_page_color_) {
    glyphe_fade_timer_.Stop();
    FinishGlyphePageColorFade();
    return;
  }
  // Bluelium : une teinte transparente laisse apparaître le thème.
  glyphe_fade_from_ = glyphe_shown_page_color_.value_or(SK_ColorTRANSPARENT);
'''),
    (WIDGET,
     '''  if (t >= 1.0 || !glyphe_target_page_color_) {
    glyphe_fade_timer_.Stop();
    FinishGlyphePageColorFade();
    return;
  }
  const float eased = static_cast<float>(
      gfx::Tween::CalculateValue(gfx::Tween::EASE_OUT, t));
  const SkColor color = color_utils::AlphaBlend(
      *glyphe_target_page_color_, glyphe_fade_from_, eased);
  if (glyphe_shown_page_color_ == color) {
    return;
  }
  glyphe_shown_page_color_ = color;
  glyphe_fade_steps_.push_back(color);
''',
     '''  if (t >= 1.0) {
    glyphe_fade_timer_.Stop();
    FinishGlyphePageColorFade();
    return;
  }
  const double eased = gfx::Tween::CalculateValue(gfx::Tween::EASE_OUT, t);
  const SkColor color = gfx::Tween::ColorValueBetween(
      eased, glyphe_fade_from_,
      glyphe_target_page_color_.value_or(SK_ColorTRANSPARENT));
  const std::optional<SkColor> shown = SkColorGetA(color) == SK_AlphaTRANSPARENT
                                          ? std::nullopt
                                          : std::optional<SkColor>(color);
  if (glyphe_shown_page_color_ == shown) {
    return;
  }
  glyphe_shown_page_color_ = shown;
  if (shown) {
    glyphe_fade_steps_.push_back(*shown);
  }
'''),
    (VIEW,
     '''    SetWindowManagementPermissionSubscriptionForUnframedMode(
        navigation_handle->GetWebContents());
  }
}
''',
     '''    SetWindowManagementPermissionSubscriptionForUnframedMode(
        navigation_handle->GetWebContents());
  }
  // Bluelium : une page interne ou une erreur peut garder le même fond.
  browser_widget_->UpdateGlyphePageColor(/*immediate=*/false);
}
'''),
    (VIEW,
     '''  // Update all the UI bits.
  UpdateTitleBar();
''',
     '''  // Bluelium : couvre aussi le changement d'onglet en vue divisée,
  // où le WebContents peut déjà être attaché à sa vue.
  browser_widget_->UpdateGlyphePageColor(/*immediate=*/true);
  // Update all the UI bits.
  UpdateTitleBar();
'''),
    (PRISM + '.h',
     'class ColorProvider;\n',
     'class ColorMixer;\nclass ColorProvider;\n'),
    (PRISM + '.h',
     '// Réécrit les jetons système quand une palette s’applique.\n',
     '''// Fond la palette de page (recettes à couleurs fixes) sur les couleurs
// déjà définies dans le fournisseur.
COMPONENT_EXPORT(COLOR) void AddGlyphePageColorFadeMixer(
    ColorProvider* provider, const ColorMixer& page, SkAlpha opacity);

// Réécrit les jetons système quand une palette s’applique.
'''),
    (PRISM + '.cc',
     'void AddGlyphePrismMixer(ColorProvider* provider,\n',
     '''void AddGlyphePageColorFadeMixer(ColorProvider* provider,
                                const ColorMixer& page,
                                SkAlpha opacity) {
  ColorMixer& fade = provider->AddMixer();
  for (ColorId id : page.GetDefinedColorIds()) {
    fade[id] = {AlphaBlend(page.GetResultColor(id), FromTransformInput(),
                           opacity)};
  }
}

void AddGlyphePrismMixer(ColorProvider* provider,
'''),
    (PRISM + '.cc',
     '    ColorMixer& header = provider->AddMixer();\n',
     '''    const SkAlpha opacity = SkColorGetA(*key.app_background_color);
    ColorMixer page_header;
    ColorMixer& header =
        opacity == SK_AlphaOPAQUE ? provider->AddMixer() : page_header;
'''),
    (PRISM + '.cc',
     '    header[kColorSysStateHeaderSelect] = {SkColorSetA(header_tint, 0x24)};\n',
     '''    header[kColorSysStateHeaderSelect] = {SkColorSetA(header_tint, 0x24)};
    if (opacity != SK_AlphaOPAQUE) {
      AddGlyphePageColorFadeMixer(provider, page_header, opacity);
    }
'''),
    (CHROME_MIXERS,
     '''  if (const ui::GlyphePrismPalette* prism =
          glyphe_page ? &*glyphe_page : ui::GetGlyphePrismPalette(key)) {
    ui::ColorMixer& p = provider->AddMixer();
''',
     '''  const auto add_prism_colors = [](ui::ColorMixer& p,
                                   const ui::GlyphePrismPalette& palette) {
    const auto* prism = &palette;
'''),
    (CHROME_MIXERS,
     '''      p[kColorToolbarInkDropRipple] = {SkColorSetA(prism->text, 0x1f)};
    }
  }
''',
     '''      p[kColorToolbarInkDropRipple] = {SkColorSetA(prism->text, 0x1f)};
    }
  };
  if (glyphe_page && SkColorGetA(*key.app_background_color) == SK_AlphaOPAQUE) {
    add_prism_colors(provider->AddMixer(), *glyphe_page);
  } else {
    if (const auto* base = ui::GetGlyphePrismPalette(key)) {
      add_prism_colors(provider->AddMixer(), *base);
    }
    if (glyphe_page) {
      ui::ColorMixer page;
      add_prism_colors(page, *glyphe_page);
      ui::AddGlyphePageColorFadeMixer(
          provider, page, SkColorGetA(*key.app_background_color));
    }
  }
'''),
]
