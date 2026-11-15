"""Bluelium : PDF.js Mozilla dans l'extension PDF intégrée (macOS et Linux).

La distribution est téléchargée et vérifiée par downloads.ini avant la série.
Les fichiers voisins sont des sources maintenables, injectées via NEW_FILES.
L'aperçu d'impression continue à utiliser son lecteur Chromium indépendant.
"""
import base64
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PARTS = HERE / 'pdfjs'
API = 'chrome/browser/extensions/api/pdf_viewer_private/'
NEW_FILES = {
    'third_party/pdfjs/files.txt': (PARTS / 'files.txt').read_text(),
    'third_party/pdfjs/BUILD.gn': (PARTS / 'BUILD.gn').read_text(),
    'third_party/pdfjs/generate_file_list.py': (PARTS / 'generate_file_list.py').read_text(),
    'third_party/pdfjs/web/bluelium.mjs': (PARTS / 'bluelium.mjs').read_text(),
    'third_party/pdfjs/web/bluelium.css': (
        '@font-face { font-family: "Instrument Sans"; font-style: normal; '
        'font-weight: 100 900; font-display: swap; src: url(data:font/ttf;base64,'
        + base64.b64encode((ROOT / 'assets/InstrumentSans.ttf').read_bytes()).decode()
        + ') format("truetype"); }\n' + (PARTS / 'bluelium.css').read_text()),
    'third_party/pdfjs/web/OFL-InstrumentSans.txt': (ROOT / 'assets/OFL-InstrumentSans.txt').read_text(),
    'third_party/pdfjs/README.chromium': '''Name: PDF.js
Short Name: pdfjs
URL: https://github.com/mozilla/pdf.js
Version: 6.5.438
License: Apache-2.0
License File: LICENSE
Shipped: yes
Security Critical: yes

Description:
Mozilla PDF reader, bundled offline in the built-in PDF MIME handler.

Local Modifications:
Bluelium stream bridge, browser palette and Instrument Sans (SIL OFL 1.1).
The stock viewer entry point loads only the browser-owned intercepted stream.
See specs/pdfjs_spec.py and specs/pdfjs/ in the Bluelium source repository.
''',
}
for name in ('bluelium_pdf_stream.h', 'bluelium_pdf_stream.cc'):
    NEW_FILES[API + name] = (PARTS / name).read_text()

