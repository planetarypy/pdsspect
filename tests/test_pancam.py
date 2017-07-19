import pvl
import pytest

from instrument_models.pancam import Pancam

from . import FILE_2, FILE_3


class TestPancam(object):

    pancam1 = Pancam(pvl.load(FILE_2))
    pancam2 = Pancam(pvl.load(FILE_3))

    def test_camera(self):
        assert self.pancam1.camera == 'PANCAM_RIGHT'
        assert self.pancam2.camera == 'PANCAM_LEFT'

    def test_is_left(self):
        assert not self.pancam1.is_left
        assert self.pancam2.is_left

    def test_is_right(self):
        assert self.pancam1.is_right
        assert not self.pancam2.is_right

    def test_filter_num(self):
        assert self.pancam1.filter_num == 8
        assert self.pancam2.filter_num == 8

    @pytest.mark.parametrize(
        'unit, wavelength1, wavelength2',
        [
            ('nm', 880, 440),
            ('um', 0.880, 0.440),
            ('AA', 8800, 4400)
        ]
    )
    def test_get_wavelength(self, unit, wavelength1, wavelength2):
        assert self.pancam1.get_wavelength(unit) == wavelength1
        assert self.pancam2.get_wavelength(unit) == wavelength2
