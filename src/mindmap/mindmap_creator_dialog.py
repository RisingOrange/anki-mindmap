import tempfile

from anki.lang import _
from aqt import mw
from aqt.utils import showInfo
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import *

from ._vendor.brain_dump.graphviz import THEMES, theme
from ._vendor.pyqt_image_viewer.QtImageViewer import QtImageViewer
from .anki_util import all_tags_that_have_subtags
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
        self.theme_picker.addItems(THEMES)
        layout.addWidget(self.theme_picker)

        # add "include notes" checkbox
        self.scale_branches_cb = QCheckBox('more notes - bigger branch')
        self.scale_branches_cb.move(10, 0)
        self.scale_branches_cb.adjustSize()
        layout.addWidget(self.scale_branches_cb)

        # add "include notes" checkbox
        self.with_notes_cb = QCheckBox('include notes (experimental)')
        self.with_notes_cb.move(10, 0)
        self.with_notes_cb.adjustSize()
        layout.addWidget(self.with_notes_cb)

        # add buttons
        layout.add = make_button("Show", self._on_show_button_click, layout)
        layout.save = make_button("Save", self._on_save_button_click, layout)

        self._setup_viewer()

    def _setup_tag_prefix_lineedit(self, parent):
        groupbox = QGroupBox()
        groupbox.setLayout(QVBoxLayout())
        parent.addWidget(groupbox)

        groupbox.layout().addWidget(QLabel("Choose a tag to be in the middle of the mindmap:"))

        lineedit = QLineEdit()
        lineedit.setValidator(OptionValidator(all_tags_that_have_subtags()))
        lineedit.setCompleter(QCompleter(all_tags_that_have_subtags()))
        groupbox.layout().addWidget(lineedit)

        groupbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        return lineedit

    def _setup_viewer(self):
        self.viewer = QtImageViewer()
        viewer = self.viewer

        viewer.aspectRatioMode = Qt.KeepAspectRatio
        viewer.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        viewer.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Allow zooming with right mouse button.
        # Drag for zoom box, doubleclick to view full image.
        viewer.canZoom = True

        # Allow panning with left mouse button.
        viewer.canPan = True

    # button actions
    def _on_show_button_click(self):
        if self._warn_if_invalid_tag():
            return

        with tempfile.NamedTemporaryFile() as f:
            self._save_mindmap_to_file(f.name)
            image = QImage(f.name)

        self.viewer.setImage(image)
        self.viewer.showMaximized()

    def _on_save_button_click(self):
        if self._warn_if_invalid_tag():
            return

        file_name = self._show_save_file_dialog()
        self._save_mindmap_to_file(file_name)

    # helper functions
    def _warn_if_invalid_tag(self):
        if self.tag_prefix_lineedit.text() not in all_tags_that_have_subtags():
            showInfo('Please enter a valid tag')
            return True
        return False

    def _show_save_file_dialog(self):
        last_part_of_tag = self.tag_prefix_lineedit.text().split(
            cfg('tag_seperator'))[-1]
        suggested_filename = last_part_of_tag + \
            ('_with_notes' if self.with_notes_cb.isChecked() else '') + '.svg'
        result, _ = QFileDialog.getSaveFileName(
            self, "", suggested_filename, "*.svg")
        return result

    def _save_mindmap_to_file(self, file_name):
        mindmap = TagMindmap(self.tag_prefix_lineedit.text())
        try:
            mindmap.save_as_img(
                file_name,
                theme(self.theme_picker.currentText(),
                      self.scale_branches_cb.isChecked()),
                include_notes=self.with_notes_cb.isChecked()
            )
        except OSError as e:
            if e.args[1] == '"dot" not found in path.':
                showInfo(
                    'It seems like you do not have Graphviz installed.\n' +
                    'You can get it from https://graphviz.org/download/.'
                )


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
