import pytest

from instrument_models.cassini_iss import CassiniISS

from . import NA_label, WA_label


class TestCassiniISS(object):

    ISS_NA = CassiniISS(NA_label)
    ISS_WA = CassiniISS(WA_label)

    def test_filter_name(self):
        assert self.ISS_NA.filter_name == 'BL1, BL2'
        assert self.ISS_WA.filter_name == 'CB2, CL2'

    def test_is_NA(self):
        assert self.ISS_NA.is_NA
        assert not self.ISS_WA.is_NA

    def test_is_WA(self):
        assert not self.ISS_NA.is_WA
        assert self.ISS_WA.is_WA

    @pytest.mark.parametrize(
        'unit, wavelength_na, wavelength_wa',
        [
            ('nm', 441.077, 752.354),
            ('um', 0.441, 0.752),
            ('AA', 4410.770, 7523.540)
        ]
    )
    def test_get_wavelength(self, unit, wavelength_na, wavelength_wa):
        assert self.ISS_NA.get_wavelength(unit) == wavelength_na
        assert self.ISS_WA.get_wavelength(unit) == wavelength_wa
