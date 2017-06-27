import os
import shutil
import tempfile
from contextlib import contextmanager

from . import *  # Import Test File Paths from __init__

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
    controller = SelectionController(image_set, None)

    def test_change_current_color_index(self):
        assert self.image_set.current_color_index == 0
        self.controller.change_current_color_index(1)
        assert self.image_set.current_color_index == 1
        self.controller.change_current_color_index(0)
        assert self.image_set.current_color_index == 0

    def test_selection_index(self):
        assert self.image_set.selection_index == 0
        self.controller.change_selection_index(1)
        assert self.image_set.selection_index == 1
        self.controller.change_selection_index(0)
        assert self.image_set.selection_index == 0

    def test_change_alpha(self):
        assert self.image_set.alpha == 1.0
        self.controller.change_alpha(50)
        assert self.image_set.alpha == .5
        self.controller.change_alpha(100)
        assert self.image_set.alpha == 1.0

    def test_clear_current_color(self):
        self.image_set._roi_data[4, 2] = [255.0, 0.0, 0.0, 255.]
        self.controller.clear_current_color()
        assert np.array_equal(
            self.image_set._roi_data[4, 2], [0, 0, 0, 0]
        )

    def test_clear_all(self):
        self.image_set._roi_data[4, 2] = [255.0, 0.0, 0.0, 255.]
        self.image_set._roi_data[2, 4] = [165.0, 42.0, 42.0, 255.]
        self.controller.clear_all()
        assert np.array_equal(
            self.image_set._roi_data[4, 2], [0, 0, 0, 0]
        )
        assert np.array_equal(
            self.image_set._roi_data[2, 4], [0, 0, 0, 0]
        )

    def test_add_ROI(self):
        coords = np.array([[4, 2]])
        self.controller.add_ROI(coords, 'red')
        assert np.array_equal(
            self.image_set._roi_data[4, 2], [255.0, 0.0, 0.0, 255.]
        )


class TestSelection(object):
    image_set = PDSSpectImageSet([FILE_1])
    sel = Selection(image_set)
    roi_coords = np.array(
        [
            [512, 509],
            [512, 510],
            [513, 509],
            [513, 510],
        ]
    )

    def test_change_color(self, qtbot):
        assert self.image_set.current_color_index == 0
        self.sel.change_color(1)
        assert self.image_set.current_color_index == 1
        self.sel.change_color(0)
        assert self.image_set.current_color_index == 0

        self.sel.show()
        qtbot.add_widget(self.sel)
        self.sel.color_menu.setCurrentIndex(1)
        assert self.image_set.current_color_index == 1
        self.sel.color_menu.setCurrentIndex(0)
        assert self.image_set.current_color_index == 0

    def test_change_selection_type(self, qtbot):
        assert self.image_set.selection_index == 0
        self.sel.change_selection_type(1)
        assert self.image_set.selection_index == 1
        self.sel.change_selection_type(0)
        assert self.image_set.selection_index == 0

        self.sel.show()
        qtbot.add_widget(self.sel)
        self.sel.selection_menu.setCurrentIndex(1)
        assert self.image_set.selection_index == 1
        self.sel.selection_menu.setCurrentIndex(0)
        assert self.image_set.selection_index == 0

    def test_change_alpah(self, qtbot):
        assert self.image_set.alpha == 1.0
        self.sel.change_alpha(50)
        assert self.image_set.alpha == .5
        self.sel.change_alpha(100)
        assert self.image_set.alpha == 1.0

        self.sel.show()
        qtbot.add_widget(self.sel)
        self.sel.opacity_slider.setValue(50)
        assert self.image_set.alpha == .5
        self.sel.opacity_slider.setValue(100)
        assert self.image_set.alpha == 1.0

    def test_clear_current_color(self, qtbot):
        self.image_set._roi_data[4, 2] = [255.0, 0.0, 0.0, 255.]
        self.sel.clear_current_color()
        assert np.array_equal(
            self.image_set._roi_data[4, 2], [0, 0, 0, 0]
        )

        self.image_set._roi_data[4, 2] = [255.0, 0.0, 0.0, 255.]
        self.sel.show()
        qtbot.add_widget(self.sel)
        qtbot.mouseClick(
            self.sel.clear_current_color_btn, QtCore.Qt.LeftButton
        )
        assert np.array_equal(
            self.image_set._roi_data[4, 2], [0, 0, 0, 0]
        )

    def test_clear_all(self, qtbot):
        self.image_set._roi_data[4, 2] = [255.0, 0.0, 0.0, 255.]
        self.image_set._roi_data[2, 4] = [165.0, 42.0, 42.0, 255.]
        self.sel.clear_all()
        assert np.array_equal(
            self.image_set._roi_data[4, 2], [0, 0, 0, 0]
        )
        assert np.array_equal(
            self.image_set._roi_data[2, 4], [0, 0, 0, 0]
        )

        self.image_set._roi_data[4, 2] = [255.0, 0.0, 0.0, 255.]
        self.image_set._roi_data[2, 4] = [165.0, 42.0, 42.0, 255.]
        self.sel.show()
        qtbot.add_widget(self.sel)
        qtbot.mouseClick(
            self.sel.clear_all_btn, QtCore.Qt.LeftButton
        )
        assert np.array_equal(
            self.image_set._roi_data[4, 2], [0, 0, 0, 0]
        )
        assert np.array_equal(
            self.image_set._roi_data[2, 4], [0, 0, 0, 0]
        )

    def test_get_rois_masks_to_export(self):
        self.sel.controller.add_ROI(self.roi_coords, 'red')
        test_rois_dict = self.sel._get_rois_masks_to_export()
        assert np.array_equal(
            np.where(test_rois_dict['red'])[0], np.array([512, 512, 513, 513])
        )
        assert np.array_equal(
            np.where(test_rois_dict['red'])[1], np.array([509, 510, 509, 510])
        )

    def test_export(self):
        self.sel.controller.add_ROI(self.roi_coords, 'red')
        with make_temp_directory() as tmpdirname:
            save_file = os.path.join(tmpdirname, 'temp.npz')
            self.sel.export(save_file)
            np_file = np.load(save_file)
            assert np.array_equal(
                np.where(np_file['red'])[0], np.array([512, 512, 513, 513])
            )
            assert np.array_equal(
                np.where(np_file['red'])[1], np.array([509, 510, 509, 510])
            )
            assert np_file['files'] == FILE_1_NAME

    def test_check_pdsspect_selection_is_file(self):
        self.sel._check_pdsspect_selection_is_file('foo.npz')
        with pytest.raises(RuntimeError):
            self.sel._check_pdsspect_selection_is_file('foo.txt')

    def test_check_files_in_selection_file_compatible(self):
        self.sel._check_files_in_selection_file_compatible([FILE_1])
        with pytest.raises(RuntimeError):
            self.sel._check_files_in_selection_file_compatible(TEST_FILES)

    def test_load_selections(self):
        self.sel.load_selections([SAMPLE_ROI])
        rows, cols = np.column_stack(self.roi_coords)
        for pixel in self.image_set._roi_data[rows, cols]:
            assert np.array_equal(
                pixel, [255.0, 0.0, 0.0, 255.]
            )
