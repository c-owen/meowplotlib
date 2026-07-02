"""Placement geometry: figure dims + exclusion bboxes -> cat placements.

Pure logic — no matplotlib imports, no I/O (constitution #1).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from catplotlib.core.rng import new_rng

Density = Literal["sparse", "normal", "chaotic"]

# Per-tier area divisor: target count = available_border_area / divisor. Chosen so a reference
# canvas (unit square, ~70% centered exclusion, default size_range) yields roughly 3/6/12 cats
# for sparse/normal/chaotic respectively — strictly increasing on any fixed canvas.
_DENSITY_DIVISORS: dict[Density, float] = {
    "sparse": 0.131,
    "normal": 0.0656,
    "chaotic": 0.0328,
}

# Fixed edge margin as a fraction of the smaller canvas dimension.
_EDGE_MARGIN_FRACTION = 0.03

_MAX_ATTEMPTS_PER_CANDIDATE = 30
_SHRINK_FACTOR = 0.85

# Defensive upper bound on target count regardless of canvas size, so a pathologically large
# canvas can't make placement (O(n^2) collision checks against prior placements) unbounded.
_MAX_TARGET_COUNT = 200


@dataclass(frozen=True)
class Rect:
    """Axis-aligned bounding rectangle in figure-fraction coordinates."""

    x: float
    y: float
    width: float
    height: float

    def intersects(self, other: Rect) -> bool:
        return (
            self.x < other.x + other.width
            and other.x < self.x + self.width
            and self.y < other.y + other.height
            and other.y < self.y + self.height
        )


@dataclass(frozen=True)
class PlacementConfig:
    """Input configuration for one `place_cats(...)` call."""

    density: Density
    size_range: tuple[float, float]
    seed: int | None
    styles: list[str]


@dataclass(frozen=True)
class Placement:
    """One engine output entry."""

    x: float
    y: float
    size: float
    rotation: float
    style: str

    def bbox(self) -> Rect:
        """Axis-aligned bounding box of this cat's square footprint AFTER rotation.

        Reserves the true rotated extent (side * (|cos theta| + |sin theta|), up to ~1.41x at
        45 degrees) rather than the unrotated square, so a rendered, actually-rotated image
        never exceeds the space collision-checked against exclusions and other placements. See
        specs/001-core-placement-engine/research.md's 2026-07-02 addendum.
        """
        theta = math.radians(self.rotation)
        side = self.size * (abs(math.cos(theta)) + abs(math.sin(theta)))
        half = side / 2
        return Rect(x=self.x - half, y=self.y - half, width=side, height=side)


def _margin_rects(canvas_width: float, canvas_height: float, margin: float) -> list[Rect]:
    """Four thin rectangles covering the edge-margin band, so it composes with exclusions."""
    return [
        Rect(x=0, y=0, width=canvas_width, height=margin),  # bottom
        Rect(x=0, y=canvas_height - margin, width=canvas_width, height=margin),  # top
        Rect(x=0, y=0, width=margin, height=canvas_height),  # left
        Rect(x=canvas_width - margin, y=0, width=margin, height=canvas_height),  # right
    ]


def _available_border_area(
    canvas_width: float, canvas_height: float, exclusions: list[Rect], margin: float
) -> float:
    """Coarse Monte Carlo estimate of canvas area outside exclusions and the edge margin."""
    inner = Rect(
        x=margin,
        y=margin,
        width=max(0.0, canvas_width - 2 * margin),
        height=max(0.0, canvas_height - 2 * margin),
    )
    if inner.width <= 0 or inner.height <= 0:
        return 0.0
    total = inner.width * inner.height
    excluded = 0.0
    for rect in exclusions:
        overlap_w = min(inner.x + inner.width, rect.x + rect.width) - max(inner.x, rect.x)
        overlap_h = min(inner.y + inner.height, rect.y + rect.height) - max(inner.y, rect.y)
        if overlap_w > 0 and overlap_h > 0:
            excluded += overlap_w * overlap_h
    return max(0.0, total - excluded)


def _target_count(available_area: float, density: Density) -> int:
    if available_area <= 0:
        return 0
    return min(_MAX_TARGET_COUNT, int(available_area / _DENSITY_DIVISORS[density]))


def place_cats(
    canvas_width: float,
    canvas_height: float,
    exclusions: list[Rect],
    config: PlacementConfig,
) -> list[Placement]:
    """Return non-overlapping cat placements confined to the canvas border region.

    See specs/001-core-placement-engine/contracts/placement-api.md for the full contract.
    """
    if canvas_width <= 0 or canvas_height <= 0 or not config.styles:
        return []

    margin = _EDGE_MARGIN_FRACTION * min(canvas_width, canvas_height)
    blocked = list(exclusions) + _margin_rects(canvas_width, canvas_height, margin)
    available_area = _available_border_area(canvas_width, canvas_height, exclusions, margin)
    target = _target_count(available_area, config.density)
    if target <= 0:
        return []

    rng = new_rng(config.seed)
    min_size, max_size = config.size_range
    placements: list[Placement] = []

    for _ in range(target):
        size = max_size
        placed = False
        while not placed:
            for _ in range(_MAX_ATTEMPTS_PER_CANDIDATE):
                rotation = rng.uniform(0, 360)
                theta = math.radians(rotation)
                rotated_side = size * (abs(math.cos(theta)) + abs(math.sin(theta)))
                half = rotated_side / 2
                x = rng.uniform(half, canvas_width - half)
                y = rng.uniform(half, canvas_height - half)
                candidate = Placement(
                    x=x,
                    y=y,
                    size=size,
                    rotation=rotation,
                    style=rng.choice(config.styles),
                )
                bbox = candidate.bbox()
                if any(bbox.intersects(r) for r in blocked):
                    continue
                if any(bbox.intersects(p.bbox()) for p in placements):
                    continue
                placements.append(candidate)
                placed = True
                break
            if placed:
                break
            size *= _SHRINK_FACTOR
            if size < min_size:
                break

    return placements
