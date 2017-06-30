from . import *  # Import Test File Paths from __init__

import pytest
from qtpy import QtCore

from pdsspect.basic import Basic
from pdsspect.pdsspect import PDSSpect
from pdsspect.selection import Selection
from pdsspect.transforms import Transforms
from pdsspect.pdsspect_image_set import PDSSpectImageSet


class TestPDSSpect(object):
    image_set = PDSSpectImageSet(TEST_FILES)

    @pytest.fixture
    def window(self):
        return PDSSpect(self.image_set)

    def test_init(self, window):
        assert window.selection_window is None
        assert window.basic_window is not None
        assert window.transforms_window is None

    def test_open_selection(self, qtbot, window):
        window.show()
        qtbot.add_widget(window)
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
        assert isinstance(window.basic_window, Basic)

    def test_open_transforms(self, qtbot, window):
        window.show()
        qtbot.add_widget(window)
        assert window.transforms_window is None
        qtbot.mouseClick(window.transforms_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.transforms_window)
        assert window.transforms_window is not None
        assert window.transforms_window.isVisible()
        assert isinstance(window.transforms_window, Transforms)

    def test_quit(self, qtbot, window):
        window.show()
        qtbot.add_widget(window)
        qtbot.mouseClick(window.transforms_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.transforms_window)
        qtbot.mouseClick(window.basic_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.basic_window)
        qtbot.mouseClick(window.selection_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(window.selection_window)
        assert window.transforms_window.isVisible()
        assert window.basic_window.isVisible()
        assert window.selection_window.isVisible()
        assert window.isVisible()
        qtbot.mouseClick(window.quit_btn, QtCore.Qt.LeftButton)
        assert not window.transforms_window.isVisible()
        assert not window.basic_window.isVisible()
        assert not window.selection_window.isVisible()
        assert not window.isVisible()
