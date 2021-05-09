import tempfile
import textwrap

from anki.lang import _
from aqt import mw
from aqt.utils import showInfo
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import QImage
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtWidgets import *

from ._vendor.brain_dump.graphviz import THEMES, theme
from .anki_util import all_tags
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

    def _setup_tag_prefix_lineedit(self, parent):
        groupbox = QGroupBox()
        parent.addWidget(groupbox)
        groupbox.setLayout(QVBoxLayout())

        groupbox.layout().addWidget(QLabel("Choose a tag to be in the middle of the mindmap:"))

        self.lineedit = QLineEdit()
        groupbox.layout().addWidget(self.lineedit)
        self.lineedit.setClearButtonEnabled(True)
        self.completer = Completer(self.lineedit, all_tags())
        self.lineedit.setCompleter(self.completer)

        groupbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        return self.lineedit

    # button actions
    def _on_show_button_click(self):
        if self._warn_if_invalid_tag():
            return
        if self.with_notes_cb.isChecked():
            self._warn_if_include_notes_checked()

        self.viewer = GraphicsView()
        with tempfile.NamedTemporaryFile() as f:
            self._save_mindmap_to_file(f.name)
            self.viewer.setImg(f.name)

        self.viewer.show()

    def _on_save_button_click(self):
        if self._warn_if_invalid_tag():
            return
        if self.with_notes_cb.isChecked():
            self._warn_if_include_notes_checked()

        file_name = self._show_save_file_dialog()
        if file_name:
            self._save_mindmap_to_file(file_name)

    # helper functions
    def _warn_if_invalid_tag(self):
        if self.tag_prefix_lineedit.text() not in all_tags():
            showInfo('Please enter a valid tag')
            return True
        return False

    def _warn_if_include_notes_checked(self):
        showInfo(textwrap.dedent('''\
            The "include notes" option works with Basic and Cloze notes + any note that has a field named "Front".
            The text from the front of these notes is shown on the mindmap. The text of all other notes is not. 
        '''))

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
                    'You can get it from https://graphviz.org/download/.\n'
                    'Make sure it is on the PATH.'
                )
            else:
                raise e


class GraphicsView(QGraphicsView):

    def __init__(self, *args):
        super().__init__(*args)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def setImg(self, svg_path):
        self.scene = QGraphicsScene()
        item = QGraphicsSvgItem(svg_path)
        self.scene.addItem(item)
        self.setScene(self.scene)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):

        # HACK window contents get fitted in view if the difference between
        # the old and new size is sufficiently big
        # this prevents fitInView being called when zooming using the scroll wheel
        # because otherwise fitInView gets called and zooms out again when zooming in on the image
        if(abs(event.size().width() - event.oldSize().width()) > 100):
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        factor = 1.1
        if event.angleDelta().y() < 0:
            factor = 0.9
        view_pos = event.pos()
        scene_pos = self.mapToScene(view_pos)
        self.centerOn(scene_pos)
        self.scale(factor, factor)
        delta = self.mapToScene(
            view_pos) - self.mapToScene(self.viewport().rect().center())
        self.centerOn(scene_pos - delta)


class Completer(QCompleter):

    def __init__(self, lineedit, options):
        super().__init__(options)

        self.lineedit = lineedit

        self.setFilterMode(Qt.MatchContains)
        self.setCaseSensitivity(Qt.CaseInsensitive)

        sorted_options = sorted(options, key=lambda x: str(
            x.count(cfg('tag_seperator'))) + x)
        self.model().setStringList(sorted_options)

    # show options when lineedit is clicked even if it is empty
    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            self.setCompletionPrefix(self.lineedit.text())
            self.complete()

        return super().eventFilter(source, event)


def make_button(txt, f, parent):
    b = QPushButton(txt)
    b.clicked.connect(f)
    parent.addWidget(b)
    return b


def show():
    mw.mindmap_dialog = MindmapDialog(mw.app.activeWindow())
    mw.mindmap_dialog.show()
