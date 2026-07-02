# Contract: `meowplotlib.core.placement.place_cats`

This is the public interface the render layer (M2) calls. It is the only entry point M2 needs
from this module besides the `Rect`, `PlacementConfig`, and `Placement` types themselves.

## Signature

```python
def place_cats(
    canvas_width: float,
    canvas_height: float,
    exclusions: list[Rect],
    config: PlacementConfig,
) -> list[Placement]:
    ...
```

## Preconditions

- `canvas_width`, `canvas_height`: any float, including zero or negative (see postconditions).
- `exclusions`: any list of `Rect`, including empty, including mutually overlapping rectangles.
  Rectangles are not required to lie within the canvas bounds (a rectangle partially or fully
  outside the canvas is treated as-is; its portion outside the canvas simply excludes nothing
  extra).
- `config.styles`: any list of `str`, including empty (see postconditions).

## Postconditions

1. Return value is always a `list[Placement]` — the function never raises for any input
   satisfying the preconditions above (FR-008, spec edge cases).
2. If `canvas_width <= 0` or `canvas_height <= 0`: returns `[]`.
3. If `config.styles` is empty: returns `[]`.
4. For every returned `Placement`, `placement.bbox()` does not intersect any rectangle in
   `exclusions`, and does not intersect the canvas-edge margin band (FR-002, FR-003).
5. For every pair of returned placements, their `bbox()`s do not intersect each other (FR-003a).
6. `placement.style in config.styles` for every returned placement (FR-010).
7. WHEN `config.seed is not None`: two calls with identical `canvas_width`, `canvas_height`,
   `exclusions` (same values, any order — the function treats `exclusions` as a set for
   collision purposes but may be sensitive to input order for tie-breaking; callers relying on
   determinism SHOULD pass the same order), and `config` return identical output, per-element,
   in the same order (FR-004).
8. WHEN `config.seed is None`: the function draws fresh randomness each call; two consecutive
   calls with otherwise-identical arguments are expected (not strictly guaranteed for every
   possible input, but true with overwhelming probability) to differ (FR-005).
9. On a fixed reference canvas with a fixed seed and no exclusions, `len(result)` for
   `density="sparse"` < `density="normal"` < `density="chaotic"` (FR-006).

## Non-goals of this contract

- No validation that `config.styles` entries correspond to real, loadable assets — that is the
  render layer's / asset registry's (M3) responsibility.
- No unit conversion — all coordinates are assumed to already be in the same figure-fraction
  space as the caller's exclusions.
