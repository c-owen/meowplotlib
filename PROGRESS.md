# Progress

**Status: v1 (P0 scope) shipped**, all three launch styles now real art (classic/derp/chonk),
plus two post-v1 polish changes: guaranteed full-perimeter margin and denser default tiers (see
below). `make check` green (78 passed, 1 skipped — seaborn not installed).

**Next task**: none outstanding. If picking this back up, start by re-reading this file, then
`git log --oneline -20`.

## Post-v1 changes (2026-07-02, user-requested after reviewing real-art gallery output)

- **Guaranteed perimeter margin**: `render/bboxes.py`'s new `ensure_minimum_margin(figure,
  margin)` shrinks each axes' position so at least `margin` (10%, `hook.py`'s
  `_GUARANTEED_MARGIN`) of clear figure-fraction space exists on every side before exclusions
  are extracted. Without this, matplotlib's default layout leaves ~2% bottom margin and ~6.5%
  left margin (tick labels sit tight against the plot) vs. ~10-12% top/right — cats only ever
  landed top/right in practice. **This is a deliberate, opted-in departure from pure
  "decorate around the existing layout" behavior** — catplotlib now actively resizes the user's
  plot area a little. Flagged explicitly and confirmed before implementing; the PRD's Goal 3
  ("must never... break existing layouts") needs a wording update to match — proposed but not
  yet applied, see below.
- **Denser tiers**: `_DENSITY_DIVISORS` halved (sparse/normal/chaotic now ~6/12/24 cats on the
  M1 reference canvas, was ~3/6/12). Ordering property tests still pass unmodified (they assert
  strict ordering, not exact counts); the illustrative reference numbers in code comments and
  `specs/001-core-placement-engine/quickstart.md`/`data-model.md` etc. that cite "3/6/12" are
  now stale by a factor of 2 — not yet swept for a full doc update, low priority since they're
  illustrative examples, not contracts.
- Neither change touched `core/placement.py`'s exclusion/collision math itself (margin-guarantee
  lives entirely in `render/`, upstream of `core/`) — M1's own tests and contracts are unaffected
  except for the two divisor constants.

## Known limitations (not blockers, but real gaps)

- `styles.toml`'s `scale` field is clamped to `min(scale, 1.0)` in `render/artist.py` — it can
  only shrink a cat's footprint within the bbox `core/placement.py` reserved, never grow it.
  Chonk's manifest `scale = 1.15` therefore has no visible effect. Would need style-specific
  scale threaded into `core/`'s collision math, conflicting with M1's "styles are opaque
  strings to core" design boundary — same family of issue as the (now-resolved) rotation gap.
- `ensure_minimum_margin` calls `axes.set_position()` once per decoration; figures using
  `constrained_layout=True` or `tight_layout()` may have their own layout engine re-run during
  the real draw call afterward and override this — untested against that case. Most default
  `plt.subplots()` figures (no explicit layout engine) are unaffected.

## Design decisions worth knowing before touching `core/` or `render/`

- `Placement.bbox()` (`core/placement.py`) reserves the AABB of the ROTATED square, not the
  unrotated one (dated addendum in `specs/001-core-placement-engine/research.md`). `render/
  artist.py` draws each cat at its true size within that reserved axes and applies an
  `Affine2D` rotation transform in data-space. Any future placement/rendering geometry change
  must keep the rendered footprint inside what `bbox()` reserves.
- Each cat is its own tiny inset `Axes` (tagged `_catplotlib_cat = True`, excluded from future
  exclusion extraction) — not `AnnotationBbox`/`OffsetImage`, whose point-space `zoom` caused
  real sub-pixel overlaps the chart-matrix test caught but simpler tests didn't.
- `Figure.draw` is patched exactly once, permanently, at import time. `enable()`/`disable()`
  only flip `Config.enabled`, checked first in the wrapper — pure pass-through when `False`,
  which is what makes disabled output byte-identical to unpatched matplotlib.
- `pyproject.toml`'s `[tool.mypy] python_version` is `"3.12"`, not the package's
  `requires-python` floor of `"3.10"` — numpy's bundled stubs need PEP 695 syntax mypy can only
  parse at 3.12+. Not a statement that the package needs 3.12 at runtime.

## Rules to remember

- No AI tool/assistant listed as commit author or co-author, ever (constitution.md #10).
- `core/` stays pure — no matplotlib import, no I/O.
- The `speckit-*` skills under `.claude/skills/` were not directly invocable via the Skill tool
  in this session (installed mid-session) — read each `SKILL.md` and follow its procedure by
  hand if this recurs.
- For matplotlib-internals questions, dispatch an Explore subagent to read the installed
  matplotlib source directly rather than relying on general knowledge.
- `make` is not installed on this Windows dev box — run the four `make check` commands directly
  (ruff check, ruff format --check, mypy, pytest) if `make` isn't available.
