import math

from qtpy import QtWidgets

from .pdsspect_image_set import ginga_colors
from .roi_plot import ROIPlotModel, ROIPlotController, ROIPlotWidget, ROIPlot


class ROIHistogramModel(ROIPlotModel):
    """Model for ROI histogram and accompanying widget"""

    def __init__(self, image_set):
        super(ROIHistogramModel, self).__init__(image_set)
        self._image_index = -1

    @property
    def image_index(self):
        """:obj:`int` : The index of the image to which to compare data with

        When setting :attr:`image_index`, it may be changed to ``-1`` if the
        image is the same as the current image. Furthermore, when setting the
        :attr:`view_index`, the :attr:`image_index` may be changed to ``-1`` if
        the :attr:`view_index` and the
        :attr:`~.pdsspect_image_set.PDSSpectImageSet.current_image_index` are
        the same.
        """

        return self._image_index

    @image_index.setter
    def image_index(self, index):
        index = index if index != self.image_set.current_image_index else -1
        self._image_index = index
        self.set_data()

    @property
    def compare_data(self):
        """:obj:`bool` : True if :attr:`image_index` is not ``-1``"""
        return self.image_index != -1

    def xdata(self, color):
        """Data inside a ROI with the given color for the current image

        Parameters
        ----------
        color : :obj:`str`
            The color of the ROI

        Returns
        -------
        data : :class:`numpy.ndarray`
            Data in ROI color for the xaxis
        """

        rows, cols = self.image_set.get_coordinates_of_color(color)
        data = self.image_set.current_image.data[rows, cols]
        return data

    def ydata(self, color):
        """Data inside a ROI with the given color for the image in the menu

        Parameters
        ----------
        color : :obj:`str`
            The color of the ROI

        Returns
        -------
        data : :class:`numpy.ndarray`
            Data in ROI color for the yaxis
        """

        if not self.compare_data:
            raise RuntimeError('Cannot call when not comparing images')
        rows, cols = self.image_set.get_coordinates_of_color(color)
        data = self.image_set.images[self.image_index].data[rows, cols]
        return data

    @property
    def xlim(self):
        """:obj:`list` of two :obj:`float` : min max of current image's data"""
        data = self.image_set.current_image.data
        xlim = [data.min(), data.max()]
        return xlim

    @property
    def ylim(self):
        """:obj:`list` of two :obj:`float` : min max of yaxis image"""
        if not self.compare_data:
            raise RuntimeError('Cannot call when not comparing images')
        data = self.image_set.images[self.image_index].data
        ylim = [data.min(), data.max()]
        return ylim


class ROIHistogramController(ROIPlotController):
    """Controller for ROI histogram and accompanying widget

    Parameters
    ----------
    model : :class:`ROIHistogramModel`
        The model
    view : :class:`ROIHistogramWidget` or :class:`ROIHistogram`
        The view

    Attributes
    ----------
    model : :class:`ROIHistogramModel`
        The model
    view : :class:`ROIHistogramWidget` or :class:`ROIHistogram`
        The view
    """

    def set_image_index(self, index):
        """Set the index of the image in the menu

        Parameters
        ----------
        index : :obj:`int`
            Index of the image menu
        """

        self.model.image_index = index


class ROIHistogramWidget(ROIPlotWidget):
    """Widget to hold the histogram and check boxes

    Parameters
    ----------
    model : :class:`ROIHistogramModel`
        The model

    Attributes
    ----------
    model : :class:`ROIHistogramModel`
        The model
    controller : :class:`ROIHistogramController`
        The controller
    image_menu : :class:`QtWidgets.QComboBox <PySide.QtGui.QComboBox>`
        Menu to select image for y axis
    """

    def __init__(self, model):
        self.model = model
        self.image_menu = None
        self._create_image_menu()
        super(ROIHistogramWidget, self).__init__(model)
        self.controller = ROIHistogramController(model, self)
        self.setWindowTitle('ROI Histogram')

    def _create_roi_plot(self):
        self.roi_plot = ROIHistogram(self.model)

    def _set_layout(self):
        left_vbox = QtWidgets.QVBoxLayout()
        left_vbox.addWidget(self.save_btn)
        left_vbox.addWidget(self.image_menu)
        left_vbox.addStretch()
        self.main_layout.addLayout(self.view_boxes_layout, 0, 1, 1, 2)
        self.main_layout.addLayout(left_vbox, 1, 0)
        self.main_layout.addWidget(self.roi_plot, 1, 1, 2, 2)
        self.main_layout.addLayout(self.checkbox_layout, 1, 3)
        self.main_layout.setColumnStretch(1, 1)
        self.main_layout.setRowStretch(1, 1)
        self.setLayout(self.main_layout)

    def _create_image_menu(self):
        image_menu = QtWidgets.QComboBox()
        for image in self.model.image_set.images:
            image_menu.addItem(image.image_name)
        image_menu.setCurrentIndex(self.model.image_set.current_image_index)
        image_menu.currentIndexChanged.connect(self.select_image)
        self.image_menu = image_menu

    def select_image(self, index):
        """Select an image when image is selected in the menu

        Parameters
        ----------
        index : :obj:`int`
            The index of the selected image
        """

        self.controller.set_image_index(index)

    def set_image(self):
        if self.model.image_index == self.model.image_set.current_image_index:
            self.select_image(-1)
        else:
            self.select_image(self.image_menu.currentIndex())


class ROIHistogram(ROIPlot):
    """Histogram view of the data in each ROI color

    Parameters
    ----------
    model : :class:`ROIHistogramModel`
        The model

    Attributes
    ----------
    model : :class:`ROIHistogramModel`
        The model
    """

    def __init__(self, model):
        self.model = model
        model.register(self)
        self.controller = ROIHistogramController(model, self)
        super(ROIHistogram, self).__init__(model)
        self._ax.set_xlim(self.model.xlim)

    def _plot_histogram(self):
        self._ax.set_ylabel(
            ylabel='Pixel Values',
            color='w',
            fontsize=9
        )
        for color in self.model.selected_colors:
            rgb = ginga_colors.lookup_color(color)
            data = self.model.xdata(
                color=color
            )
            self._ax.hist(data.flatten(), 100, color=rgb)

    def _create_label(self, image):
        label = image.image_name
        if not math.isnan(image.wavelength):
            label += '\n(%.3f' % (image.wavelength)
            label += r' $%s$)' % (self.model.unit)
        return label

    def _plot_comparison(self):
        ylabel = self._create_label(
            self.model.image_set.images[self.model.image_index]
        )

        self._ax.set_ylabel(
            ylabel=ylabel,
            color='w',
            fontsize=9
        )
        for color in self.model.selected_colors:
            rgb = ginga_colors.lookup_color(color)
            xdata = self.model.xdata(
                color=color,
            )
            ydata = self.model.ydata(
                color=color,
            )
            self._ax.plot(xdata, ydata, '.', color=rgb)

    def set_data(self):
        """Set the data of the selected colors on the histogram"""
        self._ax.cla()
        if self.model.compare_data:
            self._plot_comparison()
        else:
            self._plot_histogram()

        xlabel = self._create_label(self.model.image_set.current_image)

        self._ax.set_xlabel(
            xlabel=xlabel,
            color='w',
            fontsize=9,
        )
        self._ax.set_xlim(self.model.xlim)
        if self.model.compare_data:
            self._ax.set_ylim(self.model.ylim)
        self.draw()

    def set_image(self):
        """Set data when image is changed"""
        self.set_data()
