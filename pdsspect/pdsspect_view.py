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
    main_layout : :class:`QtWidgets.QVBoxLayout`
    zoom_layout : :class:`QtWidgets.QHBoxLayout`
        Layout for :attr:`zoom_label` and :attr:`zoom_text`
    zoom_label : :class:`QtWidgets.QLabel`
        Label the :attr:`zoom_text` text box
    zoom_text : :class:`QtWidgets.QLineEdit`
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
        self.view_canvas.set_image(self.image_set.current_image)
        self.view_canvas.set_desired_size(100, 100)
        self.view_canvas.set_callback('cursor-move', self.change_center)
        self.view_canvas.set_callback('cursor-down', self.change_center)

        centerx, centery = self.image_set.center
        self.pan = basic.Box(
            centerx,
            centery,
            self.image_set.pan_width,
            self.image_set.pan_height
        )
        self.view_canvas.add(self.pan)

        self.main_layout.addLayout(self.zoom_layout)
        self.main_layout.addWidget(self.view_canvas.get_widget())

        self.setLayout(self.main_layout)

        self.pan_view = PanView(image_set, self)
        self.view_canvas.add_subview(self.pan_view.view_canvas)
        self.pan_view.show()

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
        self.pan.xradius = self.image_set.pan_width
        self.pan.yradius = self.image_set.pan_height
        self.image_set.center = self.pan.get_center_pt()
        self.view_canvas.redraw()
        self.image_set._move_rois = True

    def resizeEvent(self, event):
        self.view_canvas.zoom_fit()
        self.view_canvas.delayed_redraw()

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
