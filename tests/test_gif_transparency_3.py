from io import BytesIO

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine


def test_resized_gif_keeps_transparent_background():
    src = Image.new("P", (40, 40), 0)
    src.putpalette([255, 0, 0, 0, 0, 255] + [0] * 762)
    src.paste(1, (10, 10, 30, 30))
    src.info["transparency"] = 0
    buffer = BytesIO()
    src.save(buffer, "GIF", transparency=0)

    cfg = Config(PILLOW_PRESERVE_INDEXED_MODE=True)
    engine = Engine(Context(config=cfg))
    engine.load(buffer.getvalue(), ".gif")
    engine.resize(80, 80)

    out = Image.open(BytesIO(engine.read(".gif")))
    assert "transparency" in out.info
    assert out.convert("RGBA").getchannel("A").getextrema()[0] == 0
