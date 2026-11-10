# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

import unittest

from thumbor.ext.filters import _round_corner

W, H, R = 200, 200, 60
SRC = (40, 120, 200)
FILL = (255, 255, 255)


def _solid_buffer():
    return bytes(SRC + (255,)) * (W * H)


def _render(transparent):
    out = _round_corner.apply(
        1,
        "RGBA",
        R,
        R,
        FILL[0],
        FILL[1],
        FILL[2],
        W,
        H,
        _solid_buffer(),
        transparent,
    )
    return bytes(out)


def _pixel(buf, x, y):
    i = 4 * (y * W + x)
    return tuple(buf[i : i + 4])


def _corner_pixels(left, top):
    # Yield (local_x, local_y, x, y) for the RxR corner, mapped to the image.
    for ly in range(R):
        for lx in range(R):
            x = lx if left else W - 1 - lx
            y = ly if top else H - 1 - ly
            yield lx, ly, x, y


CORNERS = [(True, True), (False, True), (True, False), (False, False)]


class RoundCornerTransparentRegressionTestCase(unittest.TestCase):
    def test_transparent_partial_alpha_in_every_corner_and_arc_side(self):
        buf = _render(1)
        for left, top in CORNERS:
            above = []
            below = []
            for lx, ly, x, y in _corner_pixels(left, top):
                a = _pixel(buf, x, y)[3]
                if 0 < a < 255:
                    (above if lx <= ly else below).append((x, y))
            assert (
                above
            ), f"no partial alpha, corner {(left, top)}, above diagonal"
            assert (
                below
            ), f"no partial alpha, corner {(left, top)}, below diagonal"

    def test_transparent_partial_pixels_keep_exact_source_rgb(self):
        buf = _render(1)
        for left, top in CORNERS:
            for lx, ly, x, y in _corner_pixels(left, top):
                r, g, b, a = _pixel(buf, x, y)
                if a > 0:
                    assert (
                        r,
                        g,
                        b,
                    ) == SRC, f"RGB changed at {(x, y)} alpha {a}: {(r, g, b)}"

    def test_opaque_corners_stay_opaque_and_blend_toward_fill(self):
        buf = _render(0)
        for left, top in CORNERS:
            for lx, ly, x, y in _corner_pixels(left, top):
                r, g, b, a = _pixel(buf, x, y)
                assert a == 255, f"opaque alpha changed at {(x, y)}: {a}"
                for c, s, f in zip((r, g, b), SRC, FILL):
                    lo, hi = min(s, f), max(s, f)
                    assert (
                        lo <= c <= hi
                    ), f"opaque pixel {(x, y)} not blended toward fill: {(r, g, b)}"
