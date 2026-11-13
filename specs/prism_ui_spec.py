# Helium Glyphe — interface dans la DA de la maquette (charte Prism), v4.
#
# Thèmes (onglet « Personnaliser » de Helium) :
#  - la grille de couleurs ne propose plus que les thèmes Glyphe : Prism (bleu,
#    par défaut), Ardoise, Ambre, Sauge, Lilas, Rose, chacun en clair et en
#    sombre ; la pastille grise et les couleurs de Helium sont retirées
#    (la pipette de couleur libre reste) ;
#  - Prism est appliqué aux nouveaux profils, aux profils restés sur le gris de
#    Helium et après « Réinitialiser » ;
# Bluelium : modes Clair, Sombre, OLED (noir pur), Nuit (lumière chaude),
#    Appareil ;
#  - interrupteur « Couleur de la page dans la barre » : le cadre, les onglets et
#    la barre d'outils prennent la couleur de la page active (theme-color, sinon
#    fond de la page), texte noir ou blanc selon le contraste.
# Désactivé avec un thème d'extension, un thème GTK/Qt, le contraste élevé et
# Bluelium : les couleurs forcées sont conservées ; Nuit filtre les pages.
#
# Mise en page alignée sur la maquette : onglets de 30 × 176 px, 8 px entre
# favicon et titre, séparateurs de 14 px ; boutons et champ d'adresse de 30 px,
# icônes de 18 px, 2 px entre les outils ; champ d'adresse à coins de 10 px ;
# page en retrait de 6 px à coins de 10 px.
# Texte : Instrument Sans Medium 13 px si la police est installée, lissage en
# niveaux de gris sans hinting avec positionnement sous-pixel.
from pathlib import Path


def rgb(h):
  h = h.lstrip('#')
  return f'SkColorSetRGB(0x{h[0:2]}, 0x{h[2:4]}, 0x{h[4:6]})'


FIELDS = ['frame', 'card', 'tab', 'field', 'text', 'muted', 'subtle', 'divider', 'accent', 'on_accent']

# (nom, libellé IDS pour l'accessibilité, clair, sombre). La graine de la
# pastille est l'accent clair.
THEMES = [
  ('Prism', 'IDS_NTP_COLORS_BLUE',
   ['#e3e8ff', '#fbfcff', '#fbfcff', '#d7ddfc', '#0d1c64', '#475a7f', '#646f9a', '#bcc3e3', '#3450d1', '#ffffff'],
   ['#151932', '#0e1123', '#0e1123', '#222641', '#e3e6f2', '#8f9bcb', '#7985b2', '#3b405f', '#b3beec', '#0d1c64']),
  ('Ardoise', 'IDS_NTP_COLORS_GREY',
   ['#e8e8ec', '#fcfcfd', '#fcfcfd', '#dcdce2', '#18181b', '#52525b', '#71717a', '#c4c4cc', '#27272a', '#ffffff'],
   ['#1c1c20', '#111114', '#111114', '#2a2a30', '#ececef', '#a1a1aa', '#7c7c86', '#3a3a42', '#e4e4e7', '#18181b']),
  ('Ambre', 'IDS_NTP_COLORS_APRICOT',
   ['#efeeec', '#fbfaf8', '#fbfaf8', '#e4e2df', '#111111', '#3d3b39', '#6b6966', '#cfccc8', '#c4530a', '#ffffff'],
   ['#1a1816', '#0d0c0b', '#0d0c0b', '#292623', '#f1f1f1', '#c9c7c4', '#909090', '#3a3633', '#ed6a0c', '#111111']),
  ('Sauge', 'IDS_NTP_COLORS_GREEN',
   ['#e2ebe5', '#fbfdfb', '#fbfdfb', '#d5e2d9', '#0f2a1d', '#415a4c', '#637a6d', '#bccfc3', '#2f6b4f', '#ffffff'],
   ['#142019', '#0c1510', '#0c1510', '#1f2e25', '#e1ece5', '#94ad9f', '#758c7f', '#33463b', '#a8d5bc', '#0f2a1d']),
  ('Lilas', 'IDS_NTP_COLORS_VIOLET',
   ['#ebe5ff', '#fdfcff', '#fdfcff', '#ded6fb', '#23125e', '#574a80', '#736a99', '#cbc2e8', '#6b4fd1', '#ffffff'],
   ['#1c1633', '#120e24', '#120e24', '#2a2346', '#ebe6f7', '#a698cf', '#8a7fb3', '#41385f', '#c9bcf5', '#23125e']),
  ('Rose', 'IDS_NTP_COLORS_ROSE',
   ['#fde4e8', '#fffbfc', '#fffbfc', '#f7d5db', '#5a0f1f', '#7f4651', '#9a6b74', '#ecc1c9', '#c2304d', '#ffffff'],
   ['#2a1419', '#1c0c10', '#1c0c10', '#3a1f25', '#f7e3e7', '#cf98a3', '#b07c87', '#55333b', '#f5b3c0', '#5a0f1f']),
]


def _derive(name, ids, seed):
  """Thème dérivé de Prism : même luminosité et saturation, teinte de `seed`
  (couleurs des pastilles de Shimmer). L'accent clair est la graine exacte."""
  import colorsys
  def hls(h):
    h = h.lstrip('#')
    return colorsys.rgb_to_hls(*(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))
  def hexa(hue, l, s):
    return '#' + ''.join(f'{round(c * 255):02x}' for c in colorsys.hls_to_rgb(hue, l, s))
  hue = hls(seed)[0]
  light, dark = ([hexa(hue, *hls(c)[1:]) for c in palette] for palette in THEMES[0][2:4])
  light[8], light[9] = seed, '#ffffff'
  return (name, ids, light, dark)


# Pastilles de Shimmer absentes des thèmes Glyphe (#3450d1 est Prism).
THEMES += [
  _derive('Azur', 'IDS_NTP_COLORS_LIGHT_BLUE', '#1a73e8'),
  _derive('Émeraude', 'IDS_NTP_COLORS_DARK_GREEN', '#0b8043'),
  _derive('Carmin', 'IDS_NTP_COLORS_DARK_PINK_AND_RED', '#c5221f'),
  _derive('Mandarine', 'IDS_NTP_COLORS_ORANGE', '#e8710a'),
  _derive('Améthyste', 'IDS_NTP_COLORS_DARK_PURPLE', '#9334e6'),
]
OLED = ['#000000', '#000000', '#1a1a1f', '#0f0f12', '#ececef', '#8b8b95', '#6b6b74', '#26262c', '#ffffff', '#000000']


def pal(values, dark, indent='    '):
  body = ',\n'.join(f'{indent}    .{f} = {rgb(v)}' for f, v in zip(FIELDS, values))
  return '{\n' + body + f',\n{indent}    .dark = {"true" if dark else "false"}}}'


