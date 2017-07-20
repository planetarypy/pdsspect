import os
import sys
import argparse
from glob import glob

from qtpy import QtWidgets, QtCore

from .set_wavelength import SetWavelengthWidget, SetWavelengthModel
from .basic import BasicWidget
from .pan_view import PanViewWidget
from .selection import Selection
from .transforms import Transforms
from .pdsspect_view import PDSSpectViewWidget
from .roi_line_plot import ROILinePlotWidget, ROILinePlotModel
from .roi_histogram import ROIHistogramWidget, ROIHistogramModel
from .pdsspect_image_set import PDSSpectImageSet, PDSSpectImageSetViewBase


class PDSSpect(QtWidgets.QMainWindow, PDSSpectImageSetViewBase):
    """Main Window of pdsspect

    Parameters
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        pdsspect model

    Attributes
    ----------
    image_set : :class:`~.pdsspect_image_set.PDSSpectImageSet`
        The model for each view
    pdsspect_view : :class:`~.pdsspect_view.PDSSpectViewWidget`
        The main viewer for panning
    pan_view : :class:`~.pdsspect.pan_view.PanView`
        The view in which the user makes ROI selections
    selection_btn : :class:`QtWidgets.QPushButton <PySide.QtGui.QPushButton>`
        Button to open the selections window
    selection_window : :class:`~.selection.Selection`
        The selection window to adjust ROI, import ROIs, and export ROIs
    basic_btn : :class:`QtWidgets.QPushButton <PySide.QtGui.QPushButton>`
        Button to open the basic window
    basic_window : :class:`~.basic.BasicWidget`
        Window to adjust cut levels and change images
    transforms_btn : :class:`QtWidgets.QPushButton <PySide.QtGui.QPushButton>`
        Open Transforms window
    transforms_window : :class:`~.transforms.Transforms`
        Window to flip x axis, flip y axis, or switch x and y axis
    roi_histogram_btn : :class:`QPushButton <PySide.QtGui.QPushButton>`
        Open ROI Histogram window
    roi_histogram_window : :class:`~.roi_histogram.ROIHistogramWidget`
        The ROI Histogram Window
    roi_line_plot_btn : :class:`QPushButton <PySide.QtGui.QPushButton>`
        Open ROI Line Plot window
    roi_line_plot_window : :class:`~.roi_line_plot.ROILinePlotWidget`
        The ROI Line Plot Window
    add_window_btn : :class:`QPushButton <PySide.QtGui.QPushButton>`
        Add another window
    quit_btn : :class:`QtWidgets.QPushButton <PySide.QtGui.QPushButton>`
        Quit
    button_layout1 : :class:`QtWidgets.QHBoxLayout <PySide.QtGui.QHBoxLayout>`
        Layout for the buttons. If you want to re-adjust where the buttons
        go, override this attribute
    button_layout2 : :class:`QtWidgets.QHBoxLayout <PySide.QtGui.QHBoxLayout>`
        Layout for the buttons. If you want to re-adjust where the buttons
        go, override this attribute
    main_layout : :class:`QtWidgets.QVBoxLayout <PySide.QtGui.QVBoxLayout>`
        Place the image viewer over the buttons. Overide this attribute if
        changing overall layout
    """

    def __init__(self, image_set):
        super(PDSSpect, self).__init__()
        self.image_set = image_set
        self.image_set.register(self)

        self.pdsspect_view = PDSSpectViewWidget(image_set)
        self.pan_view = PanViewWidget(
            self.pdsspect_view.spect_views[0].pan_view,
            self
        )

        self.selection_btn = QtWidgets.QPushButton('Selection')
        self.selection_btn.clicked.connect(self.open_selection)
        self.selection_window = None

        self.basic_btn = QtWidgets.QPushButton('Basic')
        self.basic_btn.clicked.connect(self.open_basic)
        self.basic_window = None

        self.transforms_btn = QtWidgets.QPushButton('Transforms')
        self.transforms_btn.clicked.connect(self.open_transforms)
        self.transforms_window = None

        self.roi_histogram_btn = QtWidgets.QPushButton('ROI Histogram')
        self.roi_histogram_btn.clicked.connect(self.open_roi_histogram)
        self.roi_histogram_window = None

        self.roi_line_plot_btn = QtWidgets.QPushButton('ROI Line Plot')
        self.roi_line_plot_btn.clicked.connect(self.open_roi_line_plot)
        self.roi_line_plot_window = None

        self.add_window_btn = QtWidgets.QPushButton('Add Window')
        self.add_window_btn.clicked.connect(self.add_window)

        self.set_wavelengths_btn = QtWidgets.QPushButton('Set Wavelengths')
        self.set_wavelengths_btn.clicked.connect(self.open_set_wavelengths)
        self.set_wavelength_window = None

        self.quit_btn = QtWidgets.QPushButton('Quit')
        self.quit_btn.clicked.connect(self.quit)

        self.button_layout1 = QtWidgets.QHBoxLayout()
        self.button_layout2 = QtWidgets.QHBoxLayout()
        self.button_layout1.addWidget(self.selection_btn)
        self.button_layout1.addWidget(self.basic_btn)
        self.button_layout1.addWidget(self.transforms_btn)
        self.button_layout1.addWidget(self.roi_histogram_btn)
        self.button_layout2.addWidget(self.roi_line_plot_btn)
        self.button_layout2.addWidget(self.add_window_btn)
        self.button_layout2.addWidget(self.set_wavelengths_btn)
        self.button_layout2.addWidget(self.quit_btn)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.pdsspect_view)
        self.main_layout.addLayout(self.button_layout1)
        self.main_layout.addLayout(self.button_layout2)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)
        self.open_basic()

    @property
    def image_sets(self):
        """:obj:`list` : All the image sets, including the current one"""
        return [self.image_set] + self.image_set.subsets

    def open_selection(self):
        """Open the Selection Window"""
        if not self.selection_window:
            self.selection_window = Selection(self.image_set, self)
        self.selection_window.show()

    def open_basic(self):
        """Open the Basic Window"""
        if not self.basic_window:
            self.basic_window = BasicWidget(
                self.image_set,
                self.pdsspect_view.spect_views[0].view_canvas
            )
        self.basic_window.show()

    def open_transforms(self):
        """Open the Transforms Window"""
        if not self.transforms_window:
            self.transforms_window = Transforms(
                self.image_set,
                self.pdsspect_view.spect_views[0].view_canvas
            )
        self.transforms_window.show()

    def open_roi_histogram(self):
        """Open the ROI Histogram Window"""
        if not self.roi_histogram_window:
            roi_histogram_model = ROIHistogramModel(self.image_set)
            self.roi_histogram_window = ROIHistogramWidget(roi_histogram_model)
        self.roi_histogram_window.show()

    def open_roi_line_plot(self):
        """Open the ROI Line Plot Window"""
        if not self.roi_line_plot_window:
            roi_line_plot_model = ROILinePlotModel(self.image_set)
            self.roi_line_plot_window = ROILinePlotWidget(roi_line_plot_model)
        self.roi_line_plot_window.show()

    def add_window(self):
        """Add another window to make more ROIs"""
        subset = self.image_set.create_subset()
        spect_view = self.pdsspect_view.create_spect_view(subset)
        self.pan_view.add_pan(spect_view.pan_view)
        if self.basic_window:
            self.basic_window.add_basic(subset, spect_view.view_canvas)
        if self.roi_histogram_window:
            self.roi_histogram_window.add_view()
        if self.roi_line_plot_window:
            self.roi_line_plot_window.add_view()
        spect_view.show()
        spect_view.pan_view.show()
        spect_view.pan_view.resizeEvent(None)
        spect_view.resizeEvent(None)

    def open_set_wavelengths(self):
        if not self.set_wavelength_window:
            set_wavelength_model = SetWavelengthModel(self.image_set)
            self.set_wavelength_window = SetWavelengthWidget(
                set_wavelength_model
            )
        self.set_wavelength_window.show()

    def quit(self, *args):
        """Quit pdsspect"""
        self.pdsspect_view.close()
        self.pan_view.close()
        if self.selection_window:
            self.selection_window.close()
        if self.basic_window:
            self.basic_window.close()
        if self.transforms_window:
            self.transforms_window.close()
        if self.roi_histogram_window:
            self.roi_histogram_window.close()
        if self.roi_line_plot_window:
            self.roi_line_plot_window.close()
        if self.set_wavelength_window:
            self.set_wavelength_window.close()
        self.close()


def pdsspect(inlist=None):
    """Run pdsview from python shell or command line with arguments

    Parameters
    ----------
    inlist : list
        A list of file names/paths to display in the pdsview

    Examples
    --------

    From the command line:

    To view all images from current directory

    pdsspect

    To view all images in a different directory

    pdsspect path/to/different/directory/

    This is the same as:

    pdsspect path/to/different/directory/*

    To view a specific image or types of images

    pdsspect 1p*img

    To view images from multiple directories:

    pdsspect * path/to/other/directory/

    From the (i)python command line:

    >>> from pdsspect.pdsspect import pdsspect
    >>> pdsspect()
    Displays all of the images from current directory
    >>> pdsspect('path/to/different/directory')
    Displays all of the images in the different directory
    >>> pdsspect ('1p*img')
    Displays all of the images that follow the glob pattern
    >>> pdsspect('a1.img, b*.img, example/path/x*img')
    You can display multiple images, globs, and paths in one window by
    separating each item by a command
    >>> pdsspect(['a1.img, b3.img, c1.img, d*img'])
    You can also pass in a list of files/globs
    pdsspect returns a dictionary of the ROIs:
    >>> rois = pdsspect(['a1.img, b3.img, c1.img, d*img'])
    >>> rois['red'][:2, :2]
    array(
        [
            [False, False],
            [False, False]
        ],
        dtype=bool
    )
    """

    app = QtWidgets.QApplication(sys.argv)
    files = []
    if isinstance(inlist, list):
        if inlist:
            for item in inlist:
                files += arg_parser(item)
        else:
            files = glob('*')
    elif isinstance(inlist, str):
        names = inlist.split(',')
        for name in names:
            files = files + arg_parser(name.strip())
    elif inlist is None:
        files = glob('*')

    image_set = PDSSpectImageSet(files)
    window = PDSSpect(image_set)
    geometry = app.desktop().screenGeometry()
    geo_center = geometry.center()
    width = geometry.width()
    height = geometry.height()
    width_to_height = width / height
    window_width = width * .25
    window_height = window_width / width_to_height
    center = QtCore.QPoint(
        geo_center.x() - window_width * .7, geo_center.y() - window_height * .2
    )
    window.resize(window_width, window_height)
    window.move(center)
    window.show()
    window.pan_view.show()
    pan_width = width * .2
    pan_height = pan_width / width_to_height
    window.pan_view.resize(pan_width, pan_height)
    window.basic_window.resize(pan_width, pan_height)
    window.pan_view.move(center.x(), center.y() - window_height * .9)
    window.basic_window.move(center.x() + window_width + 5, center.y())
    app.setActiveWindow(window)
    app.setActiveWindow(window.pan_view)
    try:
        sys.exit(app.exec_())
    except SystemExit:
        pass
    return window.image_set.get_rois_masks_to_export()


def arg_parser(args):
    if os.path.isdir(args):
        files = glob(os.path.join('%s' % (args), '*'))
    elif args:
        files = glob(args)
    else:
        files = glob('*')
    return files


def cli():
    """Give pdsview ability to run from command line"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'file', nargs='*',
        help="Input filename or glob for files with certain extensions"
    )
    args = parser.parse_args()
    pdsspect(args.file)
