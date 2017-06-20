from qtpy import QtWidgets
from ginga.canvas.types import basic

from .pan_view import PanView
from .pds_image_view_canvas import PDSImageViewCanvas
from .pdsspect_image_set import PDSSpectImageSetViewBase


class PDSSpectViewController(object):

    def __init__(self, model, view):
        self.image_set = model
        self.view = view

    def change_pan_center(self, x, y):
        self.image_set.center = x, y

    def change_pan_size(self, zoom):
        self.image_set._move_rois = False
        self.image_set.zoom = zoom


class PDSSpectView(QtWidgets.QWidget, PDSSpectImageSetViewBase):

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
        self.box = basic.Box(
            centerx,
            centery,
            self.image_set.pan_width,
            self.image_set.pan_height
        )
        self.view_canvas.add(self.box)

        self.main_layout.addLayout(self.zoom_layout)
        self.main_layout.addWidget(self.view_canvas.get_widget())

        self.setLayout(self.main_layout)

        self.pan_view = PanView(image_set, self)
        self.view_canvas.add_subview(self.pan_view.view_canvas)
        self.pan_view.show()

    def set_image(self):
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
        self.view_canvas.transform(*self.image_set.transforms)

    def change_zoom(self):
        try:
            zoom = float(self.zoom_text.text())
            self.controller.change_pan_size(zoom)
        except ValueError:
            self.zoom_text.setText(str(self.image_set.zoom))

    def adjust_pan_size(self):
        self.box.xradius = self.image_set.pan_width
        self.box.yradius = self.image_set.pan_height
        self.image_set.center = self.box.get_center_pt()
        self.view_canvas.redraw()
        self.image_set._move_rois = True

    def resizeEvent(self, event):
        self.view_canvas.zoom_fit()
        self.view_canvas.delayed_redraw()

    def change_center(self, view_canvas, button, data_x, data_y):
        self.controller.change_pan_center(data_x, data_y)

    def move_pan(self):
        self.box.x, self.box.y = self.image_set.center
        self.view_canvas.redraw()

    def redraw(self):
        self.view_canvas.redraw()
