"""Region of interest creation"""
import abc
import six
import warnings
from functools import wraps
from contextlib import contextmanager

import numpy as np
from ginga.canvas.types import basic


@six.add_metaclass(abc.ABCMeta)
class ROIBase(basic.Polygon):
    """Base class for all ROI shapes"""

    def __init__(self, image_set, view_canvas, color='red',
                 linewidth=1, linestyle='solid', showcap=False,
                 fill=True, fillcolor=None, alpha=1.0,
                 drawdims=False, font='Sans Serif', fillalpha=1.0,
                 **kwargs):
        self.image_set = image_set
        self.view_canvas = view_canvas
        self.color = color
        self.linewidth = linewidth
        self.linestyle = linestyle
        self.showcap = showcap
        self.fill = True
        self.fillcolor = fillcolor
        self.alpha = alpha
        self.drawdims = drawdims
        self.font = font
        self.fillalpha = fillalpha
        self.kwargs = kwargs
        self._has_temp_point = False
        self._current_path = None

    @staticmethod
    def draw_after(func):
        """Wrapper to redraw canvas after function"""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            run_func = func(self, *args, **kwargs)
            self.view_canvas.redraw()
            return run_func
        return wrapper

    @property
    def top(self):
        """:obj:`float` : The top edge of the image

        The top edge is 1.5 units past the edge of the image due to how ginga
        renders the image. I feel like this is a bug but I haven't had time to
        try to expose it in a simple example so working around it will have
        to do for now.
        """

        return self.image_set.current_image.shape[0] + 1.5

    @property
    def right(self):
        """:obj:`float` : The right edge of the image

        The right edge is 0.5 units before the right edge of the image.
        """

        return self.image_set.current_image.shape[1] - 0.5

    def _get_default_point_value(self, point, high_edge):
        """Get a default value for a single edge case

        Either the top or bottom edge case or the left or right edge case

        Parameters
        ----------
        point : :obj:`float`
            The given x or y coordinate
        high_edge : :obj:`float`
            Either the right or top edge

        Returns
        -------
        default_point : :obj:`float` or None
            Returns the default value if an edge case, None otherwise
        """

        default_point = None

        # Since the center coordinate of the left and bottom pixels is zero,
        # the outer edge coordinate of the left and bottom pixels is -0.5
        low_edge = -0.5

        if point <= 0:
            default_point = low_edge
        elif point >= high_edge + 0.5:
            default_point = high_edge

        return default_point

    def _get_default_data_values(self, data_x, data_y):
        """Get default values for edge cases

        Parameters
        ----------
        data_x : :obj:`float`
            The given x coordinate
        data_y : :obj:`float`
            The given y coordinate

        Returns
        -------
        default_x : :obj:`float` or None
            The x coordinate for the edge case. If not an edge case then None
        default_y : :obj:`float` or None
            The y coordinate for the edge case. If not an edge case then None
        """

        default_x = self._get_default_point_value(data_x, self.right)
        default_y = self._get_default_point_value(data_y, self.top)

        return default_x, default_y

    def lock_coords_to_pixel(self, data_x, data_y):
        """Lock the coordinates to the pixel

        The coordinate of the pixel is located at the bottom left corner of the
        pixel square while the center of the pixel .5 units up and to the right
        of the corner. So if the given coordinates are (2.3, 3.7), the pixel
        coordinates will be (2, 3) and the center of the pixel is (2.5, 3.5).
        This method locks the given coordinates to the pixel's coordinates

        Parameters
        ----------
        data_x : :obj:`float`
            The given x coordinate
        data_y : :obj:`float`
            The given y coordinate

        Returns
        -------
        point_x : :obj:`float`
            The corresponding x pixel coordinate
        point_y : :obj:`float`
            The corresponding y pixel coordinate
        """

        point_x, point_y = self._get_default_data_values(data_x, data_y)

        if None not in (point_x, point_y):
            return point_x, point_y

        X, Y = np.ceil((data_x, data_y))
        x, y = np.floor((data_x, data_y))

        if point_x is None:
            if X - data_x <= 0.5:
                point_x = x + 0.5
            else:
                point_x = x - 0.5

        if point_y is None:
            if Y - data_y <= 0.5:
                point_y = y + 0.5
            else:
                point_y = y - 0.5

        return point_x, point_y

    @staticmethod
    def lock_coords_to_pixel_wrapper(func):
        """Wrapper to lock data coordinates to the corresponding pixels"""
        @wraps(func)
        def wrapper(self, data_x, data_y):
            point_x, point_y = self.lock_coords_to_pixel(data_x, data_y)
            return func(self, point_x, point_y)
        return wrapper

    @abc.abstractmethod
    def start_ROI(self, data_x, data_y):
        """Abstract method to start the ROI process"""
        pass

    @abc.abstractmethod
    def continue_ROI(self, data_x, data_y):
        """Abstract method to continue the ROI process"""
        pass

    @abc.abstractmethod
    def extend_ROI(self, data_x, data_y):
        """Abstract method to extend the ROI process"""
        pass

    @abc.abstractmethod
    def stop_ROI(self, data_x, data_y):
        """Abstract method to stop the ROI process"""
        pass

    def create_ROI(self, points=None):
        """Create a Region of interest

        Parameters
        ----------
        points : :obj:`list` of :obj:`tuple` of two :obj:`int`
            Points that make up the vertices of the ROI

        Returns
        -------
        coordinates : :class:`numpy.ndarray`
            ``m x 2`` array of coordinates.
        """

        points = self._current_path.get_points() if points is None else points
        super(ROIBase, self).__init__(
            points, color=self.color,
            linewidth=self.linewidth, linestyle=self.linestyle,
            showcap=self.showcap, fill=self.fill, fillcolor=self.color,
            alpha=self.alpha, drawdims=self.drawdims, font=self.font,
            fillalpha=self.fillalpha, **self.kwargs)
        self.view_canvas.add(self)
        coords = self._get_roi_coords()
        self.view_canvas.deleteObject(self)
        coordinates = np.stack(coords, axis=-1)
        return coordinates

    def contains_arr(self, x_arr, y_arr):
        """Determine whether the points in the ROI are in arrays

        The arrays must be the same shape. The arrays should be result of
        ``np.mgrid[y1:y2:1, x1:x2:1]``

        Parameters
        ----------
        x_arr : :class:`numpy.ndarray`
            Array of x coodinates
        y_arr : :class:`numpy.ndarray`
            Array of y coordinates

        Returns
        -------
        result : :class:`numpy.ndarray`
            Boolean array where coordinates that are in ROI are True
        """

        # NOTE: we use a version of the ray casting algorithm
        # See: http://alienryderflex.com/polygon/
        xa, ya = x_arr, y_arr

        # promote input arrays dimension cardinality, if necessary
        promoted = False
        if len(x_arr.shape) == 1:
            x_arr = x_arr.reshape(1, -1)
            promoted = True
        if len(y_arr.shape) == 1:
            y_arr = y_arr.reshape(-1, 1)
            promoted = True

        result = np.zeros(y_arr.shape, dtype=np.bool)
        result1 = np.zeros(y_arr.shape, dtype=np.bool)
        result2 = np.zeros(y_arr.shape, dtype=np.bool)

        points = self.get_data_points()

        xj, yj = points[-1]
        for point in points:
            xi, yi = point
            tf = np.logical_and(
                np.logical_or(np.logical_and(yi < ya, yj >= ya),
                              np.logical_and(yj < ya, yi >= ya)),
                np.logical_or(xi <= xa, xj <= xa)
            )
            rs, cs = np.where(tf)
            cross1 = np.zeros(ya.shape, dtype=bool)
            cross2 = np.zeros(ya.shape, dtype=bool)
            mask1 = (
                (xi + (ya[rs, cs] - yi) / (yj - yi) * (xj - xi)) < xa[rs, cs]
            )
            mask2 = (
                (xi + (ya[rs, cs] - yi) / (yj - yi) * (xj - xi)) <= xa[rs, cs]
            )
            cross1[rs, cs] = mask1
            cross2[rs, cs] = mask2
            result1[tf] ^= cross1[tf]
            result2[tf] ^= cross2[tf]
            xj, yj = xi, yi
        result = np.logical_or(result1, result2)

        if promoted:
            # de-promote result
            result = result[np.eye(len(y_arr), len(x_arr), dtype=np.bool)]

        return result

    def _get_mask_from_roi(self, roi, mask=None):
        """Get mask array from ROI

        Parameters
        ----------
        roi : :class:`ROIBase`
            The region of interest
        mask : :class:`numpy.ndarray`
            Boolean array of the image

        Returns
        -------
        mask : :class:`numpy.ndarray`
            Boolean array of the image with ROI coordinates as ``True``
        """

        if mask is None:
            mask = np.zeros(self.image_set.current_image.shape, dtype=np.bool)
        x1, y1, x2, y2 = roi.get_llur()
        x1, y1 = np.floor([x1, y1]).astype(int)
        x2, y2 = np.ceil([x2, y2]).astype(int)

        # Fix top edge case. Due to display reasons, the top edge case must be
        # dealt with differently than right edge case.
        ends_above_top = y2 == self.top - .5
        starts_and_ends_above_top = y1 == self.top - 2.5 and ends_above_top
        if ends_above_top:
            if starts_and_ends_above_top:
                y1 = int(self.top - 3.5)
                # Must move roi so the points are inside the region
                self.move_delta(0, -1)
            y2 = int(self.top - 1.5)

        X, Y = np.mgrid[x1:x2, y1:y2]
        rows, cols = Y, X
        coords = roi.contains_arr(X, Y)
        mask[rows, cols] = coords
        return mask

    @contextmanager
    def _temporary_move_by_delta(self, delta):
        """Context manager to move the ROI by delta temporarily

        Parameters
        ----------
        delta : :obj:`tuple` of two :obj:`float`
            Change the roi position by x and y

        Example
        -------
        >>> with _temporary_move_by_delta((10, 15)) as moved_roi:
        ...     moved_roi.get_points()
        """

        delta_x, delta_y = delta
        self.move_delta(delta_x, delta_y)
        yield self
        self.move_delta(-delta_x, -delta_y)

    def _get_roi_coords(self):
        """Get the coordinates in the region of interest"""
        delta = self.image_set.map_zoom_to_full_view()
        with self._temporary_move_by_delta(delta) as moved_roi:
            mask = self._get_mask_from_roi(moved_roi)
            roi_coords = np.where(mask)
        return roi_coords


