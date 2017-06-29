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

    def __init__(self, image_set):
        self._views = []
        self.image_set = image_set
        self.selected_colors = []

    def register(self, view):
        if view not in self._views:
            self._views.append(view)

    def unregister(self, view):
        if view in self._views:
            self._views.remove(view)

    def add_selected_color(self, color):
        self.selected_colors.append(color)
        for view in self._views:
            view.set_data()

    def remove_selected_color(self, color):
        self.selected_colors.remove(color)
        for view in self._views:
            view.set_data()

    def data_in_roi_with_color(self, color):
        rows, cols = self.image_set.get_coordinates_of_color(color)
        data = self.image_set.current_image.data[rows, cols]
        return data

    @property
    def xlim(self):
        data = self.image_set.current_image.data
        xlim = [data.min(), data.max()]
        return xlim


class ROIHistogramController(object):

    def __init__(self, model, view):
        self.model = model
        self.view = view

    def color_state_changed(self, color):
        if color not in self.model.selected_colors:
            self.select_color(color)
        else:
            self.remove_color(color)

    def select_color(self, color):
        self.model.add_selected_color(color)

    def remove_color(self, color):
        self.model.remove_selected_color(color)


class ColorCheckBox(QtWidgets.QCheckBox):

    stateChanged = QtCore.Signal(str)

    def __init__(self, color):
        super(ColorCheckBox, self).__init__(color)
        self.color = color

    def nextCheckState(self):
        self.setChecked(not self.isChecked())
        self.stateChanged.emit(self.color)


class ROIHistogramWidget(QtWidgets.QWidget):

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
        name = color + '_checkbox'
        color_checkbox = ColorCheckBox(color)
        color_checkbox.stateChanged.connect(self.check_color)
        setattr(self, name, color_checkbox)
        self.checkbox_layout.addWidget(color_checkbox)

    def check_color(self, checkbox_color):
        self.controller.color_state_changed(checkbox_color)

    def set_data(self):
        pass


class ROIHistogram(FigureCanvasQTAgg, PDSSpectImageSetViewBase):

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
        self.set_data()

    def set_image(self):
        self.set_data()
