"""Seeded RNG wrapper for reproducible placements. No matplotlib imports, no I/O."""

from __future__ import annotations

import random


def new_rng(seed: int | None) -> random.Random:
    """Return a fresh `random.Random` instance seeded from `seed`, or unseeded if `None`."""
    return random.Random(seed)
