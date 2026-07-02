# Implementation Plan: Matplotlib Integration & Activation

**Branch**: `002-matplotlib-integration` | **Date**: 2026-07-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-matplotlib-integration/spec.md`

## Summary

Wire M1's pure placement engine into live matplotlib figures. Monkeypatch
`matplotlib.figure.Figure.draw` once at import time; the wrapper checks `Config.enabled` and a
per-instance `_meowplotlib_decorated` flag, extracts whole-axes tight-bbox exclusions, calls
`place_cats()`, and adds the resulting cat artists — all before delegating to the original draw.
`disable()`/`enable()` only flip `Config.enabled`; the patch itself is permanent and never
reversed. See [research.md](research.md) for the matplotlib-internals findings this is based on.

## Technical Context

**Language/Version**: Python 3.10+ (unchanged from M0/M1)

**Primary Dependencies**: `matplotlib` (already a required dependency). No new dependencies.

**Storage**: N/A.

**Testing**: `pytest` under the `Agg` backend (headless-safe, matches CI). `hypothesis` not
needed here — M2's guarantees are about a fixed, enumerable test matrix (chart types × figsizes
× legend presence), not a property over an open input space; example-based tests are the right
tool (matches STANDUP_PLAN.md §8's "render integration" testing strategy description).

**Target Platform**: Anywhere matplotlib runs; explicitly verified headless (`Agg`).

**Project Type**: Library module — new code lives entirely in `src/meowplotlib/render/` (already
stubbed in M0) plus a small addition to `src/meowplotlib/__init__.py` to call `hook.install()`.

**Performance Goals**: Decoration adds a bounded, small amount of work (bbox extraction + M1's
placement algorithm, both O(placements × exclusions)) to each figure's *first* draw only;
subsequent redraws pay only the idempotency-flag check. No explicit numeric target.

**Constraints**: Must never raise on import (constitution #5); disabled output must be
byte-identical to unpatched matplotlib (constitution #4); must work under `Agg`.

**Scale/Scope**: Three new modules filled in (`render/hook.py`, `render/bboxes.py`,
`render/artist.py`), one new `install()` call wired into `__init__.py`, one new test package
(`tests/render/`) covering the chart-type × figsize × legend matrix.

## Constitution Check

*GATE: Must pass before Phase 0 research (already conducted above). Re-checked after Phase 1
design below.*

| Rule | Status | Notes |
|---|---|---|
| #1 Core purity | PASS | This feature adds no code to `core/`; M1's `place_cats()` is called, not modified. |
| #2 Non-destructive rendering | PASS (design-level) | Whole-axes tight bbox extraction feeds M1's already-proven non-overlap guarantee; SC-004 covers the full chart-type matrix. |
| #3 Seed reproducibility | PASS | Unaffected — M2 passes `Config.seed` straight through to M1, no new randomness introduced. |
| #4 Clean disable → byte-identical output | PASS (design-level) | The disabled path in the draw wrapper executes zero meowplotlib code before delegating to the original draw (research.md). |
| #5 Import never raises | PASS (design-level) | `install()` only touches well-established matplotlib APIs (`Figure.draw` attribute assignment) with no I/O or environment-dependent branching. |
| #6 No network calls, minimal deps | PASS | Zero new dependencies. |
| #8 `make check` gate | PASS (process) | Enforced every commit in this milestone. |
| #9 Public API surface unchanged | PASS | `enable()`/`disable()` already exist in `api.py` from M0; this milestone implements their real effect, doesn't add new public functions. |

No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/002-matplotlib-integration/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── hook-api.md
└── tasks.md   # /speckit-tasks output, not yet created
```

### Source Code (repository root)

```text
src/meowplotlib/
├── __init__.py       # add: render.hook.install() call at import time
└── render/
    ├── hook.py        # install() + the Figure.draw wrapper
    ├── bboxes.py       # extract_exclusions(figure) -> list[Rect]
    └── artist.py       # draw_placements(figure, placements) -> None

tests/render/
├── test_hook.py         # idempotency, enable/disable byte-identity, import-never-raises
├── test_bboxes.py        # exclusion extraction correctness on known layouts
└── test_matrix.py        # the chart-type x figsize x legend non-overlap matrix (SC-004)
```

**Structure Decision**: Single-project layout, same as M1 — fills in M0's `render/` stubs and
adds `tests/render/` test modules. No new top-level directories.

## Complexity Tracking

*No Constitution Check violations — section intentionally empty.*
