import pytest

from pdsspect.pds_image_view_canvas import PDSImageViewCanvas, ImageViewCanvas


def test_add_subview():
    view = PDSImageViewCanvas()
    subview1 = PDSImageViewCanvas()
    view.add_subview(subview1)
    assert subview1 in view._subviews
    subview2 = ImageViewCanvas()
    view.add_subview(subview2)
    assert subview2 in view._subviews

    with pytest.raises(TypeError):
        view.add_subview('foo')
