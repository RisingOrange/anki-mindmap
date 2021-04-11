from anki.hooks import addHook
from PyQt5.QtWidgets import *

from .mindmap_creator_dialog import show as show_dialog


def main():
    addHook('browser.setupMenus', lambda self: setup_menu(self))


def setup_menu(self):

    # self is an aqt.browser.Browser instance
    self.menuTags = QMenu("Mindmap")
    self.menuBar().insertMenu(self.mw.form.menuTools.menuAction(), self.menuTags)

    menu = self.menuTags

    a = menu.addAction("Create a Mindmap")
    a.triggered.connect(lambda _: show_dialog())


main()
