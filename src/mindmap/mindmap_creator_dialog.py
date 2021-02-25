
from anki.lang import _
from aqt import mw
from aqt.utils import showInfo
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ._vendor.brain_dump.graphviz import THEMES
from .anki_util import tags_that_have_subtags
from .config import cfg
from .mindmap import TagMindmap


class MindmapDialog(QDialog):

    window_title = 'Mindmap Creator'

    def __init__(self, parent=None):
        super(MindmapDialog, self).__init__(parent)

        self.resize(500, 300)
        self.setWindowTitle(self.window_title)

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # add "tag prefix lineedit"
        self.tag_prefix_lineedit = self._setup_tag_prefix_lineedit(layout)

        self.theme_picker = QComboBox()
        self.theme_picker.addItems(list(THEMES.keys()))
        layout.addWidget(self.theme_picker)

        # add "include notes" checkbox
        self.with_notes_cb = QCheckBox('include notes (experimental)')
        self.with_notes_cb.move(10, 0)
        self.with_notes_cb.adjustSize()
        layout.addWidget(self.with_notes_cb)

        # add "Draw" button
        layout.add = make_button("Draw", self._on_button_click, layout)

    def _setup_tag_prefix_lineedit(self, parent):
        groupbox = QGroupBox()
        groupbox.setLayout(QVBoxLayout())
        parent.addWidget(groupbox)

        groupbox.layout().addWidget(QLabel("Choose a tag to be in the middle of the mindmap:"))

        lineedit = QLineEdit()
        lineedit.setValidator(OptionValidator(tags_that_have_subtags()))
        lineedit.setCompleter(QCompleter(tags_that_have_subtags()))
        groupbox.layout().addWidget(lineedit)

        groupbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        return lineedit

    def _on_button_click(self):
        if self.tag_prefix_lineedit.text() not in tags_that_have_subtags():
            showInfo('Please enter a valid tag')
            return

        file_name = self.show_save_file_dialog()
        if file_name:
            mindmap = TagMindmap(self.tag_prefix_lineedit.text())
            mindmap.save_as_img(
                file_name, 
                THEMES[self.theme_picker.currentText()], 
                include_notes=self.with_notes_cb.isChecked()
            )
            showInfo(f'{file_name} is ready')

    def show_save_file_dialog(self):
        last_part_of_tag = self.tag_prefix_lineedit.text().split(
            cfg('tag_seperator'))[-1]
        suggested_filename = last_part_of_tag + \
            ('_with_notes' if self.with_notes_cb.isChecked() else '') + '.svg'
        result, _ = QFileDialog.getSaveFileName(
            self, "", suggested_filename, "*.svg")
        return result


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


def make_button(txt, f, parent):
    b = QPushButton(txt)
    b.clicked.connect(f)
    parent.addWidget(b)
    return b


def show():
    mw.mindmap_dialog = MindmapDialog(mw.app.activeWindow())
    mw.mindmap_dialog.show()
