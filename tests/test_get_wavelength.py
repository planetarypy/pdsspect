import pvl
import math
import pytest

from instrument_models import get_wavelength

from . import FILE_2

mock_label = pvl.PVLModule({'foo': 'bar'})
# Use mastcam_label until available test image
mastcam_label = pvl.PVLModule(
    {
        'INSTRUMENT_NAME': 'MAST CAMERA LEFT',
        'INSTRUMENT_STATE_PARMS': {
            'CENTER_FILTER_WAVELENGTH': pvl._collections.Units(
                value=500,
                units='nm'
            ),
        },
    }
)
pancam_label = pvl.load(FILE_2)


@pytest.mark.parametrize(
    'label, expected',
    [
        (pancam_label, True),
        (mastcam_label, False),
        (mock_label, False)
    ]
)
def test_is_pancam(label, expected):
    assert get_wavelength.is_pancam(label) is expected


@pytest.mark.parametrize(
    'label, expected',
    [
        (pancam_label, False),
        (mastcam_label, True),
        (mock_label, False)
    ]
)
def test_is_mastcam(label, expected):
    assert get_wavelength.is_mastcam(label) is expected


@pytest.mark.parametrize(
    'label, unit, wavelength',
    [
        (pancam_label, 'nm', 880),
        (pancam_label, 'um', 0.880),
        (pancam_label, 'AA', 8800),
        (mastcam_label, 'nm', 500),
        (mastcam_label, 'um', 0.5),
        (mastcam_label, 'AA', 5000),
        (mock_label, 'nm', float('nan')),
        (mock_label, 'um', float('nan')),
        (mock_label, 'AA', float('nan')),
    ]
)
def test_get_wavelength(label, unit, wavelength):
    if math.isnan(wavelength):
        assert math.isnan(get_wavelength.get_wavelength(label, unit))
    else:
        assert get_wavelength.get_wavelength(label, unit) == wavelength
