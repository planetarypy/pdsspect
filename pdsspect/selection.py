"""Window to pick selection type/color, load/export ROIs and clear ROIS"""
import os

import numpy as np
from qtpy import QtWidgets, QtCore

from .pdsspect_image_set import PDSSpectImageSetViewBase


class SelectionController(object):
    """Controller for :class:`Selection`

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view : :class:`Selection`
        View to control

    Attributes
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view : :class:`Selection`
        View to control
    """

    def __init__(self, image_set, view):
        self.image_set = image_set
        self.view = view

    def change_current_color_index(self, index):
        """Change the current color index to a new index

        Parameters
        ----------
        index : :obj:`int`
            The new color index
        """

        self.image_set.current_color_index = index
        for subset in self.image_set.subsets:
            subset.current_color_index = index

    def change_selection_index(self, index):
        """Change the selection index to a new index

        Parameters
        ----------
        index : :obj:`int`
            The new selection index
        """

        self.image_set.selection_index = index
        for subset in self.image_set.subsets:
            subset.selection_index = index

    def change_alpha(self, new_alpha):
        """Change the alpha value to a new alpha value

        Parameters
        ----------
        new_alpha : :obj:`float`
            Value between 0 and 100
        """

        new_alpha /= 100.
        self.image_set.alpha = new_alpha
        for subset in self.image_set.subsets:
            subset.alpha = new_alpha

    def clear_current_color(self):
        """Clear all the ROIs with the currently selcted color"""
        self.image_set.delete_rois_with_color(self.image_set.color)
        for subset in self.image_set.subsets:
            subset.delete_rois_with_color(subset.color)

    def clear_all(self):
        """Clear all ROIs"""
        self.image_set.delete_all_rois()
        for subset in self.image_set.subsets:
            subset.delete_all_rois()

    def add_ROI(self, coordinates, color, image_set=None):
        """Add ROI with the given coordinates and color

        Parameters
        ----------
        coordinates : :class:`numpy.ndarray` or :obj:`tuple`
            Either a ``(m x 2)`` array or a tuple of two arrays

            If an array, the first column are the x coordinates and the second
            are the y coordinates. If a tuple of arrays, the first array are x
            coordinates and the second are the corresponding y coordinates.
        color : :obj:`str`
            The name a color in
            :attr:`~pdsspect.pdsspect_image_set.PDSSpectImageSet.colors`
        """

        image_set = self.image_set if image_set is None else image_set

        image_set.add_coords_to_roi_data_with_color(
            coordinates=coordinates,
            color=color
        )

    def set_simultaneous_roi(self, state):
        self.image_set.simultaneous_roi = state


