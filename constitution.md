# catplotlib — Constitution

Non-negotiables for this project. Each rule is testable; several are enforced directly by hooks or tests.

1. `src/catplotlib/core/` SHALL NOT import matplotlib or perform I/O. (Enforced: a test that greps imports in `core/`.)
2. At default settings, cat artwork SHALL NOT intersect the data area, axis labels, tick labels, or legend of any figure. (Enforced: automated bbox-intersection tests.)
3. WHEN the same seed is set, repeated renders of the same figure SHALL produce identical cat placements. (Enforced: test.)
4. WHEN `catplotlib.disable()` has been called, figure output SHALL be byte-identical to output without catplotlib imported. (Enforced: test comparing savefig bytes.)
5. `import catplotlib` SHALL never raise, regardless of backend or headless environment. (Enforced: test under `Agg`.)
6. The package SHALL make no network calls and add no required dependencies beyond matplotlib (numpy acceptable as transitive).
7. Every style SHALL be defined purely by files under `assets/images/<style>/` plus a manifest entry — adding a style SHALL require zero code changes. (Enforced: test that registers a temp style dir.)
8. `make check` SHALL pass (ruff + mypy --strict + pytest) before any task is declared done. Changes SHALL NOT lower test coverage.
9. Public API SHALL remain: import side-effect, `enable()`, `disable()`, `set_style()`, `set_density()`, `set_seed()`, `config()` context manager. Additions require a spec in `specs/` first.
10. No AI tool or assistant SHALL be listed as an author, co-author, or contributor on any commit, tag, or release in this repository.

See `STANDUP_PLAN.md` for the full execution contract and milestone sequence.
