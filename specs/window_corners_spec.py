"""Helium Glyphe : coins de fenêtre arrondis partout (Linux, cadre Chromium).

Chromium n'arrondit sous Linux que les deux coins du haut, et seulement le
dessin du cadre : tout ce qui est peint dans un calque (barre d'onglets,
barre d'outils des modes compact et vertical) déborde sur les coins, qui
paraissent carrés. Ici :
  - les quatre coins sont arrondis, au rayon des coins de la page
    (GetSystemWindowRadius) ;
  - toute la zone du navigateur (BrowserView) est peinte dans un calque
    découpé en arrondi : plus rien ne déborde, quel que soit le mode.
Fenêtre maximisée, en plein écran ou en mosaïque : coins droits (rayon 0).
"""

F = 'chrome/browser/ui/views/frame/browser_frame_view_linux'

NEW_FILES = {}

EDITS = [
  (F + '.cc',
   '      gfx::RoundedCornersF(radius, radius, 0, 0));\n',
   '      gfx::RoundedCornersF(radius, radius, radius, radius));  // Glyphe\n'),
  (F + '.cc',
   '    return gfx::RoundedCornersF(radius_dip, radius_dip, 0, 0);\n',
   '    // Glyphe : les quatre coins.\n'
   '    return gfx::RoundedCornersF(radius_dip, radius_dip, radius_dip,\n'
   '                                radius_dip);\n'),
  (F + '.cc',
   '  return ChromeLayoutProvider::Get()->GetCornerRadiusMetric(\n'
   '      views::Emphasis::kHigh);\n}\n',
   '  return GetSystemWindowRadius();  // Glyphe : même rayon que la page\n}\n'),
  (F + '.cc',
   'float BrowserFrameViewLinux::GetRestoredCornerRadiusDip() const {\n',
   'void BrowserFrameViewLinux::Layout(PassKey) {\n'
   '  LayoutSuperclass<OpaqueBrowserFrameView>(this);\n'
   '  // Glyphe : découpe arrondie de toute la zone du navigateur, pour que les\n'
   '  // vues peintes dans un calque (onglets, barre d’outils) ne débordent pas\n'
   '  // sur les coins de la fenêtre.\n'
   '  BrowserView* view = GetBrowserView();\n'
   '  if (!view) {\n'
   '    return;\n'
   '  }\n'
   '  const gfx::RoundedCornersF radii = GetWindowRoundedCorners();\n'
   '  if (!view->layer()) {\n'
   '    if (radii.IsEmpty()) {\n'
   '      return;\n'
   '    }\n'
   '    view->SetPaintToLayer();\n'
   '    view->layer()->SetFillsBoundsOpaquely(false);\n'
   '  }\n'
   '  view->layer()->SetRoundedCornerRadius(radii);\n'
   '  view->layer()->SetIsFastRoundedCorner(true);\n'
   '}\n\n'
   'float BrowserFrameViewLinux::GetRestoredCornerRadiusDip() const {\n'),
  (F + '.cc',
   '#include "chrome/browser/ui/views/frame/browser_view.h"\n',
   '#include "chrome/browser/ui/views/frame/browser_view.h"\n'
   '#include "chrome/browser/ui/views/helium/frame_corner_radius.h"\n'
   '#include "ui/compositor/layer.h"\n'),
  (F + '.h',
   '  gfx::RoundedCornersF GetWindowRoundedCorners() const override;\n',
   '  gfx::RoundedCornersF GetWindowRoundedCorners() const override;\n'
   '  void Layout(PassKey) override;  // Glyphe : coins arrondis\n'),
]
