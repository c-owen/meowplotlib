"""Draws placed cats onto the figure.

M2 uses a minimal internal single-image stub so this milestone doesn't depend on M3's style
registry (see specs/002-matplotlib-integration/research.md). M3 replaces `_resolve_image` with a
real per-style lookup.

Each cat is drawn in its own tiny inset Axes positioned at the placement's exact figure-fraction
bounding box (`Placement.bbox()`), rather than via OffsetImage/AnnotationBbox's point-space
`zoom`. This makes the actual rendered footprint match the bbox M1's collision math assumed
exactly, instead of approximating it through a DPI-dependent zoom factor. Cat axes are tagged
with `_catplotlib_cat = True` so `render/bboxes.py` can exclude them from exclusion extraction.
"""

from __future__ import annotations

import importlib.resources
from typing import TYPE_CHECKING

import matplotlib.image as mpimg

if TYPE_CHECKING:
    import numpy as np
    from matplotlib.figure import Figure

    from catplotlib.core.placement import Placement

_STUB_IMAGE_CACHE: dict[str, np.ndarray] = {}


def _resolve_image(style: str) -> np.ndarray:
    """M2 stub: always returns the classic placeholder image, ignoring `style`."""
    if "classic" not in _STUB_IMAGE_CACHE:
        with importlib.resources.as_file(
            importlib.resources.files("catplotlib.assets.images") / "classic" / "classic_01.png"
        ) as path:
            _STUB_IMAGE_CACHE["classic"] = mpimg.imread(path)
    return _STUB_IMAGE_CACHE["classic"]


def draw_placements(figure: Figure, placements: list[Placement]) -> None:
    """Add one cat image per placement, each in its own figure-fraction-positioned inset axes."""
    for placement in placements:
        image = _resolve_image(placement.style)
        bbox = placement.bbox()
        cat_axes = figure.add_axes((bbox.x, bbox.y, bbox.width, bbox.height))
        cat_axes._catplotlib_cat = True  # type: ignore[attr-defined]
        cat_axes.set_axis_off()
        cat_axes.patch.set_alpha(0.0)
        cat_axes.imshow(image, aspect="auto")
