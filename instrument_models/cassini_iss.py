from astropy import units as astro_units

from .instrument import InstrumentBase


class CassiniISS(InstrumentBase):
    """Model to get the filter wavelength from Cassini ISS image

    See `Cassini Imaging Science Subsystem (ISS) Data User's Guide (Page 149)
    <http://www.ciclops.org/sci/docs/ISS_Data_User_Guide_141215.pdf>`_
    for table of filter name and corresponding wavelengths. We use the
    effective wavelength rather than the center wavelength.wavelength

    Attributes
    ----------
    NA_filters : :obj:`dict`
        Dictionary of the ISS Narrow Angle Camera filter names and wavelengths

        Key is the two filternames and the value is the wavelength in nm
    WA_filters : :obj:`dict`
        Dictionary of the ISS Wide Angle Camera filter names and wavelengths

        Key is the two filternames and the value is the wavelength in nm
    unit : :obj:`str`
        The default unit is ``nm``
    """

    NA_filters = {
        'BL1, BL2': 441.077,
        'BL1, CL2': 455.471,
        'BL1, GRN': 497.435,
        'BL1, UV3': 389.22,
        'CL1, BL2': 440.98,
        'CL1, CB1': 619.292,
        'CL1, CB1A': 602.917,
        'CL1, CB1B': 634.526,
        'CL1, CB2': 750.495,
        'CL1, CB3': 937.928,
        'CL1, CL2': 651.057,
        'CL1, GRN': 569.236,
        'CL1, IR1': 750.048,
        'CL1, IR3': 928.304,
        'CL1, MT1': 618.949,
        'CL1, MT2': 727.415,
        'CL1, MT3': 889.196,
        'CL1, UV3': 343.136,
        'HAL, CB1': 650.466,
        'HAL, CL2': 655.621,
        'HAL, GRN': 647.808,
        'HAL, IR1': 663.431,
        'IR2, CB3': 933.593,
        'IR2, CL2': 861.066,
        'IR2, IR1': 827.331,
        'IR2, IR3': 901.63,
        'IR2, MT3': 889.176,
        'IR4, CL2': 1001.91,
        'IR4, IR3': 996.46,
        'RED, CB1': 619.481,
        'RED, CB2': 743.912,
        'RED, CL2': 648.879,
        'RED, GRN': 600.959,
        'RED, IR1': 701.692,
        'RED, IR3': 695.04,
        'RED, MT1': 618.922,
        'RED, MT2': 726.624,
        'UV1, CL2': 266.321,
        'UV1, UV3': 353.878,
        'UV2, CL2': 306.477,
        'UV2, UV3': 317.609,
    }

    WA_filters = {
        'CB2, CL2': 752.354,
        'CB2, IR1': 752.314,
        'CB2, RED': 747.317,
        'CB3, CL2': 938.445,
        'CL1, BL1': 462.865,
        'CL1, CL2': 633.817,
        'CL1, GRN': 568.214,
        'CL1, HAL': 656.386,
        'CL1, IR1': 739.826,
        'CL1, RED': 647.239,
        'CL1, VIO': 419.822,
        'IR2, CL2': 852.448,
        'IR2, IR1': 826.255,
        'IR3, CL2': 916.727,
        'IR3, IR1': 783.722,
        'IR3, RED': 689.959,
        'IR4, CL2': 1001.88,
        'IR5, CL2': 1033.87,
        'MT2, CL2': 728.418,
        'MT2, IR1': 728.284,
        'MT2, RED': 727.507,
        'MT3, CL2': 890.332,
    }

    unit = 'nm'

    @property
    def filter_name(self):
        """:obj:`str` : The image's filter names joined by a comma and space

        For example, in the label the filtername appears as ``("CL1","UV3")``
        and so :attr:`filter_name` returns ``'CL1, UV3'``
        """

        filter_name = ', '.join(self.label['FILTER_NAME'])
        return filter_name

    @property
    def is_NA(self):
        """:obj:`bool` : ``True`` if image is from Narrow Angle Camera"""
        NA_key = 'IMAGING SCIENCE SUBSYSTEM NARROW ANGLE'
        is_NA = self.label['INSTRUMENT_NAME'] == NA_key
        return is_NA

    @property
    def is_WA(self):
        """:obj:`bool` : ``True`` if image is from Wide Angle Camera"""
        WA_key = 'IMAGING SCIENCE SUBSYSTEM WIDE ANGLE'
        is_WA = self.label['INSTRUMENT_NAME'] == WA_key
        return is_WA

    def get_wavelength(self, unit='nm'):
        """Get the image's filter wavelength

        Parameters
        ----------
        unit : :obj:`str` [``nm``]
            The desired wavelength of the unit

        Returns
        -------
        wavelength : :obj:`float`
            The image's filter wavelength rounded to 3 decimal places
        """

        if self.is_NA:
            filters = self.NA_filters
        elif self.is_WA:
            filters = self.WA_filters
        else:
            filters = None

        if filters is not None:
            wavelength = filters.get(self.filter_name)
            wavelength = wavelength if wavelength is not None else float('nan')
        else:
            wavelength = float('nan')

        wavelength = wavelength * astro_units.Unit(self.unit)
        wavelength = wavelength.to(astro_units.Unit(unit))
        return round(wavelength.value, 3)
