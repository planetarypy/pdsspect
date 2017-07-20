"""Window to pan the main image and open other dialog windows"""
from qtpy import QtWidgets
from ginga.canvas.types import basic

from .pan_view import PanView
from .pds_image_view_canvas import PDSImageViewCanvas
from .pdsspect_image_set import PDSSpectImageSetViewBase


class PDSSpectViewController(object):
    """Controller for the :class:`PDSSpectView`

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view : :class:`PDSpectView`
        View to control
    """

    def __init__(self, model, view):
        self.image_set = model
        self.view = view

    def change_pan_center(self, x, y):
        """Change the center of the pan

        Parameters
        ----------
        x : :obj:`float`
            The x coordinate of the center of the pan
        y : :obj:`float`
            The y coordinate of the center of the pan
        """

        self.image_set.center = x, y

    def change_pan_size(self, zoom):
        """Change the size of the pan by changing the zoom factor

        Parameters
        ----------
        zoom : :obj:`float`
            The new zoom factor
        """

        self.image_set.zoom = zoom


class PDSSpectView(QtWidgets.QWidget, PDSSpectImageSetViewBase):
    """View to pan the main image

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model

    Attributes
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    controller : :class:`PDSSpectViewController`
    main_layout : :class:`QtWidgets.QVBoxLayout <PySide.QtGui.QVBoxLayout>`
    zoom_layout : :class:`QtWidgets.QHBoxLayout <PySide.QtGui.QHBoxLayout>`
        Layout for :attr:`zoom_label` and :attr:`zoom_text`
    zoom_label : :class:`QtWidgets.QLabel <PySide.QtGui.QLabel>`
        Label the :attr:`zoom_text` text box
    zoom_text : :class:`QtWidgets.QLineEdit <PySide.QtGui.QLineEdit>`
        Text box to enter the zoom factor. Zoom will change on ``return key``
    view_canvas : :class:`PDSImageViewCanvas`
        canvas to place the image on
    pan : :class:`ginga.canvas.types.basic.Box`
        Pan that represents the pan. Data inside the pan is displayed in
        :class:`~pdsspect.pan_view.PanView`
    pan_view : :class:`~pdsspect.pan_view.PanView`
        View to display data in the :attr:`pan`
    """

    def __init__(self, image_set):
        super(PDSSpectView, self).__init__()
        self.image_set = image_set
        self.image_set.register(self)
        self.controller = PDSSpectViewController(self.image_set, self)

        self.main_layout = QtWidgets.QVBoxLayout()

        self.zoom_layout = QtWidgets.QHBoxLayout()
        self.zoom_label = QtWidgets.QLabel("Image Zoom")
        self.zoom_text = QtWidgets.QLineEdit(str(self.image_set.zoom))
        self.zoom_text.returnPressed.connect(self.change_zoom)
        self.zoom_text.adjustSize()
        self.zoom_layout.addWidget(self.zoom_label)
        self.zoom_layout.addWidget(self.zoom_text)

        self.view_canvas = PDSImageViewCanvas()
        self.view_canvas.set_window_size(*self.image_set.current_image.shape)
        self.view_canvas.set_image(self.image_set.current_image)
        self.view_canvas.set_callback('cursor-move', self.change_center)
        self.view_canvas.set_callback('cursor-down', self.change_center)
        self.view_canvas.set_callback('key-press', self.arrow_key_move_center)
        self.view_canvas.set_callback('zoom-scroll', self.zoom_with_scroll)

        centerx, centery = self.image_set.center
        self.pan = basic.Box(
            centerx,
            centery,
            self.image_set.pan_width + .5,
            self.image_set.pan_height + .5
        )
        self.view_canvas.add(self.pan)

        self.main_layout.addLayout(self.zoom_layout)
        self.main_layout.addWidget(self.view_canvas.get_widget())

        self.setLayout(self.main_layout)

        self.pan_view = PanView(image_set, self)
        self.view_canvas.add_subview(self.pan_view.view_canvas)
        self.pan_view.show()
        self.view_canvas.transform(*image_set.transforms)

    def set_image(self):
        """Set image on :attr:`view_canvas`"""
        self.view_canvas.set_image(self.image_set.current_image)
        if not self.image_set.current_image.seen:
            self.view_canvas.auto_levels()
            self.image_set.current_image.seen = True
        if any(self.image_set.current_image.cuts):
            cut_low, cut_high = self.image_set.current_image.cuts
            self.view_canvas.cut_levels(cut_low, cut_high)
        self.adjust_pan_size()
        self.image_set.reset_center()
        self.move_pan()
        self.view_canvas.zoom_fit()

    def set_transforms(self):
        """Apply transforms ``flip_x``, ``flip_y``, and ``switch_xy``"""
        self.view_canvas.transform(*self.image_set.transforms)

    def change_zoom(self):
        """Change zoom to what is in the text box"""
        try:
            zoom = float(self.zoom_text.text())
            self.controller.change_pan_size(zoom)
        except ValueError:
            self.zoom_text.setText(str(self.image_set.zoom))

    def adjust_pan_size(self):
        """Change the pan size as deterined by :attr:`image_set`"""
        self.pan.xradius = self.image_set.pan_width + .5
        self.pan.yradius = self.image_set.pan_height + .5
        self.image_set.center = self.pan.get_center_pt()
        self.view_canvas.redraw()
        self.image_set._move_rois = True
        self.zoom_text.setText(str(self.image_set.zoom))

    def resizeEvent(self, event):
        self.view_canvas.zoom_fit()
        self.view_canvas.delayed_redraw()

    def zoom_with_scroll(self, view_canvas, zoom_event):
        """Change the zoom by 1 with the mouse wheel

        Parameters
        ----------
        view_canvas : :attr:`view_canvas`
            The view canvas
        zoom_event : :class:`ginga.Bindings.ScrollEvent`
            The zoom event
        """

        is_foward = zoom_event.direction == 0.0
        if self.image_set.zoom == 1.0 and not is_foward:
            return
        delta_zoom = 1 if is_foward else -1
        self.controller.change_pan_size(self.image_set.zoom + delta_zoom)

    def arrow_key_move_center(self, view_canvas, keyname):
        """Adjust center with arrow press by a single pixel

        Parameters
        ----------
        view_canvas : :attr:`view_canvas`
            The view canvas
        keyname : :obj:`str`
            Name of the key
        """

        centerx, centery = self.image_set.center
        if keyname == 'left':
            self.controller.change_pan_center(centerx - 1, centery)
        if keyname == 'right':
            self.controller.change_pan_center(centerx + 1, centery)
        if keyname == 'down':
            self.controller.change_pan_center(centerx, centery - 1)
        if keyname == 'up':
            self.controller.change_pan_center(centerx, centery + 1)

    def change_center(self, view_canvas, button, data_x, data_y):
        """Adjust center to mouse position. Arguments supplied by callback

        Parameters
        ----------
        view_canvas : :attr:`view_canvas`
            The view canvas
        button : :class:`qtpy.QtCore.QMouseButton`
            The mouse button pressed
        data_x : :obj:`float`
            x coordinate of mouse
        data_y : :obj:`float`
            y coordinate of the mouse
        """

        self.controller.change_pan_center(data_x, data_y)

    def move_pan(self):
        """Move the pan as determined by the :attr:`image_set`"""
        self.pan.x, self.pan.y = self.image_set.center
        self.view_canvas.redraw()

    def redraw(self):
        """Redraw the :attr:`view_canvas`"""
        self.view_canvas.redraw()


class PDSSpectViewWidget(QtWidgets.QWidget):
    """Widget to hold the the differen :class:`PDSSpectView`

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model

    Attributes
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    """

    def __init__(self, image_set):
        super(PDSSpectViewWidget, self).__init__()
        self.image_set = image_set
        self.main_layout = QtWidgets.QHBoxLayout()
        self.spect_views = []
        self.create_spect_view(image_set)
        self.setWindowTitle('PDSSpect')
        self.setLayout(self.main_layout)

    def create_spect_view(self, image_set):
        """Create a :class:`PDSSpectView` and add to the widget

        Parameters
        ----------
        image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
            pdsspect model

        Returns
        -------
        spect_view : :class:`PDSSpectView`
            :class:`PDSSpectView` added to the widget
        """

        spect_view = PDSSpectView(image_set)
        self.spect_views.append(spect_view)
        self.main_layout.addWidget(spect_view)
        return spect_view
