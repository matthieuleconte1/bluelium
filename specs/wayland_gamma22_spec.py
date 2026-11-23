"""Bluelium : couleurs exactes sous Wayland avec gestion des couleurs (KWin HDR).

Chromium déclare ses surfaces SDR avec la courbe « srgb » du protocole
wp_color_management_v1 (sRGB par morceaux). KWin, comme les autres
compositeurs et les autres navigateurs (Firefox/Zen), traite le contenu sRGB
comme décodé par une courbe gamma 2.2, celle des écrans sRGB réels. Le
décalage éclaircit les sombres : #080604 sortait en #100e0c, #111111 en
#181818, #404040 en #424242 (mesuré sur un écran HDR sous KWin, Zen affiche
les valeurs exactes). La courbe « srgb » est d'ailleurs dépréciée dans le
protocole pour cette ambiguïté.

L'écart vient de Chromium lui-même : KWin (et mutter) décrivent un écran sRGB
avec la courbe gamma 2.2, et Chromium convertit alors chaque page, qu'il
considère en sRGB par morceaux, vers ce gamma 2.2 (le code de Chromium le
signale, sa seule parade est --force-color-profile).

Correction, en deux points :
- un écran décrit en gamma 2.2 (quelles que soient ses primaires : BT.2020 en
  HDR, point blanc chaud avec la Couleur de nuit) est traité comme un écran
  SDR à courbe sRGB : aucune conversion de courbe des pages ;
- une surface en sRGB est déclarée en gamma 2.2 quand le compositeur la gère
  (KWin ne propose pas la courbe « srgb »).
Résultat identique à --disable-features=WaylandWpColorManagerV1, mesuré égal
à Zen. Les écrans décrits en PQ ou HLG ne sont pas touchés.
"""

W = 'ui/ozone/platform/wayland/host/wayland_wp_color_manager.cc'
D = 'ui/ozone/platform/wayland/host/wayland_wp_image_description.cc'

NEW_FILES = {}

EDITS = [
  (D,
   '  self->hdr_max_luminance_relative_ = max_lum / self->sdr_max_luminance_nits_;\n'
   '\n'
   '  bool is_hdr = self->hdr_max_luminance_relative_ > 1.f;\n',
   '  self->hdr_max_luminance_relative_ = max_lum / self->sdr_max_luminance_nits_;\n'
   '\n'
   '  // Bluelium : un écran décrit en gamma 2.2 (KWin, mutter) affiche le sRGB\n'
   '  // tel quel. Sans cela, Chromium convertit les pages du sRGB par morceaux\n'
   '  // vers le gamma 2.2 et éclaircit les sombres, là où Firefox et le\n'
   '  // compositeur affichent les valeurs telles quelles. Toutes primaires :\n'
   '  // KWin donne des primaires élargies en HDR (BT.2020) et un point blanc\n'
   '  // chaud avec la Couleur de nuit.\n'
   '  if (self->pending_transfer_id_ == gfx::ColorSpace::TransferID::GAMMA22) {\n'
   '    self->pending_transfer_id_ = gfx::ColorSpace::TransferID::SRGB;\n'
   '    self->hdr_max_luminance_relative_ = 1.f;\n'
   '  }\n'
   '\n'
   '  bool is_hdr = self->hdr_max_luminance_relative_ > 1.f;\n'),
  (W,
   '  // Set named transfer function if possible.\n'
   '  if (auto transfer = TransferIdToTransferFunction(color_space.GetTransferID());\n'
   '      transfer && IsSupportedTransferFunction(*transfer)) {\n',
   '  // Bluelium : le sRGB est décodé en gamma 2.2 par le compositeur (et par\n'
   '  // les écrans sRGB) ; l\'annoncer en « srgb » par morceaux éclaircit les\n'
   '  // sombres. On le déclare en gamma 2.2 quand c\'est possible.\n'
   '  auto transfer = TransferIdToTransferFunction(color_space.GetTransferID());\n'
   '  if (transfer == WP_COLOR_MANAGER_V1_TRANSFER_FUNCTION_SRGB &&\n'
   '      IsSupportedTransferFunction(\n'
   '          WP_COLOR_MANAGER_V1_TRANSFER_FUNCTION_GAMMA22)) {\n'
   '    transfer = WP_COLOR_MANAGER_V1_TRANSFER_FUNCTION_GAMMA22;\n'
   '  }\n'
   '\n'
   '  // Set named transfer function if possible.\n'
   '  if (transfer && IsSupportedTransferFunction(*transfer)) {\n'),
]
