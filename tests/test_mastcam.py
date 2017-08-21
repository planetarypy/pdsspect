import pytest
import numpy as np

from instrument_models.mastcam import Mastcam

from . import mastcam_label1, mastcam_label2, EMPTY_LABEL


class TestMastcam(object):

    mastcam1 = Mastcam(mastcam_label1)
    mastcam2 = Mastcam(mastcam_label2)
    empty = Mastcam(EMPTY_LABEL)

    def test_group(self):
        assert self.mastcam1.group == 'INSTRUMENT_STATE_PARMS'

    def test_wavelength_key(self):
        assert self.mastcam1.wavelength_key1 == 'CENTER_FILTER_WAVELENGTH'
        assert self.mastcam1.wavelength_key2 == 'FILTER_CENTER_WAVELENGTH'

    @pytest.mark.parametrize(
        'unit, wavelength',
        [
            ('nm', 500),
            ('um', 0.5),
            ('AA', 5000)
        ]
    )
    def test_get_wavelength(self, unit, wavelength):
        assert self.mastcam1.get_wavelength(unit) == wavelength
        assert self.mastcam2.get_wavelength(unit) == wavelength
        assert np.isnan(self.empty.get_wavelength(unit))
