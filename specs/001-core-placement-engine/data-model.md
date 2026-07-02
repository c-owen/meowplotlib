# Data Model: Core Placement Engine

All types are plain `dataclasses` (frozen where the value is never mutated after creation) in
`src/meowplotlib/core/placement.py`. No matplotlib types appear anywhere in this module
(constitution #1).

## `Rect`

Axis-aligned bounding rectangle in figure-fraction coordinates (`0..1`).

| Field | Type | Notes |
|---|---|---|
| `x` | `float` | Left edge. |
| `y` | `float` | Bottom edge. |
| `width` | `float` | ≥ 0. |
| `height` | `float` | ≥ 0. |

Used for both exclusion zones (input) and each placement's collision bounding box (derived,
not stored separately — computed from a `Placement`'s center/size on demand).

Method: `intersects(other: Rect) -> bool` — standard AABB overlap test, `>` not `>=` at the
boundary so exactly-touching rectangles do not count as intersecting (matches FR-002's intent:
cats must not visually overlap protected content, and share-an-edge is not overlap).

## `PlacementConfig`

Input configuration for one `place_cats(...)` call. Distinct from `core.config.Config` (the
session-wide user-facing config in `api.py`) — the render layer (M2) translates the session
`Config` into a `PlacementConfig` per draw call.

| Field | Type | Notes |
|---|---|---|
| `density` | `Literal["sparse", "normal", "chaotic"]` | Selects the per-tier area multiplier. |
| `size_range` | `tuple[float, float]` | `(min, max)` cat size as a fraction of the smaller canvas dimension. |
| `seed` | `int \| None` | `None` means unseeded/random. |
| `styles` | `list[str]` | Allowed style identifiers; opaque strings, not validated by this module (see spec Assumptions). Must be non-empty for any placement to be produced. |

## `Placement`

One engine output entry.

| Field | Type | Notes |
|---|---|---|
| `x` | `float` | Center x, figure-fraction. |
| `y` | `float` | Center y, figure-fraction. |
| `size` | `float` | Side length of the (square) bounding box, figure-fraction of the smaller canvas dimension. |
| `rotation` | `float` | Degrees, `[0, 360)`. Used in collision as of the 2026-07-02 addendum: `bbox()` reserves the axis-aligned bounding box of the square AFTER this rotation is applied, not the unrotated square (see research.md). |
| `style` | `str` | One of `PlacementConfig.styles`. |

Method: `bbox() -> Rect` — derives the AABB collision rectangle from `(x, y, size)`.

## `place_cats` function contract

```text
place_cats(canvas_width: float, canvas_height: float, exclusions: list[Rect],
           config: PlacementConfig) -> list[Placement]
```

See `contracts/placement-api.md` for the full behavioral contract.

## State transitions

None — this module is stateless between calls (constitution #1, FR-009). `core/rng.py` exposes a
thin wrapper that constructs one `random.Random` instance per call (seeded or not) and is passed
through the call; no RNG state persists across calls.
