from . import TEST_FILES

import pytest
from qtpy import QtCore

from pdsspect.basic import BasicWidget
from pdsspect.pdsspect import PDSSpect
from pdsspect.transforms import Transforms
from pdsspect.selection import Selection
from pdsspect.roi_histogram import ROIHistogramWidget
from pdsspect.pdsspect_image_set import PDSSpectImageSet
from pdsspect.roi_line_plot import ROILinePlotWidget


class TestPDSSpect(object):
    image_set = PDSSpectImageSet(TEST_FILES)

    @pytest.fixture
    def window(self):
        self.image_set._subsets = []
        return PDSSpect(self.image_set)

    def test_init(self, qtbot, window):
        window.show()
        qtbot.add_widget(window)
        qtbot.add_widget(window.basic_window)
        assert window.selection_window is None
        assert window.basic_window is not None
        assert window.transforms_window is None

    def test_image_sets(self, qtbot, window):
        window.show()
        qtbot.add_widget(window)
        qtbot.add_widget(window.basic_window)
        assert window.image_sets == [self.image_set]
        subset = self.image_set.create_subset()
        assert window.image_sets == [self.image_set, subset]
        self.image_set.remove_subset(subset)
        assert window.image_sets == [self.image_set]

    def test_open_selection(self, qtbot, window):
        window.show()
        qtbot.add_widget(window)
        qtbot.add_widget(window.basic_window)
        qtbot.mouseClick(window.selection_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.selection_window)
        assert window.selection_window is not None
        assert isinstance(window.selection_window, Selection)
        assert window.selection_window.isVisible()

    def test_open_basic(self, qtbot, window):
        window.show()
        qtbot.add_widget(window)
        qtbot.add_widget(window.basic_window)
        window.basic_window.close()
        qtbot.mouseClick(window.basic_btn, QtCore.Qt.LeftButton)
        assert window.basic_window.isVisible()
        assert isinstance(window.basic_window, BasicWidget)

    def test_open_transforms(self, qtbot, window):
        window.show()
        qtbot.add_widget(window)
        qtbot.add_widget(window.basic_window)
        assert window.transforms_window is None
        qtbot.mouseClick(window.transforms_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.transforms_window)
        assert window.transforms_window is not None
        assert window.transforms_window.isVisible()
        assert isinstance(window.transforms_window, Transforms)

    def test_open_roi_histogram(self, qtbot, window):
        window.show()
        qtbot.add_widget(window)
        qtbot.add_widget(window.basic_window)
        assert window.roi_histogram_window is None
        qtbot.mouseClick(window.roi_histogram_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.roi_histogram_window)
        assert window.roi_histogram_window is not None
        assert window.roi_histogram_window.isVisible()
        assert isinstance(window.roi_histogram_window, ROIHistogramWidget)

    def test_open_roi_line_plot(self, qtbot, window):
        window.show()
        qtbot.add_widget(window)
        qtbot.add_widget(window.basic_window)
        assert window.roi_line_plot_window is None
        qtbot.mouseClick(window.roi_line_plot_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.roi_line_plot_window)
        assert window.roi_line_plot_window is not None
        assert window.roi_line_plot_window.isVisible()
        assert isinstance(window.roi_line_plot_window, ROILinePlotWidget)

    def test_add_window(self, qtbot, window):
        window.show()
        qtbot.add_widget(window)
        qtbot.add_widget(window.pan_view)
        qtbot.add_widget(window.basic_window)
        qtbot.mouseClick(window.selection_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.selection_window)
        qtbot.mouseClick(window.roi_histogram_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.roi_histogram_window)
        qtbot.mouseClick(window.roi_line_plot_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.roi_line_plot_window)
        assert len(window.image_sets) == 1
        assert len(window.basic_window.basics) == 1
        assert len(window.pan_view.pans) == 1
        qtbot.mouseClick(window.add_window_btn, QtCore.Qt.LeftButton)
        assert len(window.image_sets) == 2
        assert len(window.basic_window.basics) == 2
        assert len(window.pan_view.pans) == 2

    def test_quit(self, qtbot, window):
        window.show()
        qtbot.add_widget(window)
        qtbot.mouseClick(window.transforms_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.transforms_window)
        qtbot.mouseClick(window.basic_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.basic_window)
        qtbot.mouseClick(window.selection_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.selection_window)
        qtbot.mouseClick(window.roi_histogram_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.roi_histogram_window)
        qtbot.mouseClick(window.roi_line_plot_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.roi_line_plot_window)
        assert window.transforms_window.isVisible()
        assert window.basic_window.isVisible()
        assert window.selection_window.isVisible()
        assert window.isVisible()
        qtbot.mouseClick(window.quit_btn, QtCore.Qt.LeftButton)
        assert not window.transforms_window.isVisible()
        assert not window.basic_window.isVisible()
        assert not window.selection_window.isVisible()
        assert not window.isVisible()
