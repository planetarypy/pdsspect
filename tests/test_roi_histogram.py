from pdsspect import roi_histogram
from pdsspect.pdsspect_image_set import PDSSpectImageSet

from . import *  # Import Test File Paths from __init__

import pytest
import numpy as np


class TestROIHistogramModel(object):

    image_set = PDSSpectImageSet([FILE_1])
    model = roi_histogram.ROIHistogramModel(image_set)

    @pytest.fixture()
    def test_model(self):
        yield self.model
        self.model.selected_colors = []
        self.image_set.delete_all_rois()

    def test_add_selected_color(self, test_model):
        assert test_model.selected_colors == []
        test_model.add_selected_color('red')
        assert test_model.selected_colors == ['red']

    def test_remove_selected_color(self):
        self.model.selected_colors = ['red']
        self.model.remove_selected_color('red')
        assert self.model.selected_colors == []

    def test_data_in_roi_with_color(self, test_model):
        coords = np.array([[42, 24]])
        self.image_set.add_coords_to_roi_data_with_color(coords, 'red')
        test_data = test_model.data_in_roi_with_color('red')[0]
        assert round(test_data, 4) == round(1163.19384766, 4)

    def test_xlim(self):
        assert self.model.xlim[0] == 0
        assert round(self.model.xlim[1], 4) == 2959.8835


class TestROIHistogramController(object):

    image_set = PDSSpectImageSet([FILE_1])
    model = roi_histogram.ROIHistogramModel(image_set)
    controller = roi_histogram.ROIHistogramController(model, None)

    @pytest.fixture()
    def test_model(self):
        yield self.model
        self.model.selected_colors = []

    def test_color_state_changed(self, test_model):
        assert test_model.selected_colors == []
        self.controller.color_state_changed('red')
        assert test_model.selected_colors == ['red']
        self.controller.color_state_changed('red')
        assert test_model.selected_colors == []

    def test_select_color(self, test_model):
        assert test_model.selected_colors == []
        self.controller.select_color('red')
        assert test_model.selected_colors == ['red']

    def test_remove_color(self, test_model):
        assert test_model.selected_colors == []
        test_model.selected_colors = ['red']
        self.controller.remove_color('red')
        assert self.model.selected_colors == []


class TestROIHistogramWidget(object):
    image_set = PDSSpectImageSet([FILE_1])
    model = roi_histogram.ROIHistogramModel(image_set)
    widget = roi_histogram.ROIHistogramWidget(model)

    def test_init(self):
        assert self.widget in self.model._views
        for color in self.model.image_set.colors[:-1]:
            assert hasattr(self.widget, color + '_checkbox')
        assert not hasattr(self.widget, 'eraser_checkbox')

    def test_create_color_checkbox(self):
        assert not hasattr(self.widget, 'foo_checkbox')
        self.widget.create_color_checkbox('foo')
        assert hasattr(self.widget, 'foo_checkbox')

    def test_check_color(self, qtbot):
        qtbot.add_widget(self.widget)
        self.widget.show()
        assert self.model.selected_colors == []
        self.widget.check_color('red')
        assert self.model.selected_colors == ['red']
        self.widget.check_color('red')
        assert self.model.selected_colors == []
        assert not self.widget.red_checkbox.isChecked()
        self.widget.red_checkbox.nextCheckState()
        assert self.widget.red_checkbox.isChecked()
        assert self.model.selected_colors == ['red']
        assert self.widget.red_checkbox.isChecked()
        self.widget.red_checkbox.nextCheckState()
        assert self.model.selected_colors == []
        assert not self.widget.red_checkbox.isChecked()

# TODO: Test ROIHistogram. I can't figure out a good to test this class
# effectively. However, with the model and controller tested, I'm not as
# worried about testing the histogram itself
