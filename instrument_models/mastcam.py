from astropy import units as astro_units

from .instrument import InstrumentBase


class Mastcam(InstrumentBase):
    """Model to get the filter wavelength of a Mastcam image

    See `Mastcam Multispectral Imaging on the Mars Science Laboratory Rover:
    Wavelength Coverage and Imaging Strategies at the Gale Crater Field Site
    <https://molokai.sese.asu.edu/attachments/download/47>`_ for more details
    on Mastcam's filter wavelengths

    Attributes
    ----------
    group : :obj:`str`
        ``INSTRUMENT_STATE_PARMS``
    wavelength_key1 : :obj:`str`
        ``CENTER_FILTER_WAVELENGTH``
    wavelength_key2 : :obj:`str`
        ``FILTER_CENTER_WAVELENGTH``
    """

    group = 'INSTRUMENT_STATE_PARMS'
    wavelength_key1 = 'CENTER_FILTER_WAVELENGTH'
    wavelength_key2 = 'FILTER_CENTER_WAVELENGTH'

    def get_wavelength(self, unit='nm'):
        """Get the wavelength from mastcam image

        Parameters
        ----------
        unit : :obj:`str` [``nm``]
            The wavelength unit. Best practice for ``unit`` to exist in
            :class:`pdsspect.pdsspect_image_set.ImageStamp.accepted_units`

        Returns
        -------
        wavelength : :obj:`float`
            Filter wavelength of the mastcam image
        """

        params = self.label[self.group]
        wavelength = params.get(self.wavelength_key1)
        if wavelength is None:
            wavelength = params.get(self.wavelength_key2)
        if wavelength is None:
            return float('nan')
        wavelength = wavelength.value * astro_units.Unit(wavelength.units)
        wavelength = wavelength.to(astro_units.Unit(unit))
        return round(wavelength.value, 3)
