"""The main model for all the views in pdsspect"""
import os
import warnings

import numpy as np
from astropy import units as astro_units
from ginga.util.dp import masktorgb
from planetaryimage import PDS3Image
from ginga.BaseImage import BaseImage
from ginga import colors as ginga_colors
from ginga.canvas.types.image import Image

from instrument_models.get_wavelength import get_wavelength


ginga_colors.add_color('crimson', (0.86275, 0.07843, 0.23529))
ginga_colors.add_color('teal', (0.0, 0.50196, 0.50196))
ginga_colors.add_color('eraser', (0.0, 0.0, 0.0))

ACCEPTED_UNITS = [
    'nm',
    'um',
    'AA',
]


class ImageStamp(BaseImage):
    """BaseImage for the image view canvas

    Parameters
    ----------
    filepath : :obj:`str`
        The path to the image to be opened
    metadata : None
        Metadata for `BaseImage`
    logger : None
        logger for `BaseImage`
    wavelength : :obj:`float` [``nan``]
        Image's filter wavelength. If ``nan``, will try to use
        :meth:`instrument_models.get_wavelength.get_wavelength` to get the
        wavelength
    unit : :obj:`str` [``nm``]
        Wavelength unit. Must be one of :attr:`accepted_units`

    Attributes
    ----------
    pds_image : :class:`~planetaryimage.pds3image.PDS3Image`
        Image object that holds data and the image label
    image_name : :obj:`str`
        The basename of the filepath
    seen : :obj:`bool`
        False if the image has not been seen by the viewer. True otherwise
        Default if False
    cuts : :obj:`tuple`
        The cut levels of the image. Default is two `None` types
    accepted_units : :obj:`list`
        List of accepted units: ``nm``, ``um``, and ``AA``
    """

    accepted_units = ACCEPTED_UNITS

    def __init__(self, filepath, metadata=None, logger=None,
                 wavelength=float('nan'), unit='nm'):
        self.pds_image = PDS3Image.open(filepath)
        data = self.pds_image.image.astype(float)
        BaseImage.__init__(self, data_np=data,
                           metadata=metadata, logger=logger)
        self.set_data(data)
        self.image_name = os.path.basename(filepath)
        self.seen = False
        self.cuts = (None, None)
        self._check_acceptable_unit(unit)
        if np.isnan(wavelength):
            wavelength = get_wavelength(self.pds_image.label, unit)
        unit = astro_units.Unit(unit)
        self._wavelength = wavelength * unit

    @property
    def data(self):
        """:class:`numpy.ndarray` : Image data"""
        return self.get_data()

    @property
    def wavelength(self):
        """:obj:`int` : The images wavelength"""
        return float(round(self._wavelength.value, 3))

    @wavelength.setter
    def wavelength(self, new_wavelength):
        self._wavelength = new_wavelength * self._wavelength.unit

    @property
    def unit(self):
        """:class:`astropy.units.Unit` : The :attr:`wavelength` unit

        Setting the unit will convert the wavelength value as well. The new
        unit must also be one of the :attr:`accepted_units`
        """

        return self._wavelength.unit

    @unit.setter
    def unit(self, new_unit):
        self._check_acceptable_unit(new_unit)
        new_unit = astro_units.Unit(new_unit)
        self._wavelength = self._wavelength.to(new_unit)

    def _check_acceptable_unit(self, unit):
        if unit not in self.accepted_units:
            raise ValueError(
                'Unit mus be one of the following %s' % (
                    ', '.join(self.accepted_units)
                )
            )

    def get_wavelength(self):
        """:class:`astropy.units.quantity.Quantity` Copy of the wavelength"""
        return self._wavelength.copy()


