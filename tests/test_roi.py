from . import FILE_1, TEST_FILES

import pytest
import numpy as np
from ginga.canvas.types import basic

from pdsspect.roi import Rectangle, Polygon, Pencil, ROIBase
from pdsspect.pdsspect_image_set import PDSSpectImageSet
from pdsspect.pds_image_view_canvas import PDSImageViewCanvas


def test_abstract_base_class():
    image_set = PDSSpectImageSet(TEST_FILES)
    view_canvas = PDSImageViewCanvas()
    with pytest.raises(TypeError):
        ROIBase(image_set, view_canvas)


class TestPolygon(object):
    image_set = PDSSpectImageSet([FILE_1])
    view_canvas = PDSImageViewCanvas()
    shape1 = [
        (2.5, 5.5), (4.5, 3.5), (6.5, 5.5), (6.5, 2.5), (2.5, 2.5)
    ]

    @pytest.mark.parametrize(
        'x, y, expected_x, expected_y',
        [
            (0, 0, -.5, -.5),
            (1023, 1023, 1022.5, 1022.5),
            (2.3, 2.3, 1.5, 1.5),
            (1.7, 2.3, 1.5, 1.5),
            (1.7, 1.7, 1.5, 1.5),
            (2.3, 1.7, 1.5, 1.5),
            (2.5, 3.5, 2.5, 3.5)
        ]
    )
    def test_lock_coords_to_pixel(self, x, y, expected_x, expected_y):
        poly = Polygon(self.image_set, self.view_canvas)
        assert poly.lock_coords_to_pixel(x, y) == (expected_x, expected_y)

    def test_contains_arr(self):
        poly = Polygon(self.image_set, self.view_canvas)
        poly.create_ROI(self.shape1)
        x1, y1, x2, y2 = poly.get_llur()
        x1, y1 = np.floor([x1, y1]).astype(int)
        x2, y2 = np.ceil([x2, y2]).astype(int)
        X, Y = np.mgrid[x1:x2, y1:y2]
        test_mask = np.array(
            [
                [False, False, False, False],
                [False, True, True, True],
                [False, True, True, False],
                [False, True, True, False],
                [False, True, True, True],
            ]
        )
        mask = poly.contains_arr(X, Y)
        assert np.array_equal(mask, test_mask)

    def test_move_by_delta(self):
        poly = Polygon(self.image_set, self.view_canvas)
        poly.create_ROI(self.shape1)
        rect_points = poly.get_points()
        for rect_point, point in zip(rect_points, self.shape1):
            assert rect_point == point
        with poly._temporary_move_by_delta((2, 3)) as moved_rect:
            moved_points = moved_rect.get_points()
            for moved_point, point in zip(moved_points, self.shape1):
                assert moved_point[0] == point[0] + 2
                assert moved_point[1] == point[1] + 3
        rect_points = poly.get_points()
        for rect_point, point in zip(rect_points, self.shape1):
            assert rect_point == point

    def test_start_ROI(self):
        poly = Polygon(self.image_set, self.view_canvas)
        assert poly._current_path is None
        poly.start_ROI(2.5, 3.5)
        assert isinstance(poly._current_path, basic.Path)
        assert poly._current_path in self.view_canvas.objects
        assert poly._current_path.get_points() == [(2.5, 3.5)]

    def test_current_ROI(self):
        poly = Polygon(self.image_set, self.view_canvas)
        poly.start_ROI(2.5, 3.5)
        poly._has_temp_point = True
        poly.continue_ROI(5.5, 4.5)
        assert poly._current_path.get_points() == [(5.5, 4.5), (2.5, 3.5)]
        assert not poly._has_temp_point

    def test_extend_ROI(self):
        poly = Polygon(self.image_set, self.view_canvas)
        poly.start_ROI(2.5, 3.5)
        poly._has_temp_point = False
        poly.extend_ROI(5.5, 4.5)
        assert poly._current_path.get_points() == [(5.5, 4.5), (2.5, 3.5)]
        assert poly._has_temp_point
        poly.extend_ROI(6.5, 5.5)
        assert poly._current_path.get_points() == [(6.5, 5.5), (2.5, 3.5)]

    def test_stop_ROI(self):
        poly = Polygon(self.image_set, self.view_canvas)
        poly.start_ROI(2.5, 3.5)
        poly.continue_ROI(2.5, 4.5)
        poly.continue_ROI(5.5, 3.5)
        poly.extend_ROI(3.5, 3.5)
        poly.stop_ROI(2.5, 3.5)
        assert poly._current_path not in self.view_canvas.objects
        assert poly._current_path.get_points() == [
            (5.5, 3.5), (2.5, 4.5), (2.5, 3.5)
        ]
        assert poly.get_data_points() == [
            (5.5, 3.5), (2.5, 4.5), (2.5, 3.5)
        ]

        poly.start_ROI(2.5, 3.5)
        poly.continue_ROI(2.5, 4.5)
        with pytest.warns(UserWarning):
            poly.stop_ROI(2.5, 3.5)


