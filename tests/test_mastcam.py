import pytest

from instrument_models.mastcam import Mastcam

from . import mastcam_label


class TestMastcam(object):

    mastcam = Mastcam(mastcam_label)

    def test_group(self):
        assert self.mastcam.group == 'INSTRUMENT_STATE_PARMS'

    def test_wavelength_key(self):
        assert self.mastcam.wavelength_key1 == 'CENTER_FILTER_WAVELENGTH'
        assert self.mastcam.wavelength_key2 == 'FILTER_CENTER_WAVELENGTH'

    @pytest.mark.parametrize(
        'unit, wavelength',
        [
            ('nm', 500),
            ('um', 0.5),
            ('AA', 5000)
        ]
    )
    def test_get_wavelength(self, unit, wavelength):
        assert self.mastcam.get_wavelength(unit) == wavelength
