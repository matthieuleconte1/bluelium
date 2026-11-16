"""Bluelium : feux natifs et leur réservation centrés sur la pastille de 32 px.
À appliquer après layout-spacing et les ajustements macOS de Helium ; mac seul.
"""
NEW_FILES = {}
EDITS = [
 ('chrome/browser/ui/views/frame/browser_native_widget_mac.mm',
  '    if (!browser_view_->ShouldDrawTabStrip()) {\n'
  '      *titlebar_height += kWebAppMenuMargin * 2;\n'
  '    }\n',
  '    if (!browser_view_->ShouldDrawTabStrip()) {\n'
  '      *titlebar_height += kWebAppMenuMargin * 2;\n'
  '    } else if (top_element_info.tabstrip_preferred_height > 0) {\n'
  '      // Bluelium : Cocoa centre les feux dans cette hauteur. La pastille\n'
  '      // commence à y=4 et mesure 32 px : centre y=20, donc titre de 40 px.\n'
  '      // Ne pas changer les fenêtres applicatives ni les onglets verticaux.\n'
  '      *titlebar_height = 40 +\n'
  '          2 * browser_view_->browser_widget()->GetFrameView()->GetTopInset(true);\n'
  '    }\n'),
 ('chrome/browser/ui/views/frame/browser_frame_view_mac.mm',
  '    result.bounds = gfx::RectF(10, 10, 60, 14);\n',
  '    result.bounds = gfx::RectF(10, 13, 60, 14);  // Bluelium : centre y=20\n'),
 ('chrome/browser/ui/views/frame/browser_frame_view_mac.mm',
  '    result.bounds = gfx::RectF(11, 11, 52, 12);\n',
  '    result.bounds = gfx::RectF(11, 14, 52, 12);  // Bluelium : centre y=20\n'),
]
