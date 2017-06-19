from functools import wraps

from qtpy import QtWidgets

from .roi import Polygon, Rectangle, Pencil
from .pds_image_view_canvas import PDSImageViewCanvas
from .pdsspect_image_set import PDSSpectImageSetViewBase


class PanViewController(object):

    def __init__(self, image_set, view):
        self.image_set = image_set
        self.view = view

    def add_ROI(self, coords):
        self.image_set.add_coords_to_roi_data_with_color(
            coords, self.image_set.color
        )

    def erase_ROI(self, coords):
        self.image_set._erase_coords(coords)


class PanView(QtWidgets.QWidget, PDSSpectImageSetViewBase):

    def __init__(self, image_set, parent=None):
        super(PanView, self).__init__()
        self.image_set = image_set
        self.image_set.register(self)
        self.controller = PanViewController(self.image_set, self)
        self.parent = parent
        self._making_roi = False
        self._current_roi = None

        self.main_layout = QtWidgets.QVBoxLayout()

        self.view_canvas = PDSImageViewCanvas()
        self.view_canvas.set_callback('cursor-down', self.start_ROI)
        self.view_canvas.set_callback('draw-down', self.stop_ROI)
        self.view_canvas.set_callback('motion', self.extend_ROI)

        self.main_layout.addWidget(self.view_canvas.get_widget())
        self.view_canvas.get_widget().setMouseTracking(True)

        self.setLayout(self.main_layout)
        self.setMouseTracking(True)
        self.set_data()
        self.view_canvas.add(self.image_set._maskrgb_obj)

    @property
    def is_erasing(self):
        return self.image_set.color == 'eraser'

    def set_data(self):
        self.view_canvas.set_data(self.image_set.pan_data)
        self.set_roi_data()

    def set_roi_data(self):
        self.image_set._maskrgb.set_data(self.image_set.pan_mask)
        self.view_canvas.redraw()

    def set_image(self):
        self.set_data()
        self.view_canvas.zoom_fit()

    def move_pan(self):
        self.set_data()
        self.view_canvas.zoom_fit()

    def _make_x_y_in_pan(self, x, y):
        bottom, top = -.5, self.image_set.pan_height * 2 - 1.
        left, right = -.5, self.image_set.pan_width * 2 - 1.
        x = left if x < left else x
        x = right if x > right else x
        y = bottom if y < bottom else y
        y = top if y > top else y
        return x, y

    def check_ROI_in_pan(func):
        @wraps(func)
        def wrapper(self, view_canvas, button, data_x, data_y):
            data_x, data_y = self._make_x_y_in_pan(data_x, data_y)
            return func(self, view_canvas, button, data_x, data_y)
        return wrapper

    @check_ROI_in_pan
    def start_ROI(self, view_canvas, button, data_x, data_y):
        if self._making_roi:
            self.continue_ROI(view_canvas, button, data_x, data_y)
        else:
            if self.image_set.selection_type == 'filled polygon':
                ROI = Polygon
            elif self.image_set.selection_type == 'filled rectangle':
                ROI = Rectangle
            elif self.image_set.selection_type == 'pencil':
                ROI = Pencil
            fillalpha = self.image_set.alpha if not self.is_erasing else 0
            self._current_roi = ROI(
                self.image_set,
                view_canvas,
                color=self.image_set.color,
                fill=True,
                alpha=self.image_set.alpha,
                fillcolor=self.image_set.color,
                fillalpha=fillalpha,
            )
            self._current_roi.start_ROI(data_x, data_y)
            self._making_roi = True

    def check_roi_in_process(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self._making_roi or not self._current_roi:
                return
            else:
                return func(self, *args, **kwargs)
        return wrapper

    @check_ROI_in_pan
    @check_roi_in_process
    def continue_ROI(self, view_canvas, button, data_x, data_y):
        if self.image_set.selection_type == 'filled polygon':
            self._current_roi.continue_ROI(data_x, data_y)
        elif self.image_set.selection_type == 'filled rectangle':
            self.stop_ROI(view_canvas, button, data_x, data_y)
        elif self.image_set.selection_type == 'pencil':
            self._current_roi.continue_ROI(data_x, data_y)

    @check_ROI_in_pan
    @check_roi_in_process
    def extend_ROI(self, view_canvas, button, data_x, data_y):
        self._current_roi.extend_ROI(data_x, data_y)

    @check_ROI_in_pan
    @check_roi_in_process
    def stop_ROI(self, view_canvas, button, data_x, data_y):
        coords = self._current_roi.stop_ROI(data_x, data_y)
        if self.is_erasing:
            self.controller.erase_ROI(coords)
        else:
            self.controller.add_ROI(coords)
        self._making_roi = False
        self._current_roi = None

    def redraw(self):
        self.view_canvas.redraw()

    def resizeEvent(self, event):
        self.view_canvas.zoom_fit()
        self.redraw()
