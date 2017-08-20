#!/usr/bin/env python
# -*- coding: utf-8 -*-
from . import FILE_1

import pytest
import numpy as np
from qtpy import QtWidgets, QtCore
from matplotlib.lines import Line2D


from pdsspect import pdsspect_image_set, histogram
from pdsspect import pds_image_view_canvas

# test_images = pdsspect_image_set.ImageSet([FILE_1, FILE_2])
# window = pdsview.PDSViewer(test_images)
# image_view = window.view_canvas


class TestHistogramModel(object):

    image_view = pds_image_view_canvas.PDSImageViewCanvas()
    image = pdsspect_image_set.ImageStamp(FILE_1)
    image_view.set_image(image)

    @pytest.fixture
    def model(self):
        self.image_view = pds_image_view_canvas.PDSImageViewCanvas()
        self.image_view.set_image(self.image)
        return histogram.HistogramModel(self.image_view)

    def test_model_init(self, model):
        assert model._image_view == self.image_view
        assert model._views == set()
        assert model._cut_low is None
        assert model._cut_high is None
        assert model._bins == 100

    def test_image_view(self, model):
        model.image_view == self.image_view
        model.image_view == model._image_view
        # Test setter method
        image_view2 = pds_image_view_canvas.PDSImageViewCanvas()
        model.image_view = image_view2
        assert model.image_view == image_view2

    def test_cut_low(self, model):
        assert model.cut_low == model.view_cuts[0]
        assert model.cut_low == model._cut_low
        # Test Setting
        model.cut_low = 42
        assert model.cut_low == 42
        assert model._cut_low == 42
        assert model.view_cuts[0] == 42

    def test_cut_high(self, model):
        assert model.cut_high is model.view_cuts[1]
        assert model.cut_high == model._cut_high
        # Test Setting
        model.cut_high = 42
        assert model.cut_high == 42
        assert model._cut_high == 42
        assert model.view_cuts[1] == 42

    def test_cuts(self, model):
        def test_new_cuts(new_cuts, model):
            model.cuts = new_cuts
            assert model.cuts == new_cuts
            assert model.cut_low == new_cuts[0]
            assert model.cut_high == new_cuts[1]
            assert model.view_cuts == new_cuts
        assert model.cuts == model.view_cuts
        # Test Setter
        test_new_cuts((24, 42), model)
        test_new_cuts((20, 42), model)
        test_new_cuts((20, 40), model)
        with pytest.warns(UserWarning):
            model.cuts = 42, 24
        assert model.cuts == (24, 42)

    def test_view_cuts(self, model):
        assert model.view_cuts == self.image_view.get_cut_levels()
        self.image_view.cut_levels(42, 24)
        assert model.view_cuts == (24, 42)

    def test_bins(self, model):
        assert model.bins == model._bins
        # Test Setter
        model.bins = 42
        assert model.bins == 42
        assert model.bins == model._bins
        # Make sure nothing changes when set to same bin value
        model.bins = 42
        assert model.bins == 42
        assert model.bins == model._bins

    def test_data(self, model):
        assert np.array_equal(model.data, self.image_view.get_image().data)

    def test_model_register(self, model):
        mock_view = QtWidgets.QWidget()
        model.register(mock_view)
        assert mock_view in model._views

    def test_model_unregister(self, model):
        mock_view = QtWidgets.QWidget()
        model.register(mock_view)
        assert mock_view in model._views
        model.unregister(mock_view)
        assert mock_view not in model._views

    def test_set_data(self, model):
        view = histogram.Histogram(model)
        assert view._left_vline is None
        assert view._right_vline is None
        model.set_data()
        assert view._left_vline is not None
        assert view._right_vline is not None

    def test_model_restore(self, model):
        assert model.cuts == model.view_cuts
        self.image_view.cut_levels(24, 42)
        model.cuts = 10, 100
        model.restore()
        assert model.cuts == model.view_cuts

    def test_warn(self, model, qtbot):
        view = histogram.HistogramWidget(model)
        qtbot.addWidget(view)
        with pytest.warns(UserWarning):
            model.warn('foo', 'bar')

    def test_set_view_cuts(self, model):
        model._cut_low = 24
        model._cut_high = 42
        model._set_view_cuts()
        assert model.view_cuts == (24, 42)


class MockView(object):

    def change_cut_low(self):
        pass

    def change_cut_high(self):
        pass

    def change_cuts(self):
        pass

    def change_bins(self):
        pass


