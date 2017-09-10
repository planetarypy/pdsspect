from . import TEST_FILES, test_dir

import os
import sys
from glob import glob

import pytest
from qtpy import QtCore, QtWidgets

from pdsspect.basic import BasicWidget
from pdsspect.selection import Selection
from pdsspect.transforms import Transforms
from pdsspect.roi_line_plot import ROILinePlotWidget
from pdsspect.roi_histogram import ROIHistogramWidget
from pdsspect.set_wavelength import SetWavelengthWidget
from pdsspect.pdsspect_image_set import PDSSpectImageSet
from pdsspect.pdsspect import PDSSpect, open_pdsspect, arg_parser


class TestPDSSpect(object):
    image_set = PDSSpectImageSet(TEST_FILES)

    @pytest.fixture
    def window(self, qtbot):
        self.image_set._subsets = []
        window = PDSSpect(self.image_set)
        window.show()
        qtbot.add_widget(window)
        qtbot.add_widget(window.basic_window)
        qtbot.add_widget(window.pan_view)
        return window

    def test_init(self, qtbot, window):
        assert window.selection_window is None
        assert window.basic_window is not None
        assert window.transforms_window is None

    def test_image_sets(self, qtbot, window):
        assert window.image_sets == [self.image_set]
        subset = self.image_set.create_subset()
        assert window.image_sets == [self.image_set, subset]
        self.image_set.remove_subset(subset)
        assert window.image_sets == [self.image_set]

    def test_open_selection(self, qtbot, window):
        qtbot.mouseClick(window.selection_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.selection_window)
        assert window.selection_window is not None
        assert isinstance(window.selection_window, Selection)
        assert window.selection_window.isVisible()

    def test_open_basic(self, qtbot, window):
        window.basic_window.close()
        qtbot.mouseClick(window.basic_btn, QtCore.Qt.LeftButton)
        assert window.basic_window.isVisible()
        assert isinstance(window.basic_window, BasicWidget)

    def test_open_transforms(self, qtbot, window):
        assert window.transforms_window is None
        qtbot.mouseClick(window.transforms_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.transforms_window)
        assert window.transforms_window is not None
        assert window.transforms_window.isVisible()
        assert isinstance(window.transforms_window, Transforms)

    def test_open_roi_histogram(self, qtbot, window):
        assert window.roi_histogram_window is None
        qtbot.mouseClick(window.roi_histogram_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.roi_histogram_window)
        assert window.roi_histogram_window is not None
        assert window.roi_histogram_window.isVisible()
        assert isinstance(window.roi_histogram_window, ROIHistogramWidget)

    def test_open_roi_line_plot(self, qtbot, window):
        assert window.roi_line_plot_window is None
        qtbot.mouseClick(window.roi_line_plot_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.roi_line_plot_window)
        assert window.roi_line_plot_window is not None
        assert window.roi_line_plot_window.isVisible()
        assert isinstance(window.roi_line_plot_window, ROILinePlotWidget)

    def test_add_window(self, qtbot, window):
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

    def test_open_set_wavelengths(self, qtbot, window):
        assert window.set_wavelength_window is None
        qtbot.mouseClick(window.set_wavelengths_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.set_wavelength_window)
        assert window.set_wavelength_window is not None
        assert window.set_wavelength_window.isVisible()
        assert isinstance(window.set_wavelength_window, SetWavelengthWidget)

    def test_quit(self, qtbot, window):
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
        qtbot.mouseClick(window.set_wavelengths_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.set_wavelength_window)
        assert window.transforms_window.isVisible()
        assert window.basic_window.isVisible()
        assert window.selection_window.isVisible()
        assert window.roi_histogram_window.isVisible()
        assert window.roi_line_plot_window.isVisible()
        assert window.set_wavelength_window.isVisible()
        assert window.isVisible()
        qtbot.mouseClick(window.quit_btn, QtCore.Qt.LeftButton)
        assert not window.transforms_window.isVisible()
        assert not window.basic_window.isVisible()
        assert not window.selection_window.isVisible()
        assert not window.roi_histogram_window.isVisible()
        assert not window.roi_line_plot_window.isVisible()
        assert not window.set_wavelength_window.isVisible()
        assert not window.pan_view.isVisible()
        assert not window.isVisible()


@pytest.mark.parametrize(
    'inlist',
    [TEST_FILES, ','.join(TEST_FILES)]
)
def test_open_pdsspect(inlist, qtbot):
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    window = open_pdsspect(app, inlist)
    qtbot.add_widget(window)
    qtbot.add_widget(window.basic_window)
    qtbot.add_widget(window.pan_view)
    assert isinstance(window, PDSSpect)


@pytest.mark.parametrize(
    'args, expected',
    [
        (test_dir, glob(os.path.join(test_dir, '*'))),
        (os.path.join(test_dir, '*'), glob(os.path.join(test_dir, '*'))),
        ('', glob('*'))
    ])
def test_arg_parser(args, expected):
    assert arg_parser(args) == expected
