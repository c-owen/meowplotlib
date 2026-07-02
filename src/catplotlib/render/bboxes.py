"""Extracts exclusion zones (axes, labels, ticks, legend) from a live figure."""

from __future__ import annotations

from typing import TYPE_CHECKING

from catplotlib.core.placement import Rect

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.transforms import Bbox, Transform


def extract_exclusions(figure: Figure) -> list[Rect]:
    """Return one exclusion Rect per axes (tight bbox incl. ticks/labels), plus legends.

    Coordinates are converted to figure-fraction space via `figure.transFigure`.
    """
    renderer = figure._get_renderer()  # type: ignore[attr-defined]  # noqa: SLF001
    exclusions: list[Rect] = []
    inv = figure.transFigure.inverted()

    for axes in figure.axes:
        if getattr(axes, "_catplotlib_cat", False):
            continue  # a previously-placed cat's own inset axes, not a protected element
        bbox = axes.get_tightbbox(renderer)
        if bbox is None:
            continue
        exclusions.append(_bbox_to_rect(bbox, inv))

        legend = axes.get_legend()
        if legend is not None:
            legend_bbox = legend.get_window_extent(renderer)
            exclusions.append(_bbox_to_rect(legend_bbox, inv))

    return exclusions


def _bbox_to_rect(bbox: Bbox, inv: Transform) -> Rect:
    fig_bbox = bbox.transformed(inv)
    return Rect(x=fig_bbox.x0, y=fig_bbox.y0, width=fig_bbox.width, height=fig_bbox.height)