class Polygon(ROIBase):
    """Polygon Region of Interest"""

    @ROIBase.draw_after
    @ROIBase.lock_coords_to_pixel_wrapper
    def start_ROI(self, data_x, data_y):
        """Start the ROI process

        The ROI will be a :class:`ginga.canvas.types.basic.Path` object

        Parameters
        ----------
        data_x : :obj:`float`
            The x coordinate
        data_y : :obj:`float`
            The y coordinate
        """

        self._current_path = basic.Path(
            [(data_x, data_y)], color=self.color
        )
        self.view_canvas.add(self._current_path)

    @ROIBase.draw_after
    @ROIBase.lock_coords_to_pixel_wrapper
    def continue_ROI(self, data_x, data_y):
        """Create new vertex on the polygon on left click

        Parameters
        ----------
        data_x : :obj:`float`
            The x coordinate
        data_y : :obj:`float`
            The y coordinate
        """

        self._current_path.insert_pt(0, (data_x, data_y))
        self._has_temp_point = False

    @ROIBase.draw_after
    @ROIBase.lock_coords_to_pixel_wrapper
    def extend_ROI(self, data_x, data_y):
        """Extend the current edge of the polygon on mouse motion

        Parameters
        ----------
        data_x : :obj:`float`
            The x coordinate
        data_y : :obj:`float`
            The y coordinate
        """

        self._current_path.insert_pt(0, (data_x, data_y))
        if self._current_path.get_num_points() > 2 and self._has_temp_point:
            self._current_path.delete_pt(1)
        self._has_temp_point = True

    @ROIBase.draw_after
    @ROIBase.lock_coords_to_pixel_wrapper
    def stop_ROI(self, data_x, data_y):
        """Close the polygon on right click

        The polygon will close based on last left click and not on the right
        click. There must be more than 2 points to formulate a polygon

        Parameters
        ----------
        data_x : :obj:`float`
            The x coordinate
        data_y : :obj:`float`
            The y coordinate
        """

        if self._has_temp_point:
                self._current_path.delete_pt(0)
        if self._current_path.get_num_points() <= 2:
            warnings.warn("Must have more than 2 points for a polygon")
            coords = []
        else:
            coords = self.create_ROI(self._current_path.get_points())
        self.view_canvas.deleteObject(self._current_path)
        return coords


