from qtpy import QtWidgets

from .histogram import HistogramWidget, HistogramModel
from .pdsspect_image_set import PDSSpectImageSetViewBase


class BasicHistogramWidget(HistogramWidget):
    """:class:`.pdsspect.histogram.HistogramWidget` in a different layout"""

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
    """Controller for :class:`Basic` window

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view : :class:`Basic`
        View to control

    Attributes
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view : :class:`Basic`
        View to control
    """

    def __init__(self, image_set, view):
        self.image_set = image_set
        self.view = view

    def change_current_image_index(self, new_index):
        """Change the current image index to a new index

        Parameters
        ----------
        new_index : :obj:`int`
            The new index for
            :class:`~.pdsspect_image_set.PDSSpectImageSetViewBase.images` to
            determine the current image
        """

        self.image_set.current_image_index = new_index


class Basic(QtWidgets.QWidget, PDSSpectImageSetViewBase):
    """Window to apply cut levels and choose the current image

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view_canvas : :class:`~.pds_image_view_canvas.PDSImageViewCanvas`
        Canvas to view the image

    Attributes
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view_canvas : :class:`~.pds_image_view_canvas.PDSImageViewCanvas`
        Canvas to view the image
    controller : :class:`BasicController`
        Controller for view
    image_menu : :class:`QtWidgets.QComboBox <PySide.QtGui.QComboBox>`
        Drop down menu to pick the current image
    histogram : :class:`~.histogram.HistogramModel`
        Model for the :attr:`histogram_widget`
    histogram_widget : :class:`BasicHistogramWidget`
        The histogram widget to adjust the cut levels
    layout : :class:`QtWidgets.QVBoxLayout <PySide.QtGui.QVBoxLayout>`
        The main layout
    """

    def __init__(self, image_set, view_canvas, parent=None):
        super(Basic, self).__init__(parent)
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
        self.histogram_widget = BasicHistogramWidget(self.histogram, self)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.image_menu)
        self.layout.addWidget(self.histogram_widget)

        self.setLayout(self.layout)
        self.histogram.set_data()

    def change_image(self, new_index):
        """Change the image when new image selected in :attr:`image_menu`

        Parameters
        ----------
        new_index : :obj:`int`
            The new index to determine the current image
        """

        self.image_set.current_image.cuts = self.histogram.cuts
        self.controller.change_current_image_index(new_index)

    def set_image(self):
        """When the image is set, adjust the histogram"""
        self.histogram.set_data()
        self.histogram.restore()


class BasicWidget(QtWidgets.QWidget):

    def __init__(self, image_set, view_canvas):
        super(BasicWidget, self).__init__()
        self.image_set = image_set
        self.view_canvases = []
        self.basics = []
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)
        self.setWindowTitle('Basic')
        self.add_basic(image_set, view_canvas)

    def add_basic(self, image_set, view_canvas):
        basic = Basic(image_set, view_canvas, self)
        self.basics.append(basic)
        self.view_canvases.append(view_canvas)
        self.main_layout.addWidget(basic)
