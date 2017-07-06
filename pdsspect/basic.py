from functools import wraps

from qtpy import QtWidgets

from .histogram import HistogramWidget, HistogramModel, HistogramController
from .pdsspect_image_set import PDSSpectImageSetViewBase


class BasicHistogramModel(HistogramModel):
    """Model for the hhistograms in the Basic Widgets

    Attributes
    ---------
    connected_models : :obj:`list`
        Other :class:`BasicHistogramModel` for other histograms
    """

    def __init__(self, *args, **kwargs):
        super(BasicHistogramModel, self).__init__(*args, **kwargs)
        self.connected_models = []

    def check_model_type(func):
        @wraps(func)
        def wrapper(self, model):
            if not isinstance(model, BasicHistogramModel):
                raise ValueError("Model must be a BasicHistogramModel object")
            return func(self, model)
        return wrapper

    @check_model_type
    def connect_model(self, model):
        """Connect another model to this model

        Attributes
        ----------
        model : :class:`BasicHistogramModel`
            Connect the model to current model

        Raises
        ------
        ValueError
            When :attr:`model` is not :class:`BasicHistogramModel`
        """

        if model not in self.connected_models:
            self.connected_models.append(model)
            model.cuts = self.cuts

    @check_model_type
    def disconnect_model(self, model):
        """Disconnect another model from this model

        Attributes
        ----------
        model : :class:`BasicHistogramModel`
            Disconnect the model from current model

        Raises
        ------
        ValueError
            When :attr:`model` is not :class:`BasicHistogramModel`
        """

        if model in self.connected_models:
            self.connected_models.remove(model)

    def disconnect_from_all_models(self):
        """Disconnect all models from this model"""
        self.connected_models = []


class BasicHistogramController(HistogramController):
    """Controller for histogram views

    Parameters
    ----------
    model : :class:`BasicHistogramModel`
        histogram model
    view : :class:`object`
        View with :class:`BasicHistogramModel` as its model

    Attributes
    ----------
    model : :class:`BasicHistogramModel`
        histogram model
    view : :class:`object`
        View with :class:`BasicHistogramModel` as its model
    """

    def set_cut_low(self, cut_low):
        """Set the low cut level to a new value

        Parameters
        ----------
        cut_low : :obj:`float`
            New low cut value
        """

        super(BasicHistogramController, self).set_cut_low(cut_low)
        for model in self.model.connected_models:
            model.cut_low = cut_low

    def set_cut_high(self, cut_high):
        """Set the high cut level to a new value

        Parameters
        ----------
        cut_high : :obj:`float`
            New high cut value
        """

        super(BasicHistogramController, self).set_cut_high(cut_high)
        for model in self.model.connected_models:
            model.cut_high = cut_high

    def set_cuts(self, cut_low, cut_high):
        """Set both the low and high cut levels

        Parameters
        ----------
        cut_low : :obj:`float`
            New low cut value
        cut_high : :obj:`float`
            New high cut value
        """

        super(BasicHistogramController, self).set_cuts(cut_low, cut_high)
        for model in self.model.connected_models:
            model.cuts = cut_low, cut_high

    def restore(self):
        """Restore the histogram"""
        super(BasicHistogramController, self).restore()
        for model in self.model.connected_models:
            model.restore()


class BasicHistogramWidget(HistogramWidget):
    """:class:`~.pdsspect.histogram.HistogramWidget` in a different layout"""

    def __init__(self, *args, **kwargs):
        super(BasicHistogramWidget, self).__init__(*args, **kwargs)
        self.controller = BasicHistogramController(self.model, self)
        self.histogram.controller = BasicHistogramController(
            self.model, self.histogram
        )

    def _create_layout(self):
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self._cut_low_label, 0, 1)
        layout.addWidget(self._cut_low_box, 0, 2)
        layout.addWidget(self._cut_high_label, 1, 1)
        layout.addWidget(self._cut_high_box, 1, 2)
        layout.addWidget(self._bins_label, 2, 1)
        layout.addWidget(self._bins_box, 2, 2)
        layout.addWidget(self.histogram, 0, 0, 3, 1)

        return layout


