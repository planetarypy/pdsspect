from pdsspect import roi_histogram
from pdsspect.pdsspect_image_set import PDSSpectImageSet

from . import FILE_1, FILE_3

import pytest
import numpy as np


class TestROIHistogramModel(object):

    image_set = PDSSpectImageSet([FILE_1, FILE_3])

    @pytest.fixture()
    def test_model(self):
        self.image_set = PDSSpectImageSet([FILE_1, FILE_3])
        return roi_histogram.ROIHistogramModel(self.image_set)

    def test_image_index(self, test_model):
        assert test_model.image_index == -1
        test_model.image_index = 0
        assert test_model.image_index == -1
        test_model.image_index = 1
        assert test_model.image_index == 1

    def test_compare_data(self, test_model):
        assert not test_model.compare_data
        test_model.image_index = 1
        assert test_model.compare_data

    def test_xdata(self, test_model):
        coords = np.array([[42, 24]])
        self.image_set.add_coords_to_roi_data_with_color(coords, 'red')
        test_data = test_model.xdata('red')[0]
        assert round(test_data, 4) == round(1163.19384766, 4)

    def test_ydata(self, test_model):
        coords = np.array([[42, 24]])
        self.image_set.add_coords_to_roi_data_with_color(coords, 'red')
        assert not test_model.compare_data
        with pytest.raises(RuntimeError):
            test_model.ydata('red')
        test_model.image_index = 1
        test_data = test_model.ydata('red')[0]
        assert round(test_data, 4) == round(24.0, 4)

    def test_xlim(self, test_model):
        assert test_model.xlim[0] == 0
        assert round(test_model.xlim[1], 4) == 2959.6763

    def test_ylim(self, test_model):
        assert not test_model.compare_data
        with pytest.raises(RuntimeError):
            test_model.ydata('red')
        test_model.image_index = 1
        assert test_model.ylim[0] == 22.0
        assert test_model.ylim[1] == 115.0


class TestROIHistogramController(object):

    image_set = PDSSpectImageSet([FILE_1, FILE_3])
    model = roi_histogram.ROIHistogramModel(image_set)

    @pytest.fixture()
    def test_controller(self):
        self.image_set = PDSSpectImageSet([FILE_1, FILE_3])
        self.model = roi_histogram.ROIHistogramModel(self.image_set)
        return roi_histogram.ROIHistogramController(self.model, None)

    def test_set_image_index(self, test_controller):
        assert self.model.image_index == -1
        test_controller.set_image_index(0)
        assert self.model.image_index == -1
        test_controller.set_image_index(1)
        assert self.model.image_index == 1


class TestROIHistogramWidget(object):
    image_set = PDSSpectImageSet([FILE_1])
    model = roi_histogram.ROIHistogramModel(image_set)

    @pytest.fixture
    def widget(self):
        self.image_set = PDSSpectImageSet([FILE_1, FILE_3])
        self.model = roi_histogram.ROIHistogramModel(self.image_set)
        return roi_histogram.ROIHistogramWidget(self.model)

    def test_init(self, widget):
        assert widget in self.model._views
        for color in self.model.image_set.colors[:-1]:
            assert hasattr(widget, color + '_checkbox')
        assert not hasattr(widget, 'eraser_checkbox')
        assert widget in self.model.image_sets[0]._views
        assert widget.roi_plot in self.model.image_sets[0]._views

    def test_check_color(self, qtbot, widget):
        qtbot.add_widget(widget)
        widget.show()
        assert self.model.selected_colors == []
        widget.check_color('red')
        assert self.model.selected_colors == ['red']
        widget.check_color('red')
        assert self.model.selected_colors == []
        assert not widget.red_checkbox.isChecked()
        widget.red_checkbox.nextCheckState()
        assert widget.red_checkbox.isChecked()
        assert self.model.selected_colors == ['red']
        assert widget.red_checkbox.isChecked()
        widget.red_checkbox.nextCheckState()
        assert self.model.selected_colors == []
        assert not widget.red_checkbox.isChecked()

    def test_add_view(self, widget):
        subset = self.image_set.create_subset()
        assert widget.view_boxes_layout.count() == 0
        widget.add_view()
        assert widget.view_boxes_layout.count() == 2
        assert widget in subset._views
        assert widget.roi_plot in subset._views
        box1 = widget.view_boxes_layout.itemAt(0).widget()
        assert box1.isChecked()
        box2 = widget.view_boxes_layout.itemAt(1).widget()
        assert not box2.isChecked()
        subset2 = self.image_set.create_subset()
        self.model.view_index = 1
        widget.add_view(2)
        assert self.model.view_index == 1
        assert widget.view_boxes_layout.count() == 3
        assert widget in subset2._views
        assert widget.roi_plot in subset2._views
        assert not box1.isChecked()
        assert box2.isChecked()
        box3 = widget.view_boxes_layout.itemAt(2).widget()
        assert not box3.isChecked()

    def test_select_image(self, qtbot, widget):
        qtbot.add_widget(widget)
        widget.show()
        assert self.model.image_index == -1
        widget.select_image(0)
        assert self.model.image_index == -1
        widget.select_image(1)
        assert self.model.image_index == 1
        widget.select_image(0)
        assert self.model.image_index == -1

        widget.image_menu.setCurrentIndex(1)
        assert self.model.image_index == 1
        widget.image_menu.setCurrentIndex(0)
        assert self.model.image_index == -1


# TODO: Test ROIHistogram. I can't figure out a good to test this class
# effectively. However, with the model and controller tested, I'm not as
# worried about testing the histogram itself
