"""User-facing public API: enable/disable/set_style/set_density/set_seed/config."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from catplotlib.assets.registry import resolve_style_names
from catplotlib.core.config import get_config


def enable() -> None:
    """Re-enable cat decoration for the current session."""
    get_config().enabled = True


def disable() -> None:
    """Disable cat decoration for the current session."""
    get_config().enabled = False


_VALID_DENSITIES = ("sparse", "normal", "chaotic")


def _validate_style(style: object) -> None:
    if not isinstance(style, str | list):
        raise TypeError(f"style must be a str or list[str], got {type(style).__name__}")
    resolve_style_names(style)  # fail-fast; "mix" always validates, resolved fresh at render time


def _validate_density(density: object) -> None:
    if density not in _VALID_DENSITIES:
        raise ValueError(f"Unknown density: {density!r}. Valid options: {_VALID_DENSITIES}")


def set_style(style: str | list[str]) -> None:
    """Select a single style, a mix of styles, or "mix" for all styles.

    Validates eagerly: an unregistered style name raises immediately, rather than
    surfacing as a silent absence of cats at the next render.
    """
    _validate_style(style)
    get_config().style = style


def set_density(density: str) -> None:
    """Set cat density: "sparse", "normal", or "chaotic"."""
    _validate_density(density)
    get_config().density = density


def set_seed(seed: int | None) -> None:
    """Set the RNG seed for reproducible placements, or None for randomized."""
    get_config().seed = seed


@contextmanager
def config(**overrides: object) -> Iterator[None]:
    """Temporarily override config values within a `with` block.

    Applies the same validation as `set_style`/`set_density` to any overridden values.
    """
    if "style" in overrides:
        _validate_style(overrides["style"])
    if "density" in overrides:
        _validate_density(overrides["density"])

    cfg = get_config()
    saved = cfg.snapshot()
    try:
        cfg.update(**overrides)
        yield
    finally:
        cfg.restore(saved)
