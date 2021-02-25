# HACK for testing, because without running anki, importing aqt results in an error
try:
    from aqt import mw
    from .mindmap_creator_dialog import show as show_dialog
    from PyQt5.QtWidgets import *

    def main():
        setup_toolbar_button()

    def setup_toolbar_button():
        a = QAction('Create mindmap', mw)
        a.triggered.connect(show_dialog)
        mw.form.menuTools.addAction(a)

    main()

except Exception as e:
    print(e)
