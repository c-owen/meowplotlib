# Feature Specification: Matplotlib Integration & Activation

**Feature Branch**: `002-matplotlib-integration`

**Created**: 2026-07-02

**Status**: Draft

**Input**: User description: "The import-time hook: intercept figure rendering so cats appear on display and savefig with zero user code changes, and can be cleanly disabled. Riskiest feature of catplotlib v1."

## Clarifications

### Session 2026-07-02

- Q: How should enable()/disable() interact with the installed Figure.draw hook? → A: Patch once at import time, permanently, for the process. disable()/enable() only flip the global `Config.enabled` flag the wrapper checks on every call; when disabled, the wrapper calls straight through to the original draw with no other code executed, so output is provably identical to unpatched matplotlib. The class method itself is never unpatched/repatched.
- Q: How granular should exclusion-bbox extraction be for figures? → A: Whole-axes tight bbox — each Axes's `get_tightbbox()` (already includes its tick labels and axis labels) plus the legend's own extent if present, unioned into a small handful of exclusion rectangles per figure.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One import, cats everywhere (Priority: P1)

A user with an existing matplotlib script adds a single `import catplotlib` line and nothing
else. The next figure they display (e.g. in a notebook) or save (`savefig`) shows cat
decorations, using the placement engine from M1.

**Why this priority**: This is the entire product promise (PRD requirement 1). Without it,
nothing else in the package matters.

**Independent Test**: In a fresh Python process, `import matplotlib.pyplot as plt`, `import
catplotlib`, create a simple line plot, call `savefig` to a buffer, and confirm the saved image
contains cat artwork (e.g. by asserting extra artists exist on the figure, or via pixel-level
comparison against a no-catplotlib baseline).

**Acceptance Scenarios**:

1. **Given** a script that only adds `import catplotlib` to existing matplotlib code, **When**
   the user calls `plt.show()` or `fig.savefig(...)`, **Then** the resulting output includes cat
   decorations placed by the M1 engine.
2. **Given** a Jupyter-style inline display (figure rendered via its `_repr_html_`/`_repr_png_`
   or backend draw path, not an explicit `savefig` call), **When** the figure is displayed,
   **Then** cat decorations appear identically to the `savefig` case.

---

### User Story 2 - Decoration never duplicates on redraw (Priority: P1)

Interactive backends redraw a figure repeatedly (resize, any artist mutation, re-display). A
user resizes a window or re-displays the same figure object multiple times. The number of cats
on the figure stays exactly the same across all those redraws — they never accumulate.

**Why this priority**: Without this, the product actively breaks the "non-destructive" promise
(PRD requirement 2) — a figure would visually degrade the longer a notebook session runs.
Directly required by constitution: decoration must be idempotent.

**Independent Test**: Create a figure, force multiple draw passes (e.g. call
`fig.canvas.draw()` three times, or call `savefig` twice), and assert the number of cat artists
on the figure is identical after each pass.

**Acceptance Scenarios**:

1. **Given** a figure that has already been decorated once, **When** the figure is redrawn any
   number of additional times without modification, **Then** the set of cat artists present is
   unchanged (same count, same placements).
2. **Given** a decorated figure, **When** the user adds new data to it (e.g. a new line) and it
   redraws, **Then** cats are not re-placed or duplicated — only the original decoration persists
   (re-placement in response to content changes is out of scope for v1; see Assumptions).

---

### User Story 3 - Session on/off switch (Priority: P1)

A user calls `catplotlib.disable()` partway through a script or notebook session. Every figure
saved or shown after that call is pixel-identical to what matplotlib alone would have produced —
no cats, no leftover hooks, no side effects. Calling `catplotlib.enable()` later in the same
session restores decoration for subsequently rendered figures.

**Why this priority**: PRD requirement 7 (global on/off) is P0, and constitution rule #4 ties a
dedicated byte-identity test to this exact behavior — a presenter needs to produce a
client-facing, cat-free export from the same session that has cats everywhere else.

**Independent Test**: Render and save a figure with catplotlib active; call `disable()`; render
and save an equivalent fresh figure; assert the second file's bytes are identical to a baseline
save from a process that never imported catplotlib. Call `enable()`; render and save another
fresh figure; assert it again contains cats.

**Acceptance Scenarios**:

1. **Given** `catplotlib.disable()` has been called, **When** any new figure is created and
   saved, **Then** the saved file is byte-identical to the same figure saved with matplotlib
   alone (no catplotlib import at all).
2. **Given** `catplotlib.disable()` then `catplotlib.enable()` have both been called in the same
   session, **When** a new figure is created and saved, **Then** it contains cat decorations
   again, matching the always-enabled behavior.
3. **Given** a figure that was already decorated before `disable()` was called, **When**
   `disable()` is called, **Then** that already-rendered figure's existing cats are not
   retroactively removed (disable affects subsequent decoration decisions, not artists already
   added — see Assumptions).

---

### User Story 4 - Cats respect every chart's real layout (Priority: P1)

Across common chart types (line, bar, scatter, histogram) and figure sizes (small/default/large),
with and without a legend, the exclusion zones fed to the M1 placement engine accurately reflect
where the actual data, axis labels, tick labels, and legend are — so cats never visually cover
them, regardless of how a particular chart happens to be laid out.

**Why this priority**: This is where M1's placement guarantee actually gets tested against real
matplotlib output instead of synthetic rectangles. Without accurate bbox extraction, M1's
correctness is moot.

**Independent Test**: Render each chart type at each figsize (with/without legend), extract
placed cat artist bboxes and the real protected-element bboxes from the rendered figure, and
assert empty intersection — the automated harness described in STANDUP_PLAN.md §8.

**Acceptance Scenarios**:

