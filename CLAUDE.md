# meowplotlib — root map

Read `constitution.md` first (non-negotiables) and `PROGRESS.md` second (where things stand). `STANDUP_PLAN.md` is the full execution contract — milestone order, resolved decisions, acceptance criteria.

## Layout

- [constitution.md](constitution.md) — non-negotiable rules, several enforced by tests/hooks.
- [PROGRESS.md](PROGRESS.md) — externalized working memory; re-read on every session start or after compaction.
- [STANDUP_PLAN.md](STANDUP_PLAN.md) — execution contract: milestones, resolved decisions, EARS acceptance criteria.
- [specs/](specs/) — Spec Kit output, one folder per spec-required feature (M1–M3).
- `src/meowplotlib/`
  - [__init__.py](src/meowplotlib/__init__.py) — import-time activation + public API re-exports.
  - [api.py](src/meowplotlib/api.py) — user-facing: `enable`/`disable`/`set_style`/`set_density`/`set_seed`/`config`.
  - `core/` — **pure logic, no matplotlib import, no I/O** (constitution #1).
    - [config.py](src/meowplotlib/core/config.py) — the one module-level `Config` object.
    - [placement.py](src/meowplotlib/core/placement.py) — geometry: dims + exclusions → placements (M1).
    - [rng.py](src/meowplotlib/core/rng.py) — seeded RNG wrapper (M1).
  - `render/` — the impure layer, all matplotlib knowledge lives here.
    - [hook.py](src/meowplotlib/render/hook.py) — draw/savefig interception (M2).
    - [artist.py](src/meowplotlib/render/artist.py) — draws placed cats (M2/M3).
    - [bboxes.py](src/meowplotlib/render/bboxes.py) — exclusion bbox extraction (M2).
  - `assets/`
    - [registry.py](src/meowplotlib/assets/registry.py) — style discovery (M3).
    - [styles.toml](src/meowplotlib/assets/styles.toml) — style manifest.
    - `images/<style>/*.png` — Chuck's art drop-in location (see [ATTRIBUTION.md](ATTRIBUTION.md)).
- `tests/` — mirrors `src/meowplotlib/` 1:1.
- [scripts/make_placeholders.py](scripts/make_placeholders.py) — generates placeholder style PNGs.
- [scripts/gallery.py](scripts/gallery.py) — renders the visual test matrix for human review (added M2+).

## Workflow

- `make check` = ruff + ruff format --check + mypy --strict + pytest. Must be green before any task is declared done.
- M1–M3 are spec-required: run `/speckit.specify` → `/speckit.clarify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`, then verify against the spec's acceptance criteria — not just green tests.
- M0 and M4 are direct implementation, no spec.
- Small commits: code → test → commit, every commit passes `make check`.
- **No AI tool/assistant is ever listed as a commit author or co-author** (constitution #10).
- Use subagents for exploration touching >5 files or matplotlib-internals research; only conclusions return to main context.

## Compact Instructions

Preserve: current milestone and task from PROGRESS.md, unresolved design decisions, failing-test details. Discard: file contents (re-read from disk), exploration transcripts, resolved discussions.
