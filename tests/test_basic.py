from . import *  # Import Test File Paths from __init__

from pdsspect.basic import BasicController, Basic
from pdsspect.pdsspect_image_set import PDSSpectImageSet
from pdsspect.pds_image_view_canvas import PDSImageViewCanvas


class TestBasicController(object):
    image_set = PDSSpectImageSet(TEST_FILES)
    controller = BasicController(image_set, None)

    def test_change_current_image_index(self):
        assert self.image_set.current_image_index == 0
        self.controller.change_current_image_index(2)
        assert self.image_set.current_image_index == 2


class TestBasic(object):
    image_set = PDSSpectImageSet(TEST_FILES)
    view_canvas = PDSImageViewCanvas()
    view_canvas.set_image(image_set.current_image)
    basic = Basic(image_set, view_canvas)

    def test_change_image(self):
        original_cuts = self.basic.histogram.cuts
        new_cuts = original_cuts[0] + 10, original_cuts[1] + 20
        first_image = self.image_set.current_image
        self.basic.histogram._cut_low = new_cuts[0]
        self.basic.histogram._cut_high = new_cuts[1]
        self.basic.change_image(1)
        assert self.image_set.current_image_index == 1
        assert self.image_set.current_image is not first_image
        self.basic.change_image(0)
        assert self.image_set.current_image_index == 0
        assert self.image_set.current_image is first_image
        assert self.image_set.current_image.cuts == new_cuts