1. **Given** any chart in the test matrix (chart type × figsize × legend presence), **When** the
   figure is rendered with catplotlib active, **Then** no cat artist's bounding box intersects
   the bounding box of the axes data area, any axis label, any tick label, or the legend.
2. **Given** a headless environment (the `Agg` backend, no display available), **When** a figure
   is rendered and saved, **Then** decoration and bbox extraction both work without error,
   identically to an interactive backend.

---

### Edge Cases

- What happens when `import catplotlib` occurs in a headless environment with no interactive
  backend configured? The import must never raise (constitution #5); decoration must still work
  for `savefig`.
- What happens when a figure has no axes at all (a bare `Figure()` with nothing plotted)? The
  entire canvas minus the fixed edge margin is treated as available border region, per M1.
- What happens when `catplotlib` is imported multiple times (e.g. `importlib.reload`) or the
  draw hook is somehow installed twice? Installation must be idempotent — a second install must
  not double-wrap `Figure.draw` (which would otherwise cause exponential decoration attempts).
- What happens with a matplotlib figure created with `plt.figure()` before `import catplotlib`
  ran? Since the hook patches the class method (`Figure.draw`), it applies to all `Figure`
  instances regardless of creation order, including ones already created before import.
- What happens with seaborn-generated figures? Seaborn plots onto standard matplotlib
  `Figure`/`Axes` objects, so the same `Figure.draw` hook applies with no special-casing needed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Importing the package MUST install a hook that causes subsequently drawn or saved
  matplotlib figures to receive cat decorations, with no function calls required beyond the
  import.
- **FR-002**: The hook MUST cover both the interactive display path and the `savefig` path
  through one shared interception point, so behavior is identical between them.
- **FR-003**: Decoration MUST be idempotent per figure instance: any number of redraws of an
  already-decorated figure MUST NOT change the set of cat artists present on it.
- **FR-004**: The package MUST expose `enable()` and `disable()` such that, after `disable()`,
  every subsequently rendered figure's output is byte-identical to output produced without
  catplotlib imported at all.
- **FR-005**: `enable()` called after `disable()` MUST restore decoration for figures rendered
  afterward, within the same process/session.
- **FR-006**: The render layer MUST extract exclusion rectangles (in figure-fraction
  coordinates, matching M1's contract) for the axes data area, axis labels, tick labels, and
  legend of a given figure, accurately reflecting the figure's actual rendered layout.
- **FR-007**: The render layer MUST call M1's `place_cats()` with the figure's real dimensions
  and extracted exclusion rectangles, and translate the returned placements into rendered
  artwork on the figure using the currently configured style pool (M3 integration point — for
  M2, a placeholder/stub style resolution is acceptable if M3 is not yet complete; see
  Assumptions).
- **FR-008**: `import catplotlib` MUST NOT raise under any backend, including headless (`Agg`).
- **FR-009**: Hook installation MUST be idempotent at the process level: importing catplotlib
  multiple times, or any equivalent re-entry into the installation code path, MUST NOT
  double-wrap the draw method or cause repeated/duplicate decoration.
- **FR-010**: Across the chart-type × figsize × legend-presence test matrix (line, bar, scatter,
  histogram; small/default/large figsizes; with/without legend), no placed cat's bounding box
  MUST intersect any extracted exclusion rectangle.

### Key Entities

- **Draw hook**: the installed wrapper around `Figure.draw` that triggers decoration once per
  figure instance.
- **Decoration flag**: per-figure-instance state recording whether that figure has already been
  decorated, used to guarantee idempotency (FR-003).
- **Exclusion extractor**: the function that, given a live (rendered-once) `Figure`, returns the
  list of `Rect` exclusion zones M1's `place_cats()` expects.
- **Session enabled state**: the global on/off flag `enable()`/`disable()` mutate, already
  modeled as `Config.enabled` in `core/config.py` from M0.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a fresh process, `import matplotlib.pyplot as plt; import catplotlib` followed
  by creating and saving any figure produces a saved file containing cat artwork, in 100% of
  runs across the Agg backend.
- **SC-002**: A figure redrawn 5 times in a row (without content changes) has an identical count
  and identical placement data for its cat artists after every redraw, in 100% of trials.
- **SC-003**: After `catplotlib.disable()`, saved figure bytes are identical to a
  no-catplotlib-imported baseline in 100% of trials across the chart-type test matrix.
- **SC-004**: Across the full chart-type × figsize × legend-presence matrix (STANDUP_PLAN.md §8),
  zero cat-artist/protected-element bbox intersections occur in 100% of rendered figures.
- **SC-005**: `import catplotlib` completes without raising in 100% of runs under the `Agg`
  backend in a headless (no-display) environment.

## Assumptions

- M3 (style system) may not be complete when M2 implementation starts. The render layer's
  artist-drawing step (FR-007) depends on a resolved style/image to draw for each placement; if
  M3's registry isn't ready, M2 ships against a minimal internal stub (e.g. a single simple
  placeholder shape) that satisfies M2's own acceptance criteria (decoration exists, doesn't
  overlap, is idempotent, disables cleanly) without waiting on M3. Wiring the real asset registry
  in is a small follow-up once M3 lands, not a redesign.
- `disable()` stops *new* decoration; it does not retroactively strip cats already added to a
  figure that was decorated before `disable()` was called (User Story 3, Acceptance Scenario 3).
  This matches PRD requirement 7's framing ("turn the effect off ... for the rest of the
  script") rather than an "undo everything already drawn" requirement.
- The draw hook is installed exactly once per process, at import time, by replacing
  `matplotlib.figure.Figure.draw` with a wrapper. It is never unpatched/repatched; the wrapper
  itself checks `Config.enabled` on every call and is a pure pass-through to the original draw
  method when disabled.
