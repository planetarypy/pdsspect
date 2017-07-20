from . import FILE_1, FILE_1_NAME, FILE_2, TEST_FILES, TEST_FILE_NAMES

import pytest
import numpy as np
from ginga.util.dp import masktorgb
from ginga.RGBImage import RGBImage
from astropy import units as astro_units
from ginga.canvas.types.image import Image

from pdsspect.pdsspect_image_set import (
    ImageStamp, PDSSpectImageSet, ginga_colors, SubPDSSpectImageSet
)


class TestImageStamp():

    @pytest.fixture()
    def image_stamp(self):
        return ImageStamp(FILE_1)

    @pytest.fixture()
    def pancam_stamp(self):
        return ImageStamp(FILE_2)

    def test_init(self, image_stamp):
        assert image_stamp.image_name == FILE_1_NAME
        assert not image_stamp.seen
        assert image_stamp.cuts == (None, None)

    def test_data(self, image_stamp):
        assert np.array_equal(
            image_stamp.data,
            image_stamp.pds_image.image
        )

    def test_wavelength(self, image_stamp):
        assert isinstance(image_stamp.wavelength, float)
        assert np.isnan(image_stamp.wavelength)
        image_stamp.wavelength = 100.0
        assert image_stamp.wavelength == 100.0

    def test_unit(self, image_stamp):
        assert isinstance(image_stamp.unit, astro_units.Unit)
        assert image_stamp.unit == 'nm'
        image_stamp.wavelength = 10.0
        image_stamp.unit = 'AA'
        assert image_stamp.unit == 'AA'
        assert image_stamp.wavelength == 100.0
        image_stamp.unit = 'nm'
        assert image_stamp.unit == 'nm'
        assert image_stamp.wavelength == 10.0
        image_stamp.unit = 'um'
        assert image_stamp.unit == 'um'
        assert image_stamp.wavelength == 0.01
        image_stamp.unit = 'AA'
        assert image_stamp.unit == 'AA'
        assert image_stamp.wavelength == 100.0

    def test_check_acceptable_unit(self, image_stamp):
        with pytest.raises(ValueError):
            image_stamp.unit = 'foo'

    def test_get_wavelength(self, image_stamp):
        image_stamp.wavelength = 10.0
        wavelength = image_stamp.get_wavelength()
        assert isinstance(wavelength, astro_units.quantity.Quantity)
        assert wavelength.value == 10.0
        assert wavelength.unit == 'nm'
        image_stamp.unit = 'AA'
        assert wavelength.value == 10.0
        assert wavelength.unit == 'nm'

    def test_wavelength_pancam(self, pancam_stamp):
        """Test that the image stamp uses the images wavelength if exists"""
        assert pancam_stamp.wavelength == 880.0

    def test_accepted_units(self, image_stamp):
        assert image_stamp.accepted_units == ['nm', 'um', 'AA']