class PDSSpectImageSet(object):
    """Model for each view is pdsspect

    The images loaded should all have the same shape. Otherwise the images will
    have the smallest common shape and not look as expected (i.e., If when
    loading two images where one image has a shape of ``(63, 36)`` and the
    other image has a shape of ``(24, 42)``, the displayed shape will be
    ``(24, 36)``. This will cause the first image to have the right side cut
    off and the second image to have the top cut off). This is done so all ROIs
    created can apply to the entire list of images. To avoid this behavior,
    either only open images that have the same shape or open images one at a
    time.

    Parameters
    ----------
    filepaths : :obj:`list`
        List of filepaths to images

    Attributes
    ----------
    colors : :obj:`list` of :obj:`str`
        List of possible color names to make ROIs.

        The possible choices for colors: ``red``, ``brown``, ``lightblue``,
        ``lightcyan``, ``darkgreen``, ``yellow``, ``pink``, ``teal``,
        ``goldenrod``, ``sienna``, ``darkblue``, ``crimson``, ``maroon``,
        ``purple``, and ``eraser (black)``
    selection_types : :obj:`list` of :obj:`str`
        Selection types for making ROIs. The possible types are
        :class:`Filled Rectangle <.pdsspect.roi.Rectangle>`,
        :class:`Filled Polygon <.pdsspect.roi.Polygon>`, and
        :class:`Filled Rectangle <.pdsspect.roi.Pencil>`, (single points).
    accepted_units : :obj:`list`
        List of accepted units: ``nm``, ``um``, and ``AA``
    images : :obj:`list` of :class:`ImageStamp`
        Images to view and make selections. Must all have the same dimensions
    filepaths : :obj:`list`
        List of filepaths to images
    current_color_index : :obj:`int`
        Index of the current color in :attr:`colors` list for ROI creation
        (Default is 0)
    """

    colors = [
        'red',
        'brown',
        'lightblue',
        'lightcyan',
        'darkgreen',
        'yellow',
        'pink',
        'teal',
        'goldenrod',
        'sienna',
        'darkblue',
        'crimson',
        'maroon',
        'purple',
        'eraser',
    ]

    selection_types = [
        'filled rectangle',
        'filled polygon',
        'pencil'
    ]

    accepted_units = ACCEPTED_UNITS

    def __init__(self, filepaths):
        self._views = []
        self.images = []
        self.filepaths = filepaths
        self._create_image_list()
        self._determin_shape()
        self._current_image_index = 0
        self.current_color_index = 0
        self._selection_index = 0
        self._zoom = 1.0
        self._center = None
        self._alpha = 1.0
        self._flip_x = False
        self._flip_y = False
        self._swap_xy = False
        mask = np.zeros(self.shape[:2], dtype=np.bool)
        self._maskrgb = masktorgb(mask, self.color, self.alpha)
        self._roi_data = self._maskrgb.get_data().astype(float)
        self._maskrgb_obj = Image(0, 0, self._maskrgb)
        self._subsets = []
        self._simultaneous_roi = False
        self._unit = 'nm'
        self.set_unit()

    def _determin_shape(self):
        shape = []
        for image in self.images:
            rows, cols = image.shape[:2]
            if len(shape) == 0:
                shape = [rows, cols]
            else:
                shape[0] = rows if shape[0] > rows else shape[0]
                shape[1] = cols if shape[1] > cols else shape[1]
        self.shape = tuple(shape)
        s_ = np.s_[:self.shape[0], :self.shape[1]]
        for image in self.images:
            image.set_data(image.data[s_])

    def _create_image_list(self):
        self.images = []
        for filepath in self.filepaths:
            try:
                image = ImageStamp(filepath)
                self.images.append(image)
            except Exception:
                warnings.warn("Unable to open %s" % (filepath))

    def register(self, view):
        """Register a View with the model"""
        if view not in self._views:
            self._views.append(view)

    def unregister(self, view):
        """Unregister a View with the model"""
        if view in self._views:
            self._views.remove(view)

    @property
    def filenames(self):
        """:obj:`list` of :obj:`str` : Basenames of the :attr:`filepaths`"""
        return [os.path.basename(filepath) for filepath in self.filepaths]

    @property
    def current_image_index(self):
        """:obj:`int` : Index of the current image in :attr:`images`

        Setting the index will set the image in the views
        """
        return self._current_image_index

    @current_image_index.setter
    def current_image_index(self, new_index):
        self._current_image_index = new_index
        for view in self._views:
            view.set_image()

    @property
    def current_image(self):
        """:class:`ImageStamp` : The current image determined by
        :attr:`current_image_index`
        """
        return self.images[self._current_image_index]

    @property
    def color(self):
        """:obj:`str` : The current color in the :attr:`colors` list determined
        by :attr:`current_color_index`
        """
        return self.colors[self.current_color_index]

    @property
    def selection_index(self):
        """:obj:`int` : Index of the ROI selection type"""
        return self._selection_index

    @selection_index.setter
    def selection_index(self, new_index):
        while new_index >= len(self.selection_types):
            new_index -= len(self.selection_types)
        while new_index < 0:
            new_index += len(self.selection_types)
        self._selection_index = new_index

    @property
    def selection_type(self):
        """:obj:`str` : The current selection type in :attr:`selection_types`
        determined by :attr:`selection_index`
        """
        return self.selection_types[self.selection_index]

    @property
    def zoom(self):
        """:obj:`int` : Zoom factor for the pan

        The zoom factor determines the width and height of the pan area. For
        example, if ``zoom=2``, then the width would be half the image width
        and the height would be half the image height. Setting the zoom will
        adjust the pan size in the views.
        """

        return self._zoom

    @zoom.setter
    def zoom(self, new_zoom):
        if new_zoom < 1.0:
            new_zoom = 1.0
        self._zoom = float(new_zoom)
        for view in self._views:
            view.adjust_pan_size()

    @property
    def x_radius(self):
        """:obj:`float` : Half the image width"""
        return self.shape[1] / 2

    @property
    def y_radius(self):
        """:obj:`float` : Half the image height"""
        return self.shape[0] / 2

    @property
    def pan_width(self):
        """:obj:`float` : Width of the pan area"""
        return self.x_radius / self.zoom

    @property
    def pan_height(self):
        """:obj:`float` : Height of the pan area"""
        return self.y_radius / self.zoom

    def reset_center(self):
        """Reset the pan to the center of the image"""
        self._center = self.current_image.get_center()

    def _point_is_in_image(self, point):
        """Determine if the point is in the image

        Parameters
        ----------
        point : :obj:`tuple` of two :obj:`int`
            Tuple with x and y coordinates

        Returns
        -------
        is_in_image : :obj:`bool`
            True if the point is in the image. False otherwise.
        """

        data_x, data_y = point
        height, width = self.shape[:2]
        in_width = -0.5 <= data_x <= (width + 0.5)
        in_height = -0.5 <= data_y <= (height + 0.5)
        is_in_image = in_width and in_height
        return is_in_image

    def _determine_center_x(self, x):
        """Determine the x coordinate of center of the pan

        This method makes sure the pan doesn't go out of the left or right
        sides of the image

        Parameters
        ----------
        x : :obj:`float`
            The x coordinate to determine the center x coordinate

        Returns
        -------
        x_center : :obj:`float`
            The x coordinate of the center of the pan
        """

        width = self.shape[1]
        left_of_left_edge = x - self.pan_width < 0
        right_of_right_edge = x + self.pan_width > (width)
        in_width = not left_of_left_edge and not right_of_right_edge
        if in_width:
            center_x = x
        elif left_of_left_edge:
            center_x = self.pan_width
        elif right_of_right_edge:
            center_x = width - self.pan_width
        return center_x

    def _determine_center_y(self, y):
        """Determine the y coordinate of center of the pan

        This method makes sure the pan doesn't go out of the top or bottom
        sides of the image

        Parameters
        ----------
        y : :obj:`float`
            The y coordinate to determine the center y coordinate

        Returns
        -------
        center_y : :obj:`float`
            The y coordinate of the center of the pan
        """

        height = self.shape[0]
        below_bottom = y - self.pan_height < -0.5
        above_top = y + self.pan_height > (height + 0.5)
        in_height = not below_bottom and not above_top
        if in_height:
            center_y = y
        elif below_bottom:
            center_y = self.pan_height
        elif above_top:
            center_y = height - self.pan_height
        return center_y

    @property
    def center(self):
        """:obj:`tuple` of two :obj:`float` : x and y coordinate of the center
        of the pan.

        Setting the center will move the pan to the new center. The center
        points cannot result in the pan being out of the image. If they are
        they will be changed so the pan only goes to the edge.
        """

        if self._center is None:
            self.reset_center()
        return self._center

    @center.setter
    def center(self, new_center):
        if self._point_is_in_image(new_center):
            x, y = new_center
            center = (
                self._determine_center_x(x), self._determine_center_y(y),
            )
            self._center = center
            for view in self._views:
                view.move_pan()

    @property
    def all_rois_coordinates(self):
        """:obj:`tuple` of two :class:`numpy.ndarray` : Coordinates of where
        there is a pixel selected in a ROI
        """
        return np.where((self._roi_data != 0).any(axis=2))

    @property
    def alpha255(self):
        """:obj:`float` The alpha value normalized between 0 and 255"""
        return self._alpha * 255.

    @property
    def alpha(self):
        """:obj:`float` : The alpha value between 0 and 1

        Setting the alpha value will change the opacity of all the ROIs and
        then set the data in the views
        """

        return self._alpha

    @alpha.setter
    def alpha(self, new_alpha):
        self._alpha = new_alpha
        rows, cols = self.all_rois_coordinates
        self._roi_data[rows, cols, 3] = self.alpha255
        for view in self._views:
            view.change_roi_opacity()

    @property
    def flip_x(self):
        """:obj:`bool` : If True, flip the x axis

        Setting the ``flip_x`` will display the transformation in the views
        """

        return self._flip_x

    @flip_x.setter
    def flip_x(self, new_flip_x):
        self._flip_x = new_flip_x
        for view in self._views:
            view.set_transforms()

    @property
    def flip_y(self):
        """:obj:`bool` : If True, flip the y axis

        Setting the ``flip_y`` will display the transformation in the views
        """
        return self._flip_y

    @flip_y.setter
    def flip_y(self, new_flip_y):
        self._flip_y = new_flip_y
        for view in self._views:
            view.set_transforms()

    @property
    def swap_xy(self):
        """:obj:`bool` : If True, swap the x and y axis

        Setting the ``swap_xy`` will display the transformation in the views
        """

        return self._swap_xy

    @swap_xy.setter
    def swap_xy(self, new_swap_xy):
        self._swap_xy = new_swap_xy
        for view in self._views:
            view.set_transforms()

    @property
    def transforms(self):
        """:obj:`tuple` of :obj:`bool` : the :attr:`flip_x`, :attr:`flip_y`, and
        :attr:`swap_xy` transformations"""
        return self.flip_x, self.flip_y, self.swap_xy

    @property
    def edges(self):
        """:obj:`tuple` of four :obj:`float` : The ``left``, ``bottom``,
        ``right`` and ``top`` edges of the pan
        """
        x, y = self.center
        left = int(round(x - self.pan_width))
        right = int(round(x + self.pan_width))
        bottom = int(round(y - self.pan_height))
        top = int(round(y + self.pan_height))
        return left, bottom, right, top

    @property
    def pan_slice(self):
        """:obj:`numpy.s_` : Slice of pan to extract data from an array"""
        x1, y1, x2, y2 = self.edges
        pan_slice = np.s_[y1:y2:1, x1:x2:1]
        return pan_slice

    @property
    def pan_data(self):
        """:class:`numpy.ndarray` : The data within the pan"""
        return self.current_image.get_data()[self.pan_slice]

    @property
    def pan_roi_data(self):
        """:class:`numpy.ndarray` : The ROI data in the pan"""
        return self._roi_data[self.pan_slice]

    def _get_rgb255_from_color(self, color):
        """Get the rgb values normalized between 0 and 255 given a color

        Parameters
        ----------
        color : :obj:`str`
            Name of a color in :attr:`colors`

        Returns
        -------
        rgb : :obj:`list` of four :obj:`float`
            The red, green, and blue values normalized between 0 and 255
        """

        rgb = np.array(ginga_colors.lookup_color(color)) * 255.
        return rgb

    def _get_rgba_from_color(self, color):
        """Get the rgba values normalized between 0 and 255 given a color

        Parameters
        ----------
        color : :obj:`str`
            Name of a color in :attr:`colors`

        Returns
        -------
        rgba : :obj:`list` of four :obj:`float`
            The red, green, blue, and alpha values normalized between 0 and 255
        """

        r, g, b = self._get_rgb255_from_color(color)
        a = self.alpha * 255.
        rgba = [r, g, b, a]
        return rgba

    def _erase_coords(self, coordinates):
        """Erase the the ROI in the coordinates

        Parameters
        ----------
        coordinates : :class:`numpy.ndarray` or :obj:`tuple`
            Either a ``(m x 2)`` array or a tuple of two arrays

            If an array, the first column are the x coordinates and the second
            are the y coordinates. If a tuple or arrays, the first array are x
            coordinates and the second are the corresponding y coordinates.
        """

        if isinstance(coordinates, np.ndarray):
            coordinates = np.column_stack(coordinates)
        rows, cols = coordinates
        self._roi_data[rows, cols] = [0.0, 0.0, 0.0, 0.0]

    def add_coords_to_roi_data_with_color(self, coordinates, color):
        """Add coordinates to ROI data in the with the given color

        Parameters
        ----------
        coordinates : :class:`numpy.ndarray` or :obj:`tuple`
            Either a ``(m x 2)`` array or a tuple of two arrays

            If an array, the first column are the x coordinates and the second
            are the y coordinates. If a tuple of arrays, the first array are x
            coordinates and the second are the corresponding y coordinates.
        color : :obj:`str`
            The name a color in :attr:`colors`
        """

        if isinstance(coordinates, np.ndarray):
            coordinates = np.column_stack(coordinates)
        rows, cols = coordinates
        rgba = self._get_rgba_from_color(color)
        self._roi_data[rows, cols] = rgba
        for view in self._views:
            view.set_roi_data()

    def map_zoom_to_full_view(self):
        """Get the change in x and y values to the center of the image

        Returns
        -------
        delta_x : :obj:`float`
            The horizontal distance to the center of the full image
        delta_y : :obj:`float`
            The vertical distance to the center of the full image
        """

        center_x1, center_y1 = self.current_image.get_center()
        center_x2, center_y2 = self.center
        delta_x = (self.x_radius - self.pan_width) + (center_x2 - center_x1)
        delta_y = (self.y_radius - self.pan_height) + (center_y2 - center_y1)
        return delta_x, delta_y

    def get_coordinates_of_color(self, color):
        """The coordinates of the ROI with the given color

        Parameters
        ----------
        color : :obj:`str`
            The name a color in :attr:`colors`

        Returns
        -------
        coordinates : :obj:`tuple` of two :class:`numpy.ndarray`
            The first array are the x coordinates and the second are the
            corresponding y coordinates
        """

        rgba = self._get_rgba_from_color(color)
        coordinates = np.where(
            (self._roi_data == rgba).all(axis=2)
        )

        return coordinates

    def delete_rois_with_color(self, color):
        """Delete the ROIs with the given color

        Parameters
        ----------
        color : :obj:`str`
            The name a color in :attr:`colors`
        """

        coords = self.get_coordinates_of_color(color)
        self._erase_coords(coords)
        for view in self._views:
            view.set_roi_data()

    def delete_all_rois(self):
        """Delete all of the ROIs"""
        self._erase_coords(self.all_rois_coordinates)
        for view in self._views:
            view.set_roi_data()

    def create_subset(self):
        """Create a subset and add it to the list of subsets

        Returns
        -------
        subset : :class:`SubPDSSpectImageSet`
            The newly created subset
        """

        subset = SubPDSSpectImageSet(self)
        self.add_subset(subset)
        return subset

    @property
    def subsets(self):
        """:obj:`list` of :class:`SubPDSSpectImageSet` : The list of subsets"""
        return list(self._subsets)

    def add_subset(self, subset):
        """Add a subset to the list of subsets

        Parameters
        ----------
        subset : :class:`SubPDSSpectImageSet`
            Subset to add to the list of subsets
        """

        if isinstance(subset, SubPDSSpectImageSet):
            self._subsets.append(subset)

    def remove_subset(self, subset):
        """Remove a subset to the list of subsets

        Parameters
        ----------
        subset : :class:`SubPDSSpectImageSet`
            Subset to remove to the list of subsets
        """

        if isinstance(subset, SubPDSSpectImageSet) and subset in self._subsets:
            self._subsets.remove(subset)

    def get_rois_masks_to_export(self):
        exported_rois = {}

        def add_mask_to_exported_rois(image_set, color, name):
            mask = np.zeros(image_set.shape, dtype=np.bool)
            rows, cols = image_set.get_coordinates_of_color(color)
            mask[rows, cols] = True
            exported_rois[name] = mask

        for color in self.colors:
            add_mask_to_exported_rois(self, color, color)
            for i, subset in enumerate(self.subsets):
                name = color + str(i + 2)
                add_mask_to_exported_rois(subset, color, name)

        return exported_rois

    @property
    def simultaneous_roi(self):
        """:obj:`bool` : If true, new ROIs appear in every view

        Setting :attr:`simultaneous_roi` will set all windows to have the same
        ROIs as the first window. Any new ROI created will appear in each
        window
        """

        return self._simultaneous_roi

    @simultaneous_roi.setter
    def simultaneous_roi(self, state):
        self._simultaneous_roi = state
        if state:
            for subset in self.subsets:
                subset._simultaneous_roi = state
                subset._roi_data = self._roi_data.copy()
                for view in subset._views:
                    view.set_roi_data()
        else:
            for subset in self.subsets:
                subset._simultaneous_roi = state

    @property
    def unit(self):
        """:obj:`str` : The image set's current wavelength unit"""
        return self._unit

    def set_unit(self):
        """Set each image to :attr:`unit`"""
        for image in self.images:
            image.unit = self.unit

    @unit.setter
    def unit(self, new_unit):
        if new_unit not in self.accepted_units:
            raise ValueError(
                'Unit mus be one of the following %s' % (
                    ', '.join(self.accepted_units)
                )
            )
        self._unit = new_unit
        self.set_unit()
        for subset in self.subsets:
            subset._unit = new_unit
        for view in self._views:
            view.set_roi_data()


