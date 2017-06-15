from qtpy import QtWidgets

from .pdsspect_image_set import PDSSpectImageSetViewBase


class TransformsController(object):

    def __init__(self, image_set, view):
        self.image_set = image_set
        self.view = view

    def set_flip_x(self, flip_x):
        self.image_set.flip_x = flip_x

    def set_flip_y(self, flip_y):
        self.image_set.flip_y = flip_y

    def set_swap_xy(self, swap_xy):
        self.image_set.swap_xy = swap_xy


class Transforms(QtWidgets.QDialog, PDSSpectImageSetViewBase):

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
        if self.flip_x_box.isChecked():
            self.controller.set_flip_x(True)
        else:
            self.controller.set_flip_x(False)

    def flip_y_checked(self, state):
        if self.flip_y_box.isChecked():
            self.controller.set_flip_y(True)
        else:
            self.controller.set_flip_y(False)

    def swap_xy_checked(self, state):
        if self.swap_xy_box.isChecked():
            self.controller.set_swap_xy(True)
        else:
            self.controller.set_swap_xy(False)
