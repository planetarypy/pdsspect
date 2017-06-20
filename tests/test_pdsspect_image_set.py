from functools import wraps

from . import *  # Import Test File Paths from __init__

import pytest
import numpy as np
from ginga.util.dp import masktorgb
from ginga.RGBImage import RGBImage
from ginga.canvas.types.image import Image

from pdsspect.pdsspect_image_set import (
    ImageStamp, PDSSPectImageSet, ginga_colors
)


def test_ImageStamp():
    test_stamp = ImageStamp(FILE_1)
    assert isinstance(test_stamp, ImageStamp)
    assert np.array_equal(test_stamp.get_data(), test_stamp.pds_image.image)
    assert not test_stamp.seen
    assert test_stamp.cuts == (None, None)


class TestPDSSPectImageSet(object):
    test_set = PDSSPectImageSet(TEST_FILES)

    def reset_test_set_state(self):
        self.test_set._current_image_index = 0
        self.test_set.current_color_index = 0
        self.test_set._selection_index = 0
        self.test_set._zoom = 1.0
        self.test_set._center = None
        self.test_set.rois = {
            color: np.array([]) for color in self.test_set.colors
        }
        self.test_set._delta_x = 0
        self.test_set._delta_y = 0
        self.test_set._last_zoom = 1.0
        self.test_set._move_rois = True
        self.test_set._alpha = 1.0
        self.test_set._flip_x = False
        self.test_set._flip_y = False
        self.test_set._swap_xy = False
        mask = np.zeros(self.test_set.current_image.shape, dtype=np.bool)
        self.test_set._maskrgb = masktorgb(
            mask, self.test_set.color, self.test_set.alpha)
        self.test_set._roi_data = self.test_set._maskrgb.get_data().astype(
            float)
        self.test_set._maskrgb_obj = Image(0, 0, self.test_set._maskrgb)

    def ensure_correct_state(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.reset_test_set_state()
            result = func(self, *args, **kwargs)
            self.reset_test_set_state()
            return result
        return wrapper

    def test_init(self):
        test_set = self.test_set
        assert test_set._views == []
        assert isinstance(test_set, PDSSPectImageSet)
        assert len(test_set.images) == 5
        for image in test_set.images:
            assert isinstance(image, ImageStamp)
        assert test_set.filepaths == TEST_FILES
        assert test_set._current_image_index == 0
        assert isinstance(test_set._current_image_index, int)
        assert test_set._zoom == 1.0
        assert isinstance(test_set._zoom, float)
        assert test_set._center is None
        assert test_set._selection_index == 0
        assert isinstance(test_set._selection_index, int)
        assert test_set.current_color_index == 0
        assert isinstance(test_set.current_color_index, int)
        # assert isinstance(test_set.rois, dict)
        assert test_set._delta_x == 0
        assert test_set._delta_y == 0
        assert test_set._last_zoom == 1.0
        assert test_set._move_rois
        assert test_set._alpha == 1.0
        assert isinstance(test_set._alpha, float)
        assert not test_set._flip_x
        assert not test_set._flip_y
        assert not test_set._swap_xy
        assert isinstance(test_set._maskrgb, RGBImage)
        assert not test_set._roi_data.any()
        assert isinstance(test_set._maskrgb_obj, Image)

    @ensure_correct_state
    def test_register(self):
        assert self.test_set._views == []
        self.test_set.register('foo')
        assert 'foo' in self.test_set._views

    @ensure_correct_state
    def test_unregister(self):
        self.test_set._views = ['foo']
        assert 'foo' in self.test_set._views
        self.test_set.unregister('foo')
        assert 'foo' not in self.test_set._views
        assert self.test_set._views == []

    def test_filenames(self):
        assert self.test_set.filenames == TEST_FILE_NAMES

    @ensure_correct_state
    def test_current_image_index(self):
        test_set = self.test_set
        assert test_set._current_image_index == test_set.current_image_index
        test_set.current_image_index = 2
        assert test_set._current_image_index == test_set.current_image_index
        assert test_set._current_image_index == 2
        test_set.current_image_index = 1
        assert test_set._current_image_index == test_set.current_image_index
        assert test_set._current_image_index == 1

    @ensure_correct_state
    def test_current_image(self):
        test_indices = [0, 1, 2, 3, 4, 0]
        for index in test_indices:
            self.test_set.current_image_index = index
            test_current_image = self.test_set.images[index]
            assert test_current_image == self.test_set.current_image

    @pytest.mark.parametrize(
        'index, color, rgb',
        [
            (0, 'red', (1.0, 0.0, 0.0)),
            (1, 'brown', (0.6471, 0.1647, 0.1647)),
            (2, 'lightblue', (0.6784, 0.8471, 0.902)),
            (3, 'lightcyan', (0.8784, 1.0, 1.0)),
            (4, 'darkgreen', (0.0, 0.3922, 0.0)),
            (5, 'yellow', (1.0, 1.0, 0.0)),
            (6, 'pink', (1.0, 0.7529, 0.7961)),
            (7, 'teal', (0.0, 0.502, 0.502)),
            (8, 'goldenrod', (0.8549, 0.6471, 0.1255)),
            (9, 'sienna', (0.6275, 0.3216, 0.1765)),
            (10, 'darkblue', (0.0, 0.0, 0.5451)),
            (11, 'crimson', (0.8628, 0.0784, 0.2353)),
            (12, 'maroon', (0.6902, 0.1882, 0.3765)),
            (13, 'purple', (0.6275, 0.1255, 0.9412)),
            (14, 'eraser', (0.0, 0.0, 0.0)),
        ]
    )
    @ensure_correct_state
    def test_color(self, index, color, rgb):
        self.test_set.current_color_index = index
        assert self.test_set.color == color
        test_rgb = ginga_colors.lookup_color(color)
        for val, test_val in zip(rgb, test_rgb):
            assert val == round(test_val, 4)

    @pytest.mark.parametrize(
        'index, expected',
        [
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 0),
            (4, 1),
            (5, 2),
            (6, 0),
            (-1, 2),
            (-2, 1),
            (-3, 0),
            (-4, 2),
        ]
    )
    @ensure_correct_state
    def test_selection_index(self, index, expected):
        test_set = self.test_set
        test_set.selection_index = index
        assert test_set._selection_index == expected
        assert test_set._selection_index == test_set.selection_index

    @pytest.mark.parametrize(
        'index, expected',
        [
            (0, 'filled rectangle'),
            (1, 'filled polygon'),
            (2, 'pencil'),
            (3, 'filled rectangle'),
            (4, 'filled polygon'),
            (5, 'pencil'),
            (6, 'filled rectangle'),
            (-1, 'pencil'),
            (-2, 'filled polygon'),
            (-3, 'filled rectangle'),
            (-4, 'pencil'),
            (0, 'filled rectangle'),
        ]
    )
    @ensure_correct_state
    def test_selection_type(self, index, expected):
        self.test_set.selection_index = index
        assert self.test_set.selection_type == expected

    @ensure_correct_state
    def test_zoom(self):
        assert self.test_set._zoom == 1.0
        assert self.test_set._zoom == self.test_set.zoom
        self.test_set.zoom = 42.0
        assert self.test_set._zoom == 42.0
        assert self.test_set._zoom == self.test_set.zoom
        assert self.test_set._last_zoom == 1.0
        with pytest.raises(ValueError):
            self.test_set.zoom = -42.0
        self.test_set.zoom = 1.0
        assert self.test_set._zoom == 1.0
        assert self.test_set._zoom == self.test_set.zoom
        assert self.test_set._last_zoom == 42.0
        self.test_set._last_zoom = 1.0
        assert self.test_set._last_zoom == 1.0

    def test_x_radius(self):
        test_x_radius = 512
        assert self.test_set.current_image.shape[1] == 1024
        assert self.test_set.x_radius == test_x_radius

    def test_y_radius(self):
        test_y_radius = 512
        assert self.test_set.current_image.shape[0] == 1024
        assert self.test_set.y_radius == test_y_radius

    @pytest.mark.parametrize(
        'zoom, expected',
        [
            (1.0, 512),
            (2.0, 256),
            (4.0, 128),
        ]
    )
    @ensure_correct_state
    def test_pan_width(self, zoom, expected):
        self.test_set.zoom = zoom
        assert self.test_set.pan_width == expected

    @ensure_correct_state
    def test_last_pan_width(self):
        assert self.test_set._last_pan_width == 512
        self.test_set.zoom = 2.0
        assert self.test_set._last_pan_width == 512
        self.test_set.zoom = 1.0
        assert self.test_set._last_pan_width == 256

    @pytest.mark.parametrize(
        'zoom, expected',
        [
            (1.0, 512),
            (2.0, 256),
            (4.0, 128),
        ]
    )
    @ensure_correct_state
    def test_pan_height(self, zoom, expected):
        self.test_set.zoom = zoom
        assert self.test_set.pan_height == expected

    @ensure_correct_state
    def test_last_pan_height(self):
        self.test_set.zoom = 1.0
        self.test_set._last_zoom = 1.0
        assert self.test_set._last_pan_height == 512
        self.test_set.zoom = 2.0
        assert self.test_set._last_pan_height == 512
        self.test_set.zoom = 1.0
        assert self.test_set._last_pan_height == 256

    def test_reset_center(self):
        test_center = (512, 512)
        assert self.test_set._center is None
        self.test_set.reset_center()
        assert self.test_set._center == test_center
        self.test_set._center = None
        assert self.test_set._center is None

    @pytest.mark.parametrize(
        'point, expected',
        [
            ((512, 512), True),
            ((-.5, -.5), True),
            ((-.5, 1024.5), True),
            ((1024.5, -.5), True),
            ((1024.5, 1024.5), True),
            ((-.6, -.5), False),
            ((-.5, -.6), False),
            ((-.6, -.6), False),
            ((1024.6, -.5), False),
            ((-.5, 1024.6), False),
            ((1024.6, 1024.6), False),
        ]
    )
    def test_point_is_in_image(self, point, expected):
        assert self.test_set._point_is_in_image(point) is expected

    @pytest.mark.parametrize(
        'zoom, x, expected',
        [
            (1, 512, 512),
            (2, 256, 256),
            (2, -.5, 256),
            (2, 768, 768),
            (2, 1024.5, 768),
            (4, 128, 128),
            (4, -.5, 128),
            (4, 896, 896),
            (4, 896, 896),
            (1, 512, 512),
            (1, 512, 512),
        ]
    )
    def test_determine_center_x(self, zoom, x, expected):
        self.test_set.zoom = zoom
        assert self.test_set._determine_center_x(x) == expected

    @pytest.mark.parametrize(
        'zoom, y, expected',
        [
            (1, 512, 512),
            (2, 256, 256),
            (2, -.5, 256),
            (2, 768, 768),
            (2, 1024.5, 768),
            (4, 128, 128),
            (4, -.5, 128),
            (4, 896, 896),
            (4, 896, 896),
            (1, 512, 512),
            (1, 512, 512),
        ]
    )
    def test_determine_center_y(self, zoom, y, expected):
        self.test_set.zoom = zoom
        assert self.test_set._determine_center_y(y) == expected

    @pytest.mark.parametrize(
        'zoom, center, expected',
        [
            (1, (512, 512), (512, 512)),
            (1, (511, 511), (512, 512)),
            (1, (513, 513), (512, 512)),
            (1, (512, 511), (512, 512)),
            (1, (513, 512), (512, 512)),
            (2, (256, 256), (256, 256)),
            (2, (255, 256), (256, 256)),
            (2, (256, 255), (256, 256)),
            (2, (768, 768), (768, 768)),
            (2, (769, 768), (768, 768)),
            (2, (768, 769), (768, 768)),
            (4, (128, 128), (128, 128)),
            (4, (127, 128), (128, 128)),
            (4, (128, 127), (128, 128)),
            (4, (896, 896), (896, 896)),
            (4, (897, 896), (896, 896)),
            (4, (896, 897), (896, 896)),
            (1, (512, 512), (512, 512)),
            (1, (512, 512), (512, 512)),
        ]
    )
    @ensure_correct_state
    def test_center1(self, zoom, center, expected):
        self.test_set.zoom = zoom
        self.test_set.center = center
        assert self.test_set.center == expected
        assert self.test_set._center == expected

    @ensure_correct_state
    def test_center2(self):
        assert self.test_set._delta_x == 0
        assert self.test_set._delta_y == 0
        assert self.test_set.center == (512, 512)
        self.test_set.zoom = 2
        assert self.test_set.center == (512, 512)
        self.test_set.center = (513, 512)
        assert self.test_set._delta_x == -1
        assert self.test_set._delta_y == 0
        self.test_set.center = (513, 513)
        assert self.test_set._delta_x == 0
        assert self.test_set._delta_y == -1
        self.test_set.center = (613, 613)
        assert self.test_set._delta_x == -100
        assert self.test_set._delta_y == -100
        self.test_set.center = (513, 513)
        assert self.test_set._delta_x == 100
        assert self.test_set._delta_y == 100
        self.test_set.center = (255, 769)
        assert self.test_set.center == (256, 768)
        assert self.test_set._delta_x == 257
        assert self.test_set._delta_y == -255
        self.test_set.center = (769, 255)
        assert self.test_set.center == (768, 256)
        assert self.test_set._delta_x == -512
        assert self.test_set._delta_y == 512
        self.test_set._move_rois = False
        self.test_set.center = (512, 512)
        assert self.test_set._delta_x == 0
        assert self.test_set._delta_y == 0

    @pytest.mark.parametrize(
        'alpha, expected',
        [
            (1., 255.),
            (.75, 191.25),
            (.5, 127.5),
            (.25, 63.75),
        ]
    )
    @ensure_correct_state
    def test_alpha255(self, alpha, expected):
        self.test_set._alpha = alpha
        assert self.test_set.alpha255 == expected

    @pytest.mark.parametrize(
        'alpha, alpha255',
        [
            (1., 255.),
            (.75, 191.25),
            (.5, 127.5),
            (.25, 63.75),
        ]
    )
    @ensure_correct_state
    def test_alpha(self, alpha, alpha255):
        red_coords = np.array([[0, 0], [512, 512]])
        for red_coord in red_coords:
            row, col = red_coord
            assert self.test_set._roi_data[row, col, 3] == 0
        self.test_set.rois['red'] = red_coords
        self.test_set.alpha = alpha
        assert self.test_set._alpha == alpha
        assert self.test_set._alpha == self.test_set.alpha
        for red_coord in red_coords:
            row, col = red_coord
            assert self.test_set._roi_data[row, col, 3] == alpha255

    @ensure_correct_state
    def test_flip_x(self):
        assert self.test_set._flip_x == self.test_set.flip_x
        self.test_set.flip_x = True
        assert self.test_set._flip_x
        assert self.test_set._flip_x == self.test_set.flip_x

    @ensure_correct_state
    def test_flip_y(self):
        assert self.test_set._flip_y == self.test_set.flip_y
        self.test_set.flip_y = True
        assert self.test_set._flip_y
        assert self.test_set._flip_y == self.test_set.flip_y

    @ensure_correct_state
    def test_swap_xy(self):
        assert self.test_set._swap_xy == self.test_set.swap_xy
        self.test_set.swap_xy = True
        assert self.test_set._swap_xy
        assert self.test_set._swap_xy == self.test_set.swap_xy

    @ensure_correct_state
    def test_transforms(self):
        assert self.test_set.transforms == (False, False, False)
        self.test_set.flip_x = True
        assert self.test_set.transforms == (True, False, False)
        self.test_set.flip_y = True
        assert self.test_set.transforms == (True, True, False)
        self.test_set.swap_xy = True
        assert self.test_set.transforms == (True, True, True)

    @ensure_correct_state
    def test_rois_iterator(self):
        assert self.test_set.rois_iterator == []
        red_arr = np.array([[1, 2], [3, 4]])
        self.test_set.rois['red'] = red_arr
        assert np.array_equal(self.test_set.rois_iterator, [red_arr])
        brown_arr = np.array([[5, 6]])
        self.test_set.rois['brown'] = brown_arr
        # Have to use try statement to account for random order of dicts
        try:
            assert np.array_equal(self.test_set.rois_iterator[0], brown_arr)
            assert np.array_equal(self.test_set.rois_iterator[1], red_arr)
        except AssertionError:
            assert np.array_equal(self.test_set.rois_iterator[1], brown_arr)
            assert np.array_equal(self.test_set.rois_iterator[0], red_arr)

    @pytest.mark.parametrize(
        'zoom, center, expected',
        [
            (1, (512, 512), (0, 0, 1024, 1024)),
            (2, (256, 256), (0, 0, 512, 512)),
            (2, (768, 768), (512, 512, 1024, 1024)),
            (4, (128, 128), (0, 0, 256, 256)),
            (4, (896, 896), (768, 768, 1024, 1024)),
        ]
    )
    @ensure_correct_state
    def test_edges(self, zoom, center, expected):
        self.test_set.zoom = zoom
        self.test_set.center = center
        assert self.test_set.edges == expected

    @pytest.mark.parametrize(
        'zoom, center, edges',
        [
            (1, (512, 512), (0, 0, 1024, 1024)),
            (2, (256, 256), (0, 0, 512, 512)),
            (2, (768, 768), (512, 512, 1024, 1024)),
            (4, (128, 128), (0, 0, 256, 256)),
            (4, (896, 896), (768, 768, 1024, 1024)),
        ]
    )
    @ensure_correct_state
    def test_pan_slice(self, zoom, center, edges):
        self.test_set.zoom = zoom
        self.test_set.center = center
        x1, y1, x2, y2 = edges
        assert np.array_equal(self.test_set.pan_slice, np.s_[y1:y2:1, x1:x2:1])

    @pytest.mark.parametrize(
        'zoom, center, edges',
        [
            (1, (512, 512), (0, 0, 1024, 1024)),
            (2, (256, 256), (0, 0, 512, 512)),
            (2, (768, 768), (512, 512, 1024, 1024)),
            (4, (128, 128), (0, 0, 256, 256)),
            (4, (896, 896), (768, 768, 1024, 1024)),
        ]
    )
    @ensure_correct_state
    def test_pan_data(self, zoom, center, edges):
        self.test_set.zoom = zoom
        self.test_set.center = center
        x1, y1, x2, y2 = edges
        pan_slice = np.s_[y1:y2:1, x1:x2:1]
        pan_data = self.test_set.current_image.get_data()[pan_slice]
        assert np.array_equal(self.test_set.pan_data, pan_data)

    @pytest.mark.parametrize(
        'zoom, center, edges',
        [
            (1, (512, 512), (0, 0, 1024, 1024)),
            (2, (256, 256), (0, 0, 512, 512)),
            (2, (768, 768), (512, 512, 1024, 1024)),
            (4, (128, 128), (0, 0, 256, 256)),
            (4, (896, 896), (768, 768, 1024, 1024)),
        ]
    )
    @ensure_correct_state
    def test_pan_mask(self, zoom, center, edges):
        self.test_set.zoom = zoom
        self.test_set.center = center
        x1, y1, x2, y2 = edges
        pan_slice = np.s_[y1:y2:1, x1:x2:1]
        pan_mask = self.test_set._roi_data[pan_slice]
        assert np.array_equal(self.test_set.pan_mask, pan_mask)

    @pytest.mark.parametrize(
        'color, rgb255',
        [
            ('red', (255.0, 0.0, 0.0)),
            ('brown', (165.0, 42.0, 42.0)),
            ('lightblue', (173.0, 216.0, 230.0)),
            ('lightcyan', (224.0, 255.0, 255.0)),
            ('darkgreen', (0.0, 100.0, 0.0)),
            ('yellow', (255.0, 255.0, 0.0)),
            ('pink', (255.0, 192.0, 203.0)),
            ('teal', (0.0, 127.9998, 127.9998)),
            ('goldenrod', (218.0, 165.0, 32.0)),
            ('sienna', (160.0, 82.0, 45.0)),
            ('darkblue', (0.0, 0.0, 139.0)),
            ('crimson', (220.0012, 19.9996, 59.999)),
            ('maroon', (176.0, 48.0, 96.0)),
            ('purple', (160.0, 32.0, 240.0)),
            ('eraser', (0.0, 0.0, 0.0)),
        ]
    )
    @ensure_correct_state
    def test_get_rgb255_from_color(self, color, rgb255):
        test_rgb255 = self.test_set._get_rgb255_from_color(color)
        for val, test_val in zip(rgb255, test_rgb255):
            assert val == round(test_val, 4)

    @pytest.mark.parametrize(
        'alpha, color, rgba',
        [
            (1, 'red', [255.0, 0.0, 0.0, 255.]),
            (1, 'brown', [165.0, 42.0, 42.0, 255.]),
            (1, 'lightblue', [173.0, 216.0, 230.0, 255.]),
            (1, 'lightcyan', [224.0, 255.0, 255.0, 255.]),
            (1, 'darkgreen', [0.0, 100.0, 0.0, 255.]),
            (.75, 'yellow', [255.0, 255.0, 0.0, 191.25]),
            (.75, 'pink', [255.0, 192.0, 203.0, 191.25]),
            (.75, 'teal', [0.0, 127.9998, 127.9998, 191.25]),
            (.75, 'goldenrod', [218.0, 165.0, 32.0, 191.25]),
            (.5, 'sienna', [160.0, 82.0, 45.0, 127.5]),
            (.5, 'darkblue', [0.0, 0.0, 139.0, 127.5]),
            (.5, 'crimson', [220.0012, 19.9996, 59.999, 127.5]),
            (.25, 'maroon', [176.0, 48.0, 96.0, 63.75]),
            (.25, 'purple', [160.0, 32.0, 240.0, 63.75]),
            (.25, 'eraser', [0.0, 0.0, 0.0, 63.75]),
        ]
    )
    @ensure_correct_state
    def test_get_rgba_from_color(self, alpha, color, rgba):
        self.test_set.alpha = alpha
        test_rgba = self.test_set._get_rgba_from_color(color)
        for val, test_val in zip(rgba, test_rgba):
            assert val == round(test_val, 4)

    # @ensure_correct_state
    # def test_set_coords_in_rois_with_color(self):
    #     coords = np.array([[42, 42]])
    #     empty = np.array([])
    #     assert np.array_equal(self.test_set.rois['red'], empty)
    #     assert np.array_equal(self.test_set.rois['brown'], empty)
    #     self.test_set._set_coords_in_rois_with_color(coords, 'red')
    #     assert np.array_equal(self.test_set.rois['red'], coords)
    #     assert np.array_equal(self.test_set.rois['brown'], empty)
    #     self.test_set._set_coords_in_rois_with_color(coords, 'brown')
    #     assert np.array_equal(self.test_set.rois['red'], empty)
    #     assert np.array_equal(self.test_set.rois['brown'], coords)
    #     self.test_set._set_coords_in_rois_with_color(coords, 'purple')
    #     assert np.array_equal(self.test_set.rois['red'], empty)
    #     assert np.array_equal(self.test_set.rois['brown'], empty)
    #     assert np.array_equal(self.test_set.rois['purple'], coords)

    @ensure_correct_state
    def test_erase_coords(self):
        coords = np.array([[42, 42]])
        rows, cols = np.column_stack(coords)
        # empty = np.array([])
        self.test_set.add_coords_to_roi_data_with_color(coords, 'red')
        # assert np.array_equal(self.test_set.rois['red'], coords)
        # assert np.array_equal(self.test_set.rois['brown'], empty)
        assert np.array_equal(
            self.test_set._roi_data[rows, cols],
            np.array([[255.0, 0.0, 0.0, 255.]])
        )
        self.test_set._erase_coords(coords)
        # assert np.array_equal(self.test_set.rois['red'], empty)
        # assert np.array_equal(self.test_set.rois['brown'], empty)
        assert np.array_equal(
            self.test_set._roi_data[rows, cols],
            np.array([[0.0, 0.0, 0.0, 0.0]])
        )
        self.test_set.alpha = 1
        self.test_set.add_coords_to_roi_data_with_color(coords, 'brown')
        # assert np.array_equal(self.test_set.rois['red'], empty)
        # assert np.array_equal(self.test_set.rois['brown'], coords)
        assert np.array_equal(
            self.test_set._roi_data[rows, cols],
            np.array([[165.0, 42.0, 42.0, 255.]])
        )
        self.test_set._erase_coords(coords)
        # assert np.array_equal(self.test_set.rois['red'], empty)
        # assert np.array_equal(self.test_set.rois['brown'], empty)
        assert np.array_equal(
            self.test_set._roi_data[rows, cols],
            np.array([[0.0, 0.0, 0.0, 0.0]])
        )

    @ensure_correct_state
    def test_add_coords_to_roi_data_with_color(self):
        coords = np.array([[42, 42]])
        rows, cols = np.column_stack(coords)
        empty = np.array([])
        # assert np.array_equal(self.test_set.rois['red'], empty)
        # assert np.array_equal(self.test_set.rois['brown'], empty)
        assert np.array_equal(
            self.test_set._roi_data[rows, cols],
            np.array([[0., 0., 0., 0.]])
        )

        self.test_set.alpha = 1
        self.test_set.add_coords_to_roi_data_with_color(coords, 'red')
        # assert np.array_equal(self.test_set.rois['red'], coords)
        # assert np.array_equal(self.test_set.rois['brown'], empty)
        assert np.array_equal(
            self.test_set._roi_data[rows, cols],
            np.array([[255.0, 0.0, 0.0, 255.]])
        )

        self.test_set.alpha = .75
        self.test_set.add_coords_to_roi_data_with_color(coords, 'brown')
        # assert np.array_equal(self.test_set.rois['red'], empty)
        # assert np.array_equal(self.test_set.rois['brown'], coords)
        assert np.array_equal(
            self.test_set._roi_data[rows, cols],
            np.array([[165.0, 42.0, 42.0, 191.25]])
        )

        self.test_set.alpha = .25
        self.test_set.add_coords_to_roi_data_with_color(coords, 'purple')
        # assert np.array_equal(self.test_set.rois['red'], empty)
        # assert np.array_equal(self.test_set.rois['brown'], empty)
        # assert np.array_equal(self.test_set.rois['purple'], coords)
        assert np.array_equal(
            self.test_set._roi_data[rows, cols],
            np.array([[160.0, 32.0, 240.0, 63.75]])
        )

    @pytest.mark.parametrize(
        'zoom, center, expected',
        [
            (2, (256, 256), (0.0, 0.0)),
            (2, (768, 768), (512.0, 512.0)),
            (4, (128, 128), (0.0, 0.0)),
            (4, (896, 896), (768.0, 768.0)),
            (4, (500, 500), (372.0, 372.0)),
            (4, (200, 300), (72.0, 172.0))
        ]
    )
    @ensure_correct_state
    def test_map_zoom_to_full_view(self, zoom, center, expected):
        self.test_set.zoom = zoom
        self.test_set.center = center
        assert self.test_set.map_zoom_to_full_view() == expected

    @ensure_correct_state
    def test_delete_rois_with_color(self):
        coords1 = np.array([[42, 42]])
        coords2 = np.array([[24, 24]])
        rows1, cols1 = np.column_stack(coords1)
        rows2, cols2 = np.column_stack(coords2)
        empty = np.array([])
        self.test_set.add_coords_to_roi_data_with_color(coords1, 'red')
        self.test_set.alpha = .75
        self.test_set.add_coords_to_roi_data_with_color(coords2, 'brown')
        # assert np.array_equal(self.test_set.rois['red'], coords1)
        # assert np.array_equal(self.test_set.rois['brown'], coords2)
        assert np.array_equal(
            self.test_set._roi_data[rows1, cols1],
            np.array([[255.0, 0.0, 0.0, 191.25]])
        )
        assert np.array_equal(
            self.test_set._roi_data[rows2, cols2],
            np.array([[165.0, 42.0, 42.0, 191.25]])
        )
        self.test_set.delete_rois_with_color('red')
        # assert np.array_equal(self.test_set.rois['red'], empty)
        assert np.array_equal(
            self.test_set._roi_data[rows1, cols1],
            np.array([[0., 0., 0., 0.]])
        )
        # assert np.array_equal(self.test_set.rois['brown'], coords2)
        assert np.array_equal(
            self.test_set._roi_data[rows2, cols2],
            np.array([[165.0, 42.0, 42.0, 191.25]])
        )