class SubPDSSpectImageSet(PDSSpectImageSet):
    """A Subset of an :class:`PDSSpectImageSet`

    Parameters
    ----------
    parent_set : :class:`PDSSpectImageSet`
        The subset's parent

    Attributes
    ----------
    parent_set : :class:`PDSSpectImageSet`
        The subset's parent
    """

    def __init__(self, parent_set):
        self.parent_set = parent_set
        super(SubPDSSpectImageSet, self).__init__(parent_set.filepaths)
        self._views = []
        self._current_image_index = parent_set.current_image_index
        self.current_color_index = parent_set.current_color_index
        self._zoom = parent_set.zoom
        self._center = parent_set.center
        self._alpha = parent_set.alpha
        self._roi_data = parent_set._roi_data.copy()
        self._roi_data.fill(0)
        self._selection_index = parent_set.selection_index
        self._flip_x = parent_set.flip_x
        self._flip_y = parent_set.flip_y
        self._swap_xy = parent_set.swap_xy
        self._simultaneous_roi = parent_set.simultaneous_roi

    def _determin_shape(self):
        self.shape = self.parent_set.shape

    def _create_image_list(self):
        self.images = self.parent_set.images


class PDSSpectImageSetViewBase(object):
    """Base class for all views of the ImageSet model

    Setting the view as child of this class will make it so only the needed
    methods have to be defines
    """

    def move_pan(self):
        pass

    def adjust_pan_size(self):
        pass

    def set_image(self):
        pass

    def redraw(self):
        pass

    def set_transforms(self):
        pass

    def set_roi_data(self):
        pass

    def change_roi_opacity(self):
        pass