class Rectangle(ROIBase):
    """Rectangle Region of interest"""

    # anchor point is pixel coordinate of the pixel first selected
    # This pixel will always be selected as a result
    _anchor_point = (0, 0)

    @ROIBase.draw_after
    @ROIBase.lock_coords_to_pixel_wrapper
    def start_ROI(self, data_x, data_y):
        """Start the region of interest on left click

        Parameters
        ----------
        data_x : :obj:`float`
            The x coordinate
        data_y : :obj:`float`
            The y coordinate
        """

        data_x = data_x - 1 if data_x == self.right else data_x
        data_y = data_y - 1 if data_y == self.top else data_y

        self._current_path = basic.Rectangle(
            data_x, data_y, data_x + 1, data_y + 1, color=self.color)
        self.view_canvas.add(self._current_path)
        self._anchor_point = (self._current_path.x1, self._current_path.y1)

    def continue_ROI(self, data_x, data_y):
        pass

    def _extend_point(self, point, anchor_point, edge):
        """Determine the x1, x2 or y1, y2 coordinates when extending

        Parameters
        ----------
        point : :obj:`float`
            The x or y coordinate in extending the rectangle
        anchor_point : :obj:`float`
            The x or y coordinate anchor point for the rectangle
        edge : :obj:`float`
            The top or right edge

        Returns
        -------
        p1 : :obj:`float`
            x1 or y1 coordinate
        p2 : :obj:`float`
            x2 or y2 coordinate
        """

        if point >= anchor_point:
            p1 = anchor_point
            p2 = point + 1 if point != edge else point
        else:
            p1 = point
            p2 = anchor_point + 1

        return p1, p2

    @ROIBase.draw_after
    @ROIBase.lock_coords_to_pixel_wrapper
    def extend_ROI(self, data_x, data_y):
        """Exend the rectangle on region of interest on mouse motion

        Parameters
        ----------
        data_x : :obj:`float`
            The x coordinate
        data_y : :obj:`float`
            The y coordinate
        """

        self._current_path.x1, self._current_path.x2 = self._extend_point(
            point=data_x,
            anchor_point=self._anchor_point[0],
            edge=self.right
        )
        self._current_path.y1, self._current_path.y2 = self._extend_point(
            point=data_y,
            anchor_point=self._anchor_point[1],
            edge=self.top
        )

    @ROIBase.draw_after
    @ROIBase.lock_coords_to_pixel_wrapper
    def stop_ROI(self, data_x, data_y):
        """Stop the region of interest on right click

        Parameters
        ----------
        data_x : :obj:`float`
            The x coordinate
        data_y : :obj:`float`
            The y coordinate
        """

        coords = self.create_ROI(self._current_path.get_points())
        self.view_canvas.deleteObject(self._current_path)
        return coords


