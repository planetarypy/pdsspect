from functools import wraps

from . import FILE_1

import pytest
import numpy as np

from pdsspect.roi import Rectangle, Polygon, Pencil
from pdsspect.pan_view import PanViewController, PanView, PanViewWidget
from pdsspect.pdsspect_image_set import PDSSpectImageSet, SubPDSSpectImageSet


class TestPanViewController(object):
    image_set = PDSSpectImageSet([FILE_1])
    controller = PanViewController(image_set, None)
    default_roi_data = image_set._roi_data.copy()

    @pytest.fixture
    def test_set(self):
        yield self.image_set
        self.image_set._roi_data = self.default_roi_data
        self.image_set._alpha = 1
        self.image_set._subsets = []

    def test_get_parent_set(self, test_set):
        subset = test_set.create_subset()
        assert self.controller._get_parent_set() == test_set
        controller2 = PanViewController(subset, None)
        assert controller2._get_parent_set() == test_set

    def test_add_ROI(self, test_set):
        subset = test_set.create_subset()
        assert test_set.current_color_index == 0
        assert test_set.color == 'red'
        coords = np.array([[42, 42]])
        rows, cols = np.column_stack(coords)
        assert np.array_equal(
            test_set._roi_data[rows, cols],
            np.array([[0.0, 0.0, 0.0, 0.0]])
        )
        assert np.array_equal(
            subset._roi_data[rows, cols],
            np.array([[0.0, 0.0, 0.0, 0.0]])
        )

        self.image_set.alpha = 1
        self.controller.add_ROI(coords)
        assert np.array_equal(
            self.image_set._roi_data[rows, cols],
            np.array([[255.0, 0.0, 0.0, 255.]])
        )
        assert np.array_equal(
            subset._roi_data[rows, cols],
            np.array([[0.0, 0.0, 0.0, 0.0]])
        )

        self.image_set.alpha = .75
        self.image_set.current_color_index = 1
        self.controller.add_ROI(coords)
        assert np.array_equal(
            self.image_set._roi_data[rows, cols],
            np.array([[165.0, 42.0, 42.0, 191.25]])
        )
        assert np.array_equal(
            subset._roi_data[rows, cols],
            np.array([[0.0, 0.0, 0.0, 0.0]])
        )

        self.image_set.alpha = .25
        self.image_set.current_color_index = 13
        self.controller.add_ROI(coords)
        assert np.array_equal(
            self.image_set._roi_data[rows, cols],
            np.array([[160.0, 32.0, 240.0, 63.75]])
        )
        assert np.array_equal(
            subset._roi_data[rows, cols],
            np.array([[0.0, 0.0, 0.0, 0.0]])
        )

        self.image_set.alpha = 1
        self.image_set.current_color_index = 0
        test_set.simultaneous_roi = True
        self.controller.add_ROI(coords)
        assert np.array_equal(
            self.image_set._roi_data[rows, cols],
            np.array([[255.0, 0.0, 0.0, 255.0]])
        )
        assert np.array_equal(
            subset._roi_data[rows, cols],
            np.array([[255.0, 0.0, 0.0, 255.0]])
        )
        self.image_set.current_color_index = 1
        test_set.simultaneous_roi = False
        self.controller.add_ROI(coords)
        assert np.array_equal(
            self.image_set._roi_data[rows, cols],
            np.array([[165.0, 42.0, 42.0, 255.0]])
        )
        assert np.array_equal(
            subset._roi_data[rows, cols],
            np.array([[255.0, 0.0, 0.0, 255.0]])
        )

    def test_erase_ROI(self, test_set):
        subset = test_set.create_subset()
        coords = np.array([[42, 42]])
        rows, cols = np.column_stack(coords)
        test_set.add_coords_to_roi_data_with_color(coords, 'red')
        subset.add_coords_to_roi_data_with_color(coords, 'red')
        assert np.array_equal(
            test_set._roi_data[rows, cols],
            np.array([[255.0, 0.0, 0.0, 255.0]])
        )
        assert np.array_equal(
            subset._roi_data[rows, cols],
            np.array([[255.0, 0.0, 0.0, 255.0]])
        )
        self.controller.erase_ROI(coords)
        assert np.array_equal(
            test_set._roi_data[rows, cols],
            np.array([[0.0, 0.0, 0.0, 0.0]])
        )
        assert np.array_equal(
            subset._roi_data[rows, cols],
            np.array([[255.0, 0.0, 0.0, 255.0]])
        )
        test_set.add_coords_to_roi_data_with_color(coords, 'brown')
        assert np.array_equal(
            test_set._roi_data[rows, cols],
            np.array([[165.0, 42.0, 42.0, 255.0]])
        )
        self.controller.erase_ROI(coords)
        assert np.array_equal(
            test_set._roi_data[rows, cols],
            np.array([[0.0, 0.0, 0.0, 0.0]])
        )
        test_set.simultaneous_roi = True
        test_set.add_coords_to_roi_data_with_color(coords, 'red')
        subset.add_coords_to_roi_data_with_color(coords, 'red')
        self.controller.erase_ROI(coords)
        assert np.array_equal(
            test_set._roi_data[rows, cols],
            np.array([[0.0, 0.0, 0.0, 0.0]])
        )
        assert np.array_equal(
            subset._roi_data[rows, cols],
            np.array([[0.0, 0.0, 0.0, 0.0]])
        )


