"""Chart-type x figsize x legend-presence non-overlap matrix — see STANDUP_PLAN.md §8."""

from __future__ import annotations

from collections.abc import Callable

import matplotlib.pyplot as plt
import pytest

from meowplotlib.core.config import get_config
from meowplotlib.render.bboxes import extract_exclusions

FIGSIZES = {
    "small": (2.0, 2.0),
    "default": (6.4, 4.8),
    "large": (12.0, 9.0),
}


def _line(ax: plt.Axes) -> None:
    ax.plot([1, 2, 3, 4], [1, 4, 9, 16], label="series")


def _bar(ax: plt.Axes) -> None:
    ax.bar(["a", "b", "c"], [3, 7, 5], label="series")


def _scatter(ax: plt.Axes) -> None:
    ax.scatter([1, 2, 3, 4], [4, 1, 9, 3], label="series")


def _histogram(ax: plt.Axes) -> None:
    ax.hist([1, 1, 2, 3, 3, 3, 4, 5], bins=5, label="series")


CHART_TYPES: dict[str, Callable[[plt.Axes], None]] = {
    "line": _line,
    "bar": _bar,
    "scatter": _scatter,
    "histogram": _histogram,
}

MATRIX_CELLS = [
    (chart_name, figsize_name, legend)
    for chart_name in CHART_TYPES
    for figsize_name in FIGSIZES
    for legend in (True, False)
]


@pytest.mark.parametrize(
    "chart_name,figsize_name,legend",
    MATRIX_CELLS,
    ids=[f"{c}-{f}-legend={has_legend}" for c, f, has_legend in MATRIX_CELLS],
)
def test_no_cat_overlaps_protected_elements(
    chart_name: str, figsize_name: str, legend: bool
) -> None:
    get_config().density = "chaotic"  # stress-test with the highest cat count
    fig, ax = plt.subplots(figsize=FIGSIZES[figsize_name])
    CHART_TYPES[chart_name](ax)
    ax.set_xlabel("x label")
    ax.set_ylabel("y label")
    if legend:
        ax.legend()

    fig.canvas.draw()
    exclusions = extract_exclusions(fig)

    cat_axes = [ax for ax in fig.axes if getattr(ax, "_meowplotlib_cat", False)]
    for cat_ax in cat_axes:
        cat_bbox = cat_ax.get_position()  # figure-fraction, exactly what artist.py requested
        for exclusion in exclusions:
            overlap_w = min(cat_bbox.x1, exclusion.x + exclusion.width) - max(
                cat_bbox.x0, exclusion.x
            )
            overlap_h = min(cat_bbox.y1, exclusion.y + exclusion.height) - max(
                cat_bbox.y0, exclusion.y
            )
            assert not (overlap_w > 0 and overlap_h > 0), (
                f"cat overlaps protected element: {chart_name}/{figsize_name}/legend={legend}"
            )
    plt.close(fig)
