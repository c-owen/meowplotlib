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


def ensure_minimum_margin(figure: Figure, margin: float) -> None:
    """Shrink each axes so at least `margin` (figure-fraction) of clear space remains between
    its tight bbox and every figure edge, so cats have room to land on all four sides.

    This actively resizes the user's plot area — a deliberate, opted-in departure from pure
    "decorate around the existing layout" behavior. See PROGRESS.md for the tradeoff record.
    Only shrinks when needed: axes with an already-generous margin on a given side are left
    untouched on that side.
    """
    renderer = figure._get_renderer()  # type: ignore[attr-defined]  # noqa: SLF001
    inv = figure.transFigure.inverted()

    for axes in figure.axes:
        if getattr(axes, "_catplotlib_cat", False):
            continue
        tight = axes.get_tightbbox(renderer)
        if tight is None:
            continue
        fig_tight = tight.transformed(inv)

        left_deficit = max(0.0, margin - fig_tight.x0)
        bottom_deficit = max(0.0, margin - fig_tight.y0)
        right_deficit = max(0.0, margin - (1.0 - fig_tight.x1))
        top_deficit = max(0.0, margin - (1.0 - fig_tight.y1))
        if not (left_deficit or bottom_deficit or right_deficit or top_deficit):
            continue

        pos = axes.get_position()
        new_width = pos.width - left_deficit - right_deficit
        new_height = pos.height - bottom_deficit - top_deficit
        if new_width <= 0 or new_height <= 0:
            continue  # figure too small to guarantee this margin; leave axes as-is
        axes.set_position((pos.x0 + left_deficit, pos.y0 + bottom_deficit, new_width, new_height))


def _bbox_to_rect(bbox: Bbox, inv: Transform) -> Rect:
    fig_bbox = bbox.transformed(inv)
    return Rect(x=fig_bbox.x0, y=fig_bbox.y0, width=fig_bbox.width, height=fig_bbox.height)