class TestHistogramController(object):

    image_view = pds_image_view_canvas.PDSImageViewCanvas()
    image = pdsspect_image_set.ImageStamp(FILE_1)
    image_view.set_image(image)
    view = MockView()
    model = histogram.HistogramModel(image_view, view)
    model.register(view)

    @pytest.fixture
    def controller(self):
        self.image_view = pds_image_view_canvas.PDSImageViewCanvas()
        self.image_view.set_image(self.image)
        self.model = histogram.HistogramModel(self.image_view)
        self.model.register(self.view)
        controller = histogram.HistogramController(self.model, self.view)
        return controller

    def test_set_cut_low(self, controller):
        controller.set_cut_low(24)
        assert self.model.cut_low == 24
        assert self.model.view_cuts[0] == 24

    def test_set_cut_high(self, controller):
        controller.set_cut_high(42)
        assert self.model.cut_high == 42
        assert self.model.view_cuts[1] == 42

    def test_set_cuts(self, controller):
        controller.set_cuts(10, 100)
        assert self.model.cut_low == 10
        assert self.model.cut_high == 100
        assert self.model.cuts == (10, 100)
        assert self.model.view_cuts == (10, 100)

    def test_set_bins(self, controller):
        controller.set_bins(50)
        assert self.model.bins == 50

    def test_controller_restore(self, controller):
        def_cuts = self.model.view_cuts
        self.model.cuts = 24, 42
        self.image_view.cut_levels(*def_cuts)
        controller.restore()
        assert self.model.cuts != (24, 42)
        assert self.model.cuts == def_cuts
        assert self.model.view_cuts == def_cuts


class TestHistogram(object):
    image_view = pds_image_view_canvas.PDSImageViewCanvas()
    image = pdsspect_image_set.ImageStamp(FILE_1)
    image_view.set_image(image)
    model = histogram.HistogramModel(image_view)

    @pytest.fixture
    def hist(self, qtbot):
        self.image_view = pds_image_view_canvas.PDSImageViewCanvas()
        self.image_view.set_image(self.image)
        self.model = histogram.HistogramModel(self.image_view)
        hist = histogram.Histogram(self.model)
        qtbot.addWidget(hist)
        hist.show()
        return hist

    def test_init(self, hist):
        assert hist.model == self.model
        assert hist in self.model._views
        assert hist.sizePolicy().hasHeightForWidth()
        assert hist._right_vline is None
        assert hist._left_vline is None

    def test_set_vlines(self, hist):
        assert hist._right_vline is None
        assert hist._left_vline is None
        hist._set_vlines()
        assert isinstance(hist._left_vline, Line2D)
        assert isinstance(hist._right_vline, Line2D)
        assert hist._left_vline.get_xdata()[0] == self.model.cut_low
        assert hist._right_vline.get_xdata()[0] == self.model.cut_high
        assert hist._left_vline.get_xdata()[1] == self.model.cut_low
        assert hist._right_vline.get_xdata()[1] == self.model.cut_high

    def test_change_cut_low(self, hist):
        hist._set_vlines()
        self.model._cut_low = 24
        hist.change_cut_low(draw=True)
        assert hist._left_vline.get_xdata()[0] == 24
        assert hist._right_vline.get_xdata()[0] == self.model.cut_high
        assert hist._left_vline.get_xdata()[1] == 24
        assert hist._right_vline.get_xdata()[1] == self.model.cut_high

    def test_change_cut_high(self, hist):
        hist._set_vlines()
        self.model._cut_high = 42
        hist.change_cut_high(draw=True)
        assert hist._right_vline.get_xdata()[0] == 42
        assert hist._left_vline.get_xdata()[0] == self.model.cut_low
        assert hist._right_vline.get_xdata()[1] == 42
        assert hist._left_vline.get_xdata()[1] == self.model.cut_low

    def test_change_cuts(self, hist):
        self.model._cut_low = 24
        self.model._cut_high = 42
        with pytest.raises(AttributeError):
            hist.change_cuts()
            assert hist._left_vline.get_xdata()[0] == 24
        with pytest.raises(AttributeError):
            hist.change_cuts()
            assert hist._right_vline.get_xdata()[0] == 42
        hist._set_vlines()
        self.model._cut_low = 24
        self.model._cut_high = 42
        hist.change_cuts()
        assert hist._left_vline.get_xdata()[0] == 24
        assert hist._right_vline.get_xdata()[0] == 42
        assert hist._left_vline.get_xdata()[1] == 24
        assert hist._right_vline.get_xdata()[1] == 42

    def test_change_bins(self, hist):
        hist.set_data()
        assert self.model.bins == 100
        assert len(hist._ax.patches) == 100
        self.model._bins = 50
        hist.change_bins()
        assert len(hist._ax.patches) == 50

    # def test_histogram_move_line(qtbot):
    #     """Testing the move line is much more difficult than I thought
    #     Passing in the correct data points is very tough and I can't
    #     figure out exactly how to do so."""

    def test_warn(self, hist):
        assert not hist.warn('foo', 'bar')


