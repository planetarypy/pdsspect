from . import *  # Import Test File Paths from __init__

import pytest
import numpy as np

from pdsspect.roi import Rectangle, Polygon, ROIBase
from pdsspect.pdsspect_image_set import PDSSPectImageSet
from pdsspect.pds_image_view_canvas import PDSImageViewCanvas


def test_abstract_base_class():
    image_set = PDSSPectImageSet(TEST_FILES)
    view_canvas = PDSImageViewCanvas()
    with pytest.raises(TypeError):
        ROIBase(image_set, view_canvas)


class TestPolygon(object):
    image_set = PDSSPectImageSet(TEST_FILES)
    view_canvas = PDSImageViewCanvas()
    rect = Polygon(image_set, view_canvas)
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
            (2.3, 1.7, 1.5, 1.5)
        ]
    )
    def test_lock_coords_to_pixel(self, x, y, expected_x, expected_y):
        assert self.rect.lock_coords_to_pixel(x, y) == (expected_x, expected_y)

    # def test_contains_arr(self):
    #     self.rect.create_ROI(self.shape1)
    #     x1, y1, x2, y2 = self.rect.get_llur()
    #     x1, y1 = np.floor([x1, y1]).astype(int)
    #     x2, y2 = np.ceil([x2, y2]).astype(int)
    #     X, Y = np.mgrid[x1:x2, y1:y2]
    #     test_mask = np.array(
    #         [
    #             [False, False, False, False],
    #             [False, True, True, True],
    #             [False, True, True, False],
    #             [False, True, True, False],
    #             [False, True, True, True],
    #         ]
    #     )
    #     assert np.array_equal(self.rect.contains_arr(X, Y), test_mask)
