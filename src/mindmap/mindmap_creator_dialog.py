from textwrap import dedent

from anki import tags
from anki.lang import _
from aqt import mw
from aqt.utils import showInfo
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .create_mindmap import create_mindmap
from .util import tag_prefixes

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
        self.tag_prefix_lineedit = self._setup_tag_prefix_lineedit(layout)

        # add with notes checkbox
        self.with_notes_cb = QCheckBox('include notes')
        self.with_notes_cb.move(10, 0)
        self.with_notes_cb.adjustSize()
        layout.addWidget(self.with_notes_cb)

        # add button
        layout.add = make_button("Draw", self._on_button_click, layout)

    def _setup_tag_prefix_lineedit(self, parent):
        groupbox = QGroupBox()
        groupbox.setLayout(QVBoxLayout())
        parent.addWidget(groupbox)

        groupbox.layout().addWidget(QLabel("Choose a tag to be in the middle of the mindmap:"))

        lineedit = QLineEdit()
        lineedit.setValidator(OptionValidator(tag_prefixes()))
        lineedit.setCompleter(QCompleter(tag_prefixes()))
        groupbox.layout().addWidget(lineedit)

        groupbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        return lineedit

    def _on_button_click(self):
        file_name = self.saveFileDialog()
        if file_name:
            create_mindmap(
                self.tag_prefix_lineedit.text(),
                file_name,
                only_tags=not self.with_notes_cb.isChecked()
            )
            showInfo(f'{file_name} is ready')

    def saveFileDialog(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "", "mindmap.png", "*.png")
        return file_name


def make_button(txt, f, parent):
    b = QPushButton(txt)
    b.clicked.connect(f)
    parent.addWidget(b)
    return b


def show():
    mw.mindmap_dialog = MindmapDialog(mw.app.activeWindow())
    mw.mindmap_dialog.show()