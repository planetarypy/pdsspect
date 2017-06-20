import os
import warnings
from functools import wraps

import numpy as np
from ginga.util.dp import masktorgb

from planetaryimage import PDS3Image
from ginga.BaseImage import BaseImage
from ginga import colors as ginga_colors
from ginga.canvas.types.image import Image
import time


def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        finish = time.time()
        print(finish - start)
        return result
    return wrapper


ginga_colors.add_color('crimson', (0.86275, 0.07843, 0.23529))
ginga_colors.add_color('teal', (0.0, 0.50196, 0.50196))
ginga_colors.add_color('eraser', (0.0, 0.0, 0.0))


class ImageStamp(BaseImage):

    def __init__(self, filepath, metadata=None, logger=None):
        self.pds_image = PDS3Image.open(filepath)
        data = self.pds_image.image.astype(float)
        BaseImage.__init__(self, data_np=data,
                           metadata=metadata, logger=logger)
        self.set_data(data)
        self.image_name = os.path.basename(filepath)
        self.seen = False
        self.cuts = (None, None)


class PDSSPectImageSet(object):

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

    def __init__(self, filepaths):
        self._views = []
        self.images = []
        self.filepaths = filepaths
        for filepath in filepaths:
            try:
                image = ImageStamp(filepath)
                self.images.append(image)
            except Exception:
                warnings.warn("Unable to open %s" % (filepath))
        self._current_image_index = 0
        self.current_color_index = 0
        self._selection_index = 0
        self._zoom = 1.0
        self._center = None
        # self.rois = {color: np.array([]) for color in self.colors}
        self._delta_x = 0
        self._delta_y = 0
        self._last_zoom = 1.0
        self._move_rois = True
        self._alpha = 1.0
        self._flip_x = False
        self._flip_y = False
        self._swap_xy = False
        mask = np.zeros(self.current_image.shape, dtype=np.bool)
        self._maskrgb = masktorgb(mask, self.color, self.alpha)
        self._roi_data = self._maskrgb.get_data().astype(float)
        self._maskrgb_obj = Image(0, 0, self._maskrgb)

    def register(self, view):
        self._views.append(view)

    def unregister(self, view):
        self._views.remove(view)

    @property
    def filenames(self):
        return [os.path.basename(filepath) for filepath in self.filepaths]

    @property
    def current_image_index(self):
        return self._current_image_index

    @current_image_index.setter
    def current_image_index(self, new_index):
        self._current_image_index = new_index
        for view in self._views:
            view.set_image()

    @property
    def current_image(self):
        return self.images[self._current_image_index]

    @property
    def color(self):
        return self.colors[self.current_color_index]

    @property
    def selection_index(self):
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
        return self.selection_types[self.selection_index]

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, new_zoom):
        if new_zoom <= 0.0:
            raise ValueError("Zoom must be a positive value")
        self._last_zoom = self._zoom
        self._zoom = float(new_zoom)
        for view in self._views:
            view.adjust_pan_size()

    @property
    def x_radius(self):
        return self.current_image.shape[1] / 2

    @property
    def y_radius(self):
        return self.current_image.shape[0] / 2

    @property
    def pan_width(self):
        return self.x_radius / self.zoom

    @property
    def _last_pan_width(self):
        return self.x_radius / self._last_zoom

    @property
    def pan_height(self):
        return self.y_radius / self.zoom

    @property
    def _last_pan_height(self):
        return self.y_radius / self._last_zoom

    def reset_center(self):
        self._center = self.current_image.get_center()

    def _point_is_in_image(self, point):
        data_x, data_y = point
        height, width = self.current_image.shape[:2]
        in_width = data_x >= -0.5 and data_x <= (width + 0.5)
        in_height = data_y >= -0.5 and data_y <= (height + 0.5)
        return in_width and in_height

    def _determine_center_x(self, x):
        width = self.current_image.shape[1]
        left_of_left_edge = x - self.pan_width < -0.5
        right_of_right_edge = x + self.pan_width > (width + 0.5)
        in_width = not left_of_left_edge and not right_of_right_edge
        if in_width:
            center_x = x
        elif left_of_left_edge:
            self._move_roi = True
            center_x = self.pan_width
        elif right_of_right_edge:
            self._move_rois = True
            center_x = width - self.pan_width
        return center_x

    def _determine_center_y(self, y):
        height = self.current_image.shape[0]
        below_bottom = y - self.pan_height < -0.5
        above_top = y + self.pan_height > (height + 0.5)
        in_height = not below_bottom and not above_top
        if in_height:
            center_y = y
        elif below_bottom:
            self._move_rois = True
            center_y = self.pan_height
        elif above_top:
            self._move_rois = True
            center_y = height - self.pan_height
        return center_y

    @property
    def center(self):
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
            if self._move_rois:
                self._delta_x = self.center[0] - center[0]
                self._delta_y = self.center[1] - center[1]
            else:
                self._delta_x = 0
                self._delta_y = 0
            self._center = center
            for view in self._views:
                view.move_pan()

    @property
    def alpha255(self):
        return self._alpha * 255.

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, new_alpha):
        self._alpha = new_alpha
        rows, cols = np.where((~(self._roi_data == 0)).any(axis=2))
        # rows, cols = np.column_stack(roi)
        self._roi_data[rows, cols, 3] = self.alpha255
        for view in self._views:
            view.set_roi_data()

    @property
    def flip_x(self):
        return self._flip_x

    @flip_x.setter
    def flip_x(self, new_flip_x):
        self._flip_x = new_flip_x
        for view in self._views:
            view.set_transforms()

    @property
    def flip_y(self):
        return self._flip_y

    @flip_y.setter
    def flip_y(self, new_flip_y):
        self._flip_y = new_flip_y
        for view in self._views:
            view.set_transforms()

    @property
    def swap_xy(self):
        return self._swap_xy

    @swap_xy.setter
    def swap_xy(self, new_swap_xy):
        self._swap_xy = new_swap_xy
        for view in self._views:
            view.set_transforms()

    @property
    def transforms(self):
        return self.flip_x, self.flip_y, self.swap_xy

    @property
    def rois_iterator(self):
        rois = [roi for roi in self.rois.values() if roi.size > 0]
        return rois

    # @property
    # def _image_radius(self):
    #     height, width = self.current_image.shape[:2]
    #     image_radius = width / 2 if width < height else height / 2
    #     return image_radius

    # @property
    # def radius(self):
    #     return self._image_radius / self.zoom

    # @property
    # def _last_radius(self):
    #     return self._image_radius / self._last_zoom

    @property
    def edges(self):
        x, y = self.center
        left = int(round(x - self.pan_width))
        right = int(round(x + self.pan_width))
        bottom = int(round(y - self.pan_height))
        top = int(round(y + self.pan_height))
        return left, bottom, right, top

    @property
    def pan_slice(self):
        x1, y1, x2, y2 = self.edges
        pan_slice = np.s_[y1:y2:1, x1:x2:1]
        return pan_slice

    @property
    def pan_data(self):
        return self.current_image.get_data()[self.pan_slice]

    @property
    def pan_mask(self):
        return self._roi_data[self.pan_slice]

    def _get_rgb255_from_color(self, color):
        r, g, b = np.array(ginga_colors.lookup_color(color)) * 255.
        return r, g, b

    def _get_rgba_from_color(self, color):
        r, g, b = self._get_rgb255_from_color(color)
        a = self.alpha * 255.
        rgba = [r, g, b, a]
        return rgba

    # def _set_coords_in_rois_with_color(self, coords, color):
    #     for roi_name in self.rois:
    #         roi_coords = self.rois[roi_name].tolist()
    #         for coord in coords.tolist():
    #             add_coord_to_list = all(
    #                 (coord not in roi_coords, roi_name == color)
    #             )
    #             if add_coord_to_list:
    #                 roi_coords.append(coord)

    #             remove_coord_from_list = all(
    #                 (coord in roi_coords, roi_name != color)
    #             )
    #             if remove_coord_from_list:
    #                 roi_coords.remove(coord)
    #         self.rois[roi_name] = np.array(roi_coords)

    def _erase_coords(self, coords):
        rows, cols = np.column_stack(coords)
        self._roi_data[rows, cols] = [0.0, 0.0, 0.0, 0.0]
        # for roi_name in self.rois:
        #     roi_coords = self.rois[roi_name].tolist()
        #     for coord in coords.tolist():
        #         if coord in roi_coords:
        #             roi_coords.remove(coord)
        #     self.rois[roi_name] = np.array(roi_coords)

    def add_coords_to_roi_data_with_color(self, coords, color):
        rows, cols = np.column_stack(coords)
        rgba = self._get_rgba_from_color(color)
        self._roi_data[rows, cols] = rgba
        for view in self._views:
            view.set_roi_data()
        # self._set_coords_in_rois_with_color(coords, color)
        # print((self._roi_data == rgba).all(axis=2))
        # r, c = np.where((self._roi_data == rgba).all(axis=2))
        # print(np.column_stack([r, c]))
        # print(self.rois[color])

    # def _get_canvas_coordinate(self, side, coordinate):
    #     if self._last_zoom > self._zoom:
    #         canvas_coordinate = side + coordinate
    #     elif self._last_zoom < self._zoom:
    #         canvas_coordinate = side - coordinate
    #     else:
    #         canvas_coordinate = coordinate
    #     return canvas_coordinate

    # def map_zoom_point_to_view(self):
    #     delta_x = self.pan_width - self._last_pan_width
    #     delta_y = self.pan_height - self._last_pan_height
    #     return delta_x, delta_y

    def map_zoom_to_full_view(self):
        center_x1, center_y1 = self.current_image.get_center()
        center_x2, center_y2 = self.center
        delta_x = (self.x_radius - self.pan_width) + (center_x2 - center_x1)
        delta_y = (self.y_radius - self.pan_height) + (center_y2 - center_y1)
        return delta_x, delta_y

    def delete_rois_with_color(self, color):
        if coords.size != 0:
            rows, cols = np.column_stack(coords)
            self._roi_data[rows, cols] = [0, 0, 0, 0]
            # self.rois[color] = np.array([])
            for view in self._views:
                view.set_roi_data()


class PDSSpectImageSetViewBase(object):

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
