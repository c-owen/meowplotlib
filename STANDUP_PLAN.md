# catplotlib — Project Standup Plan

**Handoff target:** Claude Sonnet 5 (implementing agent)
**Inputs:** `catplotlib` PRD (Draft v1) + "Standing Up a New Project the Agentic Way" recipe (July 2026)
**Repo root:** this directory (currently empty — you are doing `git init`)
**Scope:** Full P0 v1, stood up per the full recipe (constitution, root map, hooks, Spec Kit, spec-driven features).

---

## 1. Mission

Build `catplotlib`: a pip-installable Python package that adds whimsical cat artwork to the borders of matplotlib figures via a single import. Novelty/delight product — the bar is "charming and screenshot-worthy by default," not data-viz utility. Never obscure data. See the PRD for personas and full rationale; this plan is the execution contract.

## 2. Resolved decisions (do not re-litigate)

1. **Activation model:** opt-out global after import (PRD's assumed default). `import catplotlib` applies cats to all subsequently rendered/saved figures; `catplotlib.disable()` turns it off in-session.
2. **Art assets:** the owner (Chuck) will manually drop image files (likely multiple images per style) into the repo. Licensing is **not** a blocker or a gate for this project — do not build licensing checks or block work on attribution. Keep a simple `ATTRIBUTION.md` listing asset sources as a courtesy, nothing more.
3. **Until real assets arrive:** generate simple programmatic placeholder PNGs (one per style, visually distinct) so development and tests never block on assets. The asset system must make swapping placeholders for real images a pure file-drop (see §7).
4. **Style mix default:** even weighting across styles when mixing. Ship it; adjust later on feedback.
5. **Small-figure default:** automatically reduce cat count/size on small figures (graceful degradation is automatic, not user-managed).
6. **Support:** matplotlib only (seaborn works implicitly). Python ≥3.10. Minimal deps: matplotlib + numpy (already a matplotlib dep) + pillow only if needed for image loading matplotlib can't do natively (it usually can — prefer `plt.imread`).

## 3. Phase 0 — decisions made for you (30 minutes → 0 minutes)

### 3.1 Module boundaries

```
catplotlib/
├── CLAUDE.md                  # lean root map (symlink AGENTS.md → CLAUDE.md)
├── constitution.md            # non-negotiables (§3.2)
├── STANDUP_PLAN.md            # this file
├── ATTRIBUTION.md             # asset sources, courtesy only
├── README.md                  # before/after image at the very top (P0 marketing surface)
├── pyproject.toml             # hatchling build; ruff/mypy/pytest config in-file
├── Makefile                   # `make check` = verify command (§3.3)
├── specs/                     # Spec Kit output, one folder per non-trivial feature
├── evals/                     # empty at start; added only on repeated observed failure (§9)
├── src/catplotlib/
│   ├── __init__.py            # import-time activation + public API re-exports
│   ├── core/                  # PURE logic — no matplotlib imports, no I/O
│   │   ├── config.py          # config dataclass: density, style, seed, enabled, etc.
│   │   ├── placement.py       # geometry: given figure dims + exclusion bboxes → cat placements
│   │   └── rng.py             # seeded RNG wrapper (reproducibility)
│   ├── render/                # matplotlib integration (the impure layer)
│   │   ├── hook.py            # figure draw/savefig interception
│   │   ├── artist.py          # draws placed cats onto the figure
│   │   └── bboxes.py          # extracts exclusion zones (axes, labels, ticks, legend) from a live figure
│   ├── assets/                # style registry + image loading
│   │   ├── registry.py        # discovers styles from the assets dir + manifest
│   │   └── images/            # <style-name>/*.png  ← Chuck's drop-in location
│   └── api.py                 # user-facing functions: enable/disable/set_style/set_density/set_seed/config
├── tests/                     # mirrors src/catplotlib/
│   ├── core/
│   ├── render/
│   └── assets/
├── scripts/
│   └── make_placeholders.py   # generates placeholder style PNGs
└── .claude/
    ├── settings.json          # hooks (§3.4)
    └── skills/                # added when a procedure is pasted twice, not before
```

The `core/` vs `render/` boundary is the load-bearing one: placement math takes plain numbers (figure width/height, list of exclusion rectangles) and returns plain placements (x, y, size, rotation, style). All matplotlib knowledge lives in `render/`. This makes the hardest requirement (non-destructive rendering) unit-testable without rendering a single pixel.

### 3.2 constitution.md — write it with exactly these rules

Each is testable; several are enforced by hooks or tests directly.

1. `src/catplotlib/core/` SHALL NOT import matplotlib or perform I/O. (Enforced: import-linter or a trivial test that greps imports.)
2. At default settings, cat artwork SHALL NOT intersect the data area, axis labels, tick labels, or legend of any figure. (Enforced: automated bbox-intersection tests, §8.)
3. WHEN the same seed is set, repeated renders of the same figure SHALL produce identical cat placements. (Enforced: test.)
4. WHEN `catplotlib.disable()` has been called, figure output SHALL be byte-identical to output without catplotlib imported. (Enforced: test comparing savefig bytes.)
5. `import catplotlib` SHALL never raise, regardless of backend or headless environment. (Enforced: test under `Agg`.)
6. The package SHALL make no network calls and add no required dependencies beyond matplotlib (numpy acceptable as transitive).
7. Every style SHALL be defined purely by files under `assets/images/<style>/` plus a manifest entry — adding a style SHALL require zero code changes. (Enforced: test that registers a temp style dir.)
8. `make check` SHALL pass (ruff + mypy --strict + pytest) before any task is declared done. Changes SHALL NOT lower test coverage.
9. Public API SHALL remain: import side-effect, `enable()`, `disable()`, `set_style()`, `set_density()`, `set_seed()`, `config()` context manager. Additions require a spec in `specs/` first.

### 3.3 Verify command

`Makefile`:

```make
check:
	ruff check src tests && ruff format --check src tests && mypy src && pytest -q
```

All tool config lives in `pyproject.toml`. Use `uv` for env management if available; plain `pip install -e ".[dev]"` otherwise.

### 3.4 Hooks — `.claude/settings.json`

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "ruff check --fix src tests && ruff format src tests && mypy src" }]
      }
    ],
    "Stop": [
      { "hooks": [{ "type": "command", "command": "pytest -q" }] }
    ]
  }
}
```

## 4. Day 1 — scaffold (Milestone 0)

In order:

1. `git init`; create the layout in §3.1 with empty-but-importable packages.
2. Write `constitution.md` (§3.2), `CLAUDE.md` root map (map-not-manual, <150 lines, `file:line` pointers, points at constitution + `make check` + specs workflow), symlink `AGENTS.md`.
3. `pyproject.toml` (hatchling, ruff, mypy strict, pytest), `Makefile`, install dev env, confirm `make check` passes on the empty skeleton.
4. Install hooks (§3.4).
5. Initialize Spec Kit: `uvx --from git+https://github.com/github/spec-kit.git specify init . --integration claude` (adapt its constitution template to §3.2 rather than replacing it).
6. `scripts/make_placeholders.py`: generate three visually distinct placeholder PNGs into `assets/images/{classic,derp,chonk}/` (e.g. simple drawn cat silhouettes in different shapes/colors — distinct at 64px).
7. First commit. From here on: **code → test → commit**, small commits, tests in every commit.

