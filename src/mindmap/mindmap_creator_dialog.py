from textwrap import dedent

from anki.lang import _
from aqt import mw
from aqt.utils import showInfo
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .create_mindmap import main


class MindmapDialog(QDialog):

    window_title = 'Mindmap Creator'
    description = dedent('''
        Description
    ''').strip()

    def __init__(self, parent=None):
        super(MindmapDialog, self).__init__(parent)

        self.resize(500, 300)
        self.setWindowTitle(self.window_title)

        self.vbox = QVBoxLayout(self)

        # add description
        label = QLabel(self.description)
        label.setWordWrap(True)
        font = label.font()
        font.setPixelSize(10)
        label.setFont(font)
        self.vbox.addWidget(label)

        # add deck picker
        self.deck_picker = QComboBox()
        deck_names = mw.col.decks.allNames()
        self.deck_picker.addItems(deck_names)
        self.deck_picker.setCurrentText(mw.col.decks.name(mw.col.decks.selected()))
        self.vbox.addWidget(self.deck_picker)

        # add buttons
        self.add = make_button("Draw", self._on_button_click, self.vbox)
        
        self.setLayout(self.vbox)
    
    def _on_button_click(self):
        chosen_deck_name = self.deck_picker.currentText()
        showInfo(chosen_deck_name)
        main(chosen_deck_name)


def make_button(txt, f, parent):
    b = QPushButton(txt)
    b.clicked.connect(f)
    parent.addWidget(b)
    return b

def show():
    mw.mindmap_dialog = MindmapDialog(mw.app.activeWindow())
    mw.mindmap_dialog.show()