"""User-facing public API: enable/disable/set_style/set_density/set_seed/config."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from catplotlib.core.config import get_config


def enable() -> None:
    """Re-enable cat decoration for the current session."""
    get_config().enabled = True


def disable() -> None:
    """Disable cat decoration for the current session."""
    get_config().enabled = False


def set_style(style: str | list[str]) -> None:
    """Select a single style, a mix of styles, or "mix" for all styles."""
    get_config().style = style


def set_density(density: str) -> None:
    """Set cat density: "sparse", "normal", or "chaotic"."""
    get_config().density = density


def set_seed(seed: int | None) -> None:
    """Set the RNG seed for reproducible placements, or None for randomized."""
    get_config().seed = seed


@contextmanager
def config(**overrides: object) -> Iterator[None]:
    """Temporarily override config values within a `with` block."""
    cfg = get_config()
    saved = cfg.snapshot()
    try:
        cfg.update(**overrides)
        yield
    finally:
        cfg.restore(saved)
