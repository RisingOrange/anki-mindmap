
from anki.utils import isMac
from aqt import mw
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QProgressBar, QWidget


def get_progress_widget(max):
    progressWidget = QWidget()
    progressWidget.setFixedSize(400, 70)
    progressWidget.setWindowModality(Qt.WindowModality.ApplicationModal)
    progressWidget.bar = bar = QProgressBar(progressWidget)
    if isMac:
        bar.setFixedSize(380, 50)
    else:
        bar.setFixedSize(390, 50)
    bar.move(10, 10)
    per = QLabel(bar)
    per.setAlignment(Qt.AlignCenter)

    bar.setMinimum(0)
    bar.setMaximum(max)

    progressWidget.show()

    def callback():
        bar.setValue(callback.i)
        callback.i += 1
        if not progressWidget.isVisible():
            raise Exception('user cancelled')
        mw.app.processEvents()
    callback.i = 0

    return progressWidget, callback
