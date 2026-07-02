# Progress

**Current milestone:** M0 — COMPLETE (commits 052c68e, aff1303, ca016c2). Starting M1 next.
**Last completed:** Spec Kit installed (`specify init --here --integration claude --script sh`); `.specify/memory/constitution.md` adapted from root `constitution.md` (root file stays source of truth — update both if constitution changes). speckit skills available: /speckit-specify, /speckit-clarify, /speckit-plan, /speckit-tasks, /speckit-implement, /speckit-analyze, /speckit-checklist, /speckit-constitution, /speckit-converge. `make check` reverified green after install.
**Next task:** M1 — core placement engine. Run `/speckit-specify` for `core/placement.py` + `core/rng.py` per STANDUP_PLAN.md §5 (M1 section): given canvas dims, exclusion rectangles, config (density/size/seed/styles) → list of placements confined to border region, non-overlapping with exclusions, seed-reproducible. Then `/speckit-clarify` (resolve border-region definition, cat-cat overlap policy, density→count function), `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`. Use `hypothesis` for property-based exclusion tests.

## In-flight design decisions
None yet — M0 is pure scaffold, no design calls beyond STANDUP_PLAN.md §2/§3.

## Known open issues
- `make` is not installed on this Windows box; verified the check pipeline by running its four commands directly (ruff check, ruff format --check, mypy, pytest) instead of via `make check`. Works fine in CI/any Unix env; local devs on Windows without `make` should run the four commands directly or install `make` (e.g. via choco/scoop/MSYS2).
- `git config core.symlinks` is false on this machine, so `AGENTS.md` was created as a plain-file copy of `CLAUDE.md`, not a real symlink. Keep both in sync manually if CLAUDE.md changes materially (or revisit once symlinks are enabled).
- Running `uvx --from git+...` piped through `| tail -N` in a background shell hides all output until the process exits (pipe buffering) and looked like a 16-minute hang. Non-piped, it took ~30s once uv's build cache was warm. Avoid piping uvx/long-running CLI output through tail/head when backgrounding — read output directly or run in foreground.

## Rules to remember
- No AI tool/assistant listed as commit author or co-author, ever (constitution.md #10).
- `core/` stays pure — no matplotlib import, no I/O.
