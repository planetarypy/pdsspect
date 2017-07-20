from . import TEST_FILES

import pytest
from qtpy import QtCore

from pdsspect.pdsspect_image_set import PDSSpectImageSet, SubPDSSpectImageSet
from pdsspect.pdsspect_view import (
    PDSSpectView,
    PDSSpectViewWidget,
    PDSSpectViewController
)


class TestPDSSpectViewController(object):
    image_set = PDSSpectImageSet(TEST_FILES)
    controller = PDSSpectViewController(image_set, None)
    default_center = image_set.center

    @pytest.fixture
    def test_set(self):
        yield self.image_set
        self.image_set.zoom = 1
        self.image_set.center = self.default_center

    def test_init(self, test_set):
        assert self.controller.image_set == test_set
        assert self.controller.view is None

    def test_change_pan_center(self, test_set):
        test_set.zoom = 2
        assert test_set.center == (16, 32)
        self.controller.change_pan_center(24, 48)
        assert test_set.center == (24, 48)
        self.controller.change_pan_center(8, 16)
        assert test_set.center == (8, 16)
        self.controller.change_pan_center(16, 32)
        assert test_set.center == (16, 32)
        test_set.zoom = 1
        assert test_set.center == (16, 32)

    def test_change_pan_size(self, test_set):
        assert test_set.zoom == 1
        self.controller.change_pan_size(2)
        assert test_set.zoom == 2
        self.controller.change_pan_size(1)
        assert test_set.zoom == 1


class TestPDSSpectView(object):
    image_set = PDSSpectImageSet(TEST_FILES)
    view = PDSSpectView(image_set)

    @pytest.fixture
    def test_set(self, qtbot):
        self.view.show()
        qtbot.add_widget(self.view)
        qtbot.add_widget(self.view.pan_view)
        yield self.image_set
        self.image_set._current_image_index = 0
        self.image_set.images[0].cuts = (None, None)
        self.image_set.images[1].cuts = (None, None)
        self.view.set_image()
        self.image_set._flip_x = False
        self.image_set._flip_y = False
        self.image_set._swap_xy = False
        self.image_set.zoom = 1

    def test_set_image(self, qtbot, test_set):
        view_image = self.view.view_canvas.get_image()
        assert view_image == test_set.current_image
        test_set._current_image_index += 1
        self.view.set_image()
        assert not view_image == test_set.current_image
        view_image = self.view.view_canvas.get_image()
        assert view_image == test_set.current_image
        test_set._current_image_index -= 1
        test_set.current_image.cuts = (10, 100)
        self.view.set_image()
        assert not view_image == test_set.current_image
        view_image = self.view.view_canvas.get_image()
        assert view_image == test_set.current_image
        assert self.view.view_canvas.get_cut_levels() == (10, 100)

    def test_set_transforms(self, qtbot, test_set):
        assert self.view.view_canvas.get_transforms() == (False, False, False)
        assert test_set.transforms == (False, False, False)
        test_set._flip_x = True
        assert test_set.transforms == (True, False, False)
        assert self.view.view_canvas.get_transforms() == (False, False, False)
        self.view.set_transforms()
        assert self.view.view_canvas.get_transforms() == (True, False, False)
        test_set._swap_xy = True
        self.view.set_transforms()
        assert self.view.view_canvas.get_transforms() == (True, False, True)
        test_set._flip_x = False
        test_set._swap_xy = False
        self.view.set_transforms()
        assert self.view.view_canvas.get_transforms() == (False, False, False)

    def test_change_zoom(self, qtbot, test_set):
        assert float(self.view.zoom_text.text()) == test_set.zoom
        self.view.zoom_text.setText('2')
        self.view.change_zoom()
        assert test_set.zoom == 2.0
        self.view.zoom_text.setText('1.00')
        qtbot.keyPress(self.view.zoom_text, QtCore.Qt.Key_Return)
        assert test_set.zoom == 1.0
        self.view.zoom_text.setText('foo')
        qtbot.keyPress(self.view.zoom_text, QtCore.Qt.Key_Return)
        assert test_set.zoom == 1.0

    def test_adjust_pan_size(self, qtbot, test_set):
        assert self.view.pan.xradius == 16.5
        assert self.view.pan.yradius == 32.5
        test_set._zoom = 2
        self.view.pan.x = 20
        self.view.pan.y = 30
        self.view.adjust_pan_size()
        assert self.view.pan.xradius == 8.5
        assert self.view.pan.yradius == 16.5
        assert test_set.center == (20, 30)
        test_set._zoom = 1
        self.view.adjust_pan_size()
        assert self.view.pan.xradius == 16.5
        assert self.view.pan.yradius == 32.5
        assert test_set.center == (16, 32)

    def test_change_center(self, qtbot, test_set):
        test_set.zoom = 2
        assert test_set.center == (16, 32)
        self.view.change_center(None, None, 20, 30)
        assert test_set.center == (20, 30)
        self.view.change_center(None, None, 8, 16)
        assert test_set.center == (8, 16)
        self.view.change_center(None, None, 16, 32)
        assert test_set.center == (16, 32)
        test_set.zoom = 1
        assert test_set.center == (16, 32)

    def test_move_pan(self, qtbot, test_set):
        test_set.zoom = 2
        test_set._center = (20, 30)
        assert self.view.pan.x == 16
        assert self.view.pan.y == 32
        self.view.move_pan()
        assert self.view.pan.x == 20
        assert self.view.pan.y == 30
        test_set._center = (16, 32)
        self.view.move_pan()
        assert self.view.pan.x == 16
        assert self.view.pan.y == 32
        test_set.zoom = 1


class TestPDSSpectViewWidget(object):
    image_set = PDSSpectImageSet(TEST_FILES)

    @pytest.fixture
    def view_widget(self):
        self.image_set = PDSSpectImageSet(TEST_FILES)
        return PDSSpectViewWidget(self.image_set)

    def test_init(self, view_widget):
        assert view_widget.image_set == self.image_set
        spect_view = view_widget.spect_views[0]
        assert view_widget.main_layout.itemAt(0).widget() == spect_view

    def test_create_spect_view(self, view_widget):
        subset = SubPDSSpectImageSet(self.image_set)
        spect_view = view_widget.create_spect_view(subset)
        spect_view == view_widget.spect_views[1]
        assert view_widget.main_layout.itemAt(1).widget() == spect_view
