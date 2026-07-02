"""Tests for the public api.py surface: enable/disable/set_style/set_density/set_seed/config."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

import catplotlib
from catplotlib.core.config import get_config


@pytest.fixture(autouse=True)
def _reset_config() -> Iterator[None]:
    config = get_config()
    snapshot = config.snapshot()
    yield
    config.restore(snapshot)


def test_enable_disable_toggle_config_flag() -> None:
    catplotlib.disable()
    assert get_config().enabled is False
    catplotlib.enable()
    assert get_config().enabled is True


def test_set_density_accepts_valid_tiers() -> None:
    for density in ("sparse", "normal", "chaotic"):
        catplotlib.set_density(density)
        assert get_config().density == density


def test_set_density_rejects_unknown_value() -> None:
    with pytest.raises(ValueError, match="Unknown density"):
        catplotlib.set_density("extreme")


def test_set_seed_accepts_int_or_none() -> None:
    catplotlib.set_seed(42)
    assert get_config().seed == 42
    catplotlib.set_seed(None)
    assert get_config().seed is None


def test_set_style_rejects_unknown_style() -> None:
    with pytest.raises(ValueError, match="Unknown style"):
        catplotlib.set_style("not-a-real-style")


def test_config_context_manager_restores_previous_values() -> None:
    catplotlib.set_density("normal")
    with catplotlib.config(density="chaotic", enabled=False):
        assert get_config().density == "chaotic"
        assert get_config().enabled is False
    assert get_config().density == "normal"
    assert get_config().enabled is True


def test_config_context_manager_restores_on_exception() -> None:
    catplotlib.set_density("normal")
    with pytest.raises(RuntimeError), catplotlib.config(density="chaotic"):
        assert get_config().density == "chaotic"
        raise RuntimeError("boom")
    assert get_config().density == "normal"


def test_config_context_manager_validates_density() -> None:
    with pytest.raises(ValueError, match="Unknown density"), catplotlib.config(density="extreme"):
        pass
    assert get_config().density != "extreme"


def test_config_context_manager_validates_style() -> None:
    with (
        pytest.raises(ValueError, match="Unknown style"),
        catplotlib.config(style="not-a-real-style"),
    ):
        pass


def test_config_context_manager_rejects_unknown_field() -> None:
    with (
        pytest.raises(TypeError, match="Unknown config option"),
        catplotlib.config(not_a_real_field=True),
    ):
        pass
