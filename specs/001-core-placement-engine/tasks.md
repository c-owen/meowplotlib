# Tasks: Core Placement Engine

**Input**: Design documents from `specs/001-core-placement-engine/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/placement-api.md, quickstart.md

**Tests**: Included — STANDUP_PLAN.md §8 and constitution #2/#3 require property-based
verification of the non-overlap and reproducibility guarantees; this is not optional for M1.

**Organization**: Tasks are grouped by user story (spec.md priorities) so each can be
implemented and verified independently, though all four share one underlying algorithm.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US4)

## Path Conventions

Single project. `src/catplotlib/core/`, `tests/core/` — already scaffolded in M0.

---

## Phase 1: Setup

**Purpose**: Nothing new required — M0 already created `src/catplotlib/core/placement.py`,
`src/catplotlib/core/rng.py`, and `tests/core/` as empty/stub files, and `hypothesis` is already
a dev dependency in `pyproject.toml`.

- [ ] T001 Confirm `hypothesis` is importable in the active venv (`python -c "import hypothesis"`); no code change expected.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared types and RNG wrapper that every user story's implementation depends on.

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete.

- [ ] T002 [P] Implement `Rect` frozen dataclass with `intersects()` in `src/catplotlib/core/placement.py` (per data-model.md).
- [ ] T003 [P] Implement `PlacementConfig` and `Placement` frozen dataclasses (with `Placement.bbox()`) in `src/catplotlib/core/placement.py` (per data-model.md).
- [ ] T004 [P] Implement seeded RNG wrapper in `src/catplotlib/core/rng.py`: a function that returns a `random.Random` instance from an `int | None` seed, per research.md's "stdlib random.Random" decision.
- [ ] T005 [P] Set up `tests/core/test_placement.py` with `hypothesis` strategies for canvas sizes (including zero/negative), exclusion rectangle lists (0-N, including overlapping), density tiers, and optional seeds — no test bodies yet, just the shared strategies module-level.

**Checkpoint**: `Rect`, `PlacementConfig`, `Placement`, and the RNG helper exist and are unit-importable; `tests/core/test_purity.py` from M0 still passes (no matplotlib import introduced).

---

## Phase 3: User Story 1 - Cats never cover the chart (Priority: P1) 🎯 MVP

**Goal**: `place_cats()` returns placements that never intersect any exclusion rectangle, the
edge margin, or each other.

**Independent Test**: Call `place_cats()` with a fixed canvas, fixed exclusions, any config;
assert zero bounding-box intersections between every placement and every exclusion, and between
every pair of placements.

### Tests for User Story 1

> Write these first; they should fail against a stub/empty `place_cats()`.

- [ ] T006 [P] [US1] Example test: centered exclusion rectangle → no placement intersects it, in `tests/core/test_placement.py`.
- [ ] T007 [P] [US1] Example test: exclusion covering nearly the whole canvas → placements (if any) fit only in remaining slivers, in `tests/core/test_placement.py`.
- [ ] T008 [US1] Hypothesis property test implementing SC-001: across randomized canvases/exclusions/densities/seeds, 100% of placements have zero bbox intersection with every exclusion AND the edge margin, in `tests/core/test_placement.py`.
- [ ] T009 [US1] Hypothesis property test for FR-003a: across the same randomized inputs, no two placements in one result intersect each other, in `tests/core/test_placement.py`.

### Implementation for User Story 1

- [ ] T010 [US1] Implement the fixed edge-margin band (~3% of the smaller canvas dimension) as an implicit exclusion in `place_cats()`, `src/catplotlib/core/placement.py` (depends on T002-T004).
- [ ] T011 [US1] Implement rejection-sampling candidate placement (random center/size within size_range, tested against margin + exclusions + already-accepted placements) in `src/catplotlib/core/placement.py` (depends on T010).
- [ ] T012 [US1] Implement shrink-on-failure retry loop (bounded attempts, then shrink size by fixed factor down to size_range minimum, then skip the candidate) in `src/catplotlib/core/placement.py` (depends on T011).
- [ ] T013 [US1] Wire `place_cats()` public function signature per contracts/placement-api.md, handling the `canvas_width <= 0`, `canvas_height <= 0`, and empty-`styles` early-return cases (FR-008, postconditions 2-3), in `src/catplotlib/core/placement.py` (depends on T012).

**Checkpoint**: User Story 1 fully functional — `place_cats()` never violates exclusions, margin, or cat-cat overlap. All T006-T009 tests pass.

---

## Phase 4: User Story 2 - Reproducible layouts with a seed (Priority: P1)

**Goal**: Identical inputs + identical seed → identical output; no seed → visibly different
consecutive outputs.

**Independent Test**: Call `place_cats()` twice with identical inputs including a fixed seed;
assert element-for-element identical results. Repeat with `seed=None`; assert the two results
differ.

### Tests for User Story 2

- [ ] T014 [P] [US2] Example test: fixed seed, two calls with identical inputs → identical placement lists, in `tests/core/test_placement.py`.
- [ ] T015 [P] [US2] Example test: `seed=None`, two consecutive calls with identical other inputs → different placement lists, in `tests/core/test_placement.py`.
- [ ] T016 [US2] Hypothesis property test implementing SC-002: across randomized inputs with a fixed seed, repeated calls produce byte-for-byte identical output in 100% of trials, in `tests/core/test_placement.py`.

### Implementation for User Story 2

- [ ] T017 [US2] Ensure `place_cats()` threads a single `random.Random` instance (from T004's wrapper) through the entire call with no other source of randomness or global state touched, in `src/catplotlib/core/placement.py` (depends on T013; should require no algorithm change if T004-T013 were built correctly — this task is verification + any fix needed).

**Checkpoint**: User Stories 1 AND 2 both pass independently.

---

## Phase 5: User Story 3 - Density controls how populated the figure feels (Priority: P2)

**Goal**: `sparse < normal < chaotic` placement counts on a fixed reference canvas.

**Independent Test**: Call `place_cats()` three times on the same reference canvas/seed varying
only density; assert strictly increasing counts.

### Tests for User Story 3

- [ ] T018 [US3] Example test: reference canvas, fixed seed, three density tiers → strictly increasing placement counts, in `tests/core/test_placement.py`.
- [ ] T019 [US3] Hypothesis property test implementing SC-003: across ≥20 different seeds on the reference canvas, sparse < normal < chaotic holds every time, in `tests/core/test_placement.py`.

### Implementation for User Story 3

- [ ] T020 [US3] Implement the area-scaled target-count formula (available border area × per-tier multiplier, tiers strictly increasing) in `src/catplotlib/core/placement.py`, feeding the candidate-count loop from T011 (depends on T013).
- [ ] T021 [US3] Tune the three per-tier multiplier constants so T018/T019 pass on the reference canvas used in quickstart.md, in `src/catplotlib/core/placement.py` (depends on T020).

**Checkpoint**: User Stories 1-3 all pass independently.

---

## Phase 6: User Story 4 - Small figures degrade gracefully (Priority: P2)

**Goal**: As available border area shrinks toward zero, placement count/size shrinks toward
zero; at exactly zero available area, `place_cats()` returns `[]`, never an exception.

**Independent Test**: Sweep canvas/exclusion sizes from generous down to fully-covering; assert
non-increasing placement count, zero exceptions, and exactly zero placements at zero area.

### Tests for User Story 4

- [ ] T022 [P] [US4] Example test: exclusion rectangle exactly covering the canvas → `place_cats()` returns `[]`, in `tests/core/test_placement.py`.
- [ ] T023 [P] [US4] Example test: zero/negative canvas width or height → `place_cats()` returns `[]` without raising, in `tests/core/test_placement.py`.
- [ ] T024 [US4] Hypothesis property test implementing SC-004: sweeping available border area from generous to zero, placement count is non-increasing and hits exactly zero at zero area, with zero exceptions across the sweep, in `tests/core/test_placement.py`.

### Implementation for User Story 4

- [ ] T025 [US4] Verify the T020 area-scaled formula naturally produces zero target count at zero available area (should require no new code per research.md's design — this task is verification + any edge-case fix, e.g. clamping negative area to zero), in `src/catplotlib/core/placement.py` (depends on T020).

**Checkpoint**: All four user stories pass independently. Core placement engine feature-complete.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final gates before declaring M1 done.

- [ ] T026 [P] Add/verify SC-005 test: static-analysis check that `placement.py` and `rng.py` import zero matplotlib/I-O symbols (should already be covered by M0's `tests/core/test_purity.py` since it globs `core/*.py` — confirm coverage, no new code expected).
- [ ] T027 Run `quickstart.md`'s manual smoke script end-to-end and confirm all assertions pass.
- [ ] T028 Run `make check` (or the four commands directly) — ruff, ruff format --check, mypy --strict, pytest — and confirm all green.
- [ ] T029 Update `PROGRESS.md`: mark M1 complete, note next milestone is M2.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories.
- **US1 (Phase 3)**: Depends on Foundational. This is the MVP — the other three stories are
  properties/refinements of the same `place_cats()` function US1 builds.
- **US2 (Phase 4)**: Depends on US1's `place_cats()` existing (T013) — verifies/hardens
  determinism of the same code path, not a separate implementation.
- **US3 (Phase 5)**: Depends on US1's `place_cats()` existing (T013) — adds the density formula
  on top of the same candidate loop.
- **US4 (Phase 6)**: Depends on US3's area-scaled formula (T020) — degradation is that formula's
  behavior at low/zero area, not new logic.
- **Polish (Phase 7)**: Depends on all four user stories complete.

### Parallel Opportunities

- T002-T005 (Foundational) can run in parallel — different concerns within one growing file, but
  no task depends on another's output within this phase.
- T006-T007 (US1 example tests) can run in parallel with each other; T008-T009 (US1 property
  tests) depend on the test-strategy scaffolding from T005 but not on each other.
- T014-T015 (US2 example tests) can run in parallel.
- T022-T023 (US4 example tests) can run in parallel.

**Note on file overlap**: Because `placement.py` and `test_placement.py` are single files
touched by nearly every task, "parallel" here means conceptually independent, easily-reviewed
diffs landed as separate commits — not literally concurrent edits to the same file by multiple
agents. Follow the code → test → commit cadence per task or small task group.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (trivial) + Phase 2 (Foundational).
2. Complete Phase 3 (US1) — commit. This alone gives a correct, safe (if density/seed/degradation
   are not yet tuned) placement engine.
3. **STOP and VALIDATE**: run US1's tests independently.

### Incremental Delivery

1. Foundational → US1 (MVP, non-overlap guarantee) → commit.
2. US2 (reproducibility) → commit.
3. US3 (density tiers) → commit.
4. US4 (graceful degradation, built on US3) → commit.
5. Polish (quickstart validation, `make check`, PROGRESS.md) → commit.

Each step's `make check` must be green before its commit (constitution #8).