EDITS = [
    # Aucun effet sur les liens ou navigations PDF : uniquement les téléchargements.
    ('chrome/browser/download/download_prefs.cc',
     '  registry->RegisterBooleanPref(prefs::kOpenPdfDownloadInSystemReader, false);',
     '  // Bluelium : les téléchargements PDF utilisent le lecteur du système.\n'
     '  registry->RegisterBooleanPref(prefs::kOpenPdfDownloadInSystemReader, true);'),
    ('chrome/browser/download/download_prefs_unittest.cc',
     'TEST(DownloadPrefsTest, Pdf) {\n'
     '  const base::FilePath kPdfFile(FILE_PATH_LITERAL("abcd.pdf"));\n'
     '  const GURL kURL("http://basic.com");\n\n'
     '  content::BrowserTaskEnvironment task_environment;\n'
     '  TestingProfile profile;\n'
     '  DownloadPrefs prefs(&profile);',
     'TEST(DownloadPrefsTest, Pdf) {\n'
     '  const base::FilePath kPdfFile(FILE_PATH_LITERAL("abcd.pdf"));\n'
     '  const GURL kURL("http://basic.com");\n\n'
     '  content::BrowserTaskEnvironment task_environment;\n'
     '  TestingProfile profile;\n'
     '  DownloadPrefs prefs(&profile);\n'
     '#if BUILDFLAG(IS_WIN) || BUILDFLAG(IS_LINUX) || BUILDFLAG(IS_MAC)\n'
     '  // Bluelium : lecteur systeme par defaut, choix utilisateur reversible.\n'
     '  EXPECT_TRUE(prefs.ShouldOpenPdfInSystemReader());\n'
     '  prefs.SetShouldOpenPdfInSystemReader(false);\n'
     '#endif'),
    ('third_party/pdfjs/web/viewer.html',
     '    <link rel="stylesheet" href="viewer.css" />',
     '    <link rel="stylesheet" href="viewer.css" />\n'
     '    <!-- Bluelium : palette du navigateur et Instrument Sans. -->\n'
     '    <link rel="stylesheet" href="bluelium.css" />'),
    ('third_party/pdfjs/web/viewer.html',
     "style-src 'self';", "style-src 'self' 'unsafe-inline';"),
    ('third_party/pdfjs/web/viewer.mjs',
     '  PDFViewerApplication.run(config);',
     '  // Bluelium : flux natif, jamais de chargement via ?file=.\n'
     '  import("./bluelium.mjs").then(({ start }) =>\n'
     '    start(PDFViewerApplication, AppOptions, config));'),
    ('third_party/pdfjs/web/viewer.mjs',
     '    parent.document.dispatchEvent(event);',
     '    // Bluelium : le document hote a une origine distincte.\n'
     '    document.dispatchEvent(event);'),
    # Ne laisser aucun paramètre ?file= relancer un chargement arbitraire.
    ('third_party/pdfjs/web/viewer.mjs',
     '    file = params.get("file") ?? AppOptions.get("defaultUrl");',
     '    file = ""; // Bluelium : ouvert explicitement par le pont de flux.'),
    ('chrome/browser/resources/pdf/manifest.json',
     '  "mime_types_handler": "index.html"',
     '  "mime_types_handler": "pdfjs/web/viewer.html"'),
    ('chrome/browser/resources/pdf/manifest.json',
     '"script-src \'self\' blob: filesystem: chrome://resources chrome://webui-test; object-src * blob: externalfile: file: filesystem: data:"',
     '"script-src \'self\' \'wasm-unsafe-eval\' blob: filesystem: chrome://resources chrome://webui-test; '
     'object-src * blob: externalfile: file: filesystem: data:; connect-src \'self\' blob: data:; '
     'worker-src \'self\' blob:; style-src \'self\' \'unsafe-inline\'; font-src \'self\' data:"'),
    # Ressources distinctes pour ne pas augmenter la plage GRIT du lecteur natif.
    ('tools/gritsettings/resource_ids.spec',
     '  "<(SHARED_INTERMEDIATE_DIR)/THIS_IS_A_PLACEHOLDER.grd": {',
     '  "<(SHARED_INTERMEDIATE_DIR)/third_party/pdfjs/pdfjs_resources.grd": {\n'
     '    "META": {"sizes": {"includes": [800]}},\n'
     '    "includes": [10160],\n'
     '  },\n\n  "<(SHARED_INTERMEDIATE_DIR)/THIS_IS_A_PLACEHOLDER.grd": {'),
    ('chrome/chrome_paks.gni',
     '      "$root_gen_dir/third_party/shimmer/resources/shimmer_resources.pak",',
     '      "$root_gen_dir/third_party/shimmer/resources/shimmer_resources.pak",\n'
     '      "$root_gen_dir/third_party/pdfjs/resources/pdfjs_resources.pak",'),
    ('chrome/chrome_paks.gni',
     '      "//third_party/shimmer",',
     '      "//third_party/shimmer",\n      "//third_party/pdfjs",'),
    ('chrome/browser/pdf/BUILD.gn',
     '    "//chrome/browser/resources/pdf:resources",',
     '    "//chrome/browser/resources/pdf:resources",\n    "//third_party/pdfjs",'),
    ('chrome/browser/pdf/pdf_extension_util.cc',
     '#include "chrome/grit/pdf_resources_map.h"',
     '#include "chrome/grit/pdf_resources_map.h"\n'
     '#include "third_party/pdfjs/resources/grit/pdfjs_resources_map.h"'),
    ('chrome/browser/pdf/pdf_extension_util.cc',
     '    resources.push_back(resource);\n  }\n  return resources;',
     '    resources.push_back(resource);\n  }\n'
     '  // Bluelium : seulement le lecteur interactif, pas chrome://print.\n'
     '  if (context == PdfViewerContext::kPdfViewer) {\n'
     '    for (const auto& resource : kPdfjsResources) {\n'
     '      resources.push_back(resource);\n    }\n  }\n  return resources;'),
    (API + 'BUILD.gn',
     '    "pdf_viewer_private_api.cc",',
     '    "bluelium_pdf_stream.cc",\n    "bluelium_pdf_stream.h",\n'
     '    "pdf_viewer_private_api.cc",'),
    (API + 'BUILD.gn',
     '    "//pdf:features",\n    "//url",',
     '    "//pdf:features",\n'
     '    "//mojo/public/cpp/bindings",\n'
     '    "//mojo/public/cpp/system",\n'
     '    "//services/network/public/cpp",\n'
     '    "//services/network/public/mojom",\n'
     '    "//third_party/blink/public/mojom:mojom_platform",\n'
     '    "//ui/color",\n'
     '    "//ui/gfx:color_utils",\n    "//url",'),
    ('chrome/common/extensions/api/pdf_viewer_private.idl',
     '  callback GetTextInfoCallback = void(GetTextInfoResult result);',
     '''  // Bluelium : blocs binaires du flux appartenant a la frame appelante.
  dictionary PdfStreamChunk {
    ArrayBuffer data;
    boolean done;
  };
  dictionary BlueliumTheme {
    boolean dark;
    DOMString surface;
    DOMString background;
    DOMString field;
    DOMString text;
    DOMString muted;
    DOMString accent;
    DOMString onaccent;
    DOMString divider;
  };
  callback PdfStreamChunkCallback = void(PdfStreamChunk chunk);
  callback BlueliumThemeCallback = void(BlueliumTheme theme);
  callback GetTextInfoCallback = void(GetTextInfoResult result);'''),
    ('chrome/common/extensions/api/pdf_viewer_private.idl',
     '  interface Functions {',
     '''  interface Functions {
    // Bluelium : API privee, sans URL fournie par le renderer.
    static void readPdfStream(PdfStreamChunkCallback callback);
    static void getBlueliumTheme(BlueliumThemeCallback callback);
'''),
    (API + 'pdf_viewer_private_api.h',
     'class PdfViewerPrivateGetStreamInfoFunction : public ExtensionFunction {',
     '''// Bluelium : accès uniquement au flux du document appelant.
class PdfViewerPrivateReadPdfStreamFunction : public ExtensionFunction {
 public:
  DECLARE_EXTENSION_FUNCTION("pdfViewerPrivate.readPdfStream",
                             PDFVIEWERPRIVATE_READPDFSTREAM)
 protected:
  ~PdfViewerPrivateReadPdfStreamFunction() override = default;
  ResponseAction Run() override;
 private:
  void OnRead(std::vector<uint8_t> data, bool done, std::string error);
};
class PdfViewerPrivateGetBlueliumThemeFunction : public ExtensionFunction {
 public:
  DECLARE_EXTENSION_FUNCTION("pdfViewerPrivate.getBlueliumTheme",
                             PDFVIEWERPRIVATE_GETBLUELIUMTHEME)
 protected:
  ~PdfViewerPrivateGetBlueliumThemeFunction() override = default;
  ResponseAction Run() override;
};

class PdfViewerPrivateGetStreamInfoFunction : public ExtensionFunction {'''),
    (API + 'pdf_viewer_private_api.h',
     '#include "chrome/common/extensions/api/pdf_viewer_private.h"',
     '#include <string>\n#include <vector>\n\n'
     '#include "chrome/common/extensions/api/pdf_viewer_private.h"'),
    (API + 'pdf_viewer_private_api.cc',
     '#include <memory>',
     '#include <memory>\n\n'
     '#include "chrome/browser/extensions/api/pdf_viewer_private/bluelium_pdf_stream.h"\n'
     '#include "base/strings/stringprintf.h"\n'
     '#include "content/public/browser/web_contents.h"\n'
     '#include "ui/color/color_id.h"\n'
     '#include "ui/color/color_provider.h"\n'
     '#include "ui/gfx/color_utils.h"'),
    (API + 'pdf_viewer_private_api.cc',
     'PdfViewerPrivateGetStreamInfoFunction::PdfViewerPrivateGetStreamInfoFunction() =',
     '''ExtensionFunction::ResponseAction PdfViewerPrivateReadPdfStreamFunction::Run() {
  auto* rfh = render_frame_host();
  if (!rfh) {
    return RespondNow(Error("Aucune frame PDF."));
  }
  auto stream = GetStreamContainer(rfh);
  if (!stream || stream->extension_id() != extension_id()) {
    return RespondNow(Error("Aucun flux PDF pour ce document."));
  }
  auto* reader = BlueliumPdfStream::GetForCurrentDocument(rfh);
  if (!reader) {
    auto loader = stream->TakeTransferrableURLLoader();
    if (!loader) {
      return RespondNow(Error("Le flux PDF a déjà été consommé."));
    }
    BlueliumPdfStream::CreateForCurrentDocument(rfh, std::move(loader));
    reader = BlueliumPdfStream::GetForCurrentDocument(rfh);
    if (chrome_pdf::features::IsOopifPdfEnabled()) {
      auto* manager = mime_handler::MimeHandlerStreamManager::FromRenderFrameHost(
          rfh->GetParent());
      manager->SetPluginCanSave(rfh->GetParent(), true);
    }
  }
  reader->Read(base::BindOnce(&PdfViewerPrivateReadPdfStreamFunction::OnRead, this));
  return did_respond() ? AlreadyResponded() : RespondLater();
}

void PdfViewerPrivateReadPdfStreamFunction::OnRead(
    std::vector<uint8_t> data, bool done, std::string error) {
  if (!error.empty()) {
    Respond(Error(std::move(error)));
    return;
  }
  base::DictValue chunk;
  chunk.Set("data", base::Value(std::move(data)));
  chunk.Set("done", done);
  Respond(WithArguments(std::move(chunk)));
}

ExtensionFunction::ResponseAction PdfViewerPrivateGetBlueliumThemeFunction::Run() {
  auto* rfh = render_frame_host();
  if (!rfh || !GetStreamContainer(rfh)) {
    return RespondNow(Error("Aucun document PDF."));
  }
  const auto& colors = content::WebContents::FromRenderFrameHost(rfh)->GetColorProvider();
  const auto css = [&](ui::ColorId id) {
    SkColor color = colors.GetColor(id);
    return base::StringPrintf("#%02x%02x%02x", SkColorGetR(color),
                              SkColorGetG(color), SkColorGetB(color));
  };
  base::DictValue theme;
  theme.Set("dark", color_utils::IsDark(colors.GetColor(ui::kColorSysSurface)));
  theme.Set("surface", css(ui::kColorSysSurface));
  theme.Set("background", css(ui::kColorSysSurfaceContainer));
  theme.Set("field", css(ui::kColorSysSurfaceVariant));
  theme.Set("text", css(ui::kColorSysOnSurface));
  theme.Set("muted", css(ui::kColorSysOnSurfaceVariant));
  theme.Set("accent", css(ui::kColorSysPrimary));
  theme.Set("onaccent", css(ui::kColorSysOnPrimary));
  theme.Set("divider", css(ui::kColorSysDivider));
  return RespondNow(WithArguments(std::move(theme)));
}

PdfViewerPrivateGetStreamInfoFunction::PdfViewerPrivateGetStreamInfoFunction() ='''),
    # Le même pont fonctionne avec le chemin GuestView de secours.
    (API + 'pdf_viewer_private_api.cc',
     '  content::RenderFrameHost* embedder_host = extension_host->GetParent();',
     '''  // Bluelium : conserver la compatibilité avec --disable-features=PdfOopif.
  if (!chrome_pdf::features::IsOopifPdfEnabled()) {
    auto* guest = MimeHandlerViewGuest::FromWebContents(
        content::WebContents::FromRenderFrameHost(extension_host));
    return guest ? guest->GetStreamWeakPtr() : nullptr;
  }
  content::RenderFrameHost* embedder_host = extension_host->GetParent();'''),
    ('tools/metrics/histograms/metadata/extensions/enums.xml',
     '  <int value="1992" label="EXPERIMENTALAIDATA_GETAPCSNAPSHOT"/>',
     '  <int value="1992" label="EXPERIMENTALAIDATA_GETAPCSNAPSHOT"/>\n'
     '  <int value="1993" label="PDFVIEWERPRIVATE_READPDFSTREAM"/>\n'
     '  <int value="1994" label="PDFVIEWERPRIVATE_GETBLUELIUMTHEME"/>'),
    ('extensions/browser/extension_function_histogram_value.h',
     '  // Last entry: Add new entries above, then run:',
     '  PDFVIEWERPRIVATE_READPDFSTREAM = 1993,\n'
     '  PDFVIEWERPRIVATE_GETBLUELIUMTHEME = 1994,\n'
     '  // Last entry: Add new entries above, then run:'),
]
