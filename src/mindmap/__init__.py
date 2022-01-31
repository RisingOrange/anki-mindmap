from aqt.gui_hooks import browser_menus_did_init, profile_did_open
from aqt.qt import *

try:
    from aqt.browser.browser import Browser
except:
    from aqt.browser import Browser

from .compat import add_compat_aliases_to_anki, add_compat_aliases_to_aqt

add_compat_aliases_to_anki()

from .mindmap_creator_dialog import show as show_dialog


def setup_menu(self: Browser):
    menubar = self.form.menubar
    menu = menubar.addMenu("Mindmap")

    a = menu.addAction("Create a Mindmap")
    a.triggered.connect(lambda _: show_dialog())


profile_did_open.append(add_compat_aliases_to_aqt)

browser_menus_did_init.append(setup_menu)
