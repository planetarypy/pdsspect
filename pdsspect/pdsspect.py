import os
import sys
import argparse
from glob import glob

from qtpy import QtWidgets

from . import app
from .basic import Basic
from .selection import Selection
from .transforms import Transforms
from .pdsspect_view import PDSSPectView
from .pdsspect_image_set import PDSSPectImageSet, PDSSpectImageSetViewBase


class PDSSpect(QtWidgets.QMainWindow, PDSSpectImageSetViewBase):

    def __init__(self, image_set):
        super(PDSSpect, self).__init__()
        self.image_set = image_set
        self.image_set.register(self)

        self.pdsspect_view = PDSSPectView(image_set)
        self.pan_view = self.pdsspect_view.pan_view

        self.selection_btn = QtWidgets.QPushButton("Selection")
        self.selection_btn.clicked.connect(self.open_selection)
        self.selection_window = None

        self.basic_btn = QtWidgets.QPushButton("Basic")
        self.basic_btn.clicked.connect(self.open_basic)
        self.basic_window = None

        self.transforms_btn = QtWidgets.QPushButton("Transforms")
        self.transforms_btn.clicked.connect(self.open_transforms)
        self.transforms_window = None

        self.quit_btn = QtWidgets.QPushButton("Quit")
        self.quit_btn.clicked.connect(self.quit)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.selection_btn)
        self.button_layout.addWidget(self.basic_btn)
        self.button_layout.addWidget(self.transforms_btn)
        self.button_layout.addWidget(self.quit_btn)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.pdsspect_view)
        self.main_layout.addLayout(self.button_layout)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(self.main_layout)
        self.setCentralWidget(central_widget)
        self.open_basic()

    def open_selection(self):
        if not self.selection_window:
            self.selection_window = Selection(self.image_set, self)
        self.selection_window.show()

    def open_basic(self):
        if not self.basic_window:
            self.basic_window = Basic(
                self.image_set,
                self.pdsspect_view.view_canvas
            )
        self.basic_window.show()

    def open_transforms(self):
        if not self.transforms_window:
            self.transforms_window = Transforms(
                self.image_set,
                self.pdsspect_view.view_canvas
            )
        self.transforms_window.show()

    def quit(self, *args):
        self.pdsspect_view.close()
        self.pan_view.close()
        if self.selection_window:
            self.selection_window.close()
        if self.basic_window:
            self.basic_window.close()
        if self.transforms_window:
            self.transforms_window.close()
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

    >>> from pdsview.pdsview import pdsview
    >>> pdsspect()
    Displays all of the images from current directory
    >>> pdsspect('path/to/different/directory')
    Displays all of the images in the different directory
    >>> pdsspect ('1p*img')
    Displays all of the images that follow the glob pattern
    >>> pdsspect ('a1.img, b*.img, example/path/x*img')
    You can display multiple images, globs, and paths in one window by
    separating each item by a command
    >>> pdsspect (['a1.img, b3.img, c1.img, d*img'])
    You can also pass in a list of files/globs
    """
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

    image_set = PDSSPectImageSet(files)
    window = PDSSpect(image_set)
    window.resize(500, 500)
    window.show()
    window.pan_view.resize(400, 400)
    window.basic_window.resize(450, 300)
    spect_pos = window.pos()
    window.pan_view.move(spect_pos.x(), spect_pos.y() - 500)
    window.pan_view.show()
    window.basic_window.move(spect_pos.x() + 500, spect_pos.y())
    window.pdsspect_view.view_canvas.zoom_fit()
    window.pan_view.view_canvas.zoom_fit()
    app.setActiveWindow(window)
    app.setActiveWindow(window.pan_view)
    sys.exit(app.exec_())


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
