"""Draws placed cats onto the figure.

Each cat is drawn in its own tiny inset Axes positioned at the placement's exact figure-fraction
bounding box (`Placement.bbox()`), rather than via OffsetImage/AnnotationBbox's point-space
`zoom`. This makes the actual rendered footprint match the bbox M1's collision math assumed
exactly, instead of approximating it through a DPI-dependent zoom factor. Cat axes are tagged
with `_meowplotlib_cat = True` so `render/bboxes.py` can exclude them from exclusion extraction.

Since M1's `Placement.bbox()` reserves the true rotated footprint (see
specs/001-core-placement-engine/research.md's 2026-07-02 addendum), the cat axes here is always
exactly that (larger, square) bbox; the image itself is drawn at its true unrotated size,
centered, and rotated in data-space via an affine transform. Because the reserved bbox is by
construction the axis-aligned bounding box of a `placement.size`-side square rotated by
`placement.rotation`, the rotated image's true footprint always stays within the axes — no
overflow into neighboring exclusions or other cats regardless of the sampled rotation angle.

Style resolution goes through `assets.registry` (M3): `placement.style` selects a style, and a
deterministic (not RNG-based) hash of the placement's own fields picks one image from that
style's pool, so seeded reproducibility survives multi-image pools — see
specs/003-style-system/research.md.
"""

from __future__ import annotations

import importlib.resources
from typing import TYPE_CHECKING

import matplotlib.image as mpimg
import matplotlib.transforms as mtransforms

from meowplotlib.assets.registry import available_styles

if TYPE_CHECKING:
    from pathlib import Path

    import numpy as np
    from matplotlib.figure import Figure

    from meowplotlib.core.placement import Placement

_IMAGE_CACHE: dict[Path, np.ndarray] = {}


def _load_image(path: Path) -> np.ndarray:
    if path not in _IMAGE_CACHE:
        with importlib.resources.as_file(path) as local_path:
            _IMAGE_CACHE[path] = mpimg.imread(local_path)
    return _IMAGE_CACHE[path]


def _resolve_image(placement: Placement) -> tuple[np.ndarray, float]:
    """Return (image array, clamped scale) for `placement`, deterministic given its fields.

    Scale is clamped to <= 1.0: a style's manifest `scale` may only ever shrink a cat's
    rendered footprint within its reserved bbox, never grow it beyond the box M1's collision
    math reserved (constitution #2 takes priority over exact visual scale fidelity — see
    PROGRESS.md for the follow-up needed to let scale genuinely grow a cat's footprint).
    """
    styles = available_styles()
    style_info = styles[placement.style]
    pool = style_info.image_paths  # already filename-sorted by registry.discover_styles
    index = hash((placement.x, placement.y, placement.size, placement.rotation)) % len(pool)
    image = _load_image(pool[index])
    return image, min(style_info.scale, 1.0)


def draw_placements(figure: Figure, placements: list[Placement]) -> None:
    """Add one rotated cat image per placement, each in its own figure-fraction inset axes."""
    for placement in placements:
        image, scale = _resolve_image(placement)
        bbox = placement.bbox()  # the rotation-inclusive reserved square
        cat_axes = figure.add_axes((bbox.x, bbox.y, bbox.width, bbox.height))
        cat_axes._meowplotlib_cat = True  # type: ignore[attr-defined]
        cat_axes.set_axis_off()
        cat_axes.patch.set_alpha(0.0)

        half_span = bbox.width / 2
        cat_axes.set_xlim(-half_span, half_span)
        cat_axes.set_ylim(-half_span, half_span)

        visual_half = (placement.size * scale) / 2
        cat_image = cat_axes.imshow(
            image,
            extent=(-visual_half, visual_half, -visual_half, visual_half),
        )
        cat_image.set_transform(
            mtransforms.Affine2D().rotate_deg(placement.rotation) + cat_axes.transData
        )
