from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import (QHBoxLayout, QSlider, QStyle, QStyleOptionSlider,
                             QVBoxLayout, QWidget)

# from https://gist.github.com/wiccy46/b7d8a1d57626a4ea40b19c5dbc5029ff
class LabeledSlider(QWidget):
    def __init__(self, minimum, maximum, interval=1, orientation=Qt.Horizontal,
                 labels=None, p0=0, parent=None):
        super(LabeledSlider, self).__init__(parent=parent)

        levels = range(minimum, maximum + interval, interval)

        if labels is not None:
            if not isinstance(labels, (tuple, list)):
                raise Exception("<labels> is a list or tuple.")
            if len(labels) != len(levels):
                raise Exception("Size of <labels> doesn't match levels.")
            self.levels = list(zip(levels, labels))
        else:
            self.levels = list(zip(levels, map(str, levels)))

        if orientation == Qt.Horizontal:
            self.layout = QVBoxLayout(self)
        elif orientation == Qt.Vertical:
            self.layout = QHBoxLayout(self)
        else:
            raise Exception("<orientation> wrong.")

        # gives some space to print labels
        self.left_margin = 10
        self.top_margin = 10
        self.right_margin = 10
        self.bottom_margin = 10

        self.layout.setContentsMargins(self.left_margin, self.top_margin,
                                       self.right_margin, self.bottom_margin)

        self.sl = Slider(orientation, self)
        self.sl.setMinimum(minimum)
        self.sl.setMaximum(maximum)
        self.sl.setValue(minimum)
        self.sl.setSliderPosition(p0)
        if orientation == Qt.Horizontal:
            self.sl.setTickPosition(QSlider.TicksBelow)
            self.sl.setMinimumWidth(300)  # just to make it easier to read
        else:
            self.sl.setTickPosition(QSlider.TicksLeft)
            self.sl.setMinimumHeight(300)  # just to make it easier to read
        self.sl.setTickInterval(interval)
        self.sl.setSingleStep(1)

        self.layout.addWidget(self.sl)

    def value(self):
        return self.sl.value()
    
    def setValue(self, value):
        self.sl.setValue(value)

    def paintEvent(self, e):

        super(LabeledSlider, self).paintEvent(e)
        style = self.sl.style()
        painter = QPainter(self)
        st_slider = QStyleOptionSlider()
        st_slider.initFrom(self.sl)
        st_slider.orientation = self.sl.orientation()

        length = style.pixelMetric(QStyle.PM_SliderLength, st_slider, self.sl)
        available = style.pixelMetric(
            QStyle.PM_SliderSpaceAvailable, st_slider, self.sl)

        for v, v_str in self.levels:

            # get the size of the label
            rect = painter.drawText(QRect(), Qt.TextDontPrint, v_str)

            if self.sl.orientation() == Qt.Horizontal:
                # I assume the offset is half the length of slider, therefore
                # + length//2
                x_loc = QStyle.sliderPositionFromValue(self.sl.minimum(),
                                                       self.sl.maximum(), v, available)+length//2

                # left bound of the text = center - half of text width + L_margin
                left = x_loc-rect.width()//2+self.left_margin
                bottom = self.rect().bottom()

                # enlarge margins if clipping
                if v == self.sl.minimum():
                    if left <= 0:
                        self.left_margin = rect.width()//2-x_loc
                    if self.bottom_margin <= rect.height():
                        self.bottom_margin = rect.height()

                    self.layout.setContentsMargins(self.left_margin,
                                                   self.top_margin, self.right_margin,
                                                   self.bottom_margin)

                if v == self.sl.maximum() and rect.width()//2 >= self.right_margin:
                    self.right_margin = rect.width()//2
                    self.layout.setContentsMargins(self.left_margin,
                                                   self.top_margin, self.right_margin,
                                                   self.bottom_margin)

            else:
                y_loc = QStyle.sliderPositionFromValue(self.sl.minimum(),
                                                       self.sl.maximum(), v, available, upsideDown=True)

                bottom = y_loc+length//2+rect.height()//2+self.top_margin-3
                # there is a 3 px offset that I can't attribute to any metric

                left = self.left_margin-rect.width()
                if left <= 0:
                    self.left_margin = rect.width()+2
                    self.layout.setContentsMargins(self.left_margin,
                                                   self.top_margin, self.right_margin,
                                                   self.bottom_margin)

            pos = QPoint(left, bottom)
            painter.drawText(pos, v_str)

        return

# from https://stackoverflow.com/a/52690011/6827339
class Slider(QSlider):
    def mousePressEvent(self, event):
        super(Slider, self).mousePressEvent(event)
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

        if self.orientation() == Qt.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == Qt.Horizontal else pr.y()
        return QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), p - sliderMin,
                                              sliderMax - sliderMin, opt.upsideDown)
