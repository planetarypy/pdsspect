===============================================================
pdsspect - A Python PDS Image Region of Interest Selection Tool
===============================================================

**NOTE:** This is Alpha quality software that is being actively developed, use
at your own risk.  This software is not produced by NASA.

* Free software: BSD license
* Documentation: https://pdsspect.readthedocs.org.

Features
--------

* NASA PDS Image Viewer

**NOTE:** This is alpha quality software.  It lacks many features and lacks
support for many PDS image types.  This software is not produced by NASA.

Install
-------

On OS X you must first install the Qt UI toolkit using Homebrew
(http://brew.sh/).  After installing Homebrew, issue the following command::

    brew install qt

Create a new virtual environment, install the `pdsspect` module with pip,
and setup the PySide environment. You must install either PySide, PyQt5, or
PyQt4 as well (recommend PyQt5)::

    mkvirtualenv pdsspect
    pip install pdsspect
    pip install PyQt5

Now you should be able to run the `pdsspect` program.

This works on Linux as well (Ubuntu 14.04).  Instructions coming soon.
Installing the proper Qt dev package and running `pyside_postinstall.py`
in a similar fashion should work.
