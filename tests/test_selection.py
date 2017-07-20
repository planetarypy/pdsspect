import os
import shutil
import tempfile
from contextlib import contextmanager

from . import TEST_FILES, FILE_1, FILE_1_NAME, SAMPLE_ROI

import pytest
import numpy as np
from qtpy import QtCore

from pdsspect.pdsspect_image_set import PDSSpectImageSet
from pdsspect.selection import SelectionController, Selection


@contextmanager
def make_temp_directory():
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


class TestSelectionController(object):
    image_set = PDSSpectImageSet(TEST_FILES)
    subset = image_set.create_subset()

    @pytest.fixture
    def controller(self):
        self.image_set = PDSSpectImageSet(TEST_FILES)
        self.subset = self.image_set.create_subset()
        return SelectionController(self.image_set, None)

    def test_change_current_color_index(self, controller):
        assert self.image_set.current_color_index == 0
        assert self.subset.current_color_index == 0
        controller.change_current_color_index(1)
        assert self.image_set.current_color_index == 1
        assert self.subset.current_color_index == 1
        controller.change_current_color_index(0)
        assert self.image_set.current_color_index == 0
        assert self.subset.current_color_index == 0

    def test_selection_index(self, controller):
        assert self.image_set.selection_index == 0
        assert self.subset.selection_index == 0
        controller.change_selection_index(1)
        assert self.image_set.selection_index == 1
        assert self.subset.selection_index == 1
        controller.change_selection_index(0)
        assert self.image_set.selection_index == 0
        assert self.subset.selection_index == 0

    def test_change_alpha(self, controller):
        assert self.image_set.alpha == 1.0
        assert self.subset.alpha == 1.0
        controller.change_alpha(50)
        assert self.image_set.alpha == 0.5
        assert self.subset.alpha == 0.5
        controller.change_alpha(100)
        assert self.image_set.alpha == 1.0
        assert self.subset.alpha == 1.0

    def test_clear_current_color(self, controller):
        self.image_set._roi_data[4, 2] = [255.0, 0.0, 0.0, 255.]
        self.subset._roi_data[4, 2] = [255.0, 0.0, 0.0, 255.]
        controller.clear_current_color()
        assert np.array_equal(
            self.image_set._roi_data[4, 2], [0, 0, 0, 0]
        )
        assert np.array_equal(
            self.subset._roi_data[4, 2], [0, 0, 0, 0]
        )

    def test_clear_all(self, controller):
        self.image_set._roi_data[4, 2] = [255.0, 0.0, 0.0, 255.]
        self.image_set._roi_data[2, 4] = [165.0, 42.0, 42.0, 255.]
        self.subset._roi_data[4, 2] = [255.0, 0.0, 0.0, 255.]
        self.subset._roi_data[2, 4] = [165.0, 42.0, 42.0, 255.]
        controller.clear_all()
        assert np.array_equal(
            self.image_set._roi_data[4, 2], [0, 0, 0, 0]
        )
        assert np.array_equal(
            self.image_set._roi_data[2, 4], [0, 0, 0, 0]
        )
        assert np.array_equal(
            self.subset._roi_data[4, 2], [0, 0, 0, 0]
        )
        assert np.array_equal(
            self.subset._roi_data[2, 4], [0, 0, 0, 0]
        )

    def test_add_ROI(self, controller):
        coords = np.array([[4, 2]])
        controller.add_ROI(coords, 'red')
        assert np.array_equal(
            self.image_set._roi_data[4, 2], [255.0, 0.0, 0.0, 255.]
        )
        assert not np.array_equal(
            self.subset._roi_data[4, 2], [255.0, 0.0, 0.0, 255.]
        )
        controller.add_ROI(coords, 'red', self.subset)
        assert np.array_equal(
            self.subset._roi_data[4, 2], [255.0, 0.0, 0.0, 255.]
        )

    def test_set_simultaneous_roi(self, controller):
        assert not self.image_set.simultaneous_roi
        controller.set_simultaneous_roi(True)
        assert self.image_set.simultaneous_roi
        controller.set_simultaneous_roi(False)
        assert not self.image_set.simultaneous_roi


