import math

from qtpy import QtWidgets

from .pdsspect_image_set import ginga_colors
from .roi_plot import ROIPlotModel, ROIPlotController, ROIPlotWidget, ROIPlot


class ROIHistogramModel(ROIPlotModel):
    """Model for ROI histogram and accompanying widget

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model

    Attributes
    ----------
    selected_colors : :obj:`list`
        Colors to display in the histogram
    """

    def __init__(self, image_set):
        super(ROIHistogramModel, self).__init__(image_set)
        self._image_index = -1

    @property
    def image_index(self):
        """:obj:`int` : The index of the image to which to compare data with

        When setting :attr:`image_index`, it may be changed to ``-1`` if the
        image is the same as the current image
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
    """Widget to hold the histogram and checkboxs

    Checkboxes are created in :meth:`create_color_checkbox` which is why they
    do not appear in the :meth:`__init__` method.

    Attributes
    ----------
    model : :class:`ROIHistogramModel`
        The model
    controller : :class:`ROIHistogramController`
        The controller
    checkbox_layout : :class:`QtWidgets.QVBoxLayout <PySide.QtGui.QVBoxLayout>`
        Place the checkboxes vertically
    main_layout : :class:`QtWidgets.QGridLayout <PySide.QtGui.QGridLayout>`
        Place in grid layout so histogram stretches while boxes are stationary
    red_checkbox : :class:`ColorCheckBox`
        Red checkbox that displays red ROI data when checked
    brown_checkbox : :class:`ColorCheckBox`
        Brown checkbox that displays brown ROI data when checked
    lightblue_checkbox : :class:`ColorCheckBox`
        Lightblue checkbox that displays lightblue ROI data when checked
    lightcyan_checkbox : :class:`ColorCheckBox`
        Lightcyan checkbox that displays lightcyan ROI data when checked
    darkgreen_checkbox : :class:`ColorCheckBox`
        Darkgreen checkbox that displays darkgreen ROI data when checked
    yellow_checkbox : :class:`ColorCheckBox`
        Yellow checkbox that displays yellow ROI data when checked
    pink_checkbox : :class:`ColorCheckBox`
        Pink checkbox that displays pink ROI data when checked
    teal_checkbox : :class:`ColorCheckBox`
        Teal checkbox that displays teal ROI data when checked
    goldenrod_checkbox : :class:`ColorCheckBox`
        Goldenrod checkbox that displays goldenrod ROI data when checked
    sienna_checkbox : :class:`ColorCheckBox`
        Sienna checkbox that displays sienna ROI data when checked
    darkblue_checkbox : :class:`ColorCheckBox`
        Darkblue checkbox that displays darkblue ROI data when checked
    crimson_checkbox : :class:`ColorCheckBox`
        Crimson checkbox that displays crimson ROI data when checked
    maroon_checkbox : :class:`ColorCheckBox`
        Maroon checkbox that displays maroon ROI data when checked
    purple_checkbox : :class:`ColorCheckBox`
        Purple checkbox that displays purple ROI data when checked
    """

    def __init__(self, model):
        self.model = model
        self.image_menu = None
        self._create_image_menu()
        self.roi_histogram = ROIHistogram(model)
        super(ROIHistogramWidget, self).__init__(model)
        self.controller = ROIHistogramController(model, self)
        self.setWindowTitle('ROI Histogram')

    def _register_set_at_index(self, index):
        self.model.image_sets[index].register(self.roi_histogram)
        self.model.image_sets[index].register(self)

    def _set_layout(self):
        self.main_layout.addLayout(self.view_boxes_layout, 0, 1, 1, 2)
        self.main_layout.addWidget(self.image_menu, 1, 0, 1, 1)
        self.main_layout.addWidget(self.roi_histogram, 1, 1, 2, 2)
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
    controller : :class:`ROIHistogramController`
        The controller
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
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
