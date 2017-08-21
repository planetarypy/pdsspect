from . import numpy as np
from . import FILE_1, TEST_FILES, reset_image_set

import pytest
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

    @pytest.fixture
    def poly(self):
        self.view_canvas = PDSImageViewCanvas()
        return Polygon(self.image_set, self.view_canvas)

    def test_top(self, poly):
        assert poly.top == self.image_set.current_image.shape[0] + 1.5

    def test_right(self, poly):
        assert poly.right == self.image_set.current_image.shape[1] - 0.5

    @pytest.mark.parametrize(
        'point, expected',
        [
            (-1, -0.5),
            (-0.5, -0.5),
            (-0.4, -0.5),
            (0, -0.5),
            (0.4, None),
            (0.5, None),
            (0.9, None),
            (1, 0.5),
            (1.1, 0.5),
        ]
    )
    def test_get_default_point_value(self, point, expected, poly):
        high_edege = 0.5
        default_point_value = poly._get_default_point_value(point, high_edege)
        if expected is None:
            assert default_point_value is None
        else:
            assert default_point_value == expected

    def test_get_default_data_values(self, poly):
        assert poly._get_default_data_values(-1, -1) == (-0.5, -0.5)
        assert poly._get_default_data_values(0, 0) == (-0.5, -0.5)
        x, y = poly.right - 1, poly.top - 1
        assert poly._get_default_data_values(x, y) == (None, None)
        x, y = poly.right, poly.top
        assert poly._get_default_data_values(x, y) == (None, None)
        x, y = poly.right + 0.5, poly.top + 0.5
        assert poly._get_default_data_values(x, y) == (poly.right, poly.top)
        x, y = poly.right + 1, poly.top + 1
        assert poly._get_default_data_values(x, y) == (poly.right, poly.top)

    @pytest.mark.parametrize(
        'coordinate, expected',
        [
            (2.3, 1.5),
            (1.7, 1.5),
            (2.5, 2.5),
        ]
    )
    def test_lock_coordinate_to_pixel(self, coordinate, expected, poly):
        assert poly._lock_coordinate_to_pixel(coordinate) == expected

    @pytest.mark.parametrize(
        'x, y, expected_x, expected_y',
        [
            (0, 0, -.5, -.5),
            (1023, 1023, 1023.5, 1023.5),
            (2.3, 2.3, 1.5, 1.5),
            (1.7, 2.3, 1.5, 1.5),
            (1.7, 1.7, 1.5, 1.5),
            (2.3, 1.7, 1.5, 1.5),
            (2.5, 3.5, 2.5, 3.5)
        ]
    )
    def test_lock_coords_to_pixel(self, x, y, expected_x, expected_y, poly):
        assert poly.lock_coords_to_pixel(x, y) == (expected_x, expected_y)

    def test_contains_arr(self, poly):
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

    def test_move_by_delta(self, poly):
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

    def test_start_ROI(self, poly):
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

    def test_extend_ROI(self, poly):
        poly.start_ROI(2.5, 3.5)
        poly._has_temp_point = False
        poly.extend_ROI(5.5, 4.5)
        assert poly._current_path.get_points() == [(5.5, 4.5), (2.5, 3.5)]
        assert poly._has_temp_point
        poly.extend_ROI(6.5, 5.5)
        assert poly._current_path.get_points() == [(6.5, 5.5), (2.5, 3.5)]

    def test_stop_ROI(self, poly):
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
    image_set = PDSSpectImageSet([FILE_1])
    view_canvas = PDSImageViewCanvas()

    @pytest.fixture
    def rect(self):
        reset_image_set(self.image_set)
        self.view_canvas = PDSImageViewCanvas()
        return Rectangle(self.image_set, self.view_canvas)

    def test_start_ROI(self, rect):
        assert rect._current_path is None
        rect.start_ROI(2.5, 3.5)
        assert isinstance(rect._current_path, basic.Rectangle)
        assert rect._current_path.x1 == 2.5
        assert rect._current_path.y1 == 3.5
        assert rect._current_path.x2 == 3.5
        assert rect._current_path.y2 == 4.5
        assert rect._current_path is not None
        assert rect._current_path in self.view_canvas.objects

    @pytest.mark.parametrize(
        'point, expected',
        [
            (1, (1, 3)),
            (2, (2, 3)),
            (3, (2, 4)),
            (4, (2, 4))
        ]
    )
    def test_extend_point(self, point, expected, rect):
        anchor_point = 2
        edge = 4
        extended_point = rect._extend_point(point, anchor_point, edge)
        assert expected == extended_point

    def test_extend_ROI(self, rect):
        rect.start_ROI(2.5, 3.5)
        rect.extend_ROI(2.5, 3.5)
        assert rect._current_path.x1 == 2.5
        assert rect._current_path.x2 == 3.5
        assert rect._current_path.y1 == 3.5
        assert rect._current_path.y2 == 4.5
        rect.extend_ROI(3.5, 3.5)
        assert rect._current_path.x1 == 2.5
        assert rect._current_path.x2 == 4.5
        assert rect._current_path.y1 == 3.5
        assert rect._current_path.y2 == 4.5
        rect.extend_ROI(3.5, 4.5)
        assert rect._current_path.x1 == 2.5
        assert rect._current_path.x2 == 4.5
        assert rect._current_path.y1 == 3.5
        assert rect._current_path.y2 == 5.5
        rect.extend_ROI(1.5, 3.5)
        assert rect._current_path.x1 == 1.5
        assert rect._current_path.x2 == 3.5
        assert rect._current_path.y1 == 3.5
        assert rect._current_path.y2 == 4.5
        rect.extend_ROI(1.5, 2.5)
        assert rect._current_path.x1 == 1.5
        assert rect._current_path.x2 == 3.5
        assert rect._current_path.y1 == 2.5
        assert rect._current_path.y2 == 4.5

    def test_stop_ROI(self, rect):
        rect.start_ROI(2.5, 3.5)
        assert rect._current_path in self.view_canvas.objects
        rect.extend_ROI(3.5, 4.5)
        rect.stop_ROI(3.5, 4.5)
        assert rect._current_path not in self.view_canvas.objects
        assert rect.get_data_points() == [
            (2.5, 3.5), (4.5, 3.5), (4.5, 5.5), (2.5, 5.5)
        ]


