# Progress

**Current milestone:** M0 — scaffold
**Last completed:** dev env installed (uv venv), manual check pipeline green (ruff/ruff format/mypy strict/pytest, 4 tests passing), placeholder PNGs generated for classic/derp/chonk, first commit made (052c68e).
**Next task:** get user approval to run Spec Kit init (`uvx --from git+https://github.com/github/spec-kit.git specify init . --integration claude`) — blocked by the auto-mode permission classifier as an external-repo execution; needs explicit user approval or a Bash permission rule. Once done, M0 is complete and M1 (core placement engine spec) can start.

## In-flight design decisions
None yet — M0 is pure scaffold, no design calls beyond STANDUP_PLAN.md §2/§3.

## Known open issues
- `make` is not installed on this Windows box; verified the check pipeline by running its four commands directly (ruff check, ruff format --check, mypy, pytest) instead of via `make check`. Works fine in CI/any Unix env; local devs on Windows without `make` should run the four commands directly or install `make` (e.g. via choco/scoop/MSYS2).
- `git config core.symlinks` is false on this machine, so `AGENTS.md` was created as a plain-file copy of `CLAUDE.md`, not a real symlink. Keep both in sync manually if CLAUDE.md changes materially (or revisit once symlinks are enabled).

## Rules to remember
- No AI tool/assistant listed as commit author or co-author, ever (constitution.md #10).
- `core/` stays pure — no matplotlib import, no I/O.
