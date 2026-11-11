# Helium Glyphe — palette « nuit rouge » de l'interface (noir pur, rouge seul).
# Les jetons système (kColorSys*) sont réécrits juste après le mixer système,
# donc toutes les couleurs dérivées suivent ; un dernier mixer Chrome force
# le cadre, les onglets et la barre d'outils. Suit la pref glyphe.red_night.

SYS = ('kColorSysPrimary kColorSysOnPrimary kColorSysPrimaryContainer kColorSysOnPrimaryContainer '
       'kColorSysSecondary kColorSysOnSecondary kColorSysSecondaryContainer kColorSysOnSecondaryContainer '
       'kColorSysTertiary kColorSysOnTertiary kColorSysTertiaryContainer kColorSysOnTertiaryContainer '
       'kColorSysError kColorSysOnError kColorSysErrorContainer kColorSysOnErrorContainer kColorSysOnSurface '
       'kColorSysOnSurfaceVariant kColorSysOutline kColorSysSurfaceVariant kColorSysBlack kColorSysWhite '
       'kColorSysInversePrimary kColorSysInverseOnSurface kColorSysInverseSurface kColorSysInverseSurfacePrimary '
       'kColorSysSurface kColorSysSurface1 kColorSysSurface2 kColorSysSurface3 kColorSysSurface4 kColorSysSurface5 '
       'kColorSysSurfaceNumberedForeground kColorSysSurfaceContainerLowest kColorSysSurfaceContainerLow '
       'kColorSysSurfaceContainer kColorSysSurfaceContainerHigh kColorSysSurfaceContainerHighest '
       'kColorSysOnSurfaceSecondary kColorSysOnSurfaceSubtle kColorSysOnSurfacePrimary '
       'kColorSysOnSurfacePrimaryInactive kColorSysTonalContainer kColorSysOnTonalContainer '
       'kColorSysBaseTonalContainer kColorSysOnBaseTonalContainer kColorSysTonalOutline kColorSysNeutralOutline '
       'kColorSysNeutralContainer kColorSysDivider kColorSysBase kColorSysBaseContainer '
       'kColorSysBaseContainerElevated kColorSysHeader kColorSysHeaderInactive kColorSysHeaderContainer '
       'kColorSysHeaderContainerInactive kColorSysOnHeaderDivider kColorSysOnHeaderDividerInactive '
       'kColorSysOnHeaderPrimary kColorSysOnHeaderPrimaryInactive kColorSysStateHoverOnProminent '
       'kColorSysStateHoverOnSubtle kColorSysStateRippleNeutralOnProminent kColorSysStateRippleNeutralOnSubtle '
       'kColorSysStateRipplePrimary kColorSysStateFocusRing kColorSysStateFocusRingInverse '
       'kColorSysStateTextHighlight kColorSysStateOnTextHighlight kColorSysStateFocusHighlight '
       'kColorSysStateDisabled kColorSysStateDisabledContainer kColorSysStateHoverDimBlendProtection '
       'kColorSysStateHoverBrightBlendProtection kColorSysStateInactiveRing kColorSysStateScrim '
       'kColorSysStateOnHeaderHover kColorSysStateHeaderHover kColorSysStateHeaderHoverInactive '
       'kColorSysStateHeaderSelect kColorSysShadow kColorSysGradientPrimary kColorSysGradientTertiary '
       'kColorSysOmniboxContainer kColorSysSurfaceSection kColorSysBaseContainerOnSurface kColorSysStateHover '
       'kColorSysStateFocus kColorSysStatePressed').split()

BLACK_TEXT = {'kColorSysOnPrimary', 'kColorSysOnSecondary', 'kColorSysOnTertiary', 'kColorSysOnError',
              'kColorSysStateOnTextHighlight', 'kColorSysInverseOnSurface'}


