"""Shared test-only helpers for tests/render/."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure


def count_cat_axes(figure: Figure) -> int:
    """Count the inset axes render/artist.py added for placed cats on `figure`."""
    return sum(1 for ax in figure.axes if getattr(ax, "_meowplotlib_cat", False))