themes_table = ',\n'.join(
    f'    {{"{name}", {rgb(light[8])},\n     {pal(light, False, "     ")},\n     {pal(dark, True, "     ")}}}'
    for name, _, light, dark in THEMES)

NEW_FILES = {
  'ui/color/glyphe_prism.h': '''// Helium Glyphe — thèmes de l’interface (charte Prism).
#ifndef UI_COLOR_GLYPHE_PRISM_H_
#define UI_COLOR_GLYPHE_PRISM_H_

#include "base/component_export.h"
#include "third_party/skia/include/core/SkColor.h"

namespace ui {

class ColorProvider;
struct ColorProviderKey;

// Couleurs de base d’une palette ; tout le reste en est dérivé.
struct GlyphePrismPalette {
  SkColor frame;      // cadre et barre d’outils
  SkColor card;       // menus, bulles, fond des pages internes
  SkColor tab;        // onglet actif
  SkColor field;      // champ d’adresse posé sur le cadre
  SkColor text;       // texte principal
  SkColor muted;      // onglets inactifs, texte secondaire
  SkColor subtle;     // éléments discrets ou désactivés
  SkColor divider;    // séparateurs d’onglets et d’outils
  SkColor accent;     // accent
  SkColor on_accent;  // texte sur l’accent
  bool dark;
};

// Un thème de la grille du panneau Personnaliser ; `seed` est la couleur
// enregistrée quand on choisit sa pastille.
struct GlypheTheme {
  const char* name;
  SkColor seed;
  GlyphePrismPalette light;
  GlyphePrismPalette dark;
};

inline constexpr int kGlypheThemeCount = %(count)d;
// Graine du thème Prism, thème par défaut.
inline constexpr SkColor kGlyphePrismSeed = %(prism_seed)s;

COMPONENT_EXPORT(COLOR) const GlypheTheme& GetGlypheTheme(int index);
// Thème dont la graine est `seed`, ou nullptr.
COMPONENT_EXPORT(COLOR) const GlypheTheme* FindGlypheTheme(SkColor seed);

// Mode OLED (noir pur), choisi dans le panneau Personnaliser.
COMPONENT_EXPORT(COLOR) void SetGlypheOled(bool enabled);
COMPONENT_EXPORT(COLOR) bool IsGlypheOled();

// Palette tirée d’une couleur de page (barre du haut qui suit la page).
COMPONENT_EXPORT(COLOR) GlyphePrismPalette GlyphePageColorPalette(SkColor page);

// Palette à appliquer pour cette clé : OLED si le mode est actif, sinon le
// thème Glyphe choisi (Prism sans choix), nullptr pour une couleur libre.
COMPONENT_EXPORT(COLOR)
const GlyphePrismPalette* GetGlyphePrismPalette(const ColorProviderKey& key);

// Réécrit les jetons système quand une palette s’applique.
void AddGlyphePrismMixer(ColorProvider* provider, const ColorProviderKey& key);

}  // namespace ui

#endif  // UI_COLOR_GLYPHE_PRISM_H_
''' % dict(count=len(THEMES), prism_seed=rgb(THEMES[0][2][8])),

  'ui/color/glyphe_prism.cc': '''// Helium Glyphe — thèmes de l’interface (charte Prism).
#include "ui/color/glyphe_prism.h"

#include <atomic>

#include "ui/color/color_id.h"
#include "ui/color/color_mixer.h"
#include "ui/color/color_provider.h"
#include "ui/color/color_provider_key.h"
#include "ui/color/color_recipe.h"
#include "ui/color/glyphe_red_night.h"
#include "ui/color/system_theme.h"
#include "ui/gfx/color_utils.h"

namespace ui {

namespace {

std::atomic<bool> g_oled{false};

constexpr GlypheTheme kThemes[kGlypheThemeCount] = {
%(themes)s
};

constexpr GlyphePrismPalette kOled = %(oled)s;

// Mélange : `alpha` de `fg` sur `bg`.
SkColor Mix(SkColor fg, SkColor bg, int alpha) {
  return color_utils::AlphaBlend(fg, bg, static_cast<SkAlpha>(alpha));
}

}  // namespace

const GlypheTheme& GetGlypheTheme(int index) {
  return kThemes[index >= 0 && index < kGlypheThemeCount ? index : 0];
}

const GlypheTheme* FindGlypheTheme(SkColor seed) {
  for (const GlypheTheme& theme : kThemes) {
    if (theme.seed == seed) {
      return &theme;
    }
  }
  return nullptr;
}

void SetGlypheOled(bool enabled) {
  g_oled.store(enabled);
}

bool IsGlypheOled() {
  return g_oled.load();
}

GlyphePrismPalette GlyphePageColorPalette(SkColor page) {
  const SkColor page_bg = SkColorSetA(page, SK_AlphaOPAQUE);
  const bool dark = color_utils::IsDark(page_bg);
  const SkColor fg = dark ? SkColorSetRGB(0xf4, 0xf5, 0xf7)
                          : SkColorSetRGB(0x15, 0x16, 0x1a);
  // Bluelium : barre un peu décalée de la page (plus sombre sur une page
  // claire, plus claire sur une page sombre), même teinte : à la couleur
  // exacte, le bord de la page se confondait avec la barre.
  const SkColor bg = Mix(fg, page_bg, 0x14);
  return {.frame = bg,
          .card = bg,
          .tab = Mix(fg, bg, 0x1c),
          .field = Mix(fg, bg, 0x12),
          .text = fg,
          .muted = Mix(fg, bg, 0xb8),
          .subtle = Mix(fg, bg, 0x8a),
          .divider = Mix(fg, bg, 0x38),
          .accent = fg,
          .on_accent = bg,
          .dark = dark};
}

const GlyphePrismPalette* GetGlyphePrismPalette(const ColorProviderKey& key) {
  if (IsGlypheRedNight() || key.custom_theme ||
      key.system_theme != SystemTheme::kDefault ||
      key.contrast_mode == ColorProviderKey::ContrastMode::kHigh ||
      key.forced_colors != ColorProviderKey::ForcedColors::kNone) {
    return nullptr;
  }
  if (IsGlypheOled()) {
    return &kOled;
  }
  const bool dark = key.color_mode == ColorProviderKey::ColorMode::kDark;
  const GlypheTheme* theme = nullptr;
  if (key.user_color_source == ColorProviderKey::UserColorSource::kGrayscale ||
      !key.user_color.has_value()) {
    theme = &kThemes[0];  // Prism par défaut.
  } else {
    theme = FindGlypheTheme(*key.user_color);
  }
  if (!theme) {
    return nullptr;  // Couleur libre (pipette) : couleurs dérivées de Helium.
  }
  return dark ? &theme->dark : &theme->light;
}

void AddGlyphePrismMixer(ColorProvider* provider,
                         const ColorProviderKey& key) {
  const GlyphePrismPalette* p = GetGlyphePrismPalette(key);
  if (!p) {
    return;
  }
  // Teinte des états (survol, sélection) : l’accent en clair, le texte en
  // sombre pour rester visible sur les fonds profonds.
  const SkColor tint = p->dark ? p->text : p->accent;
  const SkColor lowest = p->dark ? Mix(SK_ColorBLACK, p->card, 0x40)
                                 : SK_ColorWHITE;
  const SkColor elevated = p->dark ? Mix(p->text, p->card, 0x12)
                                   : SK_ColorWHITE;

  ColorMixer& mixer = provider->AddMixer();
  mixer[kColorSysPrimary] = {p->accent};
  mixer[kColorSysOnPrimary] = {p->on_accent};
  mixer[kColorSysPrimaryContainer] = {Mix(p->accent, p->card, 0x2e)};
  mixer[kColorSysOnPrimaryContainer] = {p->text};
  mixer[kColorSysInversePrimary] = {Mix(p->accent, p->card, 0x80)};
  mixer[kColorSysOnSurface] = {p->text};
  mixer[kColorSysOnSurfaceVariant] = {p->muted};
  mixer[kColorSysOnSurfaceSecondary] = {p->muted};
  mixer[kColorSysOnSurfaceSubtle] = {p->subtle};
  mixer[kColorSysOnSurfacePrimary] = {p->accent};
  mixer[kColorSysOnSurfacePrimaryInactive] = {p->muted};
  mixer[kColorSysSurface] = {p->card};
  mixer[kColorSysSurface1] = {Mix(p->frame, p->card, 0x33)};
  mixer[kColorSysSurface2] = {Mix(p->frame, p->card, 0x66)};
  mixer[kColorSysSurface3] = {Mix(p->frame, p->card, 0x99)};
  mixer[kColorSysSurface4] = {Mix(p->frame, p->card, 0xcc)};
  mixer[kColorSysSurface5] = {p->frame};
  mixer[kColorSysSurfaceVariant] = {Mix(p->muted, p->card, 0x2e)};
  mixer[kColorSysSurfaceContainerLowest] = {lowest};
  mixer[kColorSysSurfaceContainerLow] = {Mix(p->frame, p->card, 0x40)};
  mixer[kColorSysSurfaceContainer] = {Mix(p->frame, p->card, 0x80)};
  mixer[kColorSysSurfaceContainerHigh] = {Mix(p->frame, p->card, 0xc0)};
  mixer[kColorSysSurfaceContainerHighest] = {Mix(p->text, p->frame, 0x10)};
  mixer[kColorSysBase] = {p->card};
  mixer[kColorSysBaseContainer] = {Mix(p->frame, p->card, 0x80)};
  mixer[kColorSysBaseContainerElevated] = {elevated};
  mixer[kColorSysHeader] = {p->frame};
  mixer[kColorSysHeaderInactive] = {p->frame};
  mixer[kColorSysHeaderContainer] = {p->tab};
  mixer[kColorSysHeaderContainerInactive] = {p->tab};
  mixer[kColorSysOnHeaderPrimary] = {p->muted};
  mixer[kColorSysOnHeaderPrimaryInactive] = {p->subtle};
  mixer[kColorSysOnHeaderDivider] = {p->divider};
  mixer[kColorSysOnHeaderDividerInactive] = {p->divider};
  mixer[kColorSysDivider] = {Mix(p->muted, p->card, 0x30)};
  mixer[kColorSysOutline] = {p->subtle};
  mixer[kColorSysNeutralOutline] = {Mix(p->muted, p->card, 0x50)};
  mixer[kColorSysTonalOutline] = {Mix(p->accent, p->card, 0x80)};
  mixer[kColorSysNeutralContainer] = {Mix(p->frame, p->card, 0xa0)};
  mixer[kColorSysTonalContainer] = {Mix(p->accent, p->card, 0x2e)};
  mixer[kColorSysOnTonalContainer] = {p->text};
  mixer[kColorSysOmniboxContainer] = {p->field};
  mixer[kColorSysStateHoverOnSubtle] = {SkColorSetA(tint, 0x14)};
  mixer[kColorSysStateHoverOnProminent] = {SkColorSetA(p->on_accent, 0x1f)};
  mixer[kColorSysStateRippleNeutralOnSubtle] = {SkColorSetA(tint, 0x29)};
  mixer[kColorSysStateHeaderHover] = {SkColorSetA(tint, 0x1a)};
  mixer[kColorSysStateHeaderHoverInactive] = {SkColorSetA(tint, 0x14)};
  mixer[kColorSysStateHeaderSelect] = {SkColorSetA(tint, 0x24)};
  mixer[kColorSysStateFocusRing] = {p->accent};
  mixer[kColorSysStateTextHighlight] = {Mix(p->accent, p->card, 0x55)};
  mixer[kColorSysStateOnTextHighlight] = {p->text};
}

}  // namespace ui
''' % dict(themes=themes_table, oled=pal(OLED, True, '')),

  # Icônes des deux modes ajoutés (masques, comme les icônes existantes).
  'ui/webui/resources/cr_components/customize_color_scheme_mode/oled_mode.svg':
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"><circle cx="12" cy="12" r="8.4"/></svg>\n',
  'ui/webui/resources/cr_components/customize_color_scheme_mode/night_mode.svg':
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24">'
    '<path d="M13.6 3.7a8.4 8.4 0 1 0 6.7 13.4 7 7 0 0 1-6.7-13.4Z"/>'
    '<path d="M18.5 3.2l.8 1.9 1.9.8-1.9.8-.8 1.9-.8-1.9-1.9-.8 1.9-.8Z"/></svg>\n',
}