class Selection(QtWidgets.QWidget, PDSSpectImageSetViewBase):
    """Window to make/clear/load/export ROIs and choose selection mode/color

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    parent : None
        Parent of the view

    Attributes
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    parent : None
        Parent of the view
    controller : :class:`SelectionController`
        View controller
    type_label : :class:`QtWidgets.QLabel <PySide.QtGui.QLabel>`
        Label for the selection menu
    selection_menu : :class:`QtWidgets.QComboBox <PySide.QtGui.QComboBox>`
        Drop down menu of selection types
    type_layout : :class:`QtWidgets.QHBoxLayout <PySide.QtGui.QHBoxLayout>`
        Horizontal box layout for selection
    color_label : :class:`QtWidgets.QLabel <PySide.QtGui.QLabel>`
        Label for the :attr:`color_menu`
    color_menu : :class:`QtWidgets.QComboBox <PySide.QtGui.QComboBox>`
        Drop down menu for color selection
    color_layout : :class:`QtWidgets.QHBoxLayout <PySide.QtGui.QHBoxLayout>`
        Horizontal box layout for color selection
    opacity_label : :class:`QtWidgets.QLabel <PySide.QtGui.QLabel>`
        Label for the :attr:`opacity_slider`
    opacity_slider : :class:`QtWidgets.QSlider <PySide.QtGui.QSlider>`
        Slider to determine opacity for ROIs
    opacity_layout : :class:`QtWidgets.QHBoxLayout <PySide.QtGui.QHBoxLayout>`
        Horizontal box layout for opacity slider
    clear_current_color_btn : :class:`QtWidgets.QPushButton\
    <PySide.QtGui.QPushButton>`
        Button to clear all ROIs will the current color
    clear_all_btn : :class:`QtWidgets.QPushButton <PySide.QtGui.QPushButton>`
        Button to clear all ROIs
    export_btn : :class:`QtWidgets.QPushButton <PySide.QtGui.QPushButton>`
        Export ROIs to ``.npz`` file
    load_btn : :class:`QtWidgets.QPushButton <PySide.QtGui.QPushButton>`
        Load ROIs from ``.npz`` file
    simultaneous_roi_box : :class:`QtWidgets.QPushButton\
    <PySide.QtGui.QPushButton>`
        When checked, new ROIs appear in every window
    main_layout : :class:`QtWidgets.QVBoxLayout <PySide.QtGui.QVBoxLayout>`
        Vertical Box layout for main layout
    """

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
            self.change_selection_type
        )
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
            'Clear Current Color'
        )
        self.clear_current_color_btn.clicked.connect(self.clear_current_color)

        self.clear_all_btn = QtWidgets.QPushButton('Clear All')
        self.clear_all_btn.clicked.connect(self.clear_all)

        self.export_btn = QtWidgets.QPushButton("Export ROIs")
        self.export_btn.clicked.connect(self.open_save_dialog)

        self.load_btn = QtWidgets.QPushButton("Load ROIs")
        self.load_btn.clicked.connect(self.show_open_dialog)

        self.simultaneous_roi_box = QtWidgets.QCheckBox(
            'Select ROIs simultaneously'
        )
        self.simultaneous_roi_box.stateChanged.connect(
            self.select_simultaneous_roi
        )

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addLayout(self.type_layout)
        self.main_layout.addLayout(self.color_layout)
        self.main_layout.addLayout(self.opacity_layout)
        self.main_layout.addWidget(self.clear_current_color_btn)
        self.main_layout.addWidget(self.clear_all_btn)
        self.main_layout.addWidget(self.export_btn)
        self.main_layout.addWidget(self.load_btn)
        self.main_layout.addWidget(self.simultaneous_roi_box)

        self.setLayout(self.main_layout)

    def change_color(self, index):
        """Change the color when color selected in :attr:`color_menu`"""
        self.controller.change_current_color_index(index)

    def change_selection_type(self, index):
        """Change selection type when selected in :attr:`selection_menu`"""
        self.controller.change_selection_index(index)

    def change_alpha(self, new_alpha):
        """Change alpha value when :attr:`opacity_slider` value changes"""
        self.controller.change_alpha(new_alpha)

    def clear_current_color(self):
        """Clear all ROIs with current color"""
        self.controller.clear_current_color()

    def clear_all(self):
        """Clear all ROIs"""
        self.controller.clear_all()

    def export(self, save_file):
        """Export ROIS to the given filename

        Parameters
        ----------
        save_file : :obj:`str`
            File with ``.npz`` extension to save ROIs
        """
        exported_rois = self.image_set.get_rois_masks_to_export()
        exported_rois['files'] = np.array(self.image_set.filenames)
        exported_rois['shape'] = self.image_set.shape
        exported_rois['views'] = len(self.image_set._subsets) + 1
        np.savez(save_file, **exported_rois)

    def open_save_dialog(self):
        """Open save file dialog and save rois to given filename"""
        save_file, _ = QtWidgets.QFileDialog.getSaveFileName(
            parent=self,
            caption='Export ROIs',
            filter='*.npz',
        )
        if save_file != '':
            self.export(save_file)

    def _check_pdsspect_selection_is_file(self, filepath):
        base, ext = os.path.splitext(filepath)
        if ext != '.npz':
            raise RuntimeError(
                '%s is not a pdsspect selection file' % filepath
            )

    def _check_files_in_selection_file_compatible(self, files):
        for file in files:
            if os.path.basename(file) not in self.image_set.filenames:
                raise RuntimeError('%s not an opened image' % file)

    def _check_shape_is_the_same(self, shape):
        if not np.array_equal(self.image_set.shape, shape):
            raise RuntimeError(
                'Cannot open import ROIs because the shapes are not the same'
            )

    def load_selections(self, selected_files):
        """Load ROIs from selected files

        Parameters
        ----------
        selected_files : :obj:`list` of :obj:`str`
            Paths to files storing ROIs
        """
        for selected_file in selected_files:
            self._check_pdsspect_selection_is_file(selected_file)
            arr_dict = np.load(selected_file)
            self._check_files_in_selection_file_compatible(arr_dict['files'])
            self._check_shape_is_the_same(arr_dict['shape'])
            num_load_views = arr_dict['views']
            num_current_views = len(self.image_set._subsets) + 1
            has_multiple_views = all(
                (num_load_views > 1, num_current_views > 1)
            )
            if has_multiple_views:
                if num_load_views < num_current_views:
                    num_views = num_load_views
                else:
                    num_views = num_current_views
            else:
                num_views = 0
            for color in self.image_set.colors:
                coords = np.column_stack(np.where(arr_dict[color]))
                if coords.size > 0:
                    self.controller.add_ROI(coords, color)
                for num_view in range(num_views - 1):
                    subset = self.image_set._subsets[num_view]
                    name = color + str(num_view + 2)
                    coords = np.column_stack(np.where(arr_dict[name]))
                    if coords.size > 0:
                        self.controller.add_ROI(coords, color, subset)

    def show_open_dialog(self):
        """Open file dialog to select ``.npz`` files to load ROIs"""
        selected_files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            parent=self,
            caption='Open ROIs',
            filter='Selections(*.npz)',
        )
        self.load_selections(selected_files)

    def select_simultaneous_roi(self, state):
        self.controller.set_simultaneous_roi(
            self.simultaneous_roi_box.isChecked()
        )
