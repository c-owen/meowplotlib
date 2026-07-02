# Progress

**Current milestone:** M1 — COMPLETE (core placement engine). M0 also complete. Starting M2 next.
**Last completed:** Full speckit flow for the core placement engine: spec.md (4 user stories, 10 FRs, 5 SCs) → clarify (3 questions resolved) → plan.md/research.md/data-model.md/contracts/quickstart.md → tasks.md (29 tasks) → implementation. `src/catplotlib/core/placement.py` (`Rect`, `PlacementConfig`, `Placement`, `place_cats()`) and `core/rng.py` (`new_rng()`) implemented. 17 tests total (13 new: example + hypothesis property tests) all passing. `make check` green. Quickstart smoke script verified manually: sparse=3, normal=6, chaotic=12 cats on the reference canvas, matching the spec's illustrative example exactly.
**Next task:** M2 — matplotlib integration & activation (spec-driven, the riskiest milestone). Run `/speckit-specify` for `render/hook.py`, `render/artist.py`, `render/bboxes.py` per STANDUP_PLAN.md §5 M2: import-time hook intercepting figure draw/savefig, idempotent across repeated draws, exclusion-bbox extraction from a live figure (axes/labels/ticks/legend), clean `disable()` byte-identity. Key clarify questions already flagged in the plan: interception point (prefer wrapping `Figure.draw` + idempotency guard over monkeypatching `show`/`savefig` separately — investigate both), avoiding double-decoration on interactive-backend redraws, bbox extraction requiring a draw pass to be accurate. Consider using an Explore/Plan subagent to research matplotlib's `Figure.draw`/backend redraw internals before writing the spec's Technical Context, per the kickoff instructions.

## In-flight design decisions
- Placement engine tuning constants (edge margin 3% of smaller canvas dimension, density divisors sparse=0.131/normal=0.0656/chaotic=0.0328 tuned to yield ~3/6/12 cats on a unit-square reference canvas with a 70%-coverage centered exclusion, max 200 target placements as a defensive cap) live in `src/catplotlib/core/placement.py` module constants — not yet exposed as user-tunable, per STANDUP_PLAN.md's out-of-scope list (size/placement-mode controls beyond defaults are P1, not v1).
- Collision model is AABB-only (rotation stored as metadata, not used in collision) — documented rationale in `specs/001-core-placement-engine/research.md`. M2/M3 must not assume placements' true rendered footprint is tighter than their axis-aligned bbox.

## Known open issues
- `make` is not installed on this Windows box; verified the check pipeline by running its four commands directly (ruff check, ruff format --check, mypy, pytest) instead of via `make check`. Works fine in CI/any Unix env; local devs on Windows without `make` should run the four commands directly or install `make` (e.g. via choco/scoop/MSYS2).
- `git config core.symlinks` is false on this machine, so `AGENTS.md` was created as a plain-file copy of `CLAUDE.md`, not a real symlink. Keep both in sync manually if CLAUDE.md changes materially (or revisit once symlinks are enabled).
- Running `uvx --from git+...` piped through `| tail -N` in a background shell hides all output until the process exits (pipe buffering) and looked like a 16-minute hang. Non-piped, it took ~30s once uv's build cache was warm. Avoid piping uvx/long-running CLI output through tail/head when backgrounding — read output directly or run in foreground.

## Rules to remember
- No AI tool/assistant listed as commit author or co-author, ever (constitution.md #10).
- `core/` stays pure — no matplotlib import, no I/O.
- The `speckit-*` skills installed under `.claude/skills/` are not directly invocable via the
  Skill tool in this environment (added mid-session, not in the session's skill snapshot) —
  read each `SKILL.md` and follow its procedure manually. This worked fine for M1's full
  specify/clarify/plan/tasks flow; repeat the same approach for M2/M3.
