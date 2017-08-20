import os
import sys

import pvl
from qtpy import QtWidgets
import numpy
np = numpy

test_dir = os.path.join('tests', 'mission_data')

if not os.path.isdir(test_dir):
    raise RuntimeError('Do not have test data. Run `get_mission_data`')

FILE_1 = os.path.join(
    test_dir, '2m132591087cfd1800p2977m2f1.img')
FILE_2 = os.path.join(
    test_dir, '2p129641989eth0361p2600r8m1.img')
FILE_3 = os.path.join(
    test_dir, '1p190678905erp64kcp2600l8c1.img')
FILE_4 = os.path.join(
    test_dir, 'h58n3118.img')
FILE_5 = os.path.join(
    test_dir, '1p134482118erp0902p2600r8m1.img')
FILE_6 = os.path.join(
    test_dir, '0047MH0000110010100214C00_DRCL.IMG')
FILE_1_NAME = os.path.basename(FILE_1)
FILE_2_NAME = os.path.basename(FILE_2)
FILE_3_NAME = os.path.basename(FILE_3)
FILE_4_NAME = os.path.basename(FILE_4)
FILE_5_NAME = os.path.basename(FILE_5)
FILE_6_NAME = os.path.basename(FILE_6)

TEST_FILES = [FILE_1, FILE_2, FILE_3, FILE_4, FILE_5]
TEST_FILE_NAMES = [
    FILE_1_NAME, FILE_2_NAME, FILE_3_NAME, FILE_4_NAME, FILE_5_NAME
]

SAMPLE_ROI = os.path.join(
    'tests', 'sample_roi.npz'
)

mastcam_label1 = pvl.PVLModule(
    {
        'INSTRUMENT_NAME': 'MAST CAMERA LEFT',
        'INSTRUMENT_STATE_PARMS': {
            'CENTER_FILTER_WAVELENGTH': pvl._collections.Units(
                value=500,
                units='nm'
            ),
        },
    }
)

mastcam_label2 = pvl.PVLModule(
    {
        'INSTRUMENT_NAME': 'MAST CAMERA LEFT',
        'INSTRUMENT_STATE_PARMS': {
            'FILTER_CENTER_WAVELENGTH': pvl._collections.Units(
                value=500,
                units='nm'
            ),
        },
    }
)


NA_label = pvl.PVLModule(
    {
        'INSTRUMENT_NAME': 'IMAGING SCIENCE SUBSYSTEM NARROW ANGLE',
        'FILTER_NAME': ["BL1", "BL2"],

    }
)

WA_label = pvl.PVLModule(
    {
        'INSTRUMENT_NAME': 'IMAGING SCIENCE SUBSYSTEM WIDE ANGLE',
        'FILTER_NAME': ["CB2", "CL2"],

    }
)

EMPTY_LABEL = pvl.PVLModule(
    {
        'INSTRUMENT_NAME': 'EMPTY',
        'FILTER_NAME': 'NO_FILTER',
        'INSTRUMENT_STATE_PARMS': {'CENTER_FILTER_WAVELENGTH': None},
    }
)


def reset_image_set(image_set):
    image_set._current_image_index = 0
    image_set.current_color_index = 0
    image_set._selection_index = 0
    image_set._zoom = 1.0
    image_set._center = None
    image_set._move_rois = True
    image_set._alpha = 1.0
    image_set._flip_x = False
    image_set._flip_y = False
    image_set._swap_xy = False
    image_set._roi_data = image_set._maskrgb.get_data().astype(float)
    image_set._subsets = []
    image_set._simultaneous_roi = False
    image_set._unit = 'nm'
    for image in image_set.images:
        image.unit = 'nm'


app = QtWidgets.QApplication.instance()
if not app:
    app = QtWidgets.QApplication(sys.argv)