class TestPanView(object):
    image_set = PDSSpectImageSet([FILE_1])
    view = PanView(image_set)

    def add_view_to_qtbot(func):
        @wraps(func)
        def wrapper(self, qtbot):
            self.view.show()
            qtbot.add_widget(self.view)
            return func(self, qtbot)
        return wrapper

    def test_is_erasing(self):
        assert not self.view.is_erasing
        self.image_set.current_color_index = 14
        assert self.view.is_erasing
        self.image_set.current_color_index = 0
        assert not self.view.is_erasing

    @add_view_to_qtbot
    def test_set_data(self, qtbot):
        assert np.array_equal(
            self.view.view_canvas.get_image().get_data(),
            self.image_set.pan_data)
        self.image_set._zoom = 2
        assert not np.array_equal(
            self.view.view_canvas.get_image().get_data(),
            self.image_set.pan_data)
        self.view.set_data()
        assert np.array_equal(
            self.view.view_canvas.get_image().get_data(),
            self.image_set.pan_data)
        self.image_set._zoom = 1
        self.view.set_data()
        assert np.array_equal(
            self.view.view_canvas.get_image().get_data(),
            self.image_set.pan_data)

    @add_view_to_qtbot
    def test_set_roi_data(self, qtbot):
        assert np.array_equal(
            self.image_set._maskrgb.get_data(),
            self.image_set.pan_roi_data)
        self.image_set._zoom = 2
        assert not np.array_equal(
            self.image_set._maskrgb.get_data(),
            self.image_set.pan_roi_data)
        self.view.set_data()
        assert np.array_equal(
            self.image_set._maskrgb.get_data(),
            self.image_set.pan_roi_data)
        self.image_set._zoom = 1
        self.view.set_data()
        assert np.array_equal(
            self.image_set._maskrgb.get_data(),
            self.image_set.pan_roi_data)

    @pytest.mark.parametrize(
        'pre_x, pre_y, expected_x, expected_y',
        [
            (512, 512, 512, 512),
            (-.5, -.5, -.5, -.5),
            (1023, -.5, 1023, -.5),
            (-.5, 1023, -.5, 1023),
            (1023, 1023, 1023, 1023),
            (-.6, -.6, -.5, -.5),
            (1024, -.6, 1023, -.5),
            (-.6, 1024, -.5, 1023),
            (1024, 1024, 1023, 1023),
        ]
    )
    def test_make_x_y_in_pan(self, pre_x, pre_y, expected_x, expected_y):
        post_x, post_y = self.view._make_x_y_in_pan(pre_x, pre_y)
        assert post_x == expected_x
        assert post_y == expected_y

    @add_view_to_qtbot
    def test_start_ROI(self, qtbot):
        assert not self.view._making_roi
        assert self.view._current_roi is None
        self.view.start_ROI(self.view.view_canvas, None, 512, 512)
        assert self.view._making_roi
        assert self.view._current_roi is not None
        assert self.image_set.selection_type == 'filled rectangle'
        assert isinstance(self.view._current_roi, Rectangle)
        self.view._making_roi = False
        self.view._current_roi = None
        self.image_set._selection_index = 1
        assert self.image_set.selection_type == 'filled polygon'
        self.view.start_ROI(self.view.view_canvas, None, 512, 512)
        assert self.view._making_roi
        assert self.view._current_roi is not None
        assert self.image_set.selection_type == 'filled polygon'
        assert isinstance(self.view._current_roi, Polygon)
        self.view._making_roi = False
        self.view._current_roi = None
        self.image_set._selection_index = 2
        assert self.image_set.selection_type == 'pencil'
        self.view.start_ROI(self.view.view_canvas, None, 512, 512)
        assert self.view._making_roi
        assert self.view._current_roi is not None
        assert self.image_set.selection_type == 'pencil'
        assert isinstance(self.view._current_roi, Pencil)
        self.view._making_roi = False
        self.view._current_roi = None
        self.image_set._selection_index = 0
        assert self.image_set.selection_type == 'filled rectangle'
        self.view.start_ROI(self.view.view_canvas, None, 512, 512)
        assert self.view._making_roi
        assert self.view._current_roi is not None
        assert self.image_set.selection_type == 'filled rectangle'
        assert isinstance(self.view._current_roi, Rectangle)
        self.view._making_roi = False
        self.view._current_roi = None


class TestPanViewWidget(object):
    image_set = PDSSpectImageSet([FILE_1])
    pan = PanView(image_set)

    @pytest.fixture
    def pan_widget(self):
        self.image_set = PDSSpectImageSet([FILE_1])
        self.pan = PanView(self.image_set)
        return PanViewWidget(self.pan, None)

    def test_init(self, pan_widget):
        assert len(pan_widget.pans) == 1
        assert pan_widget.pans[0] == self.pan
        assert pan_widget.main_layout.itemAt(0).widget() == self.pan

    def test_add_pan(self, pan_widget):
        subset = SubPDSSpectImageSet(self.image_set)
        pan2 = PanView(subset)
        pan_widget.add_pan(pan2)
        assert pan_widget.pans[1] == pan2
        assert pan_widget.main_layout.itemAt(1).widget() == pan2
