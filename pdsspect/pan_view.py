"""Display data in pan and make ROI selections"""
from functools import wraps

from qtpy import QtWidgets

from .roi import Polygon, Rectangle, Pencil
from .pds_image_view_canvas import PDSImageViewCanvas
from .pdsspect_image_set import PDSSpectImageSetViewBase, SubPDSSpectImageSet


class PanViewController(object):
    """Controller for the :class:`PanView`

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view : :class:`PanView`
        View to control

    Attributes
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view : :class:`PanView`
        View to control
    """

    def __init__(self, image_set, view):
        self.image_set = image_set
        self.view = view

    def _get_parent_set(self):
        if isinstance(self.image_set, SubPDSSpectImageSet):
            image_set = self.image_set.parent_set
        else:
            image_set = self.image_set
        return image_set

    def add_ROI(self, coordinates):
        """Add a region of interest

        Parameters
        ----------
        coordinates : :class:`numpy.ndarray` or :obj:`tuple`
            Either a ``(m x 2)`` array or a tuple of two arrays

            If an array, the first column are the x coordinates and the second
            are the y coordinates. If a tuple of arrays, the first array are x
            coordinates and the second are the corresponding y coordinates.
        """

        if self.image_set.simultaneous_roi:
            parent_set = self._get_parent_set()
            for image_set in [parent_set] + parent_set.subsets:
                image_set.add_coords_to_roi_data_with_color(
                    coordinates=coordinates,
                    color=image_set.color,
                )
        else:
            self.image_set.add_coords_to_roi_data_with_color(
                coordinates=coordinates,
                color=self.image_set.color,
            )

    def erase_ROI(self, coordinates):
        """Erase any region of interest inside coordinates

        Parameters
        ----------
        coordinates : :class:`numpy.ndarray` or :obj:`tuple`
            Either a ``(m x 2)`` array or a tuple of two arrays

            If an array, the first column are the x coordinates and the second
            are the y coordinates. If a tuple of arrays, the first array are x
            coordinates and the second are the corresponding y coordinates.
        """

        if self.image_set.simultaneous_roi:
            parent_set = self._get_parent_set()
            for image_set in [parent_set] + parent_set.subsets:
                image_set._erase_coords(coordinates)
        else:
            self.image_set._erase_coords(coordinates)


class PanView(QtWidgets.QWidget, PDSSpectImageSetViewBase):
    """View of the image inside the pan

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    parent : None
        The parent of the view

    Attributes
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    controller : :class:`PanViewController`
        The view's controller
    parent : None
        The view's parent
    main_layout : :class:`QtWidgets.QVBoxLayout <PySide.QtGui.QVBoxLayout>`
        The main layout of the view
    view_canvas : :class:`~pdsspect.pds_image_view_canvas.PDSImageViewCanvas`
        Canvas to view the image
    """

    def __init__(self, image_set, parent=None):
        super(PanView, self).__init__(parent)
        self.image_set = image_set
        self.image_set.register(self)
        self.controller = PanViewController(self.image_set, self)
        self._making_roi = False
        self._current_roi = None

        self.main_layout = QtWidgets.QVBoxLayout()
        save_layout = QtWidgets.QHBoxLayout()
        save_frame_btn = QtWidgets.QPushButton('Save Frame')
        save_frame_btn.clicked.connect(self.save_frame)
        save_layout.addWidget(save_frame_btn)
        save_layout.addStretch()
        self.main_layout.addLayout(save_layout)

        self.view_canvas = PDSImageViewCanvas()
        self.view_canvas.set_callback('cursor-down', self.start_ROI)
        self.view_canvas.set_callback('draw-down', self.stop_ROI)
        self.view_canvas.set_callback('motion', self.extend_ROI)
        self.view_canvas.set_window_size(*self.image_set.pan_data.shape)

        self.main_layout.addWidget(self.view_canvas.get_widget())
        self.view_canvas.get_widget().setMouseTracking(True)

        self.setLayout(self.main_layout)
        self.setMouseTracking(True)
        self.set_data()
        self.view_canvas.add(self.image_set._maskrgb_obj)

    @property
    def is_erasing(self):
        """:obj:`bool` : True if current color is ``eraser`` false otherwise"""
        return self.image_set.color == 'eraser'

    def set_data(self):
        """Set pan data on the canvas"""
        self.view_canvas.set_data(self.image_set.pan_data)
        self.set_roi_data()

    def set_roi_data(self):
        """Set the ROI data on the canvas"""
        self.image_set._maskrgb.set_data(self.image_set.pan_roi_data)
        self.view_canvas.redraw()

    def change_roi_opacity(self):
        self.set_roi_data()

    def set_image(self):
        """Set the data"""
        self.set_data()
        self.view_canvas.zoom_fit()

    def move_pan(self):
        """Set the data when the pan is moved"""
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
        """Wrapper to make sure ROI stays inside the current view"""
        @wraps(func)
        def wrapper(self, view_canvas, button, data_x, data_y):
            data_x, data_y = self._make_x_y_in_pan(data_x, data_y)
            return func(self, view_canvas, button, data_x, data_y)
        return wrapper

    @check_ROI_in_pan
    def start_ROI(self, view_canvas, button, data_x, data_y):
        """Start the ROI at the mouse location"""
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
        """Wrapper to make sure the roi making is in process"""
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
        """Continue the ROI making on click"""
        if self.image_set.selection_type == 'filled polygon':
            self._current_roi.continue_ROI(data_x, data_y)
        elif self.image_set.selection_type == 'filled rectangle':
            self.stop_ROI(view_canvas, button, data_x, data_y)
        elif self.image_set.selection_type == 'pencil':
            self._current_roi.continue_ROI(data_x, data_y)

    @check_ROI_in_pan
    @check_roi_in_process
    def extend_ROI(self, view_canvas, button, data_x, data_y):
        """Extend the ROI on mouse motion"""
        self._current_roi.extend_ROI(data_x, data_y)

    @check_ROI_in_pan
    @check_roi_in_process
    def stop_ROI(self, view_canvas, button, data_x, data_y):
        """Stop ROI on right click"""
        coords = self._current_roi.stop_ROI(data_x, data_y)
        if self.is_erasing:
            self.controller.erase_ROI(coords)
        else:
            self.controller.add_ROI(coords)
        self._making_roi = False
        self._current_roi = None

    def redraw(self):
        """Redraw :attr:`view_canvas`"""
        self.view_canvas.redraw()

    def resizeEvent(self, event):
        self.view_canvas.zoom_fit()
        self.redraw()

    def save_frame(self):
        """Save current frame as image"""
        save_file, _ = QtWidgets.QFileDialog.getSaveFileName(parent=self)
        frame = self.view_canvas.get_widget().grab()
        frame.save(save_file)


class PanViewWidget(QtWidgets.QDialog):
    """Widget to hold the different pan windows

    Parameters
    ----------
    pan : :class:`PanView`
        First :class:`PanView` to include in the widget
    parent : :class:`QWidget <PySide.QtWidgets.QWidget>`
        The parent widget

    Attributes
    ----------
    pans : :obj:`list` of :class:`PanView`
        The :class:`PanView`s in the widget
    """

    def __init__(self, pan, parent):
        super(PanViewWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QHBoxLayout()
        self.pans = []
        self.add_pan(pan)
        self.setWindowTitle('Pan View')
        self.setLayout(self.main_layout)

    def add_pan(self, pan):
        """Add a :class:`PanView` to the widget

        Parameters
        ----------
        pan : :class:`PanView`
            First :class:`PanView` to include in the widget
        """

        self.pans.append(pan)
        self.main_layout.addWidget(pan)
