import pytest

from instrument_models.instrument import InstrumentBase


def test_abc_InstrumentBase():
    with pytest.raises(TypeError):
        InstrumentBase()


def test_subclass_InstrumentBase():
    class TestInstrument(InstrumentBase):

        def get_wavelength(self, *args, **kwargs):
            pass
    test_inst = TestInstrument(None)
    assert test_inst.label is None
    assert isinstance(test_inst, InstrumentBase)