class TestHistogramWidget(object):

    image_view = pds_image_view_canvas.PDSImageViewCanvas()
    image = pdsspect_image_set.ImageStamp(FILE_1)
    image_view.set_image(image)
    model = histogram.HistogramModel(image_view)

    @pytest.fixture
    def hist_widget(self, qtbot):
        self.image_view = pds_image_view_canvas.PDSImageViewCanvas()
        self.image_view.set_image(self.image)
        self.model = histogram.HistogramModel(self.image_view)
        hist_widget = histogram.HistogramWidget(self.model)
        qtbot.addWidget(hist_widget)
        hist_widget.show()
        return hist_widget

    def test_histogram_widget_change_cut_low(self, hist_widget):
        new_cut_low = self.model.cut_low - 3
        self.model._cut_low = new_cut_low
        hist_widget.change_cut_low()
        assert float(hist_widget._cut_low_box.text()) == new_cut_low
        new_cut_low += 1.2
        self.model._cut_low = new_cut_low
        hist_widget.change_cut_low()
        assert float(hist_widget._cut_low_box.text()) == new_cut_low

    def test_histogram_widget_change_cut_high(self, hist_widget):
        new_cut_high = round(self.model.cut_high + 3, 3)
        self.model._cut_high = new_cut_high
        hist_widget.change_cut_high()
        assert float(hist_widget._cut_high_box.text()) == new_cut_high
        new_cut_high -= 1.2
        self.model._cut_high = new_cut_high
        hist_widget.change_cut_high()
        assert float(hist_widget._cut_high_box.text()) == new_cut_high

    def test_histogram_widget_change_cuts(self, hist_widget):
        new_cut_high = round(self.model.cut_high + 3, 3)
        self.model._cut_high = new_cut_high
        new_cut_low = round(self.model.cut_low - 3, 3)
        self.model._cut_low = new_cut_low
        hist_widget.change_cuts()
        assert float(hist_widget._cut_low_box.text()) == new_cut_low
        assert float(hist_widget._cut_high_box.text()) == new_cut_high
        new_cut_high -= 1.2
        self.model._cut_high = new_cut_high
        new_cut_low += 1.2
        self.model._cut_low = new_cut_low
        hist_widget.change_cuts()
        assert float(hist_widget._cut_low_box.text()) == new_cut_low
        assert float(hist_widget._cut_high_box.text()) == new_cut_high

    def test_histogram_widget_change_bins(self, hist_widget):
        new_bins = self.model.bins + 20
        self.model._bins = new_bins
        hist_widget.change_bins()
        assert int(hist_widget._bins_box.text()) == new_bins

    def test_histogram_widget_keyPressEvent(self, hist_widget, qtbot):
        # Change only cut low
        new_cut_low = self.model.cut_low - 3
        hist_widget._cut_low_box.setText("%.3f" % (new_cut_low))
        qtbot.keyPress(hist_widget, QtCore.Qt.Key_Return)
        assert self.model.cut_low == new_cut_low
        # Change only cut high
        new_cut_high = self.model.cut_high + 3
        hist_widget._cut_high_box.setText("%.3f" % (new_cut_high))
        qtbot.keyPress(hist_widget, QtCore.Qt.Key_Return)
        assert self.model.cut_high == new_cut_high
        # Change both cuts
        new_cut_low += 1.5
        new_cut_high -= 1.5
        hist_widget._cut_low_box.setText("%.3f" % (new_cut_low))
        hist_widget._cut_high_box.setText("%.3f" % (new_cut_high))
        qtbot.keyPress(hist_widget, QtCore.Qt.Key_Return)
        assert self.model.cut_low == new_cut_low
        assert self.model.cut_high == new_cut_high
        # Change the bins
        new_bins = self.model.bins + 50
        hist_widget._bins_box.setText("%d" % (new_bins))
        qtbot.keyPress(hist_widget, QtCore.Qt.Key_Return)
        assert self.model.bins == new_bins
        assert self.model.cut_low == new_cut_low
        assert self.model.cut_high == new_cut_high
        # Change all
        new_cut_low += 1.5
        new_cut_high -= 1.5
        hist_widget._cut_low_box.setText("%.3f" % (new_cut_low))
        hist_widget._cut_high_box.setText("%.3f" % (new_cut_high))
        new_bins -= 25
        hist_widget._bins_box.setText("%d" % (new_bins))
        qtbot.keyPress(hist_widget, QtCore.Qt.Key_Return)
        assert self.model.bins == new_bins
        assert self.model.cut_low == new_cut_low
        assert self.model.cut_high == new_cut_high
        # Test Warnings
        hist_widget._cut_low_box.setText('foo')
        qtbot.keyPress(hist_widget, QtCore.Qt.Key_Return)
        assert hist_widget._cut_low_box.text() == "%.3f" % (new_cut_low)
        hist_widget._bins_box.setText('bar')
        qtbot.keyPress(hist_widget, QtCore.Qt.Key_Return)
        assert hist_widget._bins_box.text() == "%d" % (new_bins)
