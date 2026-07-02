# Tasks: Matplotlib Integration & Activation

**Input**: Design documents from `specs/002-matplotlib-integration/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/hook-api.md, quickstart.md

**Tests**: Included — constitution #2/#4/#5 and STANDUP_PLAN.md §8's render-integration matrix
require automated verification; this is the riskiest milestone and is not shipped untested.

**Organization**: Tasks are grouped by user story (spec.md priorities). All four stories build
on one shared hook, so later stories extend rather than duplicate earlier work.

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

Single project. `src/catplotlib/render/`, `tests/render/` — stubbed in M0, filled in here.

---

## Phase 1: Setup

- [x] T001 Confirm `MPLBACKEND=Agg` is usable in the active venv (`python -c "import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt; plt.figure()"`); no code change expected.
- [x] T002 Create `tests/render/__init__.py` (empty) — M0 created the `tests/render/` directory but this package init may not yet exist for the new test modules.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The exclusion extractor and artist-drawing helper that the hook wrapper calls into.

**⚠️ CRITICAL**: No user story can be verified until this phase is complete — the hook wrapper
needs both to do anything observable.

- [x] T003 [P] Implement `extract_exclusions(figure) -> list[Rect]` in `src/catplotlib/render/bboxes.py`: for each `Axes` in `figure.axes`, compute `get_tightbbox()` (+ legend extent if `ax.get_legend()` is not `None`), convert to figure-fraction `Rect` via `figure.transFigure.inverted()`, per research.md/data-model.md. Obtain the renderer via `figure._get_renderer()`.
- [x] T004 [P] Implement a minimal internal style stub (single placeholder shape resolver) plus `draw_placements(figure, placements) -> None` in `src/catplotlib/render/artist.py`, adding one artist per `Placement` via `figure.add_artist(...)`, positioned/sized/rotated per data-model.md. Per research.md's Assumption, this does not depend on M3.
- [x] T005 [P] `tests/render/test_bboxes.py`: example tests asserting `extract_exclusions()` returns bboxes that actually cover a known axes' plotted line, its axis labels, and (when present) its legend, for a simple reference figure.

**Checkpoint**: `bboxes.extract_exclusions()` and `artist.draw_placements()` are independently callable and tested against a live (but not-yet-hooked) figure.

---

## Phase 3: User Story 1 - One import, cats everywhere (Priority: P1) 🎯 MVP

**Goal**: `import catplotlib` causes the next displayed or saved figure to contain cat artwork.

**Independent Test**: Fresh process, `import matplotlib.pyplot as plt; import catplotlib`,
create+savefig a simple line plot, assert `_catplotlib_decorated` is `True` and the figure has
extra artists beyond the plotted line.

### Tests for User Story 1

- [x] T006 [P] [US1] `tests/render/test_hook.py`: `import catplotlib` under `Agg` does not raise (FR-008/SC-005).
- [x] T007 [US1] `tests/render/test_hook.py`: create a figure, plot a line, `savefig` to a `BytesIO` buffer; assert `figure._catplotlib_decorated is True` and `len(figure.artists) > 0` after.
- [x] T008 [US1] `tests/render/test_hook.py`: same as T007 but trigger via `figure.canvas.draw()` directly (the non-savefig display path) instead of `savefig`, confirming FR-002's shared interception point.

### Implementation for User Story 1

- [x] T009 [US1] Implement `install()` in `src/catplotlib/render/hook.py`: wraps `matplotlib.figure.Figure.draw` with a function that (per data-model.md's state machine) checks `Config.enabled` and `self._catplotlib_decorated`, and on the decorate branch calls `bboxes.extract_exclusions` → `core.placement.place_cats` → `artist.draw_placements`, sets the flag, then always calls the original `draw()` (depends on T003, T004).
- [x] T010 [US1] Wire `render.hook.install()` into `src/catplotlib/__init__.py` so it runs at import time (depends on T009).

**Checkpoint**: User Story 1 fully functional — `import catplotlib` alone produces decorated output for both display and savefig paths.

---

## Phase 4: User Story 2 - Decoration never duplicates on redraw (Priority: P1)

**Goal**: Redrawing an already-decorated figure any number of times never changes its cat artist
count or placements.

**Independent Test**: Decorate a figure once, call `figure.canvas.draw()` 5 times, assert
constant artist count and identical placement data throughout.

### Tests for User Story 2

- [x] T011 [P] [US2] `tests/render/test_hook.py`: after initial decoration, call `figure.canvas.draw()` 5 more times; assert `len(figure.artists)` is unchanged after every call (SC-002).
- [x] T012 [P] [US2] `tests/render/test_hook.py`: after initial decoration, call `savefig` to a second buffer; assert the second buffer's bytes equal the first buffer's bytes (decoration didn't change between saves).

### Implementation for User Story 2

- [x] T013 [US2] Verify the T009 flag-check guards decoration correctly across repeated calls (should require no new code if T009 was implemented per data-model.md — this task is verification + any fix needed, e.g. ensuring the flag is read via `getattr` with a `False` default so it works on figures created before `install()` ran).

**Checkpoint**: User Stories 1 AND 2 both pass independently.

---

## Phase 5: User Story 3 - Session on/off switch (Priority: P1)

**Goal**: `disable()` makes all subsequently rendered *new* figures byte-identical to
matplotlib-alone output; `enable()` restores decoration afterward.

**Independent Test**: Render+save with catplotlib active; `disable()`; render+save an equivalent
fresh figure; assert its bytes equal a no-catplotlib-imported baseline. `enable()`; render+save
again; assert cats are back.

### Tests for User Story 3

- [x] T014 [P] [US3] `tests/render/test_hook.py`: generate a true baseline by rendering a reference figure in a subprocess that never imports catplotlib (`subprocess.run([sys.executable, "-c", ...])`) and capturing its saved bytes.
- [x] T015 [US3] `tests/render/test_hook.py`: in-process, call `catplotlib.disable()`, render+save an equivalent fresh figure, assert its bytes equal the T014 baseline (SC-003, constitution #4).
- [x] T016 [P] [US3] `tests/render/test_hook.py`: `catplotlib.disable()` then `catplotlib.enable()`; render+save a fresh figure; assert `_catplotlib_decorated is True` again (FR-005).
- [x] T017 [P] [US3] `tests/render/test_hook.py`: decorate a figure, then call `catplotlib.disable()`; assert the already-decorated figure's existing artists are untouched (spec User Story 3, Acceptance Scenario 3).

### Implementation for User Story 3

- [x] T018 [US3] Confirm the T009 wrapper's `Config.enabled` check is the very first thing evaluated and that the `False` branch calls only the original `draw()` with no other catplotlib code path executed (per research.md's byte-identity rationale) — fix if any extraction/logging/etc. runs before the check (depends on T009).

**Checkpoint**: User Stories 1-3 all pass independently.

---

## Phase 6: User Story 4 - Cats respect every chart's real layout (Priority: P1)

**Goal**: Across the chart-type × figsize × legend-presence matrix, no cat bbox intersects any
real extracted exclusion.

**Independent Test**: Render each matrix cell, extract placed-cat bboxes and protected-element
bboxes, assert empty intersection (the STANDUP_PLAN.md §8 harness).

### Tests for User Story 4

- [x] T019 [US4] `tests/render/test_matrix.py`: build the reference matrix — chart types {line, bar, scatter, histogram} × figsizes {small (2x2in), default (6.4x4.8in), large (12x9in)} × legend {present, absent} = 24 cells.
- [x] T020 [US4] `tests/render/test_matrix.py`: for each matrix cell, render under `Agg`, extract placed cat artist bboxes (from the `Placement` data used to draw them, or by re-deriving bboxes from the added artists) and exclusion bboxes via `bboxes.extract_exclusions`, assert zero intersections (SC-004). Use `pytest.mark.parametrize` over the 24 cells so failures identify the specific offending cell.

### Implementation for User Story 4

- [x] T021 [US4] Fix any matrix-cell failures found by T020 — likely candidates per research.md: legend extent not included for axes without `ax.legend()` called explicitly vs. implicitly, or tight-bbox coordinate conversion edge cases at very small figsizes (depends on T003, T020).

**Checkpoint**: All four user stories pass independently. Matplotlib integration feature-complete.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [x] T022 [P] Add a seaborn smoke test: `import seaborn; import catplotlib` (order matters not — both should compose), plot a seaborn chart, assert decoration + non-overlap hold, in `tests/render/test_hook.py` (spec edge case: "seaborn compatibility"). Skip gracefully if `seaborn` is not installed (it's not a project dependency).
- [x] T023 [P] Add a "figure created before import" test: construct a `Figure()` via a saved reference *before* `catplotlib.render.hook.install()` is called in a fresh subprocess sequence, then `import catplotlib`, then draw it — assert it still decorates (spec edge case).
- [x] T024 Run `quickstart.md`'s manual smoke script end-to-end and confirm all assertions pass.
- [x] T025 Run `make check` (ruff, ruff format --check, mypy --strict, pytest) and confirm all green, including the full `tests/render/` matrix.
- [ ] T026 Update `PROGRESS.md`: mark M2 complete, note next milestone is M3 (or M2.5 — the M3 stub in `artist.py` becoming the real registry).

---

## Dependencies & Execution Order

- **Setup (Phase 1)** → **Foundational (Phase 2)**: blocks all user stories.
- **US1 (Phase 3)**: the MVP — installs the hook, gets basic decoration working.
- **US2 (Phase 4)**: depends on US1's wrapper existing (T009) — hardens/verifies idempotency of the same code path.
- **US3 (Phase 5)**: depends on US1's wrapper existing (T009) — hardens/verifies the enabled-flag branch of the same code path.
- **US4 (Phase 6)**: depends on Foundational's `extract_exclusions` (T003) and US1's end-to-end pipeline (T010) — this is where the pipeline gets stress-tested against real chart variety.
- **Polish (Phase 7)**: depends on all four stories complete.

### Parallel Opportunities

- T003-T005 (Foundational) can run in parallel.
- T006/T014/T016/T017 and similar `[P]`-marked test tasks within a phase can run in parallel;
  same file-overlap caveat as M1's tasks.md applies (conceptually independent commits, not
  literally concurrent edits).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Setup + Foundational.
2. US1 → commit. This alone gives basic "import and cats appear" behavior, unverified for
   idempotency, disable, or layout accuracy.
3. **STOP and VALIDATE**: run US1's tests independently.

### Incremental Delivery

1. Foundational → US1 (MVP) → commit.
2. US2 (idempotency) → commit.
3. US3 (enable/disable byte-identity) → commit.
4. US4 (real chart-matrix non-overlap) → commit.
5. Polish (seaborn smoke test, quickstart validation, `make check`, PROGRESS.md) → commit.

Each step's `make check` must be green before its commit (constitution #8).
