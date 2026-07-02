# Implementation Plan: Core Placement Engine

**Branch**: `001-core-placement-engine` | **Date**: 2026-07-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-core-placement-engine/spec.md`

## Summary

Implement a pure-Python placement engine (`core/placement.py` + `core/rng.py`) that, given
canvas dimensions, exclusion rectangles, and a density/size/seed/styles config, returns a list
of non-overlapping cat placements confined to the canvas border region. Uses seeded rejection
sampling with shrink-on-failure against exclusion zones, a fixed edge margin, and previously
accepted placements in the same call; target count is area-scaled per density tier so graceful
degradation on small figures is an emergent property of the same formula rather than a special
case. See [research.md](research.md) for the algorithm/RNG/testing-strategy decisions.

## Technical Context

**Language/Version**: Python 3.10+ (per pyproject.toml `requires-python`)

**Primary Dependencies**: None beyond the standard library (`dataclasses`, `random`, `math`,
`typing`) for the implementation itself. `hypothesis` (already a dev dependency) for
property-based tests.

**Storage**: N/A — pure in-memory computation, no I/O (constitution #1).

**Testing**: `pytest` + `hypothesis`, per STANDUP_PLAN.md §8.

**Target Platform**: Anywhere Python 3.10+ and matplotlib run (this module itself has no
platform dependency at all — it doesn't even import matplotlib).

**Project Type**: Library module (single project — no frontend/backend/mobile split).

**Performance Goals**: Not performance-critical; a single figure typically requests O(1)-O(50)
placements. No explicit numeric target — correctness (never violating exclusions) dominates.

**Constraints**: Must remain free of matplotlib imports and I/O (constitution #1, verified by
`tests/core/test_purity.py`, already in place from M0).

**Scale/Scope**: Two new modules (~150-250 LOC combined), one new test module using both
example-based and `hypothesis` property-based tests.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design below.*

| Rule | Status | Notes |
|---|---|---|
| #1 Core purity (no matplotlib/I-O in `core/`) | PASS | Confirmed in research.md — stdlib `random` + `dataclasses` only. Enforced by existing `tests/core/test_purity.py`. |
| #2 Non-destructive rendering | PASS (design-level) | FR-002/FR-003/FR-003a make exclusion/edge/cat-cat overlap structurally impossible to violate; verified by hypothesis property tests (SC-001). |
| #3 Seed reproducibility | PASS (design-level) | Single `random.Random(seed)` threaded explicitly through one call, no global RNG state (FR-004, FR-009). |
| #6 No network calls, minimal deps | PASS | Zero new runtime dependencies. |
| #8 `make check` gate | PASS (process) | Will run ruff/mypy strict/pytest before every commit in this milestone. |
| #9 Public API surface unchanged | PASS | This module is internal (`core/`), not part of the six public `api.py` functions; no public surface change. |

No violations requiring justification — Complexity Tracking section is empty/omitted.

## Project Structure

### Documentation (this feature)

```text
specs/001-core-placement-engine/
├── plan.md              # This file
├── research.md           # Phase 0 output
├── data-model.md         # Phase 1 output
├── quickstart.md         # Phase 1 output
├── contracts/
│   └── placement-api.md  # Phase 1 output
└── tasks.md              # Phase 2 output (/speckit-tasks — not yet created)
```

### Source Code (repository root)

```text
src/meowplotlib/core/
├── placement.py    # Rect, PlacementConfig, Placement dataclasses + place_cats()
└── rng.py          # thin seeded-RNG helper used by placement.py

tests/core/
└── test_placement.py   # example-based + hypothesis property-based tests
```

**Structure Decision**: Single-project library layout already established in M0
(`src/meowplotlib/core/`, `tests/core/`). No new top-level directories needed — this feature
fills in two files that were stubbed out in M0's scaffold.

## Complexity Tracking

*No Constitution Check violations — section intentionally empty.*