def role(n):
  if n in BLACK_TEXT:
    return 'kBlack'
  if n in ('kColorSysOnHeaderDivider', 'kColorSysOnHeaderDividerInactive', 'kColorSysDivider'):
    return 'Red(0x52)'
  if n in ('kColorSysOutline', 'kColorSysTonalOutline', 'kColorSysNeutralOutline', 'kColorSysStateInactiveRing'):
    return 'Red(0x94)'
  if n == 'kColorSysStateScrim':
    return 'SkColorSetA(SK_ColorBLACK, 0xcc)'
  if n == 'kColorSysStateDisabled':
    return 'Red(0x61)'
  if n in ('kColorSysStateDisabledContainer', 'kColorSysSurfaceNumberedForeground'):
    return 'Red(0x1f)'
  if n.startswith('kColorSysState') and ('Hover' in n or 'Ripple' in n or 'Pressed' in n
                                         or 'Select' in n or n.endswith('Focus') or 'FocusHighlight' in n):
    return 'Red(0x29)'
  if n.endswith('Container') and any(k in n for k in ('Primary', 'Secondary', 'Tertiary', 'Error', 'Tonal', 'Neutral')) \
      and not n.startswith('kColorSysOn'):
    return 'Red(0x29)'
  if n.startswith('kColorSysOn') or n.startswith('kColorSysInverse'):
    return 'kRed'
  if n in ('kColorSysPrimary', 'kColorSysSecondary', 'kColorSysTertiary', 'kColorSysError', 'kColorSysWhite',
           'kColorSysStateFocusRing', 'kColorSysStateFocusRingInverse', 'kColorSysStateTextHighlight',
           'kColorSysGradientPrimary', 'kColorSysGradientTertiary'):
    return 'kRed'
  return 'kBlack'  # surfaces, base, header, omnibox, ombres


lines = '\n'.join(f'  mixer[{n}] = {{{role(n)}}};' for n in SYS)

NEW_FILES = {
  'ui/color/glyphe_red_night.h': '''// Helium Glyphe — palette « nuit rouge ».
#ifndef UI_COLOR_GLYPHE_RED_NIGHT_H_
#define UI_COLOR_GLYPHE_RED_NIGHT_H_

#include "base/component_export.h"

namespace ui {

class ColorProvider;
struct ColorProviderKey;

COMPONENT_EXPORT(COLOR) void SetGlypheRedNight(bool enabled);
COMPONENT_EXPORT(COLOR) bool IsGlypheRedNight();
COMPONENT_EXPORT(COLOR) SkColor GlypheRedNightColor();

// Réécrit les jetons système quand la palette est active.
void AddGlypheRedNightMixer(ColorProvider* provider,
                            const ColorProviderKey& key);

}  // namespace ui

#endif  // UI_COLOR_GLYPHE_RED_NIGHT_H_
''',
  'ui/color/glyphe_red_night.cc': '''// Helium Glyphe — palette « nuit rouge ».
#include "ui/color/glyphe_red_night.h"

#include <atomic>

#include "third_party/skia/include/core/SkColor.h"
#include "ui/color/color_id.h"
#include "ui/color/color_mixer.h"
#include "ui/color/color_provider.h"
#include "ui/color/color_provider_key.h"
#include "ui/color/color_recipe.h"

namespace ui {

namespace {

std::atomic<bool> g_red_night{false};

constexpr SkColor kRed = SkColorSetRGB(217, 68, 51);
constexpr SkColor kBlack = SK_ColorBLACK;

constexpr SkColor Red(SkAlpha alpha) {
  return SkColorSetA(kRed, alpha);
}

}  // namespace

void SetGlypheRedNight(bool enabled) {
  g_red_night.store(enabled);
}

bool IsGlypheRedNight() {
  return g_red_night.load();
}

SkColor GlypheRedNightColor() {
  return kRed;
}

void AddGlypheRedNightMixer(ColorProvider* provider,
                            const ColorProviderKey& key) {
  if (!IsGlypheRedNight()) {
    return;
  }
  ColorMixer& mixer = provider->AddMixer();
%s
}

}  // namespace ui
''' % lines,
}

EDITS = [
  ('ui/color/glyphe_red_night.h', '#include "base/component_export.h"\n',
   '#include "base/component_export.h"\n#include "third_party/skia/include/core/SkColor.h"\n'),
]
# (l'édition ci-dessus s'applique après la création du fichier : on l'intègre directement)
NEW_FILES['ui/color/glyphe_red_night.h'] = NEW_FILES['ui/color/glyphe_red_night.h'].replace(
    '#include "base/component_export.h"\n',
    '#include "base/component_export.h"\n#include "third_party/skia/include/core/SkColor.h"\n')