class TestPDSSpectImageSet(object):
    test_set = PDSSpectImageSet(TEST_FILES)
    centerH = 16
    centerV = 32

    def teardown_method(self, method):
        self.test_set._current_image_index = 0
        self.test_set.current_color_index = 0
        self.test_set._selection_index = 0
        self.test_set._zoom = 1.0
        self.test_set._center = None
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
        self.test_set._subsets = []
        self.test_set._simultaneous_roi = False
        self.test_set._unit = 'nm'
        for image in self.test_set.images:
            image.unit = 'nm'

    def test_init(self):
        test_set = self.test_set
        assert test_set._views == []
        assert isinstance(test_set, PDSSpectImageSet)
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
        assert test_set._alpha == 1.0
        assert isinstance(test_set._alpha, float)
        assert not test_set._flip_x
        assert not test_set._flip_y
        assert not test_set._swap_xy
        assert isinstance(test_set._maskrgb, RGBImage)
        assert not test_set._roi_data.any()
        assert isinstance(test_set._maskrgb_obj, Image)
        test_shape = (self.centerV * 2, self.centerH * 2)
        assert np.array_equal(test_set.shape, test_shape)
        assert not test_set._simultaneous_roi

    def test_register(self):
        assert self.test_set._views == []
        self.test_set.register('foo')
        assert 'foo' in self.test_set._views

    def test_unregister(self):
        self.test_set._views = ['foo']
        assert 'foo' in self.test_set._views
        self.test_set.unregister('foo')
        assert 'foo' not in self.test_set._views
        assert self.test_set._views == []

    def test_filenames(self):
        assert self.test_set.filenames == TEST_FILE_NAMES

    def test_current_image_index(self):
        test_set = self.test_set
        assert test_set._current_image_index == test_set.current_image_index
        test_set.current_image_index = 2
        assert test_set._current_image_index == test_set.current_image_index
        assert test_set._current_image_index == 2
        test_set.current_image_index = 1
        assert test_set._current_image_index == test_set.current_image_index
        assert test_set._current_image_index == 1

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
    def test_selection_type(self, index, expected):
        self.test_set.selection_index = index
        assert self.test_set.selection_type == expected

    def test_zoom(self):
        assert self.test_set._zoom == 1.0
        assert self.test_set._zoom == self.test_set.zoom
        self.test_set.zoom = 42.0
        assert self.test_set._zoom == 42.0
        assert self.test_set._zoom == self.test_set.zoom
        self.test_set.zoom = -42.0
        assert self.test_set._zoom == 1.0
        self.test_set.zoom = 1.0
        assert self.test_set._zoom == 1.0
        assert self.test_set._zoom == self.test_set.zoom

    def test_x_radius(self):
        assert self.test_set.shape[1] == self.centerH * 2
        assert self.test_set.x_radius == self.centerH

    def test_y_radius(self):
        assert self.test_set.current_image.shape[0] == self.centerV * 2
        assert self.test_set.y_radius == self.centerV

    @pytest.mark.parametrize(
        'zoom, expected',
        [
            (1.0, 16),
            (2.0, 8),
            (4.0, 4),
        ]
    )
    def test_pan_width(self, zoom, expected):
        self.test_set.zoom = zoom
        assert self.test_set.pan_width == expected

    @pytest.mark.parametrize(
        'zoom, expected',
        [
            (1.0, 32),
            (2.0, 16),
            (4.0, 8),
        ]
    )
    def test_pan_height(self, zoom, expected):
        self.test_set.zoom = zoom
        assert self.test_set.pan_height == expected

    def test_reset_center(self):
        test_center = (16, 32)
        assert self.test_set._center is None
        self.test_set.reset_center()
        assert self.test_set._center == test_center
        self.test_set._center = None
        assert self.test_set._center is None

    @pytest.mark.parametrize(
        'point, expected',
        [
            ((16, 32), True),
            ((-.5, -.5), True),
            ((-.5, 64.5), True),
            ((32.5, -.5), True),
            ((32.5, 64.5), True),
            ((-.6, -.5), False),
            ((-.5, -.6), False),
            ((-.6, -.6), False),
            ((32.6, -.5), False),
            ((-.5, 64.6), False),
            ((32.6, 64.6), False),
        ]
    )
    def test_point_is_in_image(self, point, expected):
        assert self.test_set._point_is_in_image(point) is expected

    @pytest.mark.parametrize(
        'zoom, x, expected',
        [
            (1, 16, 16),
            (2, 8, 8),
            (2, -.5, 8),
            (2, 24, 24),
            (2, 32.5, 24),
            (4, 4, 4),
            (4, -.5, 4),
            (4, 28, 28),
            (4, 32.5, 28),
        ]
    )
    def test_determine_center_x(self, zoom, x, expected):
        self.test_set.zoom = zoom
        assert self.test_set._determine_center_x(x) == expected

    @pytest.mark.parametrize(
        'zoom, y, expected',
        [
            (1, 32, 32),
            (2, 16, 16),
            (2, -.5, 16),
            (2, 48, 48),
            (2, 64.5, 48),
            (4, 8, 8),
            (4, -.5, 8),
            (4, 64.5, 56),
        ]
    )
    def test_determine_center_y(self, zoom, y, expected):
        self.test_set.zoom = zoom
        assert self.test_set._determine_center_y(y) == expected

    @pytest.mark.parametrize(
        'zoom, center, expected',
        [
            (1, (16, 32), (16, 32)),
            (1, (15, 31), (16, 32)),
            (1, (17, 33), (16, 32)),
            (1, (16, 31), (16, 32)),
            (1, (17, 32), (16, 32)),
            (2, (8, 16), (8, 16)),
            (2, (7, 16), (8, 16)),
            (2, (8, 15), (8, 16)),
            (2, (24, 48), (24, 48)),
            (2, (25, 48), (24, 48)),
            (2, (24, 49), (24, 48)),
            (4, (4, 8), (4, 8)),
            (4, (3, 8), (4, 8)),
            (4, (4, 7), (4, 8)),
            (4, (28, 56), (28, 56)),
            (4, (29, 56), (28, 56)),
            (4, (28, 57), (28, 56)),
        ]
    )
    def test_center(self, zoom, center, expected):
        self.test_set.zoom = zoom
        self.test_set.center = center
        assert self.test_set.center == expected
        assert self.test_set._center == expected

    @pytest.mark.parametrize(
        'alpha, expected',
        [
            (1., 255.),
            (.75, 191.25),
            (.5, 127.5),
            (.25, 63.75),
        ]
    )
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
    def test_alpha(self, alpha, alpha255):
        red_coords = np.array([[0, 0], [32, 16]])
        rgba = [255.0, 0.0, 0.0, 355.]
        for red_coord in red_coords:
            row, col = red_coord
            assert self.test_set._roi_data[row, col, 3] == 0
        self.test_set._roi_data[np.column_stack(red_coords)] = rgba
        self.test_set.alpha = alpha
        assert self.test_set._alpha == alpha
        assert self.test_set._alpha == self.test_set.alpha
        for red_coord in red_coords:
            row, col = red_coord
            assert self.test_set._roi_data[row, col, 3] == alpha255

    def test_flip_x(self):
        assert self.test_set._flip_x == self.test_set.flip_x
        self.test_set.flip_x = True
        assert self.test_set._flip_x
        assert self.test_set._flip_x == self.test_set.flip_x

    def test_flip_y(self):
        assert self.test_set._flip_y == self.test_set.flip_y
        self.test_set.flip_y = True
        assert self.test_set._flip_y
        assert self.test_set._flip_y == self.test_set.flip_y

    def test_swap_xy(self):
        assert self.test_set._swap_xy == self.test_set.swap_xy
        self.test_set.swap_xy = True
        assert self.test_set._swap_xy
        assert self.test_set._swap_xy == self.test_set.swap_xy

    def test_transforms(self):
        assert self.test_set.transforms == (False, False, False)
        self.test_set.flip_x = True
        assert self.test_set.transforms == (True, False, False)
        self.test_set.flip_y = True
        assert self.test_set.transforms == (True, True, False)
        self.test_set.swap_xy = True
        assert self.test_set.transforms == (True, True, True)

    @pytest.mark.parametrize(
        'zoom, center, expected',
        [
            (1, (16, 32), (0, 0, 32, 64)),
            (2, (8, 16), (0, 0, 16, 32)),
            (2, (24, 48), (16, 32, 32, 64)),
            (4, (4, 8), (0, 0, 8, 16)),
            (4, (28, 56), (24, 48, 32, 64)),
        ]
    )
    def test_edges(self, zoom, center, expected):
        self.test_set.zoom = zoom
        self.test_set.center = center
        assert self.test_set.edges == expected

    @pytest.mark.parametrize(
        'zoom, center, edges',
        [
            (1, (16, 32), (0, 0, 32, 64)),
            (2, (8, 16), (0, 0, 16, 32)),
            (2, (24, 48), (16, 32, 32, 64)),
            (4, (4, 8), (0, 0, 8, 16)),
            (4, (28, 56), (24, 48, 32, 64)),
        ]
    )
    def test_pan_slice(self, zoom, center, edges):
        self.test_set.zoom = zoom
        self.test_set.center = center
        x1, y1, x2, y2 = edges
        assert np.array_equal(self.test_set.pan_slice, np.s_[y1:y2:1, x1:x2:1])

    @pytest.mark.parametrize(
        'zoom, center, edges',
        [
            (1, (16, 32), (0, 0, 32, 64)),
            (2, (8, 16), (0, 0, 16, 32)),
            (2, (24, 48), (16, 32, 32, 64)),
            (4, (4, 8), (0, 0, 8, 16)),
            (4, (28, 56), (24, 48, 32, 64)),
        ]
    )
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
            (1, (16, 32), (0, 0, 32, 64)),
            (2, (8, 16), (0, 0, 16, 32)),
            (2, (24, 48), (16, 32, 32, 64)),
            (4, (4, 8), (0, 0, 8, 16)),
            (4, (28, 56), (24, 48, 32, 64)),
        ]
    )
    def test_pan_roi_data(self, zoom, center, edges):
        self.test_set.zoom = zoom
        self.test_set.center = center
        x1, y1, x2, y2 = edges
        pan_slice = np.s_[y1:y2:1, x1:x2:1]
        pan_roi_data = self.test_set._roi_data[pan_slice]
        assert np.array_equal(self.test_set.pan_roi_data, pan_roi_data)

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
    def test_get_rgba_from_color(self, alpha, color, rgba):
        self.test_set.alpha = alpha
        test_rgba = self.test_set._get_rgba_from_color(color)
        for val, test_val in zip(rgba, test_rgba):
            assert val == round(test_val, 4)

    def test_erase_coords(self):
        coords = np.array([[42, 24]])
        rows, cols = np.column_stack(coords)

        self.test_set.add_coords_to_roi_data_with_color(coords, 'red')

        assert np.array_equal(
            self.test_set._roi_data[rows, cols],
            np.array([[255.0, 0.0, 0.0, 255.]])
        )
        self.test_set._erase_coords(coords)

        assert np.array_equal(
            self.test_set._roi_data[rows, cols],
            np.array([[0.0, 0.0, 0.0, 0.0]])
        )
        self.test_set.alpha = 1
        self.test_set.add_coords_to_roi_data_with_color(coords, 'brown')
        assert np.array_equal(
            self.test_set._roi_data[rows, cols],
            np.array([[165.0, 42.0, 42.0, 255.]])
        )
        self.test_set._erase_coords(coords)
        assert np.array_equal(
            self.test_set._roi_data[rows, cols],
            np.array([[0.0, 0.0, 0.0, 0.0]])
        )

    def test_add_coords_to_roi_data_with_color(self):
        coords = np.array([[42, 24]])
        rows, cols = np.column_stack(coords)
        assert np.array_equal(
            self.test_set._roi_data[rows, cols],
            np.array([[0., 0., 0., 0.]])
        )

        self.test_set.alpha = 1
        self.test_set.add_coords_to_roi_data_with_color(coords, 'red')
        assert np.array_equal(
            self.test_set._roi_data[rows, cols],
            np.array([[255.0, 0.0, 0.0, 255.]])
        )

        self.test_set.alpha = .75
        self.test_set.add_coords_to_roi_data_with_color(coords, 'brown')
        assert np.array_equal(
            self.test_set._roi_data[rows, cols],
            np.array([[165.0, 42.0, 42.0, 191.25]])
        )

        self.test_set.alpha = .25
        self.test_set.add_coords_to_roi_data_with_color(coords, 'purple')
        assert np.array_equal(
            self.test_set._roi_data[rows, cols],
            np.array([[160.0, 32.0, 240.0, 63.75]])
        )

    @pytest.mark.parametrize(
        'zoom, center, expected',
        [
            (2, (8, 16), (0.0, 0.0)),
            (2, (24, 48), (16.0, 32.0)),
            (4, (4, 8), (0.0, 0.0)),
            (4, (8, 16), (4.0, 8.0)),
        ]
    )
    def test_map_zoom_to_full_view(self, zoom, center, expected):
        self.test_set.zoom = zoom
        self.test_set.center = center
        assert self.test_set.map_zoom_to_full_view() == expected

    def test_get_coordinates_of_color(self):
        coords1 = np.array([[12, 12], [42, 24]])
        self.test_set.add_coords_to_roi_data_with_color(coords1, 'red')
        rows, cols = self.test_set.get_coordinates_of_color('red')
        test_coords = np.column_stack([rows, cols])
        assert np.array_equal(coords1, test_coords)

    def test_delete_rois_with_color(self):
        coords1 = np.array([[12, 12]])
        coords2 = np.array([[42, 24]])
        rows1, cols1 = np.column_stack(coords1)
        rows2, cols2 = np.column_stack(coords2)
        self.test_set.add_coords_to_roi_data_with_color(coords1, 'red')
        self.test_set.alpha = .75
        self.test_set.add_coords_to_roi_data_with_color(coords2, 'brown')
        assert np.array_equal(
            self.test_set._roi_data[rows1, cols1],
            np.array([[255.0, 0.0, 0.0, 191.25]])
        )
        assert np.array_equal(
            self.test_set._roi_data[rows2, cols2],
            np.array([[165.0, 42.0, 42.0, 191.25]])
        )
        self.test_set.delete_rois_with_color('red')
        assert np.array_equal(
            self.test_set._roi_data[rows1, cols1],
            np.array([[0., 0., 0., 0.]])
        )
        assert np.array_equal(
            self.test_set._roi_data[rows2, cols2],
            np.array([[165.0, 42.0, 42.0, 191.25]])
        )

    def test_create_subset(self):
        assert len(self.test_set.subsets) == 0
        subset = self.test_set.create_subset()
        assert isinstance(subset, SubPDSSpectImageSet)
        assert len(self.test_set.subsets) == 1
        assert subset in self.test_set.subsets

    def test_subsets(self):
        assert len(self.test_set.subsets) == 0
        assert len(self.test_set._subsets) == 0
        subset = self.test_set.create_subset()
        assert len(self.test_set.subsets) == 1
        assert len(self.test_set._subsets) == 1
        assert subset in self.test_set._subsets
        assert subset in self.test_set.subsets
        assert self.test_set.subsets == self.test_set._subsets

    def test_add_subset(self):
        subset = SubPDSSpectImageSet(self.test_set)
        assert len(self.test_set.subsets) == 0
        self.test_set.add_subset(subset)
        assert len(self.test_set.subsets) == 1
        assert subset in self.test_set.subsets
        self.test_set.add_subset('foo')
        assert len(self.test_set.subsets) == 1
        assert 'foo' not in self.test_set.subsets

    def test_remove_subset(self):
        subset = SubPDSSpectImageSet(self.test_set)
        subset2 = SubPDSSpectImageSet(self.test_set)
        self.test_set.add_subset(subset)
        assert len(self.test_set.subsets) == 1
        self.test_set.remove_subset(subset2)
        assert len(self.test_set.subsets) == 1
        assert subset in self.test_set.subsets
        self.test_set.remove_subset('foo')
        assert len(self.test_set.subsets) == 1
        assert subset in self.test_set.subsets
        self.test_set.remove_subset(subset)
        assert len(self.test_set.subsets) == 0
        assert subset not in self.test_set.subsets

    def test_get_rois_masks_to_export(self):
        roi_coords = np.array(
            [
                [2, 3],
                [2, 5],
                [4, 3],
                [4, 5],
            ]
        )
        subset = self.test_set.create_subset()
        self.test_set.add_coords_to_roi_data_with_color(roi_coords, 'red')
        subset.add_coords_to_roi_data_with_color(roi_coords, 'darkgreen')
        test_rois_dict = self.test_set.get_rois_masks_to_export()
        rows, cols = np.column_stack(roi_coords)
        assert np.array_equal(
            np.where(test_rois_dict['red'])[0], rows
        )
        assert np.array_equal(
            np.where(test_rois_dict['red'])[1], cols
        )
        assert np.array_equal(
            np.where(test_rois_dict['darkgreen2'])[0], rows
        )
        assert np.array_equal(
            np.where(test_rois_dict['darkgreen2'])[1], cols
        )

    def test_simultaneous_roi(self):
        subset = self.test_set.create_subset()
        assert not self.test_set._simultaneous_roi
        assert not self.test_set.simultaneous_roi
        assert not subset._simultaneous_roi
        assert not subset.simultaneous_roi
        coords1 = np.array([[12, 12]])
        rows1, cols1 = np.column_stack(coords1)
        self.test_set.add_coords_to_roi_data_with_color(coords1, 'red')
        assert np.array_equal(
            self.test_set._roi_data[rows1, cols1],
            np.array([[255.0, 0.0, 0.0, 255.0]])
        )
        assert not np.array_equal(
            subset._roi_data[rows1, cols1],
            np.array([[255.0, 0.0, 0.0, 255.0]])
        )
        self.test_set.simultaneous_roi = True
        assert self.test_set._simultaneous_roi
        assert subset._simultaneous_roi
        assert np.array_equal(
            subset._roi_data[rows1, cols1],
            np.array([[255.0, 0.0, 0.0, 255.0]])
        )
        self.test_set.simultaneous_roi = False
        self.test_set.add_coords_to_roi_data_with_color(coords1, 'brown')
        assert np.array_equal(
            self.test_set._roi_data[rows1, cols1],
            np.array([[165.0, 42.0, 42.0, 255.0]])
        )
        assert np.array_equal(
            subset._roi_data[rows1, cols1],
            np.array([[255.0, 0.0, 0.0, 255.0]])
        )

    def test_unit(self):
        assert self.test_set.unit == self.test_set._unit
        assert self.test_set.unit == 'nm'
        subset = self.test_set.create_subset()
        assert subset.unit == 'nm'
        self.test_set.unit = 'um'
        assert self.test_set.unit == 'um'
        assert subset.unit == 'um'
        for image in self.test_set.images:
            assert image.unit == 'um'

    def test_set_unit(self):
        assert self.test_set.unit == 'nm'
        for image in self.test_set.images:
            assert image.unit == 'nm'
        self.test_set._unit = 'um'
        assert self.test_set.unit == 'um'
        for image in self.test_set.images:
            assert image.unit == 'nm'
        self.test_set.set_unit()
        for image in self.test_set.images:
            assert image.unit == 'um'


class TestSubPDSSpectImageSet(object):
    image_set = PDSSpectImageSet(TEST_FILES)
    subset = SubPDSSpectImageSet(image_set)

    def test_init(self):
        subset = self.subset
        assert subset.parent_set == self.image_set
        assert not subset._views
        assert subset.current_image_index == self.image_set.current_image_index
        assert subset.current_color_index == self.image_set.current_color_index
        assert subset.zoom == self.image_set.zoom
        assert subset.center == self.image_set.center
        assert subset.alpha == self.image_set.alpha
        assert not subset._roi_data.any()
        assert subset.selection_index == self.image_set.selection_index
        assert subset.flip_x == self.image_set.flip_x
        assert subset.flip_y == self.image_set.flip_y
        assert subset.swap_xy == self.image_set.swap_xy
        assert subset.shape == self.image_set.shape
        assert subset.images == self.image_set.images
        assert not subset._simultaneous_roi