**Definition of done for M0:** `make check` green, hooks firing, spec tooling installed, placeholder assets present, committed.

## 5. Feature sequence (Milestones 1–4)

Recipe rule applied: spec the risky 20%, run direct on the rest. Three features get the full `/speckit.specify → clarify → plan → tasks → implement` treatment; the config surface does not.

### M1 — Core placement engine *(SPEC REQUIRED)*

Pure-logic engine in `core/`. Given: canvas dims, exclusion rectangles, config (density tier, size range, seed, allowed styles). Returns: list of placements (position, size, rotation, style id) confined to the border region, non-overlapping with exclusions, randomized but seed-reproducible.

Key spec questions to resolve in `/speckit.clarify`: border-region definition when axes nearly fill the figure (minimum margin? expand figure? shrink to fit available slivers?); overlap between cats themselves (allow or avoid?); the density→count function and its interaction with figure size (this implements graceful degradation).

EARS acceptance criteria to carry into the spec:
- WHEN given the same inputs and seed, the engine SHALL return identical placements.
- WHEN no seed is provided, two consecutive calls SHALL return visibly different placements.
- Placements SHALL never intersect any exclusion rectangle, at any density, for any seed (property-based test with hypothesis is appropriate here).
- WHEN the available border area shrinks below a threshold, the engine SHALL reduce count and size rather than violate exclusions; at zero available area it SHALL return zero placements (never an error).
- The three density tiers (sparse/normal/chaotic) SHALL produce strictly increasing target counts on a reference canvas.

