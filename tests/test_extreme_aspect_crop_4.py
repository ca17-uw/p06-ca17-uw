from unittest import mock

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine
from thumbor.point import FocalPoint
from thumbor.transformer import Transformer


def test_auto_crop_keeps_at_least_one_pixel_for_extreme_aspect():
    context = Context(config=Config())
    engine = Engine(context)
    engine.image = Image.new("RGBA", (1, 1), (255, 0, 0, 255))

    context.request = mock.Mock(
        engine=engine,
        width=50,
        height=25,
        fit_in=False,
        stretch=False,
        focal_points=[],
        should_crop=False,
        halign="center",
        valign="middle",
    )

    transformer = Transformer(context)
    transformer.engine = engine
    transformer.target_width = 50.0
    transformer.target_height = 25.0
    transformer.focal_points = [
        FocalPoint.from_alignment("center", "middle", 1, 1)
    ]

    transformer.auto_crop()

    assert engine.size[0] >= 1
    assert engine.size[1] >= 1


def test_fit_in_keeps_at_least_one_pixel_for_tiny_box():
    context = Context(config=Config())
    engine = Engine(context)
    engine.image = Image.new("RGBA", (940, 2), (255, 0, 0, 255))

    context.request = mock.Mock(
        engine=engine,
        width=1,
        height=1,
        adaptive=False,
        full=False,
        fit_in=True,
    )

    transformer = Transformer(context)
    transformer.engine = engine
    transformer.target_width = 1.0
    transformer.target_height = 1.0

    transformer.fit_in_resize()

    assert engine.size == (1, 1)
