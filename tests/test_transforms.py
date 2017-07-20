from . import TEST_FILES

from qtpy import QtCore

from pdsspect.pdsspect_image_set import PDSSpectImageSet
from pdsspect.pds_image_view_canvas import PDSImageViewCanvas
from pdsspect.transforms import TransformsController, Transforms


class TestTransformsController(object):
    image_set = PDSSpectImageSet(TEST_FILES)
    subset = image_set.create_subset()
    controller = TransformsController(image_set, None)

    def test_set_flip_x(self):
        assert not self.image_set.flip_x
        assert not self.subset.flip_x
        self.controller.set_flip_x(True)
        assert self.image_set.flip_x
        assert self.subset.flip_x
        self.controller.set_flip_x(False)
        assert not self.image_set.flip_x
        assert not self.subset.flip_x

    def test_set_flip_y(self):
        assert not self.image_set.flip_y
        assert not self.subset.flip_y
        self.controller.set_flip_y(True)
        assert self.image_set.flip_y
        assert self.subset.flip_y
        self.controller.set_flip_y(False)
        assert not self.image_set.flip_y
        assert not self.subset.flip_y

    def test_set_swap_xy(self):
        assert not self.image_set.swap_xy
        assert not self.subset.swap_xy
        self.controller.set_swap_xy(True)
        assert self.image_set.swap_xy
        assert self.subset.swap_xy
        self.controller.set_swap_xy(False)
        assert not self.image_set.swap_xy
        assert not self.subset.swap_xy


class TestTransforms(object):
    image_set = PDSSpectImageSet(TEST_FILES)
    subset = image_set.create_subset()
    view_canvas = PDSImageViewCanvas()
    view_canvas.set_image(image_set.current_image)
    trans = Transforms(image_set, view_canvas)

    def test_flip_x_checked(self, qtbot):
        qtbot.add_widget(self.trans)
        self.trans.show()
        assert not self.trans.flip_x_box.isChecked()
        assert not self.image_set.flip_x
        assert not self.subset.flip_x
        qtbot.mouseClick(self.trans.flip_x_box, QtCore.Qt.LeftButton)
        assert self.trans.flip_x_box.isChecked()
        assert self.image_set.flip_x
        assert self.subset.flip_x
        qtbot.mouseClick(self.trans.flip_x_box, QtCore.Qt.LeftButton)
        assert not self.trans.flip_x_box.isChecked()
        assert not self.image_set.flip_x
        assert not self.subset.flip_x

    def test_flip_y_checked(self, qtbot):
        qtbot.add_widget(self.trans)
        self.trans.show()
        assert not self.trans.flip_y_box.isChecked()
        assert not self.image_set.flip_y
        assert not self.subset.flip_y
        qtbot.mouseClick(self.trans.flip_y_box, QtCore.Qt.LeftButton)
        assert self.trans.flip_y_box.isChecked()
        assert self.image_set.flip_y
        assert self.subset.flip_y
        qtbot.mouseClick(self.trans.flip_y_box, QtCore.Qt.LeftButton)
        assert not self.trans.flip_y_box.isChecked()
        assert not self.image_set.flip_y
        assert not self.subset.flip_y

    def test_swap_xy_checked(self, qtbot):
        qtbot.add_widget(self.trans)
        self.trans.show()
        assert not self.trans.swap_xy_box.isChecked()
        assert not self.image_set.swap_xy
        assert not self.subset.swap_xy
        qtbot.mouseClick(self.trans.swap_xy_box, QtCore.Qt.LeftButton)
        assert self.trans.swap_xy_box.isChecked()
        assert self.image_set.swap_xy
        assert self.subset.swap_xy
        qtbot.mouseClick(self.trans.swap_xy_box, QtCore.Qt.LeftButton)
        assert not self.trans.swap_xy_box.isChecked()
        assert not self.image_set.swap_xy
        assert not self.subset.swap_xy
