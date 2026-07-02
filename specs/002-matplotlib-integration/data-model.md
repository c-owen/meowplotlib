# Data Model: Matplotlib Integration & Activation

No new persistent data types — this feature is glue between M1's pure engine and live
matplotlib objects. The state introduced is:

## Per-figure state

| Attribute | Owner | Type | Notes |
|---|---|---|---|
| `Figure._catplotlib_decorated` | `matplotlib.figure.Figure` instance (set by `render/hook.py`) | `bool` | Absent (falsy via `getattr(..., False)`) until first decoration; set `True` after. Never reset — decoration is a one-time, per-instance event (FR-003). |

## Process-level state

| Name | Owner | Type | Notes |
|---|---|---|---|
| `Config.enabled` | `core/config.py` (already exists from M0) | `bool` | Read by the draw-hook wrapper on every call; mutated only by `api.enable()`/`api.disable()`. |
| Draw-hook installation | `render/hook.py` module-level guard | `bool` (module attribute, e.g. `_installed`) | Prevents double-wrapping `Figure.draw` if the install function is called more than once (FR-009). |

## Functions (the actual "entities" of this feature)

### `render/hook.py`

- `install() -> None` — replaces `matplotlib.figure.Figure.draw` with a wrapper, guarded by the
  module-level `_installed` flag (FR-009). Called once from `catplotlib/__init__.py` at import
  time.
- The wrapper itself (internal, not exported): on each call, checks `Config.enabled` and the
  instance's `_catplotlib_decorated` flag; if both indicate decoration should happen, calls
  `bboxes.extract_exclusions(figure)` → `placement.place_cats(...)` →
  `artist.draw_placements(figure, placements)`, then sets the flag; always calls the original
  `draw()` afterward.

### `render/bboxes.py`

- `extract_exclusions(figure: Figure) -> list[Rect]` — for each `Axes` in `figure.axes`, computes
  `get_tightbbox()` (+ legend extent if present), converts to figure-fraction `Rect` via
  `figure.transFigure.inverted()`.

### `render/artist.py`

- `draw_placements(figure: Figure, placements: list[Placement]) -> None` — for each `Placement`,
  resolves an image (M2: internal stub per research.md; M3: real registry lookup) and adds it as
  its own tiny inset `Axes` (`figure.add_axes(...)`, tagged `_catplotlib_cat = True`) positioned
  at the placement's exact figure-fraction bbox — **not** `AnnotationBbox`/`OffsetImage`, whose
  point-space `zoom` parameter caused real (if sub-pixel) overlaps with protected content; see
  `specs/002-matplotlib-integration`'s implementation commit history and
  `specs/003-style-system/data-model.md`'s 2026-07-02 addendum for the rotation-rendering
  follow-up that further changed how the image is drawn within that axes.

## State transitions

```text
Figure created (plt.figure()) → no _catplotlib_decorated attribute
  → first Figure.draw() call (display or savefig) with Config.enabled=True
    → exclusions extracted, cats placed, artists added, _catplotlib_decorated=True
  → any subsequent Figure.draw() call
    → _catplotlib_decorated is True → skip decoration → call original draw() only
```

```text
Config.enabled: True (default) --disable()--> False --enable()--> True
  (orthogonal to the per-figure flag above; a disabled call never sets the flag)
```