class TestRectangle(object):
    image_set = PDSSpectImageSet(TEST_FILES)
    view_canvas = PDSImageViewCanvas()

    def test_start_ROI(self):
        rect = Rectangle(self.image_set, self.view_canvas)
        assert rect._current_path is None
        rect.start_ROI(2.5, 3.5)
        assert isinstance(rect._current_path, basic.Rectangle)
        assert rect._current_path.x1 == 2.5
        assert rect._current_path.y1 == 3.5
        assert rect._current_path.x2 == 3.5
        assert rect._current_path.y2 == 4.5
        assert rect._current_path is not None
        assert rect._current_path in self.view_canvas.objects

    def test_extend_ROI(self):
        rect = Rectangle(self.image_set, self.view_canvas)
        rect.start_ROI(2.5, 3.5)
        rect.extend_ROI(2.5, 3.5)
        assert rect._current_path.x2 == 3.5
        assert rect._current_path.y2 == 4.5
        rect.extend_ROI(3.5, 3.5)
        assert rect._current_path.x2 == 4.5
        assert rect._current_path.y2 == 4.5
        rect.extend_ROI(3.5, 4.5)
        assert rect._current_path.x2 == 4.5
        assert rect._current_path.y2 == 5.5
        rect.extend_ROI(1.5, 3.5)
        assert rect._current_path.x2 == 1.5
        assert rect._current_path.y2 == 4.5
        rect.extend_ROI(1.5, 2.5)
        assert rect._current_path.x2 == 1.5
        assert rect._current_path.y2 == 2.5

    def test_stop_ROI(self):
        rect = Rectangle(self.image_set, self.view_canvas)
        rect.start_ROI(2.5, 3.5)
        assert rect._current_path in self.view_canvas.objects
        rect.extend_ROI(3.5, 4.5)
        rect.stop_ROI(3.5, 4.5)
        assert rect._current_path not in self.view_canvas.objects
        assert rect.get_data_points() == [
            (2.5, 3.5), (4.5, 3.5), (4.5, 5.5), (2.5, 5.5)
        ]


class TestPencil(object):
    image_set = PDSSpectImageSet(TEST_FILES)
    view_canvas = PDSImageViewCanvas()

    def test_start_ROI(self):
        pencil = Pencil(self.image_set, self.view_canvas)
        assert not pencil._current_path
        pencil.start_ROI(3.5, 1.5)
        assert isinstance(pencil._current_path[0], basic.Point)
        assert pencil._current_path[0] in self.view_canvas.objects
        assert pencil._current_path[0].x == 4
        assert pencil._current_path[0].y == 2

    def test_add_point(self):
        pencil = Pencil(self.image_set, self.view_canvas)
        pencil.start_ROI(3.5, 1.5)
        pencil._add_point(4.5, 6.5)
        assert len(pencil._current_path) == 2
        assert pencil._current_path[1].x == 5
        assert pencil._current_path[1].y == 7
        assert pencil._current_path[1] in self.view_canvas.objects

    def test_move_delta(self):
        pencil = Pencil(self.image_set, self.view_canvas)
        pencil.start_ROI(3.5, 1.5)
        pencil._add_point(4.5, 6.5)
        assert pencil._current_path[0].x == 4
        assert pencil._current_path[0].y == 2
        assert pencil._current_path[1].x == 5
        assert pencil._current_path[1].y == 7
        pencil.move_delta(-1, 3)
        assert pencil._current_path[0].x == 3
        assert pencil._current_path[0].y == 5
        assert pencil._current_path[1].x == 4
        assert pencil._current_path[1].y == 10

    def test_stop_ROI(self):
        pencil = Pencil(self.image_set, self.view_canvas)
        pencil.start_ROI(3.5, 1.5)
        pencil._add_point(4.5, 6.5)
        assert pencil._current_path[0] in self.view_canvas.objects
        assert pencil._current_path[1] in self.view_canvas.objects
        test_coords = pencil.stop_ROI(0, 0)
        assert pencil._current_path[0] not in self.view_canvas.objects
        assert pencil._current_path[1] not in self.view_canvas.objects
        assert np.array_equal(test_coords, np.array([[2, 4], [7, 5]]))
