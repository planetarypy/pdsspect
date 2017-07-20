from pdsspect import roi_plot
from pdsspect.pdsspect_image_set import PDSSpectImageSet

from . import FILE_1, FILE_3

import pytest


class TestROIHistogramModel(object):

    image_set = PDSSpectImageSet([FILE_1, FILE_3])

    @pytest.fixture()
    def test_model(self):
        self.image_set = PDSSpectImageSet([FILE_1, FILE_3])
        return roi_plot.ROIPlotModel(self.image_set)

    def test_image_sets(self, test_model):
        assert test_model.image_sets == [self.image_set]
        subset = self.image_set.create_subset()
        assert test_model.image_sets == [self.image_set, subset]

    def test_image_set(self, test_model):
        assert test_model.image_set == self.image_set
        subset = self.image_set.create_subset()
        test_model._view_index = 1
        assert test_model.image_set == subset

    def test_has_multiple_views(self, test_model):
        assert not test_model.has_multiple_views
        self.image_set.create_subset()
        assert test_model.has_multiple_views

    def test_view_index(self, test_model):
        assert not test_model.has_multiple_views
        assert test_model._view_index == 0
        assert test_model.view_index == -1
        self.image_set.create_subset()
        assert test_model.has_multiple_views
        assert test_model.view_index == 0
        test_model.view_index = 1
        assert test_model.view_index == 1
        assert test_model._view_index == 1
        test_model.image_index = 1
        test_model.view_index = 0
        assert test_model.view_index == 0
        assert test_model._view_index == 0
        assert test_model.image_index == -1

    def test_add_selected_color(self, test_model):
        assert test_model.selected_colors == []
        test_model.add_selected_color('red')
        assert test_model.selected_colors == ['red']

    def test_remove_selected_color(self, test_model):
        test_model.selected_colors = ['red']
        test_model.remove_selected_color('red')
        assert test_model.selected_colors == []

    def test_unit(self, test_model):
        assert self.image_set.unit == 'nm'
        assert test_model.unit == 'nm'
        self.image_set.unit = 'um'
        assert test_model.unit == '\mu m'
        self.image_set.unit = 'AA'
        assert test_model.unit == '\AA'


class TestROIHistogramController(object):

    image_set = PDSSpectImageSet([FILE_1, FILE_3])
    model = roi_plot.ROIPlotModel(image_set)

    @pytest.fixture()
    def test_controller(self):
        self.image_set = PDSSpectImageSet([FILE_1, FILE_3])
        self.model = roi_plot.ROIPlotModel(self.image_set)
        return roi_plot.ROIPlotController(self.model, None)

    def test_color_state_changed(self, test_controller):
        assert self.model.selected_colors == []
        test_controller.color_state_changed('red')
        assert self.model.selected_colors == ['red']
        test_controller.color_state_changed('red')
        assert self.model.selected_colors == []

    def test_select_color(self, test_controller):
        assert self.model.selected_colors == []
        test_controller.select_color('red')
        assert self.model.selected_colors == ['red']

    def test_remove_color(self, test_controller):
        assert self.model.selected_colors == []
        self.model.selected_colors = ['red']
        test_controller.remove_color('red')
        assert self.model.selected_colors == []

    def test_set_view_index(self, test_controller):
        assert not self.model.has_multiple_views
        assert self.model._view_index == 0
        assert self.model.view_index == -1
        self.image_set.create_subset()
        assert self.model.has_multiple_views
        assert self.model.view_index == 0
        test_controller.set_view_index(1)
        assert self.model.view_index == 1
        assert self.model._view_index == 1
        self.model.image_index = 1
        test_controller.set_view_index(0)
        assert self.model.view_index == 0
        assert self.model._view_index == 0
        assert self.model.image_index == -1


class TestROIHistogramWidget(object):
    image_set = PDSSpectImageSet([FILE_1])
    model = roi_plot.ROIPlotModel(image_set)

    @pytest.fixture
    def widget(self):
        self.image_set = PDSSpectImageSet([FILE_1, FILE_3])
        self.model = roi_plot.ROIPlotModel(self.image_set)
        return roi_plot.ROIPlotWidget(self.model)

    def test_init(self, widget):
        assert widget in self.model._views
        for color in self.model.image_set.colors[:-1]:
            assert hasattr(widget, color + '_checkbox')
        assert not hasattr(widget, 'eraser_checkbox')

    def test_create_color_checkbox(self, widget):
        assert not hasattr(widget, 'foo_checkbox')
        widget.create_color_checkbox('foo')
        assert hasattr(widget, 'foo_checkbox')

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
        self.image_set.create_subset()
        assert widget.view_boxes_layout.count() == 0
        widget.add_view()
        assert widget.view_boxes_layout.count() == 2
        box1 = widget.view_boxes_layout.itemAt(0).widget()
        assert box1.isChecked()
        box2 = widget.view_boxes_layout.itemAt(1).widget()
        assert not box2.isChecked()
        self.image_set.create_subset()
        self.model.view_index = 1
        widget.add_view(2)
        assert self.model.view_index == 1
        assert widget.view_boxes_layout.count() == 3
        assert not box1.isChecked()
        assert box2.isChecked()
        box3 = widget.view_boxes_layout.itemAt(2).widget()
        assert not box3.isChecked()

    def test_check_view_box(self, widget):
        self.image_set.create_subset()
        widget.add_view()
        self.image_set.create_subset()
        widget.add_view()
        box1 = widget.view_boxes_layout.itemAt(0).widget()
        box2 = widget.view_boxes_layout.itemAt(1).widget()
        box3 = widget.view_boxes_layout.itemAt(2).widget()
        assert box1.isChecked()
        assert not box2.isChecked()
        assert not box3.isChecked()
        box2.setChecked(True)
        widget.check_view_checkbox(box2)
        assert not box1.isChecked()
        assert box2.isChecked()
        assert not box3.isChecked()
        box3.setChecked(True)
        widget.check_view_checkbox(box3)
        assert not box1.isChecked()
        assert not box2.isChecked()
        assert box3.isChecked()
        box1.setChecked(True)
        widget.check_view_checkbox(box1)
        assert box1.isChecked()
        assert not box2.isChecked()
        assert not box3.isChecked()

# TODO: Test ROIHistogram. I can't figure out a good to test this class
# effectively. However, with the model and controller tested, I'm not as
# worried about testing the histogram itself