class TestPencil(object):
    image_set = PDSSpectImageSet([FILE_1])
    view_canvas = PDSImageViewCanvas()

    @pytest.fixture
    def pencil(self):
        self.image_set.zoom = 1.0
        self.view_canvas = PDSImageViewCanvas()
        return Pencil(self.image_set, self.view_canvas)

    def test_start_ROI(self, pencil):
        assert not pencil._current_path
        pencil.start_ROI(3.5, 1.5)
        assert isinstance(pencil._current_path[0], basic.Point)
        assert pencil._current_path[0] in self.view_canvas.objects
        assert pencil._current_path[0].x == 4
        assert pencil._current_path[0].y == 2

    def test_add_point(self, pencil):
        pencil.start_ROI(3.5, 1.5)
        pencil._add_point(4.5, 6.5)
        assert len(pencil._current_path) == 2
        assert pencil._current_path[1].x == 5
        assert pencil._current_path[1].y == 7
        assert pencil._current_path[1] in self.view_canvas.objects

    def test_move_delta(self, pencil):
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

    def test_fix_coordinate(self, pencil):
        assert pencil._fix_coordinate(1.7) == 2
        assert pencil._fix_coordinate(2.0) == 2
        assert pencil._fix_coordinate(2.3) == 2

    def test_stop_ROI(self, pencil):
        pencil.start_ROI(3.5, 1.5)
        pencil._add_point(4.5, 6.5)
        assert pencil._current_path[0] in self.view_canvas.objects
        assert pencil._current_path[1] in self.view_canvas.objects
        test_coords = pencil.stop_ROI(0, 0)
        assert pencil._current_path[0] not in self.view_canvas.objects
        assert pencil._current_path[1] not in self.view_canvas.objects
        # The order may be different due to using set
        try:
            assert np.array_equal(test_coords, np.array([[2, 4], [7, 5]]))
        except AssertionError:
            assert np.array_equal(test_coords, np.array([[7, 5], [2, 4]]))
        self.image_set.zoom = 2.0
        x, y = self.image_set.center
        self.image_set.center = (x + 5.2, y + 5.7)
        pencil.start_ROI(3.5, 1.5)
        pencil._add_point(4.5, 6.5)
        test_coords = pencil.stop_ROI(0, 0)
        # The order may be different due to using set
        try:
            assert np.array_equal(
                test_coords,
                np.array([[269, 266], [264, 265]])
            )
        except AssertionError:
            assert np.array_equal(
                test_coords,
                np.array([[264, 265], [269, 266]])
            )
