from qtpy import QtWidgets

import numpy as np


class SetWavelengthModel(object):

    def __init__(self, image_set):
        self._views = []
        self.image_set = image_set
        self._current_image_index = int(image_set.current_image_index)

    def register(self, view):
        if view not in self._views:
            self._views.append(view)

    def unregister(self, view):
        if view in self._views:
            self._views.remove(view)

    @property
    def accepted_units(self):
        return self.image_set.accepted_units

    @property
    def current_image_index(self):
        return self._current_image_index

    @current_image_index.setter
    def current_image_index(self, index):
        self._current_image_index = index
        self.display_current_wavelength()

    @property
    def current_image(self):
        return self.image_set.images[self.current_image_index]

    @property
    def unit(self):
        return self.image_set.unit

    @unit.setter
    def unit(self, new_unit):
        try:
            self.image_set.unit = new_unit
        except ValueError:
            pass
        finally:
            self.display_current_wavelength()

    @property
    def unit_index(self):
        return self.accepted_units.index(self.unit)

    def display_current_wavelength(self):
        for view in self._views:
            view.display_current_wavelength()


class SetWavelengthController(object):

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def set_current_image_index(self, index):
        self.model.current_image_index = index

    def change_unit(self, index):
        self.model.unit = self.model.accepted_units[index]

    def set_image_wavelength(self, wavelength):
        self.model.current_image.wavelength = wavelength
        self.model.display_current_wavelength()


class SetWavelengthWidget(QtWidgets.QWidget):

    def __init__(self, model):
        super(SetWavelengthWidget, self).__init__()
        self.model = model
        model.register(self)
        self.controller = SetWavelengthController(model, self)

        self.image_menu = QtWidgets.QComboBox()
        for image in self.model.image_set.images:
            self.image_menu.addItem(image.image_name)
        self.image_menu.setCurrentIndex(self.model.current_image_index)
        self.image_menu.currentIndexChanged.connect(self.select_image)

        self.wavelength_text = QtWidgets.QLineEdit()
        self.wavelength_text.returnPressed.connect(self.set_wavelength)

        self.units_menu = QtWidgets.QComboBox()
        for unit in self.model.accepted_units:
            self.units_menu.addItem(unit)
        self.units_menu.setCurrentIndex(self.model.unit_index)
        self.units_menu.currentIndexChanged.connect(self.change_unit)

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addWidget(self.image_menu)
        self.main_layout.addWidget(self.wavelength_text)
        self.main_layout.addWidget(self.units_menu)
        self.setLayout(self.main_layout)
        self.setWindowTitle("Set Wavelengths")

    def select_image(self, index):
        self.controller.set_current_image_index(index)

    def display_current_wavelength(self):
        wavelength = self.model.current_image.wavelength
        if np.isnan(wavelength):
            self.wavelength_text.setText('')
        else:
            self.wavelength_text.setText(str(wavelength))

    def set_wavelength(self):
        try:
            wavelength = float(self.wavelength_text.text())
            self.controller.set_image_wavelength(wavelength)
        except ValueError:
            self.display_current_wavelength()

    def change_unit(self, index):
        self.controller.change_unit(index)
