"""Parent classes for any widget that plots data"""
from qtpy import QT_VERSION
from qtpy import QtWidgets, QtCore
from matplotlib.figure import Figure

from .pdsspect_image_set import PDSSpectImageSetViewBase

qt_ver = int(QT_VERSION[0])
if qt_ver == 4:
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
elif qt_ver == 5:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


class ROIPlotModel(object):
    """Model for ROI Plot and accompanying widget

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model

    Attributes
    ----------
    selected_colors : :obj:`list`
        Colors to display in the histogram
    latex_units : :obj:`list` of 3 :obj:`str`
        The latex strings of
        :attr:`.pdsspect_image_set.PDSSpectImageSet.accepted_units`
    """

    latex_units = ['nm', '\mu m', '\AA']

    def __init__(self, image_set):
        self._views = []
        self._image_set = image_set
        self.selected_colors = []
        self._view_index = 0

    def register(self, view):
        """Register view with the model"""
        if view not in self._views:
            self._views.append(view)

    def unregister(self, view):
        """Unregister view with the model"""
        if view in self._views:
            self._views.remove(view)

    def set_data(self):
        for view in self._views:
            view.set_data()

    @property
    def image_sets(self):
        """:obj:`list` : All the image sets, including the current one"""
        return [self._image_set] + self._image_set.subsets

    @property
    def image_set(self):
        """:class:`~.pdsspect_image_set.PDSSpectImageSet` : Image set that
        corresponds with the current view
        """

        return self.image_sets[self._view_index]

    @property
    def has_multiple_views(self):
        """:obj:`bool` : True if there are multiple views, False otherwise"""
        return len(self.image_sets) > 1

    @property
    def view_index(self):
        """:obj:`int` : The index of the view to display the ROI data

        If there are not multiple views, view_index is automatically ``-1``.
        """

        if not self.has_multiple_views:
            return -1
        else:
            return self._view_index

    @view_index.setter
    def view_index(self, new_index):
        self._view_index = new_index
        if self._view_index == self.image_set.current_image_index:
            self.image_index = -1
        self.set_data()

    def add_selected_color(self, color):
        """Select a color and inform views to display new color

        Parameters
        ----------
        color : :obj:`str`
            The color to add
        """

        self.selected_colors.append(color)
        self.set_data()

    def remove_selected_color(self, color):
        """Remove a selected color and inform views to not display the color

        Parameters
        ----------
        color : :obj:`str`
            The color to remove
        """

        self.selected_colors.remove(color)
        self.set_data()

    @property
    def unit(self):
        """:obj:`str` : Latex version of
        :attr:`.pdsspect_image_set.PDSSpectImageSet.unit`"""
        index = self.image_set.accepted_units.index(self.image_set.unit)
        return self.latex_units[index]


class ROIPlotController(object):
    """Controller for ROI plot and accompanying widget

    Parameters
    ----------
    model : :class:`ROIPlotModel`
        The model
    view : :class:`QtWidgets.QWidget <PySide.QtGui.QWidget>`
        The view

    Attributes
    ----------
    model : :class:`ROIPlotModel`
        The model
    view : :class:`QtWidgets.QWidget <PySide.QtGui.QWidget>`
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

    def set_view_index(self, index):
        """Set the index of the view

        Parameters
        ----------
        index : :obj:`int`
            Index of the view
        """

        self.model.view_index = index


class ColorCheckBox(QtWidgets.QCheckBox):
    """Custom checkbox that emits its color (:obj:`str`) when toggled

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


class ViewCheckBox(QtWidgets.QCheckBox):
    """Custom checkbox that emits its index (:obj:`int`) when toggled

    Parameters
    ----------
    index : :obj:`int`
        The index of the view

    Attributes
    ----------
    index : :obj:`int`
        The index of the view
    stateChanged : :obj:`QtCore.Signal`
        Signal that emits the box itself when check box changes its state

        Read more about `Signals here
        <http://pyqt.sourceforge.net/Docs/PyQt5/signals_slots.html>`_
    """

    stateChanged = QtCore.Signal(object)

    def __init__(self, index):
        view_number = index + 1
        name = 'view ' + str(view_number)
        super(ViewCheckBox, self).__init__(name)
        self.name = name
        self.view_number = view_number
        self.index = index

    def set_check_state(self):
        self.setChecked(not self.isChecked())
        self.stateChanged.emit(self)

    def nextCheckState(self):
        """Adjust checkbox's toggle & emit checkbox when checkbox is clicked"""
        if not self.isChecked():
            self.set_check_state()