CHROME_MIXER = '''
  // Helium Glyphe : cadre, onglets et barre d’outils du thème Glyphe, de la
  // couleur de la page active (si l’option est activée) ou en OLED.
  std::optional<ui::GlyphePrismPalette> glyphe_page;
  if (!key.app_controller && key.app_background_color.has_value() &&
      !ui::IsGlypheRedNight()) {
    glyphe_page = ui::GlyphePageColorPalette(*key.app_background_color);
  }
  if (const ui::GlyphePrismPalette* prism =
          glyphe_page ? &*glyphe_page : ui::GetGlyphePrismPalette(key)) {
    ui::ColorMixer& p = provider->AddMixer();
    for (ui::ColorId id : std::initializer_list<ui::ColorId>{
             ui::kColorFrameActive, ui::kColorFrameInactive, kColorToolbar,
             kColorToolbarTopSeparatorFrameActive,
             kColorToolbarTopSeparatorFrameInactive,
             kColorToolbarContentAreaSeparator,
             kColorToolbarContentAreaSeparatorSolid}) {
      p[id] = {prism->frame};
    }
    for (ui::ColorId id : std::initializer_list<ui::ColorId>{
             kColorTabBackgroundActiveFrameActive,
             kColorTabBackgroundActiveFrameInactive,
             kColorTabBackgroundSelectedFrameActive,
             kColorTabBackgroundSelectedFrameInactive,
             kColorTabBackgroundSelectedHoverFrameActive,
             kColorTabBackgroundSelectedHoverFrameInactive}) {
      p[id] = {prism->tab};
    }
    p[kColorTabBackgroundInactiveFrameActive] = {
        SkColorSetA(prism->tab, SK_AlphaTRANSPARENT)};
    p[kColorTabBackgroundInactiveFrameInactive] = {
        SkColorSetA(prism->tab, SK_AlphaTRANSPARENT)};
    p[kColorTabBackgroundInactiveHoverFrameActive] = {
        SkColorSetA(prism->tab, 0x80)};
    p[kColorTabBackgroundInactiveHoverFrameInactive] = {
        SkColorSetA(prism->tab, 0x80)};
    p[kColorTabForegroundActiveFrameActive] = {prism->text};
    p[kColorTabForegroundActiveFrameInactive] = {prism->text};
    p[kColorTabForegroundInactiveFrameActive] = {prism->muted};
    p[kColorTabForegroundInactiveFrameInactive] = {prism->muted};
    p[kColorTabDividerFrameActive] = {prism->divider};
    p[kColorTabDividerFrameInactive] = {prism->divider};
    p[kColorNewTabButtonForegroundFrameActive] = {prism->muted};
    p[kColorLocationBarBackground] = {prism->field};
    p[kColorLocationBarBackgroundHovered] = {color_utils::AlphaBlend(
        prism->dark ? prism->text : prism->accent, prism->field,
        SkAlpha{0x14})};
    p[kColorOmniboxText] = {prism->text};
    p[kColorOmniboxTextDimmed] = {prism->muted};
    p[kColorToolbarButtonIcon] = {prism->text};
    p[kColorToolbarButtonIconInactive] = {SkColorSetA(prism->subtle, 0x99)};
    p[kColorToolbarText] = {prism->text};
    p[kColorToolbarSeparatorDefault] = {prism->divider};
    p[kColorToolbarExtensionSeparatorEnabled] = {prism->divider};
  }
'''

