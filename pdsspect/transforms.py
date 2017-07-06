"""Apply simple tranformations to the views"""
from qtpy import QtWidgets

from .pdsspect_image_set import PDSSpectImageSetViewBase


class TransformsController(object):
    """Controller for :class:`Transforms`

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view : :class:`Transforms`
        View to control

    Attributes
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view : :class:`Transforms`
        View to control
    """

    def __init__(self, image_set, view):
        self.image_set = image_set
        self.view = view

    def set_flip_x(self, flip_x):
        """Set :attr:`~.pdsspect_image_set.PDSSpectImageSet.flip_x`

        Parameters
        ----------
        flip_x : :obj:`bool`
            True to flip x axis, otherwise, False
        """

        self.image_set.flip_x = flip_x
        for image_set in self.image_set.subsets:
            image_set.flip_x = flip_x

    def set_flip_y(self, flip_y):
        """Set :attr:`~.pdsspect_image_set.PDSSpectImageSet.flip_y`

        Parameters
        ----------
        flip_y : :obj:`bool`
            True to flip y axis, otherwise, False
        """

        self.image_set.flip_y = flip_y
        for image_set in self.image_set.subsets:
            image_set.flip_y = flip_y

    def set_swap_xy(self, swap_xy):
        """Set :attr:`~.pdsspect_image_set.PDSSpectImageSet.swap_xy`

        Parameters
        ----------
        swap_xy : :obj:`bool`
            True to swap x and y axis, otherwise, False
        """

        self.image_set.swap_xy = swap_xy
        for image_set in self.image_set.subsets:
            image_set.swap_xy = swap_xy


class Transforms(QtWidgets.QDialog, PDSSpectImageSetViewBase):
    """Window to apply simple transformations

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view_canvas : :class:`.pds_image_view_canvas.PDSImageViewCanvas`
        The view canvas to apply transformations to

    Attributes
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view_canvas : :class:`.pds_image_view_canvas.PDSImageViewCanvas`
        The view canvas to apply transformations to
    controller : :class:`TransformsController`
        The view's controller
    flip_x_label : :class:`QtWidgets.QLabel <PySide.QtGui.QLabel>`
        Label for :attr:`flip_x_box`
    flip_x_box : :class:`QtWidgets.QCheckBox <PySide.QtGui.QCheckBox>`
        Flip x axis when checked
    flip_y_label : :class:`QtWidgets.QLabel <PySide.QtGui.QLabel>`
        Label for :attr:`flip_y_box`
    flip_y_box : :class:`QtWidgets.QCheckBox <PySide.QtGui.QCheckBox>`
        Flip y axis when checked
    swap_xy_label : :class:`QtWidgets.QLabel <PySide.QtGui.QLabel>`
        Label for :attr:`swap_xy_box`
    swap_xy_box : :class:`QtWidgets.QCheckBox <PySide.QtGui.QCheckBox>`
        Swap x and y axis when checked
    layout : :class:`QtWidgets.QGridLayout <PySide.QtGui.QGridLayout>`
        Layout for widget
    """

    def __init__(self, image_set, view_canvas):
        super(Transforms, self).__init__()
        self.image_set = image_set
        self.view_canvas = view_canvas
        self.image_set.register(self)
        self.controller = TransformsController(image_set, self)

        self.flip_x_label = QtWidgets.QLabel("Flip X Axes")
        self.flip_x_box = QtWidgets.QCheckBox()
        self.flip_x_box.stateChanged.connect(self.flip_x_checked)

        self.flip_y_label = QtWidgets.QLabel("Flip Y Axes")
        self.flip_y_box = QtWidgets.QCheckBox()
        self.flip_y_box.stateChanged.connect(self.flip_y_checked)

        self.swap_xy_label = QtWidgets.QLabel("Swap X and Y Axes")
        self.swap_xy_box = QtWidgets.QCheckBox()
        self.swap_xy_box.stateChanged.connect(self.swap_xy_checked)

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.flip_x_label, 0, 0)
        self.layout.addWidget(self.flip_x_box, 0, 1)
        self.layout.addWidget(self.flip_y_label, 1, 0)
        self.layout.addWidget(self.flip_y_box, 1, 1)
        self.layout.addWidget(self.swap_xy_label, 2, 0)
        self.layout.addWidget(self.swap_xy_box, 2, 1)

        self.setWindowTitle("Tranformations")

        self.setLayout(self.layout)

    def flip_x_checked(self, state):
        """Flip x axis when checked

        Parameters
        ----------
        state : :obj:`int`
            The state of the checkbox (this argument is ignored and the state
            is checked in a more explicit way)
        """

        if self.flip_x_box.isChecked():
            self.controller.set_flip_x(True)
        else:
            self.controller.set_flip_x(False)

    def flip_y_checked(self, state):
        """Flip y axis when checked

        Parameters
        ----------
        state : :obj:`int`
            The state of the checkbox (this argument is ignored and the state
            is checked in a more explicit way)
        """

        if self.flip_y_box.isChecked():
            self.controller.set_flip_y(True)
        else:
            self.controller.set_flip_y(False)

    def swap_xy_checked(self, state):
        """Swap x and y axis when checked

        Parameters
        ----------
        state : :obj:`int`
            The state of the checkbox (this argument is ignored and the state
            is checked in a more explicit way)
        """

        if self.swap_xy_box.isChecked():
            self.controller.set_swap_xy(True)
        else:
            self.controller.set_swap_xy(False)
