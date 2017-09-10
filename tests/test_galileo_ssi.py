import pytest

from instrument_models.galileo_ssi import GalileoSSI

import numpy as np

from . import SSI_label, EMPTY_LABEL


class TestGalileoSSI(object):

    SSI = GalileoSSI(SSI_label)
    EMPTY = GalileoSSI(EMPTY_LABEL)

    def test_filter_name(self):
        assert self.SSI.filter_name == 'CLEAR, 0'

    @pytest.mark.parametrize(
        'unit, wavelength',
        [
            ('nm', 624.700),
            ('um', 0.625),
            ('AA', 6247.000)
        ]
    )
    def test_get_wavelength(self, unit, wavelength):
        assert self.SSI.get_wavelength(unit) == wavelength
        assert np.isnan(self.EMPTY.get_wavelength(unit))
