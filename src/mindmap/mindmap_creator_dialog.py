import textwrap
from pathlib import Path

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
from .gui.forms.anki21.dialog import Ui_Dialog
from .libaddon.gui.dialog_webview import WebViewer
from .mindmap import TagMindmap
from .util import CustomNamedTemporaryFile, named_temporary_file


class MindmapDialog(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent, Qt.Window)
        self.parent = parent

        self.dialog = Ui_Dialog()
        self.dialog.setupUi(self)

        self.completer = Completer(self.dialog.tag_prefix_lineedit, all_tags())
        self.dialog.tag_prefix_lineedit.setCompleter(self.completer)

        self.dialog.theme_picker.addItems(THEMES)

        self.dialog.show_btn.clicked.connect(self._on_show_button_click)
        self.dialog.save_btn.clicked.connect(self._on_save_button_click)

    # button actions
    def _on_show_button_click(self):
        if self._warn_if_invalid_tag():
            return
        if self.dialog.tab_widget.currentWidget().objectName() == 'image':
            if self.dialog.with_notes_cb.isChecked():
                self._warn_if_include_notes_checked()

            self.viewer = GraphicsView()
            with CustomNamedTemporaryFile() as f:
                self._export_image_mindmap(f.name)

                # the file is empty when the user cancels the drawing process
                if Path(f.name).stat().st_size == 0:
                    return

                self.viewer.setImg(f.name)

            self.viewer.show()
        else:
            if self.dialog.with_notes_cb_i.isChecked():
                self._warn_if_include_notes_checked()
            
            f = named_temporary_file('anki_mindmap.html', 'w+')
            self._export_interactive_mindmap(f.name)

            self.viewer = WebViewer(f'file://{f.name}', 'mind map', self)
            self.viewer.setWindowFlags(
                Qt.Window |
                Qt.WindowTitleHint |
                Qt.WindowSystemMenuHint
            )
            self.viewer.resize(1000, 600)
            self.viewer.show()

    def _on_save_button_click(self):
        if self._warn_if_invalid_tag():
            return
        if self.dialog.with_notes_cb.isChecked():
            self._warn_if_include_notes_checked()


        if self.dialog.tab_widget.currentWidget().objectName() == 'image':
            file_name = self._show_save_file_dialog('.svg')
            if file_name:
                self._export_image_mindmap(file_name)
        else:
            file_name = self._show_save_file_dialog('.html')
            if file_name:
                self._export_interactive_mindmap(file_name)

    # helper functions
    def _warn_if_invalid_tag(self):
        if self.dialog.tag_prefix_lineedit.text() not in all_tags():
            showInfo('Please enter a valid tag')
            return True
        return False

    def _warn_if_include_notes_checked(self):
        showInfo(textwrap.dedent('''\
            The "include notes" option works with Basic and Cloze notes + any note that has a field named "Front".
            The text from the front of these notes is shown on the mindmap. The text of all other notes is not. 
        '''))

    def _show_save_file_dialog(self, file_extension):
        last_part_of_tag = self.dialog.tag_prefix_lineedit.text().split(
            cfg('tag_seperator'))[-1]
        suggested_filename = last_part_of_tag + \
            ('_with_notes' if self.dialog.with_notes_cb.isChecked() else '') + file_extension
        result, _ = QFileDialog.getSaveFileName(
            self, "", suggested_filename, '*' + file_extension)
        return result

    def _export_image_mindmap(self, file_name):
        mindmap = TagMindmap(self.dialog.tag_prefix_lineedit.text())
        try:
            mindmap.save_as_img(
                file_name,
                theme(self.dialog.theme_picker.currentText(),
                      self.dialog.scale_branches_cb.isChecked()),
                include_notes=self.dialog.with_notes_cb.isChecked(),
                max_depth=self.dialog.max_depth_slider.value()
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

    def _export_interactive_mindmap(self, file_name):
        mindmap = TagMindmap(self.dialog.tag_prefix_lineedit.text())
        mindmap.save_as_jsmind(file_name, include_notes=self.dialog.with_notes_cb_i.isChecked())

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
