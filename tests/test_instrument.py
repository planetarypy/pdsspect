import pytest

from instrument_models.instrument import InstrumentBase

import numpy as np


def test_abc_InstrumentBase():
    with pytest.raises(TypeError):
        InstrumentBase()


def test_subclass_InstrumentBase():
    class TestInstrument(InstrumentBase):

        def get_wavelength(self, *args, **kwargs):
            return super(TestInstrument, self).get_wavelength('unit')
    test_inst = TestInstrument(None)
    assert test_inst.label is None
    assert isinstance(test_inst, InstrumentBase)
    assert np.isnan(test_inst.get_wavelength())