RED_NIGHT_ANCHOR = '\n  // Bluelium : point d’intégration des thèmes, sans palette nuit rouge.\n'

LC = 'chrome/browser/ui/layout_constants.cc'
CSM = 'ui/webui/resources/cr_components/customize_color_scheme_mode/'
HANDLER = 'chrome/browser/ui/webui/cr_components/customize_color_scheme_mode/'
COLORS = 'chrome/browser/ui/webui/cr_components/theme_color_picker/customize_chrome_colors'
PICKER = 'chrome/browser/ui/webui/cr_components/theme_color_picker/theme_color_picker_handler.cc'
CWV = 'chrome/browser/ui/views/frame/contents_web_view'

# Liste des couleurs dynamiques : remplacée entière par les thèmes Glyphe.
# Texte d'origine figé (lu dans l'arbre, il changeait une fois patché).
OLD_COLORS = (Path(__file__).parent / 'reference/upstream/'
              'customize_chrome_colors.kDynamicCustomizeChromeColors.txt').read_text()
NEW_COLORS = (
    'const decltype(kDynamicCustomizeChromeColors) kDynamicCustomizeChromeColors =\n'
    f'    std::array<DynamicColorInfo, {len(THEMES)}>{{\n'
    '        // Helium Glyphe : seuls les thèmes Glyphe (ui/color/glyphe_prism.cc).\n'
    + ''.join(
        f'        DynamicColorInfo(/*id=*/{20 + i},\n'
        f'                         {rgb(light[8])},\n'
        f'                         {ids},\n'
        '                         ui::mojom::BrowserColorVariant::kTonalSpot),\n'
        for i, (name, ids, light, dark) in enumerate(THEMES))
    + '    };\n\n')

