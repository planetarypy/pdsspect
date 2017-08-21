from . import numpy as np
from . import FILE_1, reset_image_set

import pytest

from pdsspect.roi import Rectangle, Polygon
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

    @pytest.fixture
    def view(self, qtbot):
        reset_image_set(self.image_set)
        view = PanView(self.image_set)
        view.show()
        qtbot.add_widget(view)
        return view

    def test_is_erasing(self, view):
        assert not view.is_erasing
        self.image_set.current_color_index = 14
        assert view.is_erasing
        self.image_set.current_color_index = 0
        assert not view.is_erasing

    def test_set_data(self, view):
        assert np.array_equal(
            view.view_canvas.get_image().get_data(),
            self.image_set.pan_data)
        self.image_set._zoom = 2
        assert not np.array_equal(
            view.view_canvas.get_image().get_data(),
            self.image_set.pan_data)
        view.set_data()
        assert np.array_equal(
            view.view_canvas.get_image().get_data(),
            self.image_set.pan_data)
        self.image_set._zoom = 1
        view.set_data()
        assert np.array_equal(
            view.view_canvas.get_image().get_data(),
            self.image_set.pan_data)

    def test_set_roi_data(self, view):
        assert np.array_equal(
            self.image_set._maskrgb.get_data(),
            self.image_set.pan_roi_data)
        self.image_set._zoom = 2
        assert not np.array_equal(
            self.image_set._maskrgb.get_data(),
            self.image_set.pan_roi_data)
        view.set_data()
        assert np.array_equal(
            self.image_set._maskrgb.get_data(),
            self.image_set.pan_roi_data)
        self.image_set._zoom = 1
        view.set_data()
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
    def test_make_x_y_in_pan(self, pre_x, pre_y, expected_x, expected_y, view):
        post_x, post_y = view._make_x_y_in_pan(pre_x, pre_y)
        assert post_x == expected_x
        assert post_y == expected_y

    def test_start_ROI(self, view):
        assert not view._making_roi
        assert view._current_roi is None
        view.start_ROI(view.view_canvas, None, 512, 512)
        assert view._making_roi
        assert view._current_roi is not None
        assert self.image_set.selection_type == 'filled rectangle'
        assert isinstance(view._current_roi, Rectangle)
        view._making_roi = False
        view._current_roi = None
        self.image_set._selection_index = 1
        assert self.image_set.selection_type == 'filled polygon'
        view.start_ROI(view.view_canvas, None, 512, 512)
        assert view._making_roi
        assert view._current_roi is not None
        assert self.image_set.selection_type == 'filled polygon'
        assert isinstance(view._current_roi, Polygon)
        view._making_roi = False
        view._current_roi = None
        self.image_set._selection_index = 2
        assert self.image_set.selection_type == 'pencil'
        view.start_ROI(view.view_canvas, None, 512, 512)
        # Pencil ROIs stop directly after starting
        assert not view._making_roi
        assert view._current_roi is None
        assert self.image_set.selection_type == 'pencil'
        self.image_set._selection_index = 0
        assert self.image_set.selection_type == 'filled rectangle'
        view.start_ROI(view.view_canvas, None, 512, 512)
        assert view._making_roi
        assert view._current_roi is not None
        assert self.image_set.selection_type == 'filled rectangle'
        assert isinstance(view._current_roi, Rectangle)
        view._making_roi = False
        view._current_roi = None

    def test_continue_ROI(self, view):
        assert not view._making_roi
        assert view._current_roi is None
        view.start_ROI(view.view_canvas, None, 512, 512)
        assert view._making_roi
        assert view._current_roi is not None
        view.continue_ROI(None, None, 514, 514)
        assert not view._making_roi
        assert view._current_roi is None
        self.image_set._selection_index = 1
        assert self.image_set.selection_type == 'filled polygon'
        view.start_ROI(view.view_canvas, None, 512, 512)
        assert view._making_roi
        assert view._current_roi is not None
        # Make sure to continue ROI even when start_ROI is called
        view.start_ROI(None, None, 514, 514)
        assert view._making_roi
        assert view._current_roi is not None
        view._making_roi = False
        view._current_roi = None

    def test_extend_ROI(self, view):
        assert not view._making_roi
        assert view._current_roi is None
        view.start_ROI(view.view_canvas, None, 512, 512)
        assert view._making_roi
        assert view._current_roi is not None
        view.extend_ROI(None, None, 514, 514)
        assert view._making_roi
        assert view._current_roi is not None

    def test_stop_ROI(self, view):
        assert not view._making_roi
        assert view._current_roi is None
        view.start_ROI(view.view_canvas, None, 512, 512)
        assert view._making_roi
        assert view._current_roi is not None
        view.stop_ROI(view.view_canvas, None, 512, 512)
        assert not view._making_roi
        assert view._current_roi is None
        assert self.image_set.get_coordinates_of_color('red') == ([513], [513])
        self.image_set.current_color_index = 14
        assert self.image_set.color == 'eraser'
        view.start_ROI(view.view_canvas, None, 512, 512)
        assert view._making_roi
        assert view._current_roi is not None
        view.stop_ROI(view.view_canvas, None, 512, 512)
        assert not view._making_roi
        assert view._current_roi is None
        assert np.array_equal(
            self.image_set.get_coordinates_of_color('red'),
            (np.array([]), np.array([])))


class TestPanViewWidget(object):
    image_set = PDSSpectImageSet([FILE_1])
    pan = PanView(image_set)

    @pytest.fixture
    def pan_widget(self):
        reset_image_set(self.image_set)
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
