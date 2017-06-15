from qtpy import QtWidgets

from .histogram import HistogramWidget, HistogramModel
from .pdsspect_image_set import PDSSpectImageSetViewBase


class BasicHistogramWidget(HistogramWidget):

    def _create_layout(self):
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self._cut_low_label, 0, 1)
        layout.addWidget(self._cut_low_box, 0, 2)
        layout.addWidget(self._cut_high_label, 1, 1)
        layout.addWidget(self._cut_high_box, 1, 2)
        layout.addWidget(self._bins_label, 2, 1)
        layout.addWidget(self._bins_box, 2, 2)
        layout.addWidget(self.histogram, 0, 0, 3, 1)

        return layout


class BasicController(object):

    def __init__(self, image_set, view):
        self.image_set = image_set
        self.view = view

    def change_current_image_index(self, new_index):
        self.image_set.current_image_index = new_index


class Basic(QtWidgets.QDialog, PDSSpectImageSetViewBase):

    def __init__(self, image_set, view_canvas):
        super(Basic, self).__init__()
        self.image_set = image_set
        self.image_set.register(self)
        self.controller = BasicController(image_set, self)
        self.view_canvas = view_canvas

        self.image_menu = QtWidgets.QComboBox()
        for image in self.image_set.images:
            self.image_menu.addItem(image.image_name)
        self.image_menu.setCurrentIndex(image_set.current_image_index)
        self.image_menu.currentIndexChanged.connect(self.change_image)
        self.histogram = HistogramModel(self.view_canvas, bins=100)
        self.histogram_widget = BasicHistogramWidget(self.histogram)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.image_menu)
        self.layout.addWidget(self.histogram_widget)

        self.setLayout(self.layout)
        self.histogram.set_data()

    def change_image(self, new_index):
        self.image_set.current_image.cuts = self.histogram.cuts
        self.controller.change_current_image_index(new_index)

    def set_image(self):
        self.histogram.set_data()
        self.histogram.restore()