EDITS = [
  # --- Thèmes ----------------------------------------------------------------
  ('ui/color/BUILD.gn', '    "glyphe_red_night.cc",\n',
   '    "glyphe_prism.cc",\n    "glyphe_prism.h",\n    "glyphe_red_night.cc",\n'),
  ('ui/color/color_mixers.cc', '  AddSysColorMixer(provider, key);\n  AddGlypheRedNightMixer(provider, key);\n',
   '  AddSysColorMixer(provider, key);\n  AddGlyphePrismMixer(provider, key);\n  AddGlypheRedNightMixer(provider, key);\n'),
  ('ui/color/color_mixers.cc', '#include "ui/color/glyphe_red_night.h"\n',
   '#include "ui/color/glyphe_prism.h"\n#include "ui/color/glyphe_red_night.h"\n'),
  ('chrome/browser/ui/color/chrome_color_mixers.cc', RED_NIGHT_ANCHOR,
   CHROME_MIXER + RED_NIGHT_ANCHOR),
  ('chrome/browser/ui/color/chrome_color_mixers.cc', '#include "ui/color/glyphe_red_night.h"\n',
   '#include "ui/color/glyphe_prism.h"\n#include "ui/color/glyphe_red_night.h"\n'
   '#include "ui/gfx/color_utils.h"\n\n#include <optional>\n'),

  # Grille de couleurs : thèmes Glyphe seulement, sans la pastille grise.
  (COLORS + '.h', 'extern const std::array<DynamicColorInfo, 13> kDynamicCustomizeChromeColors;\n',
   f'extern const std::array<DynamicColorInfo, {len(THEMES)}> kDynamicCustomizeChromeColors;\n'),
  (COLORS + '.cc', OLD_COLORS, NEW_COLORS),
  (PICKER, '  color->variant = color_info.variant;\n',
   '  color->variant = color_info.variant;\n'
   '  // Helium Glyphe : la pastille montre les vraies couleurs du thème.\n'
   '  if (const ui::GlypheTheme* glyphe = ui::FindGlypheTheme(color_info.color)) {\n'
   '    const ui::GlyphePrismPalette& p = is_dark_mode ? glyphe->dark : glyphe->light;\n'
   '    color->name = glyphe->name;\n'
   '    color->background = p.frame;\n'
   '    color->foreground = p.accent;\n'
   '    color->base = p.tab;\n'
   '  }\n'),
  (PICKER, '#include "chrome/browser/ui/webui/cr_components/theme_color_picker/theme_color_picker_handler.h"\n',
   '#include "chrome/browser/ui/webui/cr_components/theme_color_picker/theme_color_picker_handler.h"\n\n'
   '#include "ui/color/glyphe_prism.h"\n'),
  ('ui/webui/resources/cr_components/theme_color_picker/theme_color_picker.html.ts',
   '  <cr-theme-color id="greyDefaultColor"\n'
   '      .backgroundColor="${this.greyDefaultColor_.background}"\n'
   '      .baseColor="${this.greyDefaultColor_.base}"\n'
   '      .foregroundColor="${this.greyDefaultColor_.foreground}"\n'
   '      title="${this.i18n(\'greyDefaultColorName\')}"\n'
   '      aria-label="${this.i18n(\'greyDefaultColorName\')}" role="radio"\n'
   '      ?checked="${this.isGreyDefaultColorSelected_}"\n'
   '      aria-checked="${this.isGreyDefaultColorSelected_}"\n'
   '      tabindex="${this.tabIndex_(this.isGreyDefaultColorSelected_)}"\n'
   '      @click="${this.onGreyDefaultColorClick_}">\n'
   '  </cr-theme-color>\n',
   '  <!-- Helium Glyphe : pastille grise retirée, Prism est le défaut. -->\n'),

  # Prism par défaut : nouveaux profils, profils restés sur le gris, réinitialisation.
  ('chrome/browser/themes/theme_service.cc',
   '  if (profile_->IsNewProfile() && !UsingPolicyTheme() &&\n'
   '      !profile_->GetPrefs()->HasPrefPath(prefs::kCurrentThemeID) &&\n'
   '      !profile_->GetPrefs()->HasPrefPath(prefs::kGrayscaleThemeEnabled)) {\n'
   '    profile_->GetPrefs()->SetBoolean(prefs::kGrayscaleThemeEnabled, true);\n'
   '  }\n',
   '  // Helium Glyphe : thème Prism par défaut, aussi pour les profils restés\n'
   '  // sur le gris de Helium (la pastille grise n’existe plus).\n'
   '  {\n'
   '    PrefService* glyphe_prefs = profile_->GetPrefs();\n'
   '    const bool glyphe_new_profile =\n'
   '        profile_->IsNewProfile() &&\n'
   '        !glyphe_prefs->HasPrefPath(prefs::kGrayscaleThemeEnabled);\n'
   '    if (!UsingPolicyTheme() &&\n'
   '        !glyphe_prefs->HasPrefPath(prefs::kCurrentThemeID) &&\n'
   '        (glyphe_new_profile ||\n'
   '         glyphe_prefs->GetBoolean(prefs::kGrayscaleThemeEnabled))) {\n'
   '      glyphe_prefs->SetBoolean(prefs::kGrayscaleThemeEnabled, false);\n'
   '      glyphe_prefs->SetInteger(prefs::kUserColor,\n'
   '                               static_cast<int>(ui::kGlyphePrismSeed));\n'
   '      glyphe_prefs->SetInteger(\n'
   '          prefs::kBrowserColorVariant,\n'
   '          static_cast<int>(ui::mojom::BrowserColorVariant::kTonalSpot));\n'
   '    }\n'
   '  }\n'),
  ('chrome/browser/themes/theme_service.cc',
   '  profile_->GetPrefs()->SetBoolean(prefs::kGrayscaleThemeEnabled, true);\n\n'
   '  NotifyThemeChanged();\n',
   '  // Helium Glyphe : la réinitialisation revient au thème Prism.\n'
   '  profile_->GetPrefs()->SetBoolean(prefs::kGrayscaleThemeEnabled, false);\n'
   '  profile_->GetPrefs()->SetInteger(prefs::kUserColor,\n'
   '                                   static_cast<int>(ui::kGlyphePrismSeed));\n'
   '  profile_->GetPrefs()->SetInteger(\n'
   '      prefs::kBrowserColorVariant,\n'
   '      static_cast<int>(ui::mojom::BrowserColorVariant::kTonalSpot));\n\n'
   '  NotifyThemeChanged();\n'),
  ('chrome/browser/themes/theme_service.cc',
   '#include "chrome/browser/themes/theme_service.h"\n',
   '#include "chrome/browser/themes/theme_service.h"\n\n#include "ui/color/glyphe_prism.h"\n'),

  # Prefs OLED et couleur de la page.
  ('chrome/common/pref_names.h',
   'inline constexpr char kGlypheRedNightEnabled[] = "glyphe.red_night.enabled";\n',
   'inline constexpr char kGlypheRedNightEnabled[] = "glyphe.red_night.enabled";\n'
   '// Helium Glyphe : interface en noir pur (mode OLED du panneau Personnaliser).\n'
   'inline constexpr char kGlypheOledEnabled[] = "glyphe.oled.enabled";\n'
   '// Helium Glyphe : la barre du haut prend la couleur de la page active.\n'
   'inline constexpr char kGlypheFollowPageColor[] = "glyphe.follow_page_color";\n'),
  ('chrome/browser/ui/prefs/prefs_tab_helper.cc',
   '  registry->RegisterBooleanPref(prefs::kGlypheRedNightEnabled, false);\n',
   '  registry->RegisterBooleanPref(prefs::kGlypheRedNightEnabled, false);\n'
   '  registry->RegisterBooleanPref(prefs::kGlypheOledEnabled, false);\n'
   '  registry->RegisterBooleanPref(prefs::kGlypheFollowPageColor, false);\n'),

  # Bluelium : OLED garde son effet sur l'interface, le filtre reste local.
  (CWV + '.cc',
   "  // Bluelium : point d'intégration OLED, indépendant du filtre des pages.\n",
   "  // Bluelium : point d'intégration OLED, indépendant du filtre des pages.\n"
   '  if (glyphe_pref_registrar_.prefs()) {\n'
   '    const bool glyphe_oled = glyphe_pref_registrar_.prefs()->GetBoolean(\n'
   '        prefs::kGlypheOledEnabled);\n'
   '    if (ui::IsGlypheOled() != glyphe_oled) {\n'
   '      ui::SetGlypheOled(glyphe_oled);\n'
   '      ui::ColorProviderManager::Get().ResetColorProviderCache();\n'
   '      ui::NativeTheme::GetInstanceForNativeUi()->NotifyOnNativeThemeUpdated();\n'
   '    }\n'
   '  }\n'),
  (CWV + '.cc',
   '    glyphe_pref_registrar_.Add(\n'
   '        prefs::kGlypheRedNightEnabled,\n'
   '        base::BindRepeating(&ContentsWebView::UpdateGlypheRedNight,\n'
   '                            base::Unretained(this)));\n',
   '    glyphe_pref_registrar_.Add(\n'
   '        prefs::kGlypheRedNightEnabled,\n'
   '        base::BindRepeating(&ContentsWebView::UpdateGlypheRedNight,\n'
   '                            base::Unretained(this)));\n'
   '    glyphe_pref_registrar_.Add(\n'
   '        prefs::kGlypheOledEnabled,\n'
   '        base::BindRepeating(&ContentsWebView::UpdateGlypheRedNight,\n'
   '                            base::Unretained(this)));\n'
   '    glyphe_pref_registrar_.Add(\n'
   '        prefs::kGlypheFollowPageColor,\n'
   '        base::BindRepeating(&ContentsWebView::UpdateGlyphePageColor,\n'
   '                            base::Unretained(this)));\n'),
  (CWV + '.cc',
   '  // Bluelium : filtre de lumière chaude appliqué au calque de contenu.\n}\n',
   '  // Bluelium : filtre de lumière chaude appliqué au calque de contenu.\n}\n\n'
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
   '}\n'),
  (CWV + '.cc',
   '  views::WebView::SetWebContents(web_contents);\n  UpdateGlypheRedNight();\n',
   '  views::WebView::SetWebContents(web_contents);\n  UpdateGlypheRedNight();\n'
   '  UpdateGlyphePageColor();\n'),
  (CWV + '.cc',
   '#include "ui/color/glyphe_red_night.h"\n',
   '#include "ui/color/glyphe_prism.h"\n#include "ui/color/glyphe_red_night.h"\n'),
  (CWV + '.h',
   '  void DidGetUserInteraction(const blink::WebInputEvent& event) override;\n#endif\n',
   '  void DidGetUserInteraction(const blink::WebInputEvent& event) override;\n#endif\n'
   '  // Hors du bloc Linux de Helium : aussi utilisés sur macOS.\n'
   '  void DidChangeThemeColor() override;\n'
   '  void OnBackgroundColorChanged() override;\n'),
  (CWV + '.h',
   '  void UpdateGlypheRedNight();\n',
   '  void UpdateGlypheRedNight();\n'
   '  // Helium Glyphe : barre du haut à la couleur de la page active.\n'
   '  void UpdateGlyphePageColor();\n'
   '  std::optional<SkColor> glyphe_page_color_;\n'
   '  bool glyphe_follow_page_ = false;\n'),
  (CWV + '.h',
   '#include "components/prefs/pref_change_registrar.h"\n',
   '#include "components/prefs/pref_change_registrar.h"\n\n#include <optional>\n\n'
   '#include "third_party/skia/include/core/SkColor.h"\n'),

  ('chrome/browser/ui/views/frame/browser_widget.cc',
   '    key.app_background_color = app_controller->GetBackgroundColor();\n  }\n',
   '    key.app_background_color = app_controller->GetBackgroundColor();\n  }\n'
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
   '  }\n'),
  ('chrome/browser/ui/views/frame/browser_widget.cc',
   '#include "chrome/common/chrome_switches.h"\n',
   '#include "chrome/common/chrome_switches.h"\n'
   '#include "chrome/common/pref_names.h"\n'
   '#include "components/prefs/pref_service.h"\n'
   '#include "content/public/browser/web_contents.h"\n'
   '#include "ui/color/glyphe_red_night.h"\n'),

  # Sélecteur de mode : Clair, Sombre, OLED, Nuit, Appareil + interrupteur
  # « Couleur de la page dans la barre ».
  (CSM + 'customize_color_scheme_mode.mojom',
   '  kDark = 2,\n};\n',
   '  kDark = 2,\n  // Helium Glyphe\n  kOled = 3,\n  kRedNight = 4,\n};\n'),
  (CSM + 'customize_color_scheme_mode.mojom',
   '  // Gets the current color mode.\n  InitializeColorSchemeMode();\n};\n',
   '  // Gets the current color mode.\n  InitializeColorSchemeMode();\n'
   '  // Helium Glyphe : la barre du haut suit la couleur de la page.\n'
   '  SetFollowPageColor(bool enabled);\n};\n'),
  (CSM + 'customize_color_scheme_mode.mojom',
   '  // Sets the current color mode.\n  SetColorSchemeMode(ColorSchemeMode colorSchemeMode);\n};\n',
   '  // Sets the current color mode.\n  SetColorSchemeMode(ColorSchemeMode colorSchemeMode);\n'
   '  // Helium Glyphe : état de « Couleur de la page dans la barre ».\n'
   '  SetFollowPageColor(bool enabled);\n};\n'),
  (CSM + 'customize_color_scheme_mode.ts',
   'export interface ColorSchemeModeOption {\n  id: string;\n  value: ColorSchemeMode;\n}\n',
   'export interface ColorSchemeModeOption {\n  id: string;\n  value: ColorSchemeMode;\n'
   '  // Helium Glyphe : libellé direct pour les modes ajoutés.\n  label?: string;\n}\n'),
  (CSM + 'customize_color_scheme_mode.ts',
   "  {\n    id: 'darkMode',\n    value: ColorSchemeMode.kDark,\n  },\n",
   "  {\n    id: 'darkMode',\n    value: ColorSchemeMode.kDark,\n  },\n"
   "  {\n    id: 'oledMode',\n    value: ColorSchemeMode.kOled,\n    label: 'OLED',\n  },\n"
   "  {\n    id: 'nightMode',\n    value: ColorSchemeMode.kRedNight,\n    label: 'Nuit',\n  },\n"),
  (CSM + 'customize_color_scheme_mode.ts',
   "import './segmented_button.js';\n",
   "import '//resources/cr_elements/cr_toggle/cr_toggle.js';\nimport './segmented_button.js';\n"),
  (CSM + 'customize_color_scheme_mode.ts',
   '      colorSchemeModeOptions_: {type: Array, state: true},\n',
   '      colorSchemeModeOptions_: {type: Array, state: true},\n'
   '      followPageColor_: {type: Boolean, state: true},\n'),
  (CSM + 'customize_color_scheme_mode.ts',
   '  private setColorSchemeModeListenerId_: number|null = null;\n',
   '  private setColorSchemeModeListenerId_: number|null = null;\n'
   '  protected accessor followPageColor_: boolean = false;\n'
   '  private setFollowPageColorListenerId_: number|null = null;\n'),
  (CSM + 'customize_color_scheme_mode.ts',
   '    this.browserProxy_.handler.initializeColorSchemeMode();\n',
   '    this.setFollowPageColorListenerId_ =\n'
   '        this.browserProxy_.callbackRouter.setFollowPageColor.addListener(\n'
   '            (enabled: boolean) => {\n'
   '              this.followPageColor_ = enabled;\n'
   '            });\n'
   '    this.browserProxy_.handler.initializeColorSchemeMode();\n'),
  (CSM + 'customize_color_scheme_mode.ts',
   '    this.setColorSchemeModeListenerId_ = null;\n',
   '    this.setColorSchemeModeListenerId_ = null;\n'
   '    if (this.setFollowPageColorListenerId_ !== null) {\n'
   '      this.browserProxy_.callbackRouter.removeListener(\n'
   '          this.setFollowPageColorListenerId_);\n'
   '      this.setFollowPageColorListenerId_ = null;\n'
   '    }\n'),
  (CSM + 'customize_color_scheme_mode.ts',
   '  protected onSelectedChanged_(e: CustomEvent<{value: string}>) {\n',
   '  protected onFollowPageColorChange_(e: CustomEvent<boolean>) {\n'
   '    this.browserProxy_.handler.setFollowPageColor(e.detail);\n'
   '  }\n\n'
   '  protected onSelectedChanged_(e: CustomEvent<{value: string}>) {\n'),
  (CSM + 'customize_color_scheme_mode.html.ts',
   '    <segmented-button-option name="${item.id}" title="${this.i18n(item.id)}">\n'
   '      <div id="${item.id}" class="cr-icon" slot="prefix-icon"></div>\n'
   '      ${this.i18n(item.id)}\n',
   '    <segmented-button-option name="${item.id}"\n'
   '        title="${item.label ?? this.i18n(item.id)}">\n'
   '      <div id="${item.id}" class="cr-icon" slot="prefix-icon"></div>\n'
   '      ${item.label ?? this.i18n(item.id)}\n'),
  (CSM + 'customize_color_scheme_mode.html.ts',
   '</segmented-button>`;\n',
   '</segmented-button>\n'
   '<div id="glypheFollowPage">\n'
   '  <span id="glypheFollowPageLabel">Couleur de la page dans la barre</span>\n'
   '  <cr-toggle ?checked="${this.followPageColor_}"\n'
   '      aria-labelledby="glypheFollowPageLabel"\n'
   '      @change="${this.onFollowPageColorChange_}"></cr-toggle>\n'
   '</div>`;\n'),
  (CSM + 'customize_color_scheme_mode.css',
   '#systemMode {\n  --cr-icon-image: url(chrome://resources/cr_components/customize_color_scheme_mode/system_mode_old.svg);\n}\n',
   '#systemMode {\n  --cr-icon-image: url(chrome://resources/cr_components/customize_color_scheme_mode/system_mode_old.svg);\n}\n\n'
   '#oledMode {\n'
   '  --cr-icon-image: url(chrome://resources/cr_components/customize_color_scheme_mode/oled_mode.svg);\n'
   '}\n\n'
   '#nightMode {\n'
   '  --cr-icon-image: url(chrome://resources/cr_components/customize_color_scheme_mode/night_mode.svg);\n'
   '}\n\n'
   '#glypheFollowPage {\n'
   '  align-items: center;\n'
   '  color: var(--cr-primary-text-color);\n'
   '  display: flex;\n'
   '  font-size: 13px;\n'
   '  gap: 12px;\n'
   '  justify-content: space-between;\n'
   '  margin-top: 12px;\n'
   '}\n'),
  (CSM + 'BUILD.gn', '    "light_mode_old.svg",\n',
   '    "light_mode_old.svg",\n    "night_mode.svg",\n    "oled_mode.svg",\n'),

  (HANDLER + 'customize_color_scheme_mode_handler.h',
   '#include "chrome/browser/themes/theme_service_observer.h"\n',
   '#include "chrome/browser/themes/theme_service_observer.h"\n'
   '#include "components/prefs/pref_change_registrar.h"\n'),
  (HANDLER + 'customize_color_scheme_mode_handler.h',
   '  void InitializeColorSchemeMode() override;\n',
   '  void InitializeColorSchemeMode() override;\n'
   '  void SetFollowPageColor(bool enabled) override;\n'),
  (HANDLER + 'customize_color_scheme_mode_handler.h',
   '  const raw_ptr<ThemeService> theme_service_;\n',
   '  const raw_ptr<ThemeService> theme_service_;\n'
   '  // Helium Glyphe : modes OLED et Nuit, couleur de la page (prefs de profil).\n'
   '  PrefChangeRegistrar glyphe_prefs_;\n'),
  (HANDLER + 'customize_color_scheme_mode_handler.cc',
   '#include "chrome/browser/themes/theme_service_factory.h"\n',
   '#include "chrome/browser/themes/theme_service_factory.h"\n'
   '#include "base/functional/bind.h"\n'
   '#include "chrome/common/pref_names.h"\n'
   '#include "components/prefs/pref_service.h"\n'),
  (HANDLER + 'customize_color_scheme_mode_handler.cc',
   '  theme_service_->AddObserver(this);\n}\n',
   '  theme_service_->AddObserver(this);\n'
   '  glyphe_prefs_.Init(profile->GetPrefs());\n'
   '  for (const char* pref :\n'
   '       {prefs::kGlypheOledEnabled, prefs::kGlypheRedNightEnabled,\n'
   '        prefs::kGlypheFollowPageColor}) {\n'
   '    glyphe_prefs_.Add(\n'
   '        pref, base::BindRepeating(\n'
   '                  &CustomizeColorSchemeModeHandler::UpdateColorSchemeMode,\n'
   '                  base::Unretained(this)));\n'
   '  }\n'
   '}\n\n'
   'void CustomizeColorSchemeModeHandler::SetFollowPageColor(bool enabled) {\n'
   '  glyphe_prefs_.prefs()->SetBoolean(prefs::kGlypheFollowPageColor, enabled);\n'
   '}\n'),
  (HANDLER + 'customize_color_scheme_mode_handler.cc',
   '    customize_color_scheme_mode::mojom::ColorSchemeMode colorMode) {\n'
   '  theme_service_->SetBrowserColorScheme(\n'
   '      static_cast<ThemeService::BrowserColorScheme>(colorMode));\n}\n',
   '    customize_color_scheme_mode::mojom::ColorSchemeMode colorMode) {\n'
   '  using Mode = customize_color_scheme_mode::mojom::ColorSchemeMode;\n'
   '  PrefService* prefs = glyphe_prefs_.prefs();\n'
   '  // Bluelium : Nuit active seulement le filtre de lumière chaude.\n'
   '  if (colorMode == Mode::kRedNight) {\n'
   '    prefs->SetBoolean(prefs::kGlypheRedNightEnabled, true);\n'
   '    return;\n'
   '  }\n'
   '  prefs->SetBoolean(prefs::kGlypheRedNightEnabled, false);\n'
   '  // OLED : mode sombre (pages comprises) et interface en noir pur.\n'
   '  prefs->SetBoolean(prefs::kGlypheOledEnabled, colorMode == Mode::kOled);\n'
   '  theme_service_->SetBrowserColorScheme(\n'
   '      colorMode == Mode::kOled\n'
   '          ? ThemeService::BrowserColorScheme::kDark\n'
   '          : static_cast<ThemeService::BrowserColorScheme>(colorMode));\n'
   '}\n'),
  (HANDLER + 'customize_color_scheme_mode_handler.cc',
   'void CustomizeColorSchemeModeHandler::UpdateColorSchemeMode() {\n'
   '  remote_client_->SetColorSchemeMode(\n',
   'void CustomizeColorSchemeModeHandler::UpdateColorSchemeMode() {\n'
   '  using Mode = customize_color_scheme_mode::mojom::ColorSchemeMode;\n'
   '  remote_client_->SetFollowPageColor(\n'
   '      glyphe_prefs_.prefs()->GetBoolean(prefs::kGlypheFollowPageColor));\n'
   '  if (glyphe_prefs_.prefs()->GetBoolean(prefs::kGlypheRedNightEnabled)) {\n'
   '    remote_client_->SetColorSchemeMode(Mode::kRedNight);\n'
   '    return;\n'
   '  }\n'
   '  if (glyphe_prefs_.prefs()->GetBoolean(prefs::kGlypheOledEnabled)) {\n'
   '    remote_client_->SetColorSchemeMode(Mode::kOled);\n'
   '    return;\n'
   '  }\n'
   '  remote_client_->SetColorSchemeMode(\n'),
  (HANDLER + 'BUILD.gn',
   '    "//chrome/browser/profiles:profile",\n    "//chrome/browser/themes",\n  ]\n',
   '    "//chrome/browser/profiles:profile",\n    "//chrome/browser/themes",\n'
   '    "//chrome/common:constants",\n    "//components/prefs",\n  ]\n'),

  # --- Mise en page de la maquette -------------------------------------------
  ('chrome/browser/ui/views/frame/multi_contents_view.h',
   '  static constexpr int kSplitViewContentInset = 3;\n',
   '  static constexpr int kSplitViewContentInset = 6;  // Glyphe : page en retrait\n'),
  ('chrome/browser/ui/views/helium/frame_corner_radius.cc',
   'int GetGenericFrameRadius() {\n  return 8;\n}\n',
   'int GetGenericFrameRadius() {\n  return 10;  // Glyphe : coins de la page\n}\n'),
  ('chrome/browser/ui/tabs/tab_style.cc',
   'constexpr int kTabWidth = 190;\n', 'constexpr int kTabWidth = 240;  // Glyphe : onglets plus larges\n'),
  ('chrome/browser/ui/tabs/tab_style.cc',
   'constexpr int kSeparatorHeight = 16;\n', 'constexpr int kSeparatorHeight = 14;  // Glyphe\n'),
  (LC, '    case LayoutConstant::kTabHeight:\n      return 31;\n',
   '    case LayoutConstant::kTabHeight:\n      return 30;  // Glyphe\n'),
  (LC, '    case LayoutConstant::kTabPreTitlePadding:\n      return 6;\n',
   '    case LayoutConstant::kTabPreTitlePadding:\n      return 8;  // Glyphe\n'),
  (LC, '    case LayoutConstant::kLocationBarHeight:\n      return touch_ui ? 36 : 28;\n',
   '    case LayoutConstant::kLocationBarHeight:\n      return touch_ui ? 36 : 30;  // Glyphe\n'),
  (LC, '    case LayoutConstant::kToolbarButtonHeight:\n      return touch_ui ? 48 : 28;\n',
   '    case LayoutConstant::kToolbarButtonHeight:\n      return touch_ui ? 48 : 30;  // Glyphe\n'),
  (LC, '      return touch_ui ? kDefaultTouchableIconSize\n                      : kDefaultIconSizeChromeRefresh;\n',
   '      return touch_ui ? kDefaultTouchableIconSize : 18;  // Glyphe\n'),
  (LC, '      return gfx::Insets(touch_ui ? 12 : 4);\n',
   '      return gfx::Insets(touch_ui ? 12 : 6);  // Glyphe : 18 + 2 × 6 = 30\n'),
  (LC, '    case LayoutConstant::kToolbarElementPadding:\n'
       '      return touch_ui ? 0 : GetLayoutConstant(LayoutConstant::kHeliumBasePadding);\n',
   '    case LayoutConstant::kToolbarElementPadding:\n      return touch_ui ? 0 : 2;  // Glyphe\n'),
  (LC, '    case LayoutConstant::kToolbarIconDefaultMargin:\n'
       '      return touch_ui ? 0 : GetLayoutConstant(LayoutConstant::kHeliumBasePadding);\n',
   '    case LayoutConstant::kToolbarIconDefaultMargin:\n      return touch_ui ? 0 : 2;  // Glyphe\n'),
  (LC, '      return gfx::Insets::VH(base, base * 2);\n',
   '      // Glyphe : rangée de 36 px, 1 px au-dessus, 5 px avant la page.\n'
   '      return gfx::Insets::TLBR(base - 2, base - 1, base + 2, base - 1);\n'),
  ('chrome/browser/ui/views/location_bar/location_bar_view.cc',
   'int LocationBarView::ComputeBorderRadius(gfx::Size size) {\n'
   '  return ChromeLayoutProvider::Get()->GetCornerRadiusMetric(\n'
   '      views::Emphasis::kHigh, size);\n}\n',
   'int LocationBarView::ComputeBorderRadius(gfx::Size size) {\n'
   '  // Glyphe : champ d’adresse à coins de 10 px.\n'
   '  return std::min(10, ChromeLayoutProvider::Get()->GetCornerRadiusMetric(\n'
   '                         views::Emphasis::kHigh, size));\n}\n'),

  # --- Texte -----------------------------------------------------------------
  ('ui/gfx/platform_font_skia.cc',
   '#include "third_party/skia/include/core/SkFontMetrics.h"\n',
   '#include "third_party/skia/include/core/SkFontMetrics.h"\n'
   '#include "third_party/skia/include/core/SkFontMgr.h"\n'),
  ('ui/gfx/platform_font_skia.cc',
   '    weight = static_cast<Font::Weight>(font_settings.weight);\n'
   '    params = linux_ui->GetDefaultFontRenderParams();\n',
   '    weight = static_cast<Font::Weight>(font_settings.weight);\n'
   '    params = linux_ui->GetDefaultFontRenderParams();\n'
   '    // Helium Glyphe : Instrument Sans Medium 13 px quand elle est installée.\n'
   '    if (sk_sp<SkTypeface> glyphe = skia::DefaultFontMgr()->matchFamilyStyle(\n'
   '            "Instrument Sans", SkFontStyle(500, SkFontStyle::kNormal_Width,\n'
   '                                           SkFontStyle::kUpright_Slant))) {\n'
   '      SkString glyphe_family;\n'
   '      glyphe->getFamilyName(&glyphe_family);\n'
   '      if (glyphe_family.equals("Instrument Sans")) {\n'
   '        family = "Instrument Sans";\n'
   '        size_pixels = 13;\n'
   '        style = Font::NORMAL;\n'
   '        weight = Font::Weight::MEDIUM;\n'
   '      }\n'
   '    }\n'),
  ('ui/gfx/font_render_params_linux.cc',
   '  // Use the first family from the list if Fontconfig didn\'t suggest a family.\n',
   '  // Helium Glyphe : lissage en niveaux de gris, sans hinting, avec\n'
   '  // positionnement sous-pixel (rendu de la maquette).\n'
   '  if (params.antialiasing) {\n'
   '    params.subpixel_rendering = FontRenderParams::SUBPIXEL_RENDERING_NONE;\n'
   '    params.subpixel_positioning = true;\n'
   '    params.hinting = FontRenderParams::HINTING_NONE;\n'
   '  }\n\n'
   '  // Use the first family from the list if Fontconfig didn\'t suggest a family.\n'),
]
