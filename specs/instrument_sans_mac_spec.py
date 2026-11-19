"""Police des Views macOS, enregistrée auprès de CoreText au démarrage."""

EDITS = [
    ('chrome/BUILD.gn',
     '''      "browser/ui/cocoa/applescript/scripting.sdef",
    ]
    outputs = [ "{{bundle_resources_dir}}/{{source_file_part}}" ]
    public_deps = [
      ":chrome_app_icon",
      ":chrome_app_strings",
      ":chrome_asset_catalog",
      "//components/policy:chrome_manifest_bundle",
''',
     '''      "browser/ui/cocoa/applescript/scripting.sdef",
      "$root_gen_dir/third_party/bluelium_instrument_sans/InstrumentSans.ttf",
      "//third_party/bluelium_instrument_sans/OFL-InstrumentSans.txt",
    ]
    outputs = [ "{{bundle_resources_dir}}/{{source_file_part}}" ]
    public_deps = [
      ":chrome_app_icon",
      ":chrome_app_strings",
      ":chrome_asset_catalog",
      "//components/policy:chrome_manifest_bundle",
      "//third_party/bluelium_instrument_sans:decode_font",
'''),
    ('chrome/browser/BUILD.gn',
     '      "//services/video_capture/public/mojom:constants",\n'
     '      "//third_party/crashpad/crashpad/client",\n',
     '      "//services/video_capture/public/mojom:constants",\n'
     '      "//third_party/crashpad/crashpad/client",\n'
     '      "//ui/gfx",\n'),
    ('chrome/browser/chrome_browser_main_mac.mm',
     '#include "ui/base/resource/resource_handle.h"\n',
     '#include "ui/base/resource/resource_handle.h"\n'
     '#include "ui/gfx/platform_font_mac.h"\n'),
    ('chrome/browser/chrome_browser_main_mac.mm',
     'int ChromeBrowserMainPartsMac::PreEarlyInitialization() {\n',
     '''int ChromeBrowserMainPartsMac::PreEarlyInitialization() {
  if (gfx::PlatformFontMac::RegisterBundledInstrumentSans() &&
      ui::ResourceBundle::HasSharedInstance()) {
    ui::ResourceBundle::GetSharedInstance().ReloadFonts();
  }

'''),
    ('ui/gfx/platform_font_mac.h',
     '  // Overridden from PlatformFont:\n',
     '''  // Registers the app resource for the browser process only.
  static bool RegisterBundledInstrumentSans();
  static PlatformFont* CreateBundledDefaultFont();

  // Overridden from PlatformFont:
'''),
    ('ui/gfx/platform_font_mac.mm',
     '#include <cmath>\n',
     '#include <atomic>\n#include <cmath>\n'),
    ('ui/gfx/platform_font_mac.mm',
     '#include "base/apple/bridging.h"\n',
     '#include "base/apple/bridging.h"\n'
     '#include "base/apple/bundle_locations.h"\n'),
    ('ui/gfx/platform_font_mac.mm',
     'namespace {\n\n// Returns the font style',
     '''namespace {

constexpr char kInstrumentSansFamily[] = "Instrument Sans";
constinit std::atomic_bool g_instrument_sans_registered{false};

base::apple::ScopedCFTypeRef<CTFontRef>
CreateBundledInstrumentSans(int size, int style, Weight weight) {
  if (!g_instrument_sans_registered.load(std::memory_order_acquire) ||
      (style & Font::ITALIC)) {
    return {};
  }

  NSFont* regular = [NSFont fontWithName:@"InstrumentSans-Regular" size:size];
  if (![regular.familyName isEqualToString:@"Instrument Sans"]) {
    return {};
  }

  base::apple::ScopedCFTypeRef<CTFontDescriptorRef> descriptor(
      CTFontCopyFontDescriptor(base::apple::NSToCFPtrCast(regular)));
  constexpr uint32_t kWeightAxis = 0x77676874;  // OpenType 'wght'.
  base::apple::ScopedCFTypeRef<CTFontDescriptorRef> variation(
      CTFontDescriptorCreateCopyWithVariation(
          descriptor.get(), base::apple::NSToCFPtrCast(@(kWeightAxis)),
          weight == Weight::INVALID ? 400 : static_cast<int>(weight)));
  return base::apple::ScopedCFTypeRef<CTFontRef>(
      CTFontCreateWithFontDescriptor(variation.get(), size, nullptr));
}

// Returns the font style'''),
    ('ui/gfx/platform_font_mac.mm',
     '''// static
base::apple::ScopedCFTypeRef<CTFontRef> PlatformFontMac::CTFontWithSpec(
    FontSpec font_spec) {
''',
     '''// static
bool PlatformFontMac::RegisterBundledInstrumentSans() {
  if (g_instrument_sans_registered.load(std::memory_order_acquire)) {
    return true;
  }

  NSURL* url = [base::apple::OuterBundle() URLForResource:@"InstrumentSans"
                                            withExtension:@"ttf"];
  if (!url) {
    return false;
  }

  const bool registered = CTFontManagerRegisterFontsForURL(
      base::apple::NSToCFPtrCast(url), kCTFontManagerScopeProcess, nullptr);
  g_instrument_sans_registered.store(registered, std::memory_order_release);
  return registered;
}

// static
PlatformFont* PlatformFontMac::CreateBundledDefaultFont() {
  constexpr int kSize = PlatformFont::kDefaultBaseFontSize;
  constexpr Weight kWeight = Weight::MEDIUM;
  auto font = CreateBundledInstrumentSans(kSize, Font::NORMAL, kWeight);
  if (!font) {
    return nullptr;
  }

  return new PlatformFontMac(
      font.get(), std::nullopt,
      {kInstrumentSansFamily, kSize, Font::NORMAL, kWeight});
}

// static
base::apple::ScopedCFTypeRef<CTFontRef> PlatformFontMac::CTFontWithSpec(
    FontSpec font_spec) {
  if (font_spec.name == kInstrumentSansFamily) {
    if (auto font = CreateBundledInstrumentSans(font_spec.size, font_spec.style,
                                                font_spec.weight)) {
      return font;
    }
  }

'''),
    ('ui/gfx/platform_font_mac.mm',
     '''PlatformFont* PlatformFont::CreateDefault() {
  return new PlatformFontMac(PlatformFontMac::SystemFontType::kGeneral);
}''',
     '''PlatformFont* PlatformFont::CreateDefault() {
  if (PlatformFont* font = PlatformFontMac::CreateBundledDefaultFont()) {
    return font;
  }
  return new PlatformFontMac(PlatformFontMac::SystemFontType::kGeneral);
}'''),
]
