"""Police des Views Linux, chargée par Skia dans le processus navigateur."""

EDITS = [
    ('chrome/browser/BUILD.gn',
     '    deps += [\n'
     '      ":fullscreen",\n'
     '      ":shell_integration_linux",\n'
     '      "//chrome/browser/lifetime",\n'
     '      "//components/os_crypt/browser:posix_key_provider",\n'
     '      "//third_party/libxml:xml_writer",\n'
     '      "//ui/linux:display_server_utils",\n',
     '    deps += [\n'
     '      ":fullscreen",\n'
     '      ":resources",\n'
     '      ":shell_integration_linux",\n'
     '      "//chrome/browser/lifetime",\n'
     '      "//components/os_crypt/browser:posix_key_provider",\n'
     '      "//third_party/libxml:xml_writer",\n'
     '      "//ui/base",\n'
     '      "//ui/gfx",\n'
     '      "//ui/linux:display_server_utils",\n'),
    ('chrome/browser/BUILD.gn',
     '    "browser_resources.pak",\n  ]\n\n  deps = []\n',
     '    "browser_resources.pak",\n  ]\n\n  deps = []\n'
     '  if (is_linux) {\n'
     '    deps += [ "//third_party/bluelium_instrument_sans:decode_font" ]\n'
     '  }\n'),
    ('chrome/browser/browser_resources.grd',
     '    <includes>\n',
     '''    <includes>
      <if expr="is_linux">
        <include name="IDR_BLUELIUM_INSTRUMENT_SANS" file="${root_gen_dir}/third_party/bluelium_instrument_sans/InstrumentSans.ttf" use_base_dir="false" type="BINDATA" compress="false" />
        <include name="IDR_BLUELIUM_INSTRUMENT_SANS_OFL" file="../../third_party/bluelium_instrument_sans/OFL-InstrumentSans.txt" type="BINDATA" compress="false" />
      </if>
'''),
    ('chrome/browser/chrome_browser_main_linux.h',
     '  // ChromeBrowserMainPartsPosix overrides.\n',
     '  // ChromeBrowserMainPartsPosix overrides.\n'
     '#if BUILDFLAG(IS_LINUX)\n'
     '  int PreEarlyInitialization() override;\n'
     '#endif\n'),
    ('chrome/browser/chrome_browser_main_linux.cc',
     '#include "chrome/browser/ui/ui_features.h"\n',
     '#include "chrome/browser/ui/ui_features.h"\n'
     '#include "chrome/grit/browser_resources.h"\n'
     '#include "ui/base/resource/resource_bundle.h"\n'
     '#include "ui/gfx/platform_font_skia.h"\n'),
    ('chrome/browser/chrome_browser_main_linux.cc',
     'ChromeBrowserMainPartsLinux::~ChromeBrowserMainPartsLinux() = default;\n',
     '''ChromeBrowserMainPartsLinux::~ChromeBrowserMainPartsLinux() = default;

#if BUILDFLAG(IS_LINUX)
int ChromeBrowserMainPartsLinux::PreEarlyInitialization() {
  if (ui::ResourceBundle::HasSharedInstance()) {
    auto& resources = ui::ResourceBundle::GetSharedInstance();
    if (gfx::PlatformFontSkia::LoadBundledInstrumentSans(
            resources.GetRawDataResource(IDR_BLUELIUM_INSTRUMENT_SANS))) {
      resources.ReloadFonts();
    }
  }
  return ChromeBrowserMainPartsPosix::PreEarlyInitialization();
}
#endif
'''),
    ('ui/gfx/platform_font_skia.h',
     '#include <string>\n',
     '#include <string>\n#include <string_view>\n'),
    ('ui/gfx/platform_font_skia.h',
     '  // Initializes the default PlatformFont.\n',
     '''#if BUILDFLAG(IS_LINUX)
  // Called during browser startup, before initializing the UI toolkit.
  static bool LoadBundledInstrumentSans(std::string_view font_data);
  static sk_sp<SkTypeface> MatchBundledInstrumentSans(std::string_view family,
                                                      Font::Weight weight);
#endif

  // Initializes the default PlatformFont.
'''),
    ('ui/gfx/platform_font_skia.cc',
     '#include <algorithm>\n',
     '#include <algorithm>\n#include <array>\n#include <atomic>\n'),
    ('ui/gfx/platform_font_skia.cc',
     '#include "third_party/skia/include/core/SkFont.h"\n',
     '#include "third_party/skia/include/core/SkData.h"\n'
     '#include "third_party/skia/include/core/SkFont.h"\n'
     '#include "third_party/skia/include/core/SkFontArguments.h"\n'),
    ('ui/gfx/platform_font_skia.cc',
     'constexpr SkGlyphID kUnsupportedGlyph = 0;\n',
     '''constexpr SkGlyphID kUnsupportedGlyph = 0;

#if BUILDFLAG(IS_LINUX)
constexpr char kInstrumentSansFamily[] = "Instrument Sans";
constexpr int kInstrumentSansSize = 13;
// The bundled variable font has an upright weight axis from 400 to 700.
using InstrumentSansFaces = std::array<sk_sp<SkTypeface>, 4>;
constinit std::atomic<const InstrumentSansFaces*> g_instrument_sans_faces{
    nullptr};
#endif
'''),
    ('ui/gfx/platform_font_skia.cc',
     '  TRACE_EVENT0("fonts", "gfx::CreateSkTypeface");\n',
     '''  TRACE_EVENT0("fonts", "gfx::CreateSkTypeface");

#if BUILDFLAG(IS_LINUX)
  if (auto typeface =
          PlatformFontSkia::MatchBundledInstrumentSans(*family, weight)) {
    *out_success = true;
    return typeface;
  }
#endif
'''),
    ('ui/gfx/platform_font_skia.cc',
     '''// static
void PlatformFontSkia::EnsuresDefaultFontIsInitialized() {
''',
     '''#if BUILDFLAG(IS_LINUX)
// static
bool PlatformFontSkia::LoadBundledInstrumentSans(std::string_view font_data) {
  if (g_instrument_sans_faces.load(std::memory_order_acquire)) {
    return true;
  }
  if (font_data.empty()) {
    return false;
  }

  auto typeface = skia::DefaultFontMgr()->makeFromData(
      SkData::MakeWithCopy(font_data.data(), font_data.size()));
  if (!typeface) {
    return false;
  }

  InstrumentSansFaces faces;
  faces.front() = std::move(typeface);
  using Coordinate = SkFontArguments::VariationPosition::Coordinate;
  for (size_t i = 1; i < faces.size(); ++i) {
    const Coordinate coordinate{Coordinate::wght, 400.0f + 100.0f * i};
    SkFontArguments arguments;
    arguments.setVariationDesignPosition({&coordinate, 1});
    faces[i] = faces.front()->makeClone(arguments);
    if (!faces[i]) {
      return false;
    }
  }

  static const base::NoDestructor<InstrumentSansFaces> bundled_faces(
      std::move(faces));
  g_instrument_sans_faces.store(bundled_faces.get(), std::memory_order_release);
  ReloadDefaultFont();
  return true;
}

// static
sk_sp<SkTypeface> PlatformFontSkia::MatchBundledInstrumentSans(
    std::string_view family,
    Font::Weight weight) {
  if (family != kInstrumentSansFamily) {
    return nullptr;
  }

  const auto* faces = g_instrument_sans_faces.load(std::memory_order_acquire);
  if (!faces) {
    return nullptr;
  }

  const int index =
      (std::clamp(static_cast<int>(weight), 400, 700) - 400) / 100;
  return (*faces)[index];
}
#endif  // BUILDFLAG(IS_LINUX)

// static
void PlatformFontSkia::EnsuresDefaultFontIsInitialized() {
'''),
    ('ui/gfx/platform_font_skia.cc',
     '''  bool success = false;
  sk_sp<SkTypeface> typeface =
      CreateSkTypeface(style & Font::ITALIC, weight, &family, &success);
''',
     '''#if BUILDFLAG(IS_LINUX)
  if (auto typeface = MatchBundledInstrumentSans(kInstrumentSansFamily,
                                                 Font::Weight::MEDIUM)) {
    GetDefaultFont() = new PlatformFontSkia(
        std::move(typeface), kInstrumentSansFamily, kInstrumentSansSize,
        Font::NORMAL, Font::Weight::MEDIUM, params);
    return;
  }
#endif

  bool success = false;
  sk_sp<SkTypeface> typeface =
      CreateSkTypeface(style & Font::ITALIC, weight, &family, &success);
'''),
    ('ui/gfx/render_text_harfbuzz.cc',
     '#if BUILDFLAG(IS_ANDROID)\n#include "base/i18n/android_locale.h"\n',
     '#if BUILDFLAG(IS_LINUX)\n'
     '#include "ui/gfx/platform_font_skia.h"\n'
     '#endif\n\n'
     '#if BUILDFLAG(IS_ANDROID)\n#include "base/i18n/android_locale.h"\n'),
    ('ui/gfx/render_text_harfbuzz.cc',
     '  return SkMakeTypefaceFromCTFont(font_with_style.GetCTFont());\n#else\n',
     '''  return SkMakeTypefaceFromCTFont(font_with_style.GetCTFont());
#else
#if BUILDFLAG(IS_LINUX)
  if (auto typeface = PlatformFontSkia::MatchBundledInstrumentSans(
          font.GetFontName(), weight)) {
    return typeface;
  }
#endif
'''),
]
