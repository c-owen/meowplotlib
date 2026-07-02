# Contract: `meowplotlib.render.hook`

## `install() -> None`

Idempotent. Safe to call more than once — subsequent calls are no-ops (FR-009). Called exactly
once, from `meowplotlib/__init__.py`, at import time. Never raises (FR-008) — any error during
installation itself (not during a later draw) should be treated as a bug, not a runtime
contingency, since installation only touches well-known matplotlib APIs.

## Draw-hook wrapper behavior (internal, not directly called by users)

Given a `Figure` instance `fig` and the module-level `Config`:

| `Config.enabled` | `fig._meowplotlib_decorated` | Behavior |
|---|---|---|
| `False` | any | Call original `draw()` only. No other meowplotlib code executes. |
| `True` | `True` | Call original `draw()` only. No re-decoration. |
| `True` | `False`/absent | Extract exclusions → place cats → add artists → set flag `True` → call original `draw()`. |

## `meowplotlib.render.bboxes.extract_exclusions(figure) -> list[Rect]`

**Preconditions**: `figure` is a `matplotlib.figure.Figure` that a renderer can be obtained for
(true for any figure with a canvas attached, which all `pyplot`-created figures have).

**Postconditions**:
- Returns one `Rect` (figure-fraction coordinates, matching `core.placement.Rect`) per `Axes` in
  `figure.axes` covering that axes' tight bbox (data + ticks + axis labels), plus one additional
  `Rect` per legend present.
- Never raises for a figure with zero axes (returns `[]`).

## `meowplotlib.render.artist.draw_placements(figure, placements) -> None`

**Preconditions**: `placements` is the output of `core.placement.place_cats(...)`.

**Postconditions**:
- Adds exactly `len(placements)` new artists to `figure`, each positioned/sized/rotated per its
  `Placement`.
- Does not modify or remove any pre-existing artist on the figure.
- Never raises for an empty `placements` list (no-op).

## End-to-end contract (what M2 as a whole guarantees)

- `import meowplotlib` → `install()` called once, never raises, works under `Agg`.
- Any figure drawn or saved afterward while `Config.enabled` is `True` gets decorated exactly
  once, regardless of how many times it's subsequently redrawn.
- `meowplotlib.disable()` → all subsequent draws produce byte-identical output to matplotlib
  without meowplotlib imported, for figures that have not yet been decorated. (Figures already
  decorated before `disable()` keep their existing cats — see spec Assumptions.)
- `meowplotlib.enable()` after `disable()` → subsequent new figures decorate normally again.
