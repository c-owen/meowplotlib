"""Constitution #9: the public API surface must remain stable."""

from __future__ import annotations

import meowplotlib


def test_public_api_surface() -> None:
    expected = {"config", "disable", "enable", "set_density", "set_seed", "set_style"}
    assert expected.issubset(set(meowplotlib.__all__))
    for name in expected:
        assert hasattr(meowplotlib, name)


def test_import_never_raises_and_defaults_enabled() -> None:
    from meowplotlib.core.config import get_config

    assert get_config().enabled is True