### M2 — matplotlib integration & activation *(SPEC REQUIRED — riskiest feature)*

The import-time hook: intercept figure rendering so cats appear on display **and** `savefig` with zero user code changes, and can be cleanly disabled.

Key spec questions for `/speckit.clarify`: interception point (wrapping `Figure.draw` vs. registering via `figure.add_artist`/draw callbacks vs. monkeypatching `show`/`savefig` — prefer the least invasive that covers both display and savefig; investigate `Figure.draw` wrapping + an idempotency guard); avoiding double-decoration on repeated draws (interactive backends redraw constantly); exclusion-zone extraction (`render/bboxes.py` — get tight bboxes of axes, labels, ticks, legends in figure coordinates; requires a draw pass to be accurate — handle that); ensuring `disable()` fully restores pristine behavior.

EARS acceptance criteria:
- WHEN a user adds only `import catplotlib` to an existing script, the next figure shown or saved SHALL include cat decorations.
- WHEN `disable()` is called, subsequently saved figures SHALL be byte-identical to a no-catplotlib baseline; `enable()` SHALL restore the effect in the same session.
- Decoration SHALL be idempotent: N draw passes of one figure SHALL yield exactly one set of cats.
- The hook SHALL work under `Agg` (headless/savefig) and at least one interactive backend, and with seaborn-generated figures.
- WHEN rendering any chart in the test matrix (line, bar, scatter, histogram; small/default/large figsizes; with/without legend), no cat bbox SHALL intersect data/label/legend bboxes (§8 harness).

### M3 — Style system & assets *(SPEC REQUIRED, lightweight)*

`assets/registry.py`: styles discovered from `assets/images/<style>/` + a small manifest (`styles.toml`: display name, per-image base scale so differently-sized source images render consistently). Multiple images per style — each cat drawn samples one image from its style's pool. API: `set_style("chonk")`, `set_style(["classic","derp"])` for a mix (even weighting), `set_style("mix")` = all styles.

EARS acceptance criteria:
- WHEN a new directory of images + manifest entry is added, the style SHALL be selectable with zero code changes.
- WHEN a single style is set, all cats on the figure SHALL come from that style's pool; WHEN a mix is set, at typical densities more than one style SHALL appear (seeded test).
- The three launch styles SHALL be visually distinguishable at typical render sizes (manual gate at v1 sign-off with real assets, placeholder-based automated test in the interim).

### M4 — Config surface, polish, packaging *(no spec — direct implementation)*

