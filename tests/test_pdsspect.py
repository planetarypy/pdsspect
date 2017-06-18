from . import *  # Import Test File Paths from __init__

from qtpy import QtCore
from pdsspect.basic import Basic
from pdsspect.pdsspect import PDSSpect
from pdsspect.selection import Selection
from pdsspect.transforms import Transforms
from pdsspect.pdsspect_image_set import PDSSPectImageSet


class TestPDSSpect(object):
    image_set = PDSSPectImageSet(TEST_FILES)
    window = PDSSpect(image_set)

    def test_init(self):
        assert self.window.selection_window is None
        assert self.window.basic_window is not None
        assert self.window.transforms_window is None

    def test_open_selection(self, qtbot):
        self.window.show()
        qtbot.add_widget(self.window)
        qtbot.mouseClick(self.window.selection_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(self.window.selection_window)
        assert self.window.selection_window is not None
        assert isinstance(self.window.selection_window, Selection)
        assert self.window.selection_window.isVisible()

    def test_open_basic(self, qtbot):
        self.window.show()
        qtbot.add_widget(self.window)
        qtbot.add_widget(self.window.basic_window)
        self.window.basic_window.close()
        qtbot.mouseClick(self.window.basic_btn, QtCore.Qt.LeftButton)
        assert self.window.basic_window.isVisible()
        assert isinstance(self.window.basic_window, Basic)

    def test_open_transforms(self, qtbot):
        self.window.show()
        qtbot.add_widget(self.window)
        assert self.window.transforms_window is None
        qtbot.mouseClick(self.window.transforms_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(self.window.transforms_window)
        assert self.window.transforms_window is not None
        assert self.window.transforms_window.isVisible()
        assert isinstance(self.window.transforms_window, Transforms)

    def test_quit(self, qtbot):
        self.window.show()
        qtbot.add_widget(self.window)
        qtbot.mouseClick(self.window.transforms_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(self.window.transforms_window)
        qtbot.mouseClick(self.window.basic_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(self.window.basic_window)
        qtbot.mouseClick(self.window.selection_btn, QtCore.Qt.LeftButton)
        qtbot.add_widget(self.window.selection_window)
        assert self.window.transforms_window.isVisible()
        assert self.window.basic_window.isVisible()
        assert self.window.selection_window.isVisible()
        assert self.window.isVisible()
        qtbot.mouseClick(self.window.quit_btn, QtCore.Qt.LeftButton)
        assert not self.window.transforms_window.isVisible()
        assert not self.window.basic_window.isVisible()
        assert not self.window.selection_window.isVisible()
        assert not self.window.isVisible()
