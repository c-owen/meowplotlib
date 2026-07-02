# Implementation Plan: Style System & Assets

**Branch**: `003-style-system` | **Date**: 2026-07-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-style-system/spec.md`

## Summary

Implement `assets/registry.py` to discover styles from `assets/images/<name>/` + `styles.toml`,
resolve `set_style()`'s various input shapes to a flat style-name list, and replace M2's
hardcoded single-image render stub with real per-style, per-placement image resolution —
deterministic (not RNG-based) so seeded reproducibility survives multi-image pools intact. See
[research.md](research.md) for the TOML-without-a-dependency and deterministic-pool-index
decisions.

## Technical Context

**Language/Version**: Python 3.10+ (unchanged).

**Primary Dependencies**: None new. `tomllib` used conditionally (stdlib, 3.11+); a small
first-party fallback parser covers 3.10 for our specific manifest subset (research.md).

**Storage**: N/A — reads from the package's own bundled `assets/` tree via
`importlib.resources`, per STANDUP_PLAN.md's packaging note (never `__file__`-relative paths for
installed data).

**Testing**: `pytest`, example-based (small, enumerable input space — style names, manifest
shapes). No `hypothesis` needed here.

**Target Platform**: Same as M1/M2.

**Project Type**: Library module — fills in M0's `assets/registry.py` stub, modifies M2's
`render/artist.py`.

**Performance Goals**: Registry scan is a handful of directory listings + a small manifest
parse; no explicit numeric target, cost is negligible at the scale involved (single-digit style
count).

**Constraints**: Zero new required dependencies (constitution #6); zero-code-change style
addition (constitution #7); must not regress M1/M2's seed-reproducibility guarantee through
multi-image pool selection.

**Scale/Scope**: One module filled in (`assets/registry.py`), one small first-party TOML-subset
parser (`assets/_toml_fallback.py` or inlined), one function signature change in
`render/artist.py`, one new test package (`tests/assets/`).

## Constitution Check

*GATE: Must pass before Phase 0 research (already conducted above). Re-checked after Phase 1
design below.*

| Rule | Status | Notes |
|---|---|---|
| #1 Core purity | PASS | No changes to `core/`; `PlacementConfig.styles` remains a flat `list[str]`, unchanged contract. |
| #3 Seed reproducibility | PASS (design-level) | Deterministic hash-based pool index (research.md) — same seed → same placements → same images, no new randomness source. |
| #6 No network calls, minimal deps | PASS (design-level) | `tomllib` (stdlib 3.11+) + first-party fallback parser for 3.10, zero new installable dependencies. |
| #7 Zero-code-change style extension | PASS (design-level) | FR-006/SC-003 — registry re-scans the filesystem each call; a fixture-registered temp style is discoverable with no code changes, tested directly. |
| #8 `make check` gate | PASS (process) | Enforced every commit. |
| #9 Public API surface unchanged | PASS | `set_style()` already exists in `api.py` from M0; this milestone implements its real effect (including the new fail-fast validation), doesn't add new public functions. |

No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/003-style-system/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── registry-api.md
└── tasks.md   # /speckit-tasks output, not yet created
```

### Source Code (repository root)

```text
src/catplotlib/
├── api.py                  # set_style(): add eager validation via registry.resolve_style_names
├── assets/
│   ├── registry.py          # discover_styles(), available_styles(), resolve_style_names()
│   └── _toml_fallback.py    # minimal parser for styles.toml on Python 3.10 (no tomllib)
└── render/
    └── artist.py             # _resolve_image(placement) replaces M2's _resolve_image(style)

tests/assets/
└── test_registry.py          # discovery, resolve_style_names, fixture-style zero-code-change test
```

**Structure Decision**: Single-project layout, same as M1/M2 — fills in M0's `assets/registry.py`
stub, adds one small new file for the TOML fallback, modifies M2's `render/artist.py` in place
(signature change, not a new module).

## Complexity Tracking

*No Constitution Check violations — section intentionally empty.*
