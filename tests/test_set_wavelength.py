import pytest
import numpy as np

from pdsspect.set_wavelength import (
    SetWavelengthModel,
    SetWavelengthWidget,
    SetWavelengthController,
)
from pdsspect.pdsspect_image_set import PDSSpectImageSet

from . import FILE_1, FILE_3


class TestSetWavelengthModel(object):

    image_set = PDSSpectImageSet([FILE_1, FILE_3])

    @pytest.fixture
    def model(self):
        self.image_set.unit = 'nm'
        return SetWavelengthModel(self.image_set)

    def test_accepted_units(self, model):
        assert model.accepted_units == ['nm', 'um', 'AA']

    def test_current_image_index(self, model):
        assert model.current_image_index == self.image_set.current_image_index
        model.current_image_index = 1
        assert model.current_image_index == 1
        assert model._current_image_index == 1
        assert model.current_image_index != self.image_set.current_image_index

    def test_current_image(self, model):
        assert model.current_image == self.image_set.current_image
        model.current_image_index = 1
        assert model.current_image == self.image_set.images[1]

    def test_unit(self, model):
        assert model.unit == self.image_set.unit
        model.unit = 'um'
        assert model.unit == 'um'
        assert self.image_set.unit == 'um'

    def test_unit_index(self, model):
        assert model.unit == 'nm'
        assert model.unit_index == 0
        model.unit = 'um'
        assert model.unit == 'um'
        assert model.unit_index == 1
        model.unit = 'AA'
        assert model.unit == 'AA'
        assert model.unit_index == 2
        model.unit = 'nm'
        assert model.unit == 'nm'
        assert model.unit_index == 0


class TestSetWavelengthController(object):

    image_set = PDSSpectImageSet([FILE_1, FILE_3])
    model = SetWavelengthModel(image_set)

    @pytest.fixture
    def controller(self):
        self.image_set = PDSSpectImageSet([FILE_1, FILE_3])
        self.model = SetWavelengthModel(self.image_set)
        return SetWavelengthController(self.model, None)

    def test_set_current_image_index(self, controller):
        assert self.model.current_image_index == 0
        controller.set_current_image_index(1)
        assert self.model.current_image_index == 1

    def test_change_unit(self, controller):
        assert self.model.unit == 'nm'
        controller.change_unit(1)
        assert self.model.unit == 'um'
        controller.change_unit(2)
        assert self.model.unit == 'AA'
        controller.change_unit(0)
        assert self.model.unit == 'nm'

    def test_set_image_wavelength(self, controller):
        assert np.isnan(self.model.current_image.wavelength)
        controller.set_image_wavelength(100.0)
        assert self.model.current_image.wavelength == 100.0
        controller.set_current_image_index(1)
        assert self.model.current_image.wavelength == 440.0
        controller.set_image_wavelength(50.0)
        assert self.model.current_image.wavelength == 50.0
        controller.set_current_image_index(0)
        assert self.model.current_image.wavelength == 100.0


class TestSetWavelengthWidget(object):

    image_set = PDSSpectImageSet([FILE_1, FILE_3])
    model = SetWavelengthModel(image_set)

    @pytest.fixture
    def widget(self, qtbot):
        self.image_set = PDSSpectImageSet([FILE_1, FILE_3])
        self.model = SetWavelengthModel(self.image_set)
        widget = SetWavelengthWidget(self.model)
        qtbot.add_widget(widget)
        widget.show()
        return widget

    def test_select_image(self, widget):
        assert self.model.current_image_index == 0
        widget.select_image(1)
        assert self.model.current_image_index == 1

    def test_display_current_wavelength(self, widget):
        assert widget.wavelength_text.text() == ''
        self.model.current_image.wavelength = 100.0
        widget.display_current_wavelength()
        assert widget.wavelength_text.text() == '100.0'
        self.model.current_image.wavelength = float('nan')
        widget.display_current_wavelength()
        assert widget.wavelength_text.text() == ''

    def test_set_wavelength(self, widget):
        assert widget.wavelength_text.text() == ''
        widget.wavelength_text.setText('100')
        assert np.isnan(self.model.current_image.wavelength)
        widget.set_wavelength()
        self.model.current_image.wavelength = 100.0
        assert widget.wavelength_text.text() == '100.0'
        widget.wavelength_text.setText('foo')
        widget.set_wavelength()
        assert widget.wavelength_text.text() == '100.0'
        widget.wavelength_text.setText('')
        widget.set_wavelength()
        assert np.isnan(self.model.current_image.wavelength)
        assert widget.wavelength_text.text() == ''

    def test_change_unit(self, widget):
        assert self.model.unit == 'nm'
        widget.change_unit(1)
        assert self.model.unit == 'um'
        widget.change_unit(2)
        assert self.model.unit == 'AA'
        widget.change_unit(0)
        assert self.model.unit == 'nm'

    def test_show_status_bar_wavelength_set(self, widget, qtbot):
        status_bar = widget.statusBar()
        widget.show_status_bar_wavelength_set()
        assert status_bar.currentMessage() == 'Wavelength Set'
        widget.show_status_bar_wavelength_set()
        qtbot.wait(1000)  # Test message disapears after 1 second
        assert status_bar.currentMessage() == ''
