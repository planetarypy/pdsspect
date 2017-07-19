from astropy import units as astro_units

from .instrument import InstrumentBase


class Pancam(InstrumentBase):
    """Model to get the filter wavelength of a Patcam image

    See `Pancam <http://pancam.sese.asu.edu/doc/tb_pancam.pdf>`_ for more
    details on Pancam's filter wavelengths.

    Attributes
    ----------
    pancam_left : :obj:`str`
        ``PANCAM_LEFT``
    pancam_right : :obj:`str`
        ``PANCAM_RIGHT``
    unit : :obj:`str`
        ``nm``
    left_filters : :obj:`dict`
        Key is the filter number and the value is the wavelength for PancamL
    right_filters : :obj:`dict`
        Key is the filter number and the value is the wavelength for PancamR
    """

    pancam_left = 'PANCAM_LEFT'
    pancam_right = 'PANCAM_RIGHT'

    left_filters = {
        1: float('nan'),
        2: 750,
        3: 670,
        4: 600,
        5: 530,
        6: 480,
        7: 430,
        8: 440,
    }

    right_filters = {
        1: 430,
        2: 750,
        3: 800,
        4: 860,
        5: 900,
        6: 930,
        7: 980,
        8: 880,
    }

    unit = 'nm'

    @property
    def camera(self):
        """:obj:`bool` : Images camera. Should either be :attr:`left_filters`
        or :attr:`right_filters`"""
        return self.label['OBSERVATION_REQUEST_PARMS']['COMMAND_INSTRUMENT_ID']

    @property
    def is_left(self):
        """:obj:`bool` : True if image is from Pancam Left"""
        return self.camera == self.pancam_left

    @property
    def is_right(self):
        """:obj:`bool` : True if image is from Pancam Right"""
        return self.camera == self.pancam_right

    @property
    def filter_num(self):
        """:obj:`int` : The images filter number"""
        return self.label['INSTRUMENT_STATE_PARMS']['FILTER_NUMBER']

    def get_wavelength(self, unit='nm'):
        """Get the filter wavelength from the image

        Parameters
        ----------
        unit : :obj:`str` [``nm``]
            The wavelength unit. Best practice for ``unit`` to exist in
            :class:`pdsspect.pdsspect_image_set.ImageStamp.accepted_units`

        Returns
        -------
        wavelength : :obj:`float`
            The image's filter wavelength
        """

        filters = self.left_filters if self.is_left else self.right_filters
        wavelength = filters[self.filter_num] * astro_units.Unit(self.unit)
        wavelength = wavelength.to(astro_units.Unit(unit)).value
        return round(wavelength, 3)
