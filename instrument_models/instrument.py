"""Provide base class for all instrument models"""
import abc
import six


@six.add_metaclass(abc.ABCMeta)
class InstrumentBase(object):
    """Abstract Base Class for all instrument models

    Parameters
    ----------
    label : :class:`pvl.PVLModule`
        Image's label

    Attributes
    ----------
    label : :class:`pvl.PVLModule`
        Image's label
    """

    def __init__(self, label):
        self.label = label

    @abc.abstractmethod
    def get_wavelength(self, unit, *args, **kwargs):
        """Abstract method to get the image's wavelength

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

        wavelength = float('nan')
        return wavelength
