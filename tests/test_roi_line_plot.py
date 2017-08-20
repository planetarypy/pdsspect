from . import numpy as np
from . import FILE_1, FILE_3, FILE_4, reset_image_set

from pdsspect import roi_line_plot
from pdsspect.pdsspect_image_set import PDSSpectImageSet

import pytest


class TestROILinePlotModel(object):

    image_set = PDSSpectImageSet([FILE_1, FILE_4, FILE_3])

    @pytest.fixture()
    def test_model(self):
        reset_image_set(self.image_set)
        self.image_set.images[0].wavelength = float('nan')
        self.image_set.images[1].wavelength = float('nan')
        return roi_line_plot.ROILinePlotModel(self.image_set)

    def test_wavelengths(self, test_model):
        self.image_set.images[0].wavelength = 2
        assert test_model.wavelengths == [2, 440.]
        self.image_set.images[1].wavelength = 1
        assert test_model.wavelengths == [1, 2, 440.]
        self.image_set.images[0].wavelength = float('nan')
        assert test_model.wavelengths == [1, 440.]

    def test_data_with_color(self, test_model):
        coords = np.array([[42, 24]])
        self.image_set.add_coords_to_roi_data_with_color(coords, 'red')
        assert test_model.data_with_color('red') == [24]
        self.image_set.images[1].wavelength = 2
        assert len(test_model.data_with_color('red')) == 2
        assert test_model.data_with_color('red')[1][0] == 24.0
        self.image_set.images[0].wavelength = 1
        assert len(test_model.data_with_color('red')) == 3
        assert test_model.data_with_color('red')[2][0] == 24.0
