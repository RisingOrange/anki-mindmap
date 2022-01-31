from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import QFont, QPainter
from PyQt5.QtWidgets import QSlider, QStyle, QStyleOptionSlider


# combined from https://gist.github.com/wiccy46/b7d8a1d57626a4ea40b19c5dbc5029ff
# and https://stackoverflow.com/a/52690011/6827339
class LabeledSlider(QSlider):

    def __init__(self, parent=None):
        super(LabeledSlider, self).__init__(parent)

        # gives some space to print labels
        self.left_margin = 10
        self.top_margin = 10
        self.right_margin = 10
        self.bottom_margin = 10

        self.font = QFont()
        self.font.setPixelSize(11)

    def mousePressEvent(self, event):
        super(LabeledSlider, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            val = self.pixelPosToRangeValue(event.pos())
            self.setValue(val)

    def pixelPosToRangeValue(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(QStyle.CC_Slider,
                                         opt, QStyle.SC_SliderGroove, self)
        sr = self.style().subControlRect(QStyle.CC_Slider,
                                         opt, QStyle.SC_SliderHandle, self)

        if self.orientation() == Qt.Orientation.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == Qt.Orientation.Horizontal else pr.y()
        return QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - sliderMin,
                                              sliderMax - sliderMin, opt.upsideDown)

    def paintEvent(self, e):
        super(LabeledSlider, self).paintEvent(e)
        painter = QPainter(self)
        painter.setFont(self.font)

        st_slider = QStyleOptionSlider()
        st_slider.initFrom(self)
        st_slider.orientation = self.orientation()

        length = self.style().pixelMetric(
            QStyle.PM_SliderLength, st_slider, self)
        available = self.style().pixelMetric(
            QStyle.PM_SliderSpaceAvailable, st_slider, self)

        for v, v_str in self._levels():

            # get the size of the label
            rect = painter.drawText(QRect(), Qt.TextDontPrint, v_str)

            if self.orientation() == Qt.Orientation.Horizontal:
                # I assume the offset is half the length of slider, therefore
                # + length//2
                x_loc = QStyle.sliderPositionFromValue(
                    self.minimum(), self.maximum(), v, available)+length//2

                # left bound of the text = center - half of text width + L_margin
                left = x_loc-rect.width()//2+self.left_margin
                bottom = self.rect().bottom()

            else:
                y_loc = QStyle.sliderPositionFromValue(
                    self.minimum(), self.maximum(), v, available, upsideDown=True)

                bottom = y_loc+length//2+rect.height()//2+self.top_margin-3
                # there is a 3 px offset that I can't attribute to any metric

                left = self.left_margin-rect.width()

            pos = QPoint(left - 10, bottom - 1)  # added offsets


            painter.drawText(pos, v_str)

        return

    def _levels(self):
        result = range(self.minimum(), self.maximum() +
                       self.tickInterval(), self.tickInterval())
        result = list(zip(result, map(str, result)))
        return result
