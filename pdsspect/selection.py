import os

import numpy as np
from qtpy import QtWidgets, QtCore

from .pdsspect_image_set import PDSSpectImageSetViewBase


class SelectionController(object):

    def __init__(self, model, view):
        self.image_set = model
        self.view = view

    def change_current_color_index(self, index):
        self.image_set.current_color_index = index

    def change_selection_index(self, index):
        self.image_set.selection_index = index

    def change_alpha(self, new_alpha):
        self.image_set.alpha = new_alpha / 100.

    def clear_current_color(self):
        self.image_set.delete_rois_with_color(self.image_set.color)

    def clear_all(self):
        self.image_set.delete_all_rois()

    def add_ROI(self, coords, color):
        self.image_set.add_coords_to_roi_data_with_color(
            coords, color)


class Selection(QtWidgets.QDialog, PDSSpectImageSetViewBase):

    def __init__(self, image_set, parent=None):
        super(Selection, self).__init__()
        self.image_set = image_set
        self.parent = parent
        self.controller = SelectionController(image_set, self)

        self.type_label = QtWidgets.QLabel('Type:')
        self.selection_menu = QtWidgets.QComboBox()
        for selection_type in self.image_set.selection_types:
            self.selection_menu.addItem(selection_type)
        self.selection_menu.setCurrentIndex(self.image_set.selection_index)
        self.selection_menu.currentIndexChanged.connect(
            self.change_selection_type)
        self.type_layout = QtWidgets.QHBoxLayout()
        self.type_layout.addWidget(self.type_label)
        self.type_layout.addWidget(self.selection_menu)

        self.color_label = QtWidgets.QLabel('Color:')
        self.color_menu = QtWidgets.QComboBox()
        for color in self.image_set.colors:
            self.color_menu.addItem(color)
        self.color_menu.setCurrentIndex(image_set.current_color_index)
        self.color_menu.currentIndexChanged.connect(self.change_color)
        self.color_layout = QtWidgets.QHBoxLayout()
        self.color_layout.addWidget(self.color_label)
        self.color_layout.addWidget(self.color_menu)

        self.opacity_label = QtWidgets.QLabel('Opacity:')
        self.opacity_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.opacity_slider.setRange(0.0, 100.)
        self.opacity_slider.setValue(self.image_set.alpha * 100.)
        self.opacity_slider.valueChanged.connect(self.change_alpha)
        self.opacity_layout = QtWidgets.QHBoxLayout()
        self.opacity_layout.addWidget(self.opacity_label)
        self.opacity_layout.addWidget(self.opacity_slider)

        self.clear_current_color_btn = QtWidgets.QPushButton(
            'Clear Current Color')
        self.clear_current_color_btn.clicked.connect(self.clear_current_color)

        self.clear_all_btn = QtWidgets.QPushButton('Clear All')
        self.clear_all_btn.clicked.connect(self.clear_all)

        self.export_btn = QtWidgets.QPushButton("Export ROIs")
        self.export_btn.clicked.connect(self.open_save_dialog)

        self.load_btn = QtWidgets.QPushButton("Load ROIs")
        self.load_btn.clicked.connect(self.show_open_dialog)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.type_layout)
        self.main_layout.addLayout(self.color_layout)
        self.main_layout.addLayout(self.opacity_layout)
        self.main_layout.addWidget(self.clear_current_color_btn)
        self.main_layout.addWidget(self.clear_all_btn)
        self.main_layout.addWidget(self.export_btn)
        self.main_layout.addWidget(self.load_btn)

        self.setLayout(self.main_layout)

    def change_color(self, index):
        self.controller.change_current_color_index(index)

    def change_selection_type(self, index):
        self.controller.change_selection_index(index)

    def change_alpha(self, new_alpha):
        self.controller.change_alpha(new_alpha)

    def clear_current_color(self):
        self.controller.clear_current_color()

    def clear_all(self):
        self.controller.clear_all()

    def _get_rois_masks_to_export(self):
        exported_rois = {}
        for color in self.image_set.colors:
            mask = np.zeros(self.image_set.current_image.shape, dtype=np.bool)
            rows, cols = self.image_set.get_coordinates_of_color(color)
            mask[rows, cols] = True
            exported_rois[color] = mask
        return exported_rois

    def open_save_dialog(self):
        save_dialog = QtWidgets.QFileDialog(self)
        save_dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        save_dialog.setNameFilter("Selections(*.npz)")
        save_dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        if save_dialog.exec_():
            save_file = save_dialog.getSaveFileName(self, None)[0]
            self.export(save_file)

    def export(self, save_file):
        exported_rois = self._get_rois_masks_to_export()
        exported_rois['files'] = np.array(self.image_set.filenames)
        np.savez(save_file, **exported_rois)

    def _check_pdsspect_selection_is_file(self, filepath):
        base, ext = os.path.splitext(filepath)
        if ext != '.npz':
            raise RuntimeError(
                '%s is not a pdsspect selection file' % filepath
            )

    def _check_files_in_selection_file_compatible(self, files):
        for file in files:
            if os.path.basename(file) not in self.image_set.filenames:
                raise RuntimeError('%s not an opened image')

    def load_selections(self, selected_files):
            for selected_file in selected_files:
                self._check_pdsspect_selection_is_file(selected_file)
                arr_dict = np.load(selected_file)
                self._check_files_in_selection_file_compatible(
                    arr_dict['files'])
                for color in self.image_set.colors:
                    coords = np.column_stack(np.where(arr_dict[color]))
                    if coords.size > 0:
                        self.controller.add_ROI(coords, color)

    def show_open_dialog(self):
        open_dialog = QtWidgets.QFileDialog(self)
        open_dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        open_dialog.setNameFilter("Selections(*.npz)")
        open_dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        if open_dialog.exec_():
            selected_files = open_dialog.getOpenFileNames(self)[0]
            self.load_selections(selected_files)
