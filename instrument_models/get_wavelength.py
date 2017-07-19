"""Get the wavelength from an image's label"""
import functools

from .pancam import Pancam
from .mastcam import Mastcam

instrument_name_key = 'INSTRUMENT_NAME'


def is_instrument(func):
    """Wrapper for instrument determining functions

    Tries the function, if there is a :class:`TypeError`, then return False.
    The :class:`TypeError` will occur when the label's :meth:`get` method
    returns ``None``
    """

    @functools.wraps(func)
    def wrapper(label):
        try:
            result = func(label)
        except TypeError:
            result = False
        return result
    return wrapper


@is_instrument
def is_pancam(label):
    """Determine if label is for a Pancam image

    Parameters
    ----------
    label : :class:`pvl.PVLModule`
        Image's label

    Returns
    -------
    is_pancam : :obj:`bool`
        ``True`` if label is from a Pancam image, ``False`` otherwise
    """

    is_pancam = 'PANORAMIC' in label.get(instrument_name_key)
    return is_pancam


@is_instrument
def is_mastcam(label):
    """Determine if label is for a Mastcam image

    Parameters
    ----------
    label : :class:`pvl.PVLModule`
        Image's label

    Returns
    -------
    is_mastcam : :obj:`bool`
        ``True`` if label is from a Mastcam image, ``False`` otherwise
    """

    is_mastcam = 'MAST CAMERA' in label.get(instrument_name_key)
    return is_mastcam


def get_wavelength(label, unit):
    """Get the filter wavelength from the label of an image

    Instruments that are supported: ``Pancam`` and ``Mastcam``

    Parameters
    ----------
    label : :class:`pvl.PVLModule`
        Image's label
    unit : :obj:`str` [``nm``]
            The wavelength unit. Best practice for ``unit`` to exist in
            :class:`pdsspect.pdsspect_image_set.ImageStamp.accepted_units`

    Returns
    -------
    wavelength : :obj:`float`
        The filter wavelenth from the image.

        If image does not have a wavelength or the instrument is not supported,
        wavelength with be ``nan``

    See Also
    --------
    instrument_models.mastcam.Mastcam.get_wavelength : Get Mastcam wavelength

    instrument_models.pancam.Pancam.get_wavelength : Get Pancam wavelength
    """

    if is_pancam(label):
        instrument = Pancam(label)
    elif is_mastcam(label):
        instrument = Mastcam(label)
    else:
        instrument = None

    if instrument is None:
        wavelength = float('nan')
    else:
        wavelength = instrument.get_wavelength(unit)
    return round(wavelength, 3)