class TestSelection(object):
    image_set = PDSSpectImageSet([FILE_1])
    subset = image_set.create_subset()
    roi_coords = np.array(
        [
            [512, 509],
            [512, 510],
            [513, 509],
            [513, 510],
        ]
    )

    @pytest.fixture
    def selection(self):
        self.image_set = PDSSpectImageSet([FILE_1])
        self.subset = self.image_set.create_subset()
        return Selection(self.image_set)

    def test_change_color(self, qtbot, selection):
        assert self.image_set.current_color_index == 0
        assert self.subset.current_color_index == 0
        selection.change_color(1)
        assert self.image_set.current_color_index == 1
        assert self.subset.current_color_index == 1
        selection.change_color(0)
        assert self.image_set.current_color_index == 0
        assert self.subset.current_color_index == 0

        selection.show()
        qtbot.add_widget(selection)
        selection.color_menu.setCurrentIndex(1)
        assert self.image_set.current_color_index == 1
        assert self.subset.current_color_index == 1
        selection.color_menu.setCurrentIndex(0)
        assert self.image_set.current_color_index == 0
        assert self.subset.current_color_index == 0

    def test_change_selection_type(self, qtbot, selection):
        assert self.image_set.selection_index == 0
        assert self.subset.selection_index == 0
        selection.change_selection_type(1)
        assert self.image_set.selection_index == 1
        assert self.subset.selection_index == 1
        selection.change_selection_type(0)
        assert self.image_set.selection_index == 0
        assert self.subset.selection_index == 0

        selection.show()
        qtbot.add_widget(selection)
        selection.selection_menu.setCurrentIndex(1)
        assert self.image_set.selection_index == 1
        assert self.subset.selection_index == 1
        selection.selection_menu.setCurrentIndex(0)
        assert self.image_set.selection_index == 0
        assert self.subset.selection_index == 0

    def test_change_alpah(self, qtbot, selection):
        assert self.image_set.alpha == 1.0
        assert self.subset.alpha == 1.0
        selection.change_alpha(50)
        assert self.image_set.alpha == .5
        assert self.subset.alpha == .5
        selection.change_alpha(100)
        assert self.image_set.alpha == 1.0
        assert self.subset.alpha == 1.0

        selection.show()
        qtbot.add_widget(selection)
        selection.opacity_slider.setValue(50)
        assert self.image_set.alpha == .5
        assert self.subset.alpha == .5
        selection.opacity_slider.setValue(100)
        assert self.image_set.alpha == 1.0
        assert self.subset.alpha == 1.0

    def test_clear_current_color(self, qtbot, selection):
        self.image_set._roi_data[4, 2] = [255.0, 0.0, 0.0, 255.]
        selection.clear_current_color()
        assert np.array_equal(
            self.image_set._roi_data[4, 2], [0, 0, 0, 0]
        )

        self.image_set._roi_data[4, 2] = [255.0, 0.0, 0.0, 255.]
        selection.show()
        qtbot.add_widget(selection)
        qtbot.mouseClick(
            selection.clear_current_color_btn, QtCore.Qt.LeftButton
        )
        assert np.array_equal(
            self.image_set._roi_data[4, 2], [0, 0, 0, 0]
        )

    def test_clear_all(self, qtbot, selection):
        self.image_set._roi_data[4, 2] = [255.0, 0.0, 0.0, 255.]
        self.image_set._roi_data[2, 4] = [165.0, 42.0, 42.0, 255.]
        selection.clear_all()
        assert np.array_equal(
            self.image_set._roi_data[4, 2], [0, 0, 0, 0]
        )
        assert np.array_equal(
            self.image_set._roi_data[2, 4], [0, 0, 0, 0]
        )

        self.image_set._roi_data[4, 2] = [255.0, 0.0, 0.0, 255.]
        self.image_set._roi_data[2, 4] = [165.0, 42.0, 42.0, 255.]
        selection.show()
        qtbot.add_widget(selection)
        qtbot.mouseClick(
            selection.clear_all_btn, QtCore.Qt.LeftButton
        )
        assert np.array_equal(
            self.image_set._roi_data[4, 2], [0, 0, 0, 0]
        )
        assert np.array_equal(
            self.image_set._roi_data[2, 4], [0, 0, 0, 0]
        )

    def test_export(self, selection):
        selection.controller.add_ROI(self.roi_coords, 'red')
        selection.controller.add_ROI(self.roi_coords, 'darkgreen', self.subset)
        rows, cols = np.column_stack(self.roi_coords)
        with make_temp_directory() as tmpdirname:
            save_file = os.path.join(tmpdirname, 'temp.npz')
            selection.export(save_file)
            np_file = np.load(save_file)
            assert np.array_equal(
                np.where(np_file['red'])[0], rows
            )
            assert np.array_equal(
                np.where(np_file['red'])[1], cols
            )
            assert np.array_equal(
                np.where(np_file['darkgreen2'])[0], rows
            )
            assert np.array_equal(
                np.where(np_file['darkgreen2'])[1], cols
            )
            assert np_file['files'] == FILE_1_NAME
            assert np_file['views'] == 2

    def test_check_pdsspect_selection_is_file(self, selection):
        selection._check_pdsspect_selection_is_file('foo.npz')
        with pytest.raises(RuntimeError):
            selection._check_pdsspect_selection_is_file('foo.txt')

    def test_check_files_in_selection_file_compatible(self, selection):
        selection._check_files_in_selection_file_compatible([FILE_1])
        with pytest.raises(RuntimeError):
            selection._check_files_in_selection_file_compatible(TEST_FILES)

    def test_check_shape_is_the_same(self, selection):
        fail_shape = (self.image_set.shape[0] - 1, self.image_set.shape[1] + 5)
        with pytest.raises(RuntimeError):
            selection._check_shape_is_the_same(fail_shape)

    def test_load_selections(self, selection):
        selection.load_selections([SAMPLE_ROI])
        rows, cols = np.column_stack(self.roi_coords)
        for pixel in self.image_set._roi_data[rows, cols]:
            assert np.array_equal(
                pixel, [255.0, 0.0, 0.0, 255.]
            )
        for pixel in self.subset._roi_data[rows, cols]:
            assert np.array_equal(
                pixel, [0.0, 100.0, 0.0, 255.]
            )

    def test_select_simultaneous_roi(self, qtbot, selection):
        selection.show()
        qtbot.add_widget(selection)
        assert not self.image_set.simultaneous_roi
        selection.simultaneous_roi_box.setChecked(True)
        assert self.image_set.simultaneous_roi
        selection.simultaneous_roi_box.setChecked(False)
        assert not self.image_set.simultaneous_roi