class ROIPlotWidget(QtWidgets.QWidget, PDSSpectImageSetViewBase):
    """Widget to hold the histogram and checkboxs

    Checkboxes are created in :meth:`create_color_checkbox` which is why they
    do not appear in the :meth:`__init__` method.

    Parameters
    ----------
    model : :class:`ROIPlotModel`
        The model

    Attributes
    ----------
    model : :class:`ROIPlotModel`
        The model
    controller : :class:`ROIPlotController`
        The controller
    checkbox_layout : :class:`QtWidgets.QVBoxLayout <PySide.QtGui.QVBoxLayout>`
        Place the checkboxes vertically
    main_layout : :class:`QtWidgets.QGridLayout <PySide.QtGui.QGridLayout>`
        Place in grid layout so histogram stretches while boxes are stationary
    roi_plot : :class:`ROIPlot`
        The plot of ROI data
    save_btn : :class:`QtWidgets.QPushButton <PySide.QtGui.QPushButton>`
        Save the plot as an image
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
        super(ROIPlotWidget, self).__init__()
        self.model = model
        self.model.register(self)
        self.controller = ROIPlotController(model, self)
        self.roi_plot = None
        self._create_roi_plot()
        self.checkbox_layout = QtWidgets.QVBoxLayout()
        for color in self.model.image_set.colors[:-1]:
            self.create_color_checkbox(color)
        self.save_btn = QtWidgets.QPushButton('Save Plot')
        self.save_btn.clicked.connect(self.save_plot)
        self.view_boxes_layout = QtWidgets.QHBoxLayout()
        self.main_layout = QtWidgets.QGridLayout()

        self._set_layout()
        if self.model.has_multiple_views:
            self.add_view()
        else:
            self._register_set_at_index(0)

    def _create_roi_plot(self):
        self.roi_plot = None

    def _register_set_at_index(self, index):
        self.model.image_sets[index].register(self.roi_plot)
        self.model.image_sets[index].register(self)

    def _set_layout(self):
        pass

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

    def add_view(self, index=None):
        """Add a view box to the widget

        Parameters
        ----------
        index : :obj:`int` [Default None]
            The index to add the view to
        """

        if self.view_boxes_layout.count() == 0 and index is None:
            for index, image_set in enumerate(self.model.image_sets):
                self.add_view(index)
            return
        if index is None:
            index = len(self.model.image_sets) - 1
        view_box = ViewCheckBox(index)
        view_box.stateChanged.connect(self.check_view_checkbox)
        self.view_boxes_layout.addWidget(view_box)
        self._register_set_at_index(index)
        box = self.view_boxes_layout.itemAt(self.model._view_index).widget()
        box.setChecked(True)
        self.check_view_checkbox(box)

    def check_view_checkbox(self, view_checkbox):
        """Check the view box at the given index

        Parameters
        ----------
        view_checkbox : :class:`ViewCheckBox`
            The view check box whose state changed
        """

        index = view_checkbox.index
        for item_index in range(self.view_boxes_layout.count()):
            if item_index != index:
                box = self.view_boxes_layout.itemAt(item_index).widget()
                box.setChecked(False)

        if view_checkbox.isChecked():
            self.controller.set_view_index(index)

    def set_data(self):
        pass

    def save_plot(self):
        """Save the plot as an image"""
        save_file, _ = QtWidgets.QFileDialog.getSaveFileName(parent=self)
        if save_file != '':
            self.roi_plot._figure.savefig(
                save_file,
                facecolor='black',
                edgecolor='black',
            )


class ROIPlot(FigureCanvasQTAgg, PDSSpectImageSetViewBase):
    """Plot of the data in each ROI color

    Parameters
    ----------
    model : :class:`ROIPlotModel`
        The model
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model

    Attributes
    ----------
    model : :class:`ROIPlotModel`
        The model
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    """

    def __init__(self, model):
        self.model = model
        self.image_set = model.image_set
        fig = Figure(figsize=(6, 4), dpi=100, facecolor='black')
        fig.subplots_adjust(
            left=0.15,
            right=0.95,
            top=0.95,
            bottom=0.15,
            wspace=0.0,
            hspace=0.0,
        )
        super(ROIPlot, self).__init__(fig)
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
        self.set_data()

    def set_roi_data(self):
        """Set data when ROI is created/destroyed or checkbox is toggled"""
        self.set_data()