EDITS = [
  ('ui/color/BUILD.gn', '    "sys_color_mixer.cc",\n',
   '    "sys_color_mixer.cc",\n    "glyphe_red_night.cc",\n    "glyphe_red_night.h",\n'),

  ('ui/color/color_mixers.cc', '  AddSysColorMixer(provider, key);\n',
   '  AddSysColorMixer(provider, key);\n  AddGlypheRedNightMixer(provider, key);\n'),
  ('ui/color/color_mixers.cc', '#include "ui/color/sys_color_mixer.h"\n',
   '#include "ui/color/glyphe_red_night.h"\n#include "ui/color/sys_color_mixer.h"\n'),

  ('chrome/browser/ui/color/chrome_color_mixers.cc',
   '  if (key.custom_theme) {\n    key.custom_theme->AddColorMixers(provider, key);\n  }\n',
   '  if (key.custom_theme) {\n    key.custom_theme->AddColorMixers(provider, key);\n  }\n\n'
   '  // Helium Glyphe : cadre, onglets et barre d’outils en nuit rouge.\n'
   '  if (ui::IsGlypheRedNight()) {\n'
   '    const SkColor red = ui::GlypheRedNightColor();\n'
   '    ui::ColorMixer& glyphe = provider->AddMixer();\n'
   '    for (ui::ColorId id : std::initializer_list<ui::ColorId>{\n'
   '             ui::kColorFrameActive, ui::kColorFrameInactive,\n'
   '                           kColorToolbar,\n'
   '                           kColorTabBackgroundInactiveFrameActive,\n'
   '                           kColorLocationBarBackground}) {\n'
   '      glyphe[id] = {SK_ColorBLACK};\n'
   '    }\n'
   '    glyphe[kColorTabBackgroundActiveFrameActive] = {red};\n'
   '    glyphe[kColorTabBackgroundActiveFrameInactive] = {red};\n'
   '    glyphe[kColorTabForegroundActiveFrameActive] = {SK_ColorBLACK};\n'
   '    for (ui::ColorId id : std::initializer_list<ui::ColorId>{\n'
   '             kColorTabForegroundInactiveFrameActive,\n'
   '                           kColorToolbarButtonIcon, kColorToolbarText,\n'
   '                           kColorOmniboxText,\n'
   '                           kColorNewTabButtonForegroundFrameActive}) {\n'
   '      glyphe[id] = {red};\n'
   '    }\n'
   '    glyphe[kColorTabDividerFrameActive] = {SkColorSetA(red, 0x52)};\n'
   '  }\n'),
  ('chrome/browser/ui/color/chrome_color_mixers.cc',
   '#include "chrome/browser/ui/color/chrome_color_mixers.h"\n',
   '#include "chrome/browser/ui/color/chrome_color_mixers.h"\n\n'
   '#include <initializer_list>\n\n#include "ui/color/color_mixer.h"\n#include "ui/color/color_provider.h"\n#include "ui/color/color_recipe.h"\n#include "ui/color/glyphe_red_night.h"\n'),

  ('chrome/browser/ui/views/frame/contents_web_view.cc',
   'void ContentsWebView::UpdateGlypheRedNight() {\n#if defined(USE_AURA)\n',
   'void ContentsWebView::UpdateGlypheRedNight() {\n'
   '  // Palette de l’interface : globale, rafraîchie seulement si elle change.\n'
   '  if (glyphe_pref_registrar_.prefs()) {\n'
   '    const bool glyphe_on = glyphe_pref_registrar_.prefs()->GetBoolean(\n'
   '        prefs::kGlypheRedNightEnabled);\n'
   '    if (ui::IsGlypheRedNight() != glyphe_on) {\n'
   '      ui::SetGlypheRedNight(glyphe_on);\n'
   '      ui::ColorProviderManager::Get().ResetColorProviderCache();\n'
   '      ui::NativeTheme::GetInstanceForNativeUi()->NotifyOnNativeThemeUpdated();\n'
   '    }\n'
   '  }\n'
   '#if defined(USE_AURA)\n'),
  ('chrome/browser/ui/views/frame/contents_web_view.cc',
   '#include "ui/compositor/layer.h"\n',
   '#include "ui/color/color_provider_manager.h"\n#include "ui/color/glyphe_red_night.h"\n'
   '#include "ui/compositor/layer.h"\n#include "ui/native_theme/native_theme.h"\n'),
]
