from functools import wraps

from . import *  # Import Test File Paths from __init__

from qtpy import QtCore

from pdsspect.pdsspect_image_set import PDSSpectImageSet
from pdsspect.pdsspect_view import PDSSpectViewController, PDSSpectView


class TestPDSSpectViewController(object):
    image_set = PDSSpectImageSet(TEST_FILES)
    controller = PDSSpectViewController(image_set, None)

    def test_init(self):
        assert self.controller.image_set == self.image_set
        assert self.controller.view is None

    def test_change_pan_center(self):
        self.image_set.zoom = 2
        assert self.image_set.center == (16, 32)
        self.controller.change_pan_center(24, 48)
        assert self.image_set.center == (24, 48)
        self.controller.change_pan_center(8, 16)
        assert self.image_set.center == (8, 16)
        self.controller.change_pan_center(16, 32)
        assert self.image_set.center == (16, 32)
        self.image_set.zoom = 1
        assert self.image_set.center == (16, 32)

    def test_change_pan_size(self):
        assert self.image_set.zoom == 1
        self.controller.change_pan_size(2)
        assert self.image_set.zoom == 2
        self.controller.change_pan_size(1)
        assert self.image_set.zoom == 1


class TestPDSSpectView(object):
    image_set = PDSSpectImageSet(TEST_FILES)
    view = PDSSpectView(image_set)

    def add_view_to_qtbot(func):
        @wraps(func)
        def wrapper(self, qtbot):
            self.view.show()
            qtbot.add_widget(self.view)
            qtbot.add_widget(self.view.pan_view)
            return func(self, qtbot)
        return wrapper

    @add_view_to_qtbot
    def test_set_image(self, qtbot):
        view_image = self.view.view_canvas.get_image()
        assert view_image == self.image_set.current_image
        self.image_set._current_image_index += 1
        self.view.set_image()
        assert not view_image == self.image_set.current_image
        view_image = self.view.view_canvas.get_image()
        assert view_image == self.image_set.current_image
        self.image_set._current_image_index -= 1
        self.image_set.current_image.cuts = (10, 100)
        self.view.set_image()
        assert not view_image == self.image_set.current_image
        view_image = self.view.view_canvas.get_image()
        assert view_image == self.image_set.current_image
        assert self.view.view_canvas.get_cut_levels() == (10, 100)

    @add_view_to_qtbot
    def test_set_transforms(self, qtbot):
        assert self.view.view_canvas.get_transforms() == (False, False, False)
        assert self.image_set.transforms == (False, False, False)
        self.image_set._flip_x = True
        assert self.image_set.transforms == (True, False, False)
        assert self.view.view_canvas.get_transforms() == (False, False, False)
        self.view.set_transforms()
        assert self.view.view_canvas.get_transforms() == (True, False, False)
        self.image_set._swap_xy = True
        self.view.set_transforms()
        assert self.view.view_canvas.get_transforms() == (True, False, True)
        self.image_set._flip_x = False
        self.image_set._swap_xy = False
        self.view.set_transforms()
        assert self.view.view_canvas.get_transforms() == (False, False, False)

    @add_view_to_qtbot
    def test_change_zoom(self, qtbot):
        assert float(self.view.zoom_text.text()) == self.image_set.zoom
        self.view.zoom_text.setText('2')
        self.view.change_zoom()
        assert self.image_set.zoom == 2.0
        self.view.zoom_text.setText('1.00')
        qtbot.keyPress(self.view.zoom_text, QtCore.Qt.Key_Return)
        assert self.image_set.zoom == 1.0
        self.view.zoom_text.setText('foo')
        qtbot.keyPress(self.view.zoom_text, QtCore.Qt.Key_Return)
        assert self.image_set.zoom == 1.0

    @add_view_to_qtbot
    def test_adjust_pan_size(self, qtbot):
        assert self.view.pan.xradius == 16.5
        assert self.view.pan.yradius == 32.5
        self.image_set._zoom = 2
        self.view.pan.x = 20
        self.view.pan.y = 30
        self.view.adjust_pan_size()
        assert self.view.pan.xradius == 8.5
        assert self.view.pan.yradius == 16.5
        assert self.image_set.center == (20, 30)
        self.image_set._zoom = 1
        self.view.adjust_pan_size()
        assert self.view.pan.xradius == 16.5
        assert self.view.pan.yradius == 32.5
        assert self.image_set.center == (16, 32)

    @add_view_to_qtbot
    def test_change_center(self, qtbot):
        self.image_set.zoom = 2
        assert self.image_set.center == (16, 32)
        self.view.change_center(None, None, 20, 30)
        assert self.image_set.center == (20, 30)
        self.view.change_center(None, None, 8, 16)
        assert self.image_set.center == (8, 16)
        self.view.change_center(None, None, 16, 32)
        assert self.image_set.center == (16, 32)
        self.image_set.zoom = 1
        assert self.image_set.center == (16, 32)

    @add_view_to_qtbot
    def test_move_pan(self, qtbot):
        self.image_set.zoom = 2
        self.image_set._center = (20, 30)
        assert self.view.pan.x == 16
        assert self.view.pan.y == 32
        self.view.move_pan()
        assert self.view.pan.x == 20
        assert self.view.pan.y == 30
        self.image_set._center = (16, 32)
        self.view.move_pan()
        assert self.view.pan.x == 16
        assert self.view.pan.y == 32
        self.image_set.zoom = 1