class Pencil(ROIBase):
    """Select individual pixels"""

    point_radius = center_shift = 0.5

    def __init__(self, *args, **kwargs):
        super(Pencil, self).__init__(*args, **kwargs)
        self._current_path = []

    @ROIBase.draw_after
    def start_ROI(self, data_x, data_y):
        """Start choosing pixels on left click

        Parameters
        ----------
        data_x : :obj:`float`
            The x coordinate
        data_y : :obj:`float`
            The y coordinate
        """

        self._add_point(data_x, data_y)

    @ROIBase.lock_coords_to_pixel_wrapper
    def _add_point(self, data_x, data_y):
        """Add a point to the current path list

        Parameters
        ----------
        data_x : :obj:`float`
            The x coordinate
        data_y : :obj:`float`
            The y coordinate
        """

        next_point = basic.Point(
            data_x + self.center_shift,
            data_y + self.center_shift,
            self.point_radius,
            color=self.color)
        self.view_canvas.add(next_point)
        self._current_path.append(next_point)

    @ROIBase.draw_after
    def continue_ROI(self, data_x, data_y):
        """Add another pixel on left click

        Parameters
        ----------
        data_x : :obj:`float`
            The x coordinate
        data_y : :obj:`float`
            The y coordinate
        """

        self._add_point(data_x, data_y)

    # @ROIBase.draw_after
    # def extend_ROI(self, data_x, data_y):
    #     self._add_point(data_x, data_y)

    def extend_ROI(self, data_x, data_y):
        pass

    def move_delta(self, delta_x, delta_y):
        """Override the move_delta function to move all the points

        Parameters
        ----------
        delta_x : :obj:`float`
            Change in the x direction
        delta_y : :obj:`float`
            Change in the y direction
        """

        for point in self._current_path:
            point.move_delta(delta_x, delta_y)

    @ROIBase.draw_after
    def stop_ROI(self, data_x, data_y):
        """Set all pixels as roi cooridinates on right click

        Parameters
        ----------
        data_x : :obj:`float`
            The x coordinate
        data_y : :obj:`float`
            The y coordinate

        Returns
        -------
        coordinates : :class:`numpy.ndarray`
            Coordinates of points selected
        """

        delta = self.image_set.map_zoom_to_full_view()
        with self._temporary_move_by_delta(delta) as moved:
            pixels = list(set([(p.x, p.y) for p in moved._current_path]))
        self.view_canvas.delete_objects(self._current_path)
        coords = [(int(y), int(np.ceil(x))) for x, y in pixels]
        coordinates = np.array(coords)
        return coordinates
