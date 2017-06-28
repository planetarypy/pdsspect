from ginga.qtw.ImageViewCanvasQt import ImageViewCanvas


class PDSImageViewCanvas(ImageViewCanvas):
    """:class:`ImageViewCanvas` for ``pdsspect`` views"""

    def __init__(self):
        super(PDSImageViewCanvas, self).__init__(render='widget')
        self._subviews = []
        self.set_autocut_params('zscale')
        self.enable_autozoom('override')
        self.enable_autocuts('override')
        self.set_bg(0, 0, 0)
        self.ui_setActive(True)

    def add_subview(self, subview):
        """Add a :class:`ImageViewCanvas` as a subview

        Parameters
        ----------
        subview : :class:`ginga.qtw.ImageViewCanvasQt`
            View canvas to add as a subview

        Raises
        ------
        TypeError
            When subview is not an :class:`ImageViewCanvas` object
        """

        if not isinstance(subview, ImageViewCanvas):
            raise TypeError("Subview must be an ImageViewCanvas")
        self._subviews.append(subview)

    def cut_levels(self, cut_low, cut_high):
        """Adjust the cut levels of the view and all the subviews

        Parameters
        ----------
        cut_low : :obj:`float`
            The low cut level
        cut_high : :obj:`float`
            The high cut level
        """

        super(PDSImageViewCanvas, self).cut_levels(cut_low, cut_high)
        for subview in self._subviews:
            subview.cut_levels(cut_low, cut_high)

    def transform(self, flip_x, flip_y, swap_xy):
        """Apply transforms to the view and all the subviews

        Parameters
        ----------
        flip_x : :obj:`bool`
            Flip x axis if True. Otherwise, do not
        flip_y : :obj:`bool`
            Flip y axis if True. Otherwise, do not
        swap_xy : :obj:`bool`
            Swap the x and y axis if True. Otherwise, do not
        """

        super(PDSImageViewCanvas, self).transform(flip_x, flip_y, swap_xy)
        for subview in self._subviews:
            subview.transform(flip_x, flip_y, swap_xy)
