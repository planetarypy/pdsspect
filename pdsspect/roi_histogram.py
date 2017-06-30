from qtpy import QT_VERSION
from qtpy import QtWidgets, QtCore
from matplotlib.figure import Figure

from .pdsspect_image_set import PDSSpectImageSetViewBase, ginga_colors

qt_ver = int(QT_VERSION[0])
if qt_ver == 4:
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
elif qt_ver == 5:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class ROIHistogramModel(object):
    """Model for ROI histogram and accompanying widget

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model

    Attributes
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    selected_colors : :obj:`list`
        Colors to display in the histogram
    """

    def __init__(self, image_set):
        self._views = []
        self.image_set = image_set
        self.selected_colors = []

    def register(self, view):
        """Register view with the model"""
        if view not in self._views:
            self._views.append(view)

    def unregister(self, view):
        """Unregister view with the model"""
        if view in self._views:
            self._views.remove(view)

    def add_selected_color(self, color):
        """Select a color and inform views to display new color

        Parameters
        ----------
        color : :obj:`str`
            The color to add
        """

        self.selected_colors.append(color)
        for view in self._views:
            view.set_data()

    def remove_selected_color(self, color):
        """Remove a selected color and inform views to not display the color

        Parameters
        ----------
        color : :obj:`str`
            The color to remove
        """

        self.selected_colors.remove(color)
        for view in self._views:
            view.set_data()

    def data_in_roi_with_color(self, color):
        """Get the data inside a ROI with the given color

        Parameters
        ----------
        color : :obj:`str`
            The color of the ROI
        """

        rows, cols = self.image_set.get_coordinates_of_color(color)
        data = self.image_set.current_image.data[rows, cols]
        return data

    @property
    def xlim(self):
        """:obj:`list` of two :obj:`float` : min max of current image's data"""
        data = self.image_set.current_image.data
        xlim = [data.min(), data.max()]
        return xlim


class ROIHistogramController(object):
    """Controller for ROI histogram and accompanying widget

    Parameters
    ----------
    model : :class:`ROIHistogramModel`
        The model
    view : :class:`ROIHistogramWidget` or :class:`ROIHistogram`
        The view
    """

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def color_state_changed(self, color):
        """Select or remove the color when a checkbox color changes

        Parameters
        ----------
        color : :obj:`str`
            The name of the checkbox whose state changed
        """

        if color not in self.model.selected_colors:
            self.select_color(color)
        else:
            self.remove_color(color)

    def select_color(self, color):
        """Selected a given color

        Parameters
        ----------
        color : :obj:`str`
            The color to select
        """

        self.model.add_selected_color(color)

    def remove_color(self, color):
        """Remove a given color

        Parameters
        ----------
        color : :obj:`str`
            The color to remove
        """

        self.model.remove_selected_color(color)


class ColorCheckBox(QtWidgets.QCheckBox):
    """Custom checkbox that emits it's color (:obj:`str`) when toggled

    Parameters
    ----------
    color : :obj:`str`
        The color to name the checkbox

    Attributes
    ----------
    color : :obj:`str`
        The color to name the checkbox
    stateChanged : :obj:`QtCore.Signal`
        Signal that emits a string when check box changes its state

        Read more about `Signals here
        <http://pyqt.sourceforge.net/Docs/PyQt5/signals_slots.html>`_
    """

    stateChanged = QtCore.Signal(str)

    def __init__(self, color):
        super(ColorCheckBox, self).__init__(color)
        self.color = color

    def nextCheckState(self):
        """Adjust checkbox's toggle & emit color when checkbox is clicked"""
        self.setChecked(not self.isChecked())
        self.stateChanged.emit(self.color)


class ROIHistogramWidget(QtWidgets.QWidget):
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
        super(ROIHistogramWidget, self).__init__()
        self.model = model
        self.model.register(self)
        self.controller = ROIHistogramController(model, self)
        self.checkbox_layout = QtWidgets.QVBoxLayout()
        for color in self.model.image_set.colors[:-1]:
            self.create_color_checkbox(color)
        roi_histogram = ROIHistogram(model)
        self.main_layout = QtWidgets.QGridLayout()
        self.main_layout.addWidget(roi_histogram, 0, 0, 2, 2)
        self.main_layout.addLayout(self.checkbox_layout, 0, 2)
        self.main_layout.setColumnStretch(1, 1)
        self.main_layout.setRowStretch(0, 1)
        self.setLayout(self.main_layout)
        self.setWindowTitle('ROI Histogram')

    def create_color_checkbox(self, color):
        """Create a checkbox with the given color

        Parameters
        ----------
        color : :obj:`str`
            The color to name the checkbox
        """

        name = color + '_checkbox'
        color_checkbox = ColorCheckBox(color)
        color_checkbox.stateChanged.connect(self.check_color)
        setattr(self, name, color_checkbox)
        self.checkbox_layout.addWidget(color_checkbox)

    def check_color(self, checkbox_color):
        """Called when the state a checkbox is changed

        Parameters
        ----------
        checkbox_color : :obj:`str`
            The color label of the check box
        """

        self.controller.color_state_changed(checkbox_color)

    def set_data(self):
        pass


class ROIHistogram(FigureCanvasQTAgg, PDSSpectImageSetViewBase):
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
        self.image_set = model.image_set
        self.image_set.register(self)
        fig = Figure(figsize=(2, 2), dpi=100, facecolor='black')
        fig.subplots_adjust(
            left=0.15,
            right=0.95,
            top=0.95,
            bottom=0.15,
            wspace=0.0,
            hspace=0.0,
        )
        super(ROIHistogram, self).__init__(fig)
        self._figure = fig
        policy = self.sizePolicy()
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)
        self.setMinimumSize(self.size())
        self._ax = fig.add_subplot(111)
        self._ax.set_facecolor('black')
        self._ax.spines['bottom'].set_color('w')
        self._ax.spines['left'].set_color('w')
        self._ax.tick_params(axis='x', colors='w', labelsize=8)
        self._ax.tick_params(axis='y', colors='w', labelsize=8)
        self._ax.set_xlim(self.model.xlim)
        self.set_data()

    def set_data(self):
        """Set the data of the selected colors on the histogram"""
        if not self.model.selected_colors:
            return
        self._ax.cla()
        for color in self.model.selected_colors:
            rgb = ginga_colors.lookup_color(color)
            data = self.model.data_in_roi_with_color(color)
            self._ax.hist(data.flatten(), 100, color=rgb)
        self._ax.set_xlim(self.model.xlim)
        self.draw()

    def set_roi_data(self):
        """Set data when ROI is created/destroyed or checkbox is toggled"""
        self.set_data()

    def set_image(self):
        """Set data when image is changed"""
        self.set_data()
