from astropy import units as astro_units

from .instrument import InstrumentBase


class GalileoSSI(InstrumentBase):
    """Model to get the filter wavelength from Galileo Solid State Imaging
    (SSI) experiment imagery

    See `SSI Raw Experiment Data Record (REDR) for Phase 2'
    <https://pds-imaging.jpl.nasa.gov/data/go-j_jsa-ssi-2-redr-v1.0/go_0023/document/redrsis.pdf>`_
    and
    see 'Calibration And Performance Of The Galileo Solid-state Imaging
    System In Jupiter Orbit`
    <http://authors.library.caltech.edu/70894/1/1178_1.pdf>`_
    for table of filter name, number, and corresponding wavelengths.
    We use the effective (solar radiance) wavelength.

    Attributes
    ----------
    SSI_filters : :obj:`dict`
        Dictionary of the Galileo Solid State Imaging (SSI) experiment
         filter names and wavelengths

        Key is the filter name and filter number and the value is the
            wavelength in nm

    unit : :obj:`str`
        The default unit is ``nm``
    """

    SSI_filters = {
        'CLEAR, 0': 624.7,
        'GREEN, 1': 559.0,
        'RED, 2': 663.6,
        'VIOLET, 3': 413.7,
        'IR-7560, 4': 756.8,
        'IR-9680, 5': 989.7,
        'IR-7270, 6': 731.1,
        'IR-8890, 7': 887.6,
    }

    unit = 'nm'

    @property
    def filter_name(self):
        """:obj:`str` : The image's filter names joined by a comma and space

        For example, in the label the filtername appears as ``("CLEAR","0")``
        and so :attr:`filter_name` returns ``'CLEAR, 0'``
        """

        filter_name = ', '.join(self.label['FILTER_NAME'])
        return filter_name

    @property
    def is_SSI(self):
        """:obj:`bool` : ``True`` if image is SSI"""
        SSI_key = 'SOLID STATE IMAGING SYSTEM'
        is_SSI = self.label['INSTRUMENT_NAME'] == SSI_key
        return is_SSI

    def get_wavelength(self, unit='nm'):
        """Get the image's filter wavelength

        Parameters
        ----------
        unit : :obj:`str` [``nm``]
            The desired wavelength of the unit

        Returns
        -------
        wavelength : :obj:`float`
            The image's filter wavelength rounded to 1 decimal.
        """

        if self.is_SSI:
            filters = self.SSI_filters
        else:
            filters = None

        if filters is not None:
            wavelength = filters.get(self.filter_name)
            wavelength = wavelength if wavelength is not None else float('nan')
        else:
            wavelength = float('nan')

        wavelength = wavelength * astro_units.Unit(self.unit)
        wavelength = wavelength.to(astro_units.Unit(unit))
        return round(wavelength.value, 1)
