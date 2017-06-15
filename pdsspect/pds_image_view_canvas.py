from ginga.qtw.ImageViewCanvasQt import ImageViewCanvas


class PDSImageViewCanvas(ImageViewCanvas):

    def __init__(self):
        super(PDSImageViewCanvas, self).__init__(render='widget')
        self._subviews = []
        self.set_autocut_params('zscale')
        self.enable_autozoom('override')
        self.enable_autocuts('override')
        self.set_bg(0, 0, 0)
        self.ui_setActive(True)

    def add_subview(self, subview):
        self._subviews.append(subview)

    def cut_levels(self, cut_low, cut_high):
        super(PDSImageViewCanvas, self).cut_levels(cut_low, cut_high)
        for subview in self._subviews:
            subview.cut_levels(cut_low, cut_high)

    def transform(self, flip_x, flip_y, swap_xy):
        super(PDSImageViewCanvas, self).transform(flip_x, flip_y, swap_xy)
        for subview in self._subviews:
            subview.transform(flip_x, flip_y, swap_xy)
