from qtpy import QtWidgets

import numpy as np


class SetWavelengthModel(object):
    """Model for :class:`SetWavelengthWidget`

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model

    Attributes
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    """

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
        """:obj:`list` : List of accepted units: ``nm``, ``um``, and ``AA``"""
        return self.image_set.accepted_units

    @property
    def current_image_index(self):
        """:obj:`int` : Index of current image in menu"""
        return self._current_image_index

    @current_image_index.setter
    def current_image_index(self, index):
        self._current_image_index = index
        self.display_current_wavelength()

    @property
    def current_image(self):
        """:class:`~.pdsspect_image_set.ImageStamp` : Current image in menu"""
        return self.image_set.images[self.current_image_index]

    @property
    def unit(self):
        """:obj:`str` : :attr:`image_set` unit

        Setting the :attr`unit` will set the :attr:`image_set` unit
        """

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
        """:obj:`int` Index of :attr`unit` in :attr:`accepted_units`"""
        return self.accepted_units.index(self.unit)

    def display_current_wavelength(self):
        """Display current wavelength in registered views"""
        for view in self._views:
            view.display_current_wavelength()


class SetWavelengthController(object):
    """Controller for :class:`SetWavelengthWidget`

    Parameters
    ----------
    model : :class:`SetWavelengthModel`
        Model for :class:`SetWavelengthWidget`
    view : :class:`SetWavelengthWidget`
        The view to control

    Attributes
    ----------
    model : :class:`SetWavelengthModel`
        Model for :class:`SetWavelengthWidget`
    view : :class:`SetWavelengthWidget`
        The view to control
    """

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def set_current_image_index(self, index):
        """Set the model's :attr:`SetWavelengthModel.current_image_index`

        Parameters
        ----------
        index : :obj:`int`
            Index to change :attr:`SetWavelengthModel.current_image_index` to
        """

        self.model.current_image_index = index

    def change_unit(self, index):
        """Set the model's :attr:`SetWavelengthModel.unit`

        Parameters
        ----------
        index : :obj:`int`
            Index of :attr:`SetWavelengthModel.accepted_units` to change the
            :attr:`SetWavelengthModel.unit` to
        """

        self.model.unit = self.model.accepted_units[index]

    def set_image_wavelength(self, wavelength):
        """Set the model's :attr:`SetWavelengthModel.current_image` wavelength

        Parameters
        ----------
        wavelength : :obj:`float`
            The model's :attr:`SetWavelengthModel.current_image` new wavelength
        """

        self.model.current_image.wavelength = wavelength
        self.model.display_current_wavelength()
        for view in self.model.image_set._views:
            view.set_roi_data()


class SetWavelengthWidget(QtWidgets.QMainWindow):
    """Widget to set images wavelength

    Using a :class:`QtWidgets.QMainWindow <PySide.QtGui.QMainWindow>` for the
    status bar at the bottom.

    Parameters
    ----------
    model : :class:`SetWavelengthModel`
        Model for :class:`SetWavelengthWidget`

    Attributes
    ----------
    model : :class:`SetWavelengthModel`
        Model for :class:`SetWavelengthWidget`
    controller : :class:`SetWavelengthController`
        The widgets controller
    image_menu : :class:`QtWidgets.QComboBox <PySide.QtGui.QComboBox>`
        Menu to choose the image to set the wavelength
    wavelength_text : :class:`QtWidgets.QLineEdit <PySide.QtGui.QLineEdit>`
        Text box to enter and display wavelength
    units_menu : :class:`QtWidgets.QComboBox <PySide.QtGui.QComboBox>`
        Menu to choose unit of wavelength
    main_layout : :class:`QtWidgets.QHBoxLayout <PySide.QtGui.QHBoxLayout>`
        Main layout of widget
    """

    def __init__(self, model):
        super(SetWavelengthWidget, self).__init__()
        self.model = model
        self._central_widget = QtWidgets.QWidget()
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
        self._central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self._central_widget)
        self.setWindowTitle('Set Wavelengths')
        self.statusBar()
        self.display_current_wavelength()

    def select_image(self, index):
        """Select current image

        Parameters
        ----------
        index : :obj:`int`
            Index to change :attr:`SetWavelengthModel.current_image_index` to
        """

        self.controller.set_current_image_index(index)

    def display_current_wavelength(self):
        """Display the :attr:`SetWavelengthModel.current_image` wavelength in
        :attr:`wavelength_text`
        """

        wavelength = self.model.current_image.wavelength
        if np.isnan(wavelength):
            self.wavelength_text.setText('')
        else:
            self.wavelength_text.setText(str(wavelength))

    def set_wavelength(self):
        """Set the :attr:`SetWavelengthModel.current_image` wavelength to value
        in :attr:`wavelength_text`
        """

        try:
            wavelength = self.wavelength_text.text()
            if wavelength == '':
                wavelength = float('nan')
            else:
                wavelength = float(wavelength)
            self.controller.set_image_wavelength(wavelength)
            self.show_status_bar_wavelength_set()
        except ValueError:
            self.display_current_wavelength()

    def change_unit(self, index):
        """Change :attr:`SetWavelengthModel.unit` to unit in :attr:`units_menu`

        Parameters
        ----------
        index : :obj:`int`
            Index of :attr:`SetWavelengthModel.accepted_units` to change the
            :attr:`SetWavelengthModel.unit` to
        """

        self.controller.change_unit(index)
        self.show_status_bar_wavelength_set()

    def show_status_bar_wavelength_set(self):
        """Alert user wavelength is set"""
        self.statusBar().showMessage('Wavelength Set', 1000)