- `api.py`: `set_density("sparse"|"normal"|"chaotic")`, `set_seed(n)`, `enable()/disable()`, and `config(...)` context manager for temporary overrides (satisfies the presenter persona's "off for this one chart" story cheaply).
- README with before/after image at the very top, one-minute quickstart, config table.
- Packaging: build sdist/wheel, verify `pip install` from the wheel in a clean venv puts assets in place (`importlib.resources`, never `__file__`-relative paths for installed data... actually `importlib.resources` handles both; test it).
- Final pass of the full acceptance checklist (§10).

## 6. Config data flow (keep it this simple)

One module-level `Config` object in `core/config.py`; `api.py` functions mutate it; `render/hook.py` reads it at draw time. The `config()` context manager saves/restores. No config files, no env vars.

## 7. Asset drop-in contract (for Chuck)

To add or replace a style, drop files and edit one TOML — nothing else:

```
src/catplotlib/assets/images/<style-name>/*.png   # transparent-background PNGs, any count ≥1
```

plus one entry in `styles.toml` (`display_name`, optional `scale`). Placeholders live in the same structure; replacing them with real images is a file swap. Record sources in `ATTRIBUTION.md` as a courtesy.

## 8. Testing strategy (how the inner loop closes)

- **Core (majority of tests):** pure placement logic — determinism, exclusion avoidance (property-based via `hypothesis`), density tiers, degradation curve. Fast, no rendering.
- **Render integration:** the chart-type × figsize × legend matrix from M2, run under `Agg`. For each cell: render, extract cat artist bboxes and protected bboxes, assert empty intersection. This automates the PRD's central "non-destructive" acceptance criterion instead of eyeballing it.
- **Byte-identity:** disabled-state savefig output vs. baseline.
- **Packaging smoke test:** install wheel in clean venv, run the one-liner, assert cats rendered.
- **Not tested automatically:** "charming." That's the developer/external loop's job (§9).

## 9. Operating the loops

- **Inner loop (you, Sonnet 5):** spec → clarify → plan → tasks → implement → verify against spec acceptance criteria, per milestone. `make check` before declaring anything done. Commit small.
- **Developer loop (Chuck):** after each milestone, produce a short visual gallery script (`scripts/gallery.py` rendering the test matrix to PNGs) so Chuck can judge charm/placement aesthetics in seconds. His feedback edits specs; regenerate from there. Keep specs alive — a drifted spec gets fixed or deleted same day.
- **Evals:** none at start. The second time the same *category* of failure recurs (e.g. "cats keep crowding the top-left corner", "legend detection misses twin axes"), promote it to `evals/` with a case file and wire into the Stop hook. Delete evals whose failure class stays dead for months.
- **Growth triggers to watch (from the recipe):** nested CLAUDE.md in `render/` if backend-quirk conventions accumulate there (most likely spot); first skill when a procedure (e.g. "add a style", "run the gallery") gets pasted twice; subagents for >5-file exploration. Do not add retrieval layers, wikis, or review tooling — this repo will never be big enough.

## 10. v1 Definition of Done (maps 1:1 to PRD P0)

| # | P0 requirement | Verified by |
|---|---|---|
| 1 | One-line activation (display + savefig) | M2 tests + packaging smoke test |
| 2 | Non-destructive rendering + graceful small-figure degradation | §8 matrix + M1 degradation tests |
| 3 | Randomized placement (unseeded runs differ) | M1 tests |
| 4 | Seed reproducibility | M1/M2 tests |
| 5 | ≥3 visually distinct density levels | M1 tests + gallery review |
| 6 | ≥3 selectable styles, single-or-mix | M3 tests + gallery review with real assets |
| 7 | In-session on/off | M2 byte-identity tests |
| 8 | Asset provenance documented | ATTRIBUTION.md entries (courtesy; not a gate) |

Plus: `make check` green, README before/after in place, installable wheel, all specs in `specs/` match shipped behavior.

**Out of scope for v1 (do not build):** other plotting libraries, placement-mode/size/rotation controls beyond defaults (P1), per-figure overrides beyond the `config()` context manager, style weighting, long-cat, animation, gallery *mode* as a shipped feature (the internal `scripts/gallery.py` is fine), GUI, any network anything.