class BasicController(object):
    """Controller for :class:`Basic` window

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view : :class:`Basic`
        View to control

    Attributes
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view : :class:`Basic`
        View to control
    """

    def __init__(self, image_set, view):
        self.image_set = image_set
        self.view = view

    def change_current_image_index(self, new_index):
        """Change the current image index to a new index

        Parameters
        ----------
        new_index : :obj:`int`
            The new index for
            :class:`~.pdsspect_image_set.PDSSpectImageSetViewBase.images` to
            determine the current image
        """

        self.image_set.current_image_index = new_index


class BasicWidget(QtWidgets.QWidget):
    """Widget to hold each basic window

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view_canvas : :class:`~.pds_image_view_canvas.PDSImageViewCanvas`
        view canvas

    Attributes
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    basics : :obj:`list` of :class:`Basic`
        :class:`Basic` in the widget
    """

    def __init__(self, image_set, view_canvas):
        super(BasicWidget, self).__init__()
        self.image_set = image_set
        self.basics = []
        self.main_layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.main_layout)
        self.setWindowTitle('Basic')
        self.add_basic(image_set, view_canvas)

    def add_basic(self, image_set, view_canvas):
        """Add a :class:`Basic` to the widget

        Parameters
        ----------
        image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
            pdsspect model
        view_canvas : :class:`~.pds_image_view_canvas.PDSImageViewCanvas`
            view canvas
        """

        basic = Basic(image_set, view_canvas, self)
        self.basics.append(basic)
        self.main_layout.addWidget(basic)
        self.connect_model(basic)

    def connect_model(self, basic):
        """Connect the models of other basic windows to the given window

        The models are connected when they have the same current image

        Parameters
        ----------
        basic : :class:`Basic`
            Basic window connect/disconnect its histogram model to others
        """

        other_basics = list(self.basics)
        other_basics.remove(basic)
        for other_basic in other_basics:
            image = other_basic.image_set.current_image
            if image == basic.image_set.current_image:
                other_basic.histogram.connect_model(basic.histogram)
                basic.histogram.connect_model(other_basic.histogram)
            else:
                other_basic.histogram.disconnect_model(basic.histogram)
                basic.histogram.disconnect_model(other_basic.histogram)


class Basic(QtWidgets.QWidget, PDSSpectImageSetViewBase):
    """Window to apply cut levels and choose the current image

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view_canvas : :class:`~.pds_image_view_canvas.PDSImageViewCanvas`
        Canvas to view the image

    Attributes
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model
    view_canvas : :class:`~.pds_image_view_canvas.PDSImageViewCanvas`
        Canvas to view the image
    controller : :class:`BasicController`
        Controller for view
    image_menu : :class:`QtWidgets.QComboBox <PySide.QtGui.QComboBox>`
        Drop down menu to pick the current image
    histogram : :class:`~.histogram.HistogramModel`
        Model for the :attr:`histogram_widget`
    histogram_widget : :class:`BasicHistogramWidget`
        The histogram widget to adjust the cut levels
    layout : :class:`QtWidgets.QVBoxLayout <PySide.QtGui.QVBoxLayout>`
        The main layout
    """

    def __init__(self, image_set, view_canvas, basic_widget):
        super(Basic, self).__init__(basic_widget)

        self.image_set = image_set
        self.image_set.register(self)
        self.basic_widget = basic_widget
        self.controller = BasicController(image_set, self)
        self.view_canvas = view_canvas

        self.image_menu = QtWidgets.QComboBox()
        for image in self.image_set.images:
            self.image_menu.addItem(image.image_name)
        self.image_menu.setCurrentIndex(image_set.current_image_index)
        self.image_menu.currentIndexChanged.connect(self.change_image)
        self.histogram = BasicHistogramModel(self.view_canvas, bins=100)
        self.histogram_widget = BasicHistogramWidget(self.histogram, self)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.image_menu)
        self.layout.addWidget(self.histogram_widget)

        self.setLayout(self.layout)
        self.histogram.set_data()

    def change_image(self, new_index):
        """Change the image when new image selected in :attr:`image_menu`

        Parameters
        ----------
        new_index : :obj:`int`
            The new index to determine the current image
        """

        self.image_set.current_image.cuts = self.histogram.cuts
        self.controller.change_current_image_index(new_index)
        self.basic_widget.connect_model(self)

    def set_image(self):
        """When the image is set, adjust the histogram"""
        self.histogram.set_data()
        self.histogram.restore()
