"""Shared fixtures for render tests: force Agg backend, reset session config."""

from __future__ import annotations

from collections.abc import Iterator

import matplotlib
import pytest

matplotlib.use("Agg")

import catplotlib  # noqa: E402,F401 - import registers the hook; must follow matplotlib.use()
from catplotlib.core.config import get_config  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_config() -> Iterator[None]:
    config = get_config()
    snapshot = config.snapshot()
    yield
    config.restore(snapshot)
