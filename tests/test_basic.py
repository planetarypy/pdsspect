from . import TEST_FILES
import pytest

from pdsspect.basic import (
    BasicController,
    Basic,
    BasicHistogramModel,
    BasicHistogramController,
    BasicWidget,
)
from pdsspect.pdsspect_image_set import PDSSpectImageSet, SubPDSSpectImageSet
from pdsspect.pds_image_view_canvas import PDSImageViewCanvas


class TestBasicHistogramModel(object):
    image_view = PDSImageViewCanvas()

    @pytest.fixture
    def model(self):
        return BasicHistogramModel(self.image_view)

    def test_connect_model(self, model):
        connect_model = BasicHistogramModel(self.image_view)
        model.cuts = (24, 42)
        assert model.connected_models == []
        model.connect_model(connect_model)
        assert model.connected_models == [connect_model]
        assert connect_model.cuts == (24, 42)

    def test_disconnect_model(self, model):
        connect_model = BasicHistogramModel(self.image_view)
        model.connected_models == [connect_model]
        model.disconnect_model(connect_model)
        assert model.connected_models == []

    def test_disconnect_from_all_models(self, model):
        connect_model1 = BasicHistogramModel(self.image_view)
        connect_model2 = BasicHistogramModel(self.image_view)
        model.connected_models == [connect_model1, connect_model2]
        model.disconnect_from_all_models()
        assert model.connected_models == []


class TestBasicHistogramController(object):
    image_view = PDSImageViewCanvas()
    model = BasicHistogramModel(image_view)
    connect_model = BasicHistogramModel(image_view)
    model.connected_models = [connect_model]

    @pytest.fixture
    def controller(self):
        self.image_view = PDSImageViewCanvas()
        self.model = BasicHistogramModel(self.image_view)
        self.connect_model = BasicHistogramModel(self.image_view)
        self.model.connected_models = [self.connect_model]
        return BasicHistogramController(self.model, None)

    def test_set_cut_low(self, controller):
        assert self.model._cut_low is None
        assert self.connect_model._cut_low is None
        controller.set_cut_low(24)
        assert self.model._cut_low == 24
        assert self.connect_model._cut_low == 24

    def test_set_cut_high(self, controller):
        assert self.model._cut_high is None
        assert self.connect_model._cut_high is None
        controller.set_cut_high(42)
        assert self.model._cut_high == 42
        assert self.connect_model._cut_high == 42

    def test_set_cuts(self, controller):
        assert self.model.cuts == (0, 0)
        assert self.connect_model.cuts == (0, 0)
        controller.set_cuts(24, 42)
        assert self.model.cuts == (24, 42)
        assert self.connect_model.cuts == (24, 42)


class TestBasicController(object):
    image_set = PDSSpectImageSet(TEST_FILES)
    controller = BasicController(image_set, None)

    def test_change_current_image_index(self):
        assert self.image_set.current_image_index == 0
        self.controller.change_current_image_index(2)
        assert self.image_set.current_image_index == 2


class TestBasicWidget(object):
    image_set = PDSSpectImageSet(TEST_FILES)
    image_view = PDSImageViewCanvas()
    image_view.set_image(image_set.images[0])

    @pytest.fixture
    def basic_widget(self):
        self.image_set = PDSSpectImageSet(TEST_FILES)
        self.image_view = PDSImageViewCanvas()
        self.image_view.set_image(self.image_set.images[0])
        return BasicWidget(self.image_set, self.image_view)

    def test_init(self, basic_widget):
        assert basic_widget.image_set == self.image_set
        assert len(basic_widget.basics) == 1
        assert basic_widget.main_layout.count() == 1
        basic = basic_widget.main_layout.itemAt(0).widget()
        assert basic == basic_widget.basics[0]

    def test_add_basic(self, basic_widget):
        basic_widget.add_basic(self.image_set, self.image_view)
        assert len(basic_widget.basics) == 2
        assert basic_widget.main_layout.count() == 2
        basic1 = basic_widget.main_layout.itemAt(0).widget()
        basic2 = basic_widget.main_layout.itemAt(1).widget()
        assert basic1 == basic_widget.basics[0]
        assert basic2 == basic_widget.basics[1]

    def test_connect_model(self, basic_widget):
        image_set = self.image_set
        basic = basic_widget.basics[0]
        subset1 = SubPDSSpectImageSet(self.image_set)
        basic1 = Basic(subset1, self.image_view, basic_widget)
        basic_widget.basics.append(basic1)
        assert image_set.current_image_index == subset1.current_image_index
        basic_widget.connect_model(basic1)
        assert basic1.histogram.connected_models == [basic.histogram]
        assert basic.histogram.connected_models == [basic1.histogram]
        subset2 = SubPDSSpectImageSet(self.image_set)
        basic2 = Basic(subset2, self.image_view, basic_widget)
        basic_widget.basics.append(basic2)
        subset2.current_image_index = 1
        assert image_set.current_image_index != subset2.current_image_index
        assert subset1.current_image_index != subset2.current_image_index
        basic_widget.connect_model(basic2)
        assert basic1.histogram.connected_models == [basic.histogram]
        assert basic.histogram.connected_models == [basic1.histogram]
        assert basic2.histogram.connected_models == []
        subset1.current_image_index = 2
        assert image_set.current_image_index != subset1.current_image_index
        assert image_set.current_image_index != subset2.current_image_index
        assert subset1.current_image_index != subset2.current_image_index
        basic_widget.connect_model(basic1)
        assert basic1.histogram.connected_models == []
        assert basic.histogram.connected_models == []
        assert basic2.histogram.connected_models == []


class TestBasic(object):
    image_set = PDSSpectImageSet(TEST_FILES)
    view_canvas = PDSImageViewCanvas()
    view_canvas.set_image(image_set.current_image)
    basic_widget = BasicWidget(image_set, view_canvas)

    @pytest.fixture
    def basic(self):
        self.image_set = PDSSpectImageSet(TEST_FILES)
        self.view_canvas = PDSImageViewCanvas()
        self.view_canvas.set_image(self.image_set.current_image)
        self.basic_widget = BasicWidget(self.image_set, self.view_canvas)
        return self.basic_widget.basics[0]

    def test_change_image1(self, basic):
        original_cuts = basic.histogram.cuts
        new_cuts = original_cuts[0] + 10, original_cuts[1] + 20
        first_image = self.image_set.current_image
        basic.histogram._cut_low = new_cuts[0]
        basic.histogram._cut_high = new_cuts[1]
        basic.change_image(1)
        assert self.image_set.current_image_index == 1
        assert self.image_set.current_image is not first_image
        basic.change_image(0)
        assert self.image_set.current_image_index == 0
        assert self.image_set.current_image is first_image
        assert self.image_set.current_image.cuts == new_cuts

    def test_change_image2(self, basic):
        subset = SubPDSSpectImageSet(self.image_set)
        basic.change_image(1)
        self.basic_widget.add_basic(subset, self.view_canvas)
        basic2 = self.basic_widget.basics[1]
        assert basic.histogram.connected_models == []
        assert basic2.histogram.connected_models == []
        basic.change_image(0)
        assert basic.histogram.connected_models == [basic2.histogram]
        assert basic2.histogram.connected_models == [basic.histogram]
