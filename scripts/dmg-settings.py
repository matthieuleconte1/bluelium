# Bluelium : mise en page de la fenêtre du .dmg pour dmgbuild.
# Appelé par scripts/package-macos.sh avec -D app=… -D background=… -D icon=….
# Positions accordées au fond dessiné par tools/dmg-background.py.
import os.path

app = defines['app']  # noqa: F821 (fourni par dmgbuild)
files = [app]
symlinks = {'Applications': '/Applications'}
icon = defines.get('icon')  # noqa: F821
background = defines['background']  # noqa: F821

format = 'ULMO'
filesystem = 'APFS'
show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
window_rect = ((200, 160), (660, 400))
default_view = 'icon-view'
show_icon_preview = False
arrange_by = None
icon_size = 112
text_size = 13
label_pos = 'bottom'
icon_locations = {
    os.path.basename(app): (165, 205),
    'Applications': (495, 205),
}
