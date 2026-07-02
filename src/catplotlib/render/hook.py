"""Figure draw interception: the single hook point for both display and savefig.

See specs/002-matplotlib-integration/research.md for why `Figure.draw` is the shared
interception point, and why the patch is permanent (enable/disable only flips a flag).
"""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any

from matplotlib.figure import Figure

from catplotlib.assets.registry import resolve_style_names
from catplotlib.core.config import get_config
from catplotlib.core.placement import PlacementConfig, place_cats
from catplotlib.render import artist, bboxes

if TYPE_CHECKING:
    from collections.abc import Callable

_installed = False


def install() -> None:
    """Wrap `Figure.draw` once, process-wide. Safe to call more than once (no-op after first)."""
    global _installed
    if _installed:
        return
    _installed = True

    original_draw: Callable[..., Any] = Figure.draw

    @functools.wraps(original_draw)
    def wrapped_draw(self: Figure, renderer: Any, *args: Any, **kwargs: Any) -> Any:
        config = get_config()
        if config.enabled and not getattr(self, "_catplotlib_decorated", False):
            _decorate(self, config.density, config.seed, config.style)
            self._catplotlib_decorated = True  # type: ignore[attr-defined]
        return original_draw(self, renderer, *args, **kwargs)

    Figure.draw = wrapped_draw  # type: ignore[assignment]


def _decorate(figure: Figure, density: str, seed: int | None, style: str | list[str]) -> None:
    # bboxes.extract_exclusions() returns rects in figure-fraction space (transFigure-normalized
    # to 0..1), so the canvas itself is always the unit square in that same coordinate system —
    # NOT figure.get_size_inches(). This also gives small-figure degradation "for free": at a
    # fixed font size, a small figure's tick/axis labels occupy a larger fraction of the unit
    # square, shrinking available border area exactly as intended.
    exclusions = bboxes.extract_exclusions(figure)
    styles = resolve_style_names(style)
    if not styles:
        return
    config = PlacementConfig(
        density=density,  # type: ignore[arg-type]
        size_range=(0.03, 0.08),
        seed=seed,
        styles=styles,
    )
    placements = place_cats(1.0, 1.0, exclusions, config)
    artist.draw_placements(figure, placements)
