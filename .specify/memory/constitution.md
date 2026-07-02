# meowplotlib Constitution

This file mirrors the project's canonical [constitution.md](../../constitution.md) at the repo
root, adapted to Spec Kit's principle format so `/speckit.plan` and friends can reference it
directly. The root file is the source of truth; update both together.

## Core Principles

### I. Core Purity
`src/meowplotlib/core/` SHALL NOT import matplotlib or perform I/O. All matplotlib knowledge lives
in `render/`. Enforced by `tests/core/test_purity.py`.

### II. Non-Destructive Rendering (NON-NEGOTIABLE)
At default settings, cat artwork SHALL NOT intersect the data area, axis labels, tick labels, or
legend of any figure. Enforced by automated bbox-intersection tests across the chart-type ×
figsize × legend matrix.

### III. Reproducibility
WHEN the same seed is set, repeated renders of the same figure SHALL produce identical cat
placements. WHEN no seed is set, consecutive renders SHALL visibly differ.

### IV. Clean Disable
WHEN `meowplotlib.disable()` has been called, figure output SHALL be byte-identical to output
without meowplotlib imported.

### V. Never Raise on Import
`import meowplotlib` SHALL never raise, regardless of backend or headless environment. Enforced
under the `Agg` backend.

### VI. Minimal Footprint
The package SHALL make no network calls and add no required dependencies beyond matplotlib
(numpy acceptable as a transitive dependency).

### VII. Zero-Code Style Extension
Every style SHALL be defined purely by files under `assets/images/<style>/` plus a manifest
entry — adding a style SHALL require zero code changes.

## Quality Gates

`make check` (ruff + ruff format --check + mypy --strict + pytest) SHALL pass before any task is
declared done. Changes SHALL NOT lower test coverage. The public API SHALL remain exactly:
import side-effect, `enable()`, `disable()`, `set_style()`, `set_density()`, `set_seed()`,
`config()` context manager — additions require a spec in `specs/` first.

## Development Workflow

M0 (scaffold) and M4 (config/polish/packaging) are direct implementation, no spec required.
M1 (core placement), M2 (matplotlib integration), M3 (style system) each require the full
`/speckit.specify` → `/speckit.clarify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`
flow, verified against the spec's EARS acceptance criteria — not just green tests. See
`STANDUP_PLAN.md` for the full execution contract.

## Governance

This constitution supersedes ad hoc practice. No AI tool or assistant SHALL be listed as an
author, co-author, or contributor on any commit, tag, or release in this repository. Amendments
require updating both this file and the root `constitution.md` together.

**Version**: 1.0.0 | **Ratified**: 2026-07-02 | **Last Amended**: 2026-07-02
