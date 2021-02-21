from textwrap import dedent

from anki import tags
from anki.lang import _
from aqt import mw
from aqt.utils import showInfo
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .create_mindmap import create_mindmap

TAG_SEPERATOR = '::'


class OptionValidator(QValidator):

    def __init__(self, options):
        super().__init__()
        self.options = set(options)

    def validate(self, string, pos):
        if string in self.options:
            return (QValidator.State.Acceptable, string, pos)

        for option in self.options:
            if option.startswith(string):
                return (QValidator.State.Intermediate, string, pos)

        return (QValidator.State.Invalid, string, pos)


class MindmapDialog(QDialog):

    window_title = 'Mindmap Creator'

    def __init__(self, parent=None):
        super(MindmapDialog, self).__init__(parent)

        self.resize(500, 300)
        self.setWindowTitle(self.window_title)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # add tag prefix picker
        tags = [ tag for tag in mw.col.tags.all() if TAG_SEPERATOR in tag]
        tag_prefixes = set((
            TAG_SEPERATOR.join(tag.split(TAG_SEPERATOR)[:i])
            for tag in tags
            for i in range(1, len(tag.split(TAG_SEPERATOR)))
        ))
        self.lineedit=QLineEdit()
        self.lineedit.setValidator(OptionValidator(tag_prefixes))
        self.lineedit.setCompleter(QCompleter(tag_prefixes))
        layout.addWidget(self.lineedit)

        # add button
        layout.add=make_button("Draw", self._on_button_click, layout)


    def _on_button_click(self):
        tag_prefix = self.lineedit.text()
        file_name=self.saveFileDialog()
        if file_name:
            create_mindmap(tag_prefix, file_name)
            showInfo(f'{file_name} is ready')

    def saveFileDialog(self):
        file_name, _=QFileDialog.getSaveFileName(
            self, "", "mindmap.png", "*.png")
        return file_name


def make_button(txt, f, parent):
    b=QPushButton(txt)
    b.clicked.connect(f)
    parent.addWidget(b)
    return b

def show():
    mw.mindmap_dialog=MindmapDialog(mw.app.activeWindow())
    mw.mindmap_dialog.show()
