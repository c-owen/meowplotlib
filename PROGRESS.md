# Progress

**Status: v1 (P0 scope) shipped.** M0-M4 all complete per STANDUP_PLAN.md. `make check` green
(76 passed, 1 skipped — seaborn not installed). Wheel builds and installs cleanly; packaging
verified end to end (`tests/test_packaging.py`). README has a real before/after hero image.

**Next task**: none outstanding for v1 as scoped. The only remaining work is external to this
repo — Chuck drops real cat PNGs into `src/catplotlib/assets/images/<style>/` (pure file-drop
per the M3 contract). Regenerate `scripts/gallery.py` afterward and flag anything that looks off
(scale, transparency); no code changes should be needed if the M3 contract held. If picking this
back up, start by re-reading this file, then `git log --oneline -20`.

## Known limitations (not v1 blockers, but real gaps)

- `styles.toml`'s `scale` field is clamped to `min(scale, 1.0)` in `render/artist.py` — it can
  only shrink a cat's footprint within the bbox `core/placement.py` reserved, never grow it.
  Chonk's manifest `scale = 1.15` therefore has no visible effect. Rotation was fixed to render
  properly (see below) since the user asked for it explicitly; this narrower "make one style
  visually bigger" case was not — would need style-specific scale threaded into `core/`'s
  collision math, conflicting with M1's "styles are opaque strings to core" design boundary.
- Style variety is currently 3 programmatic placeholders (`classic`/`derp`/`chonk`), not real
  art — see ATTRIBUTION.md and the note above.

## Design decisions worth knowing before touching `core/` or `render/`

- `Placement.bbox()` (`core/placement.py`) reserves the AABB of the ROTATED square, not the
  unrotated one — this was a mid-project design change (see dated addendum in
  `specs/001-core-placement-engine/research.md`) after the user asked for rotation to actually
  render rather than stay metadata-only. `render/artist.py` draws each cat at its true size
  within that (larger) reserved axes and applies an `Affine2D` rotation transform in data-space.
  Any future change to placement or rendering geometry must keep the rendered footprint inside
  what `bbox()` reserves — this is the constitution #2 non-overlap guarantee's actual mechanism.
- Each cat is its own tiny inset `Axes` (`figure.add_axes(...)`, tagged `_catplotlib_cat = True`
  so `render/bboxes.py` excludes it from exclusion extraction) — not `AnnotationBbox`/
  `OffsetImage`, whose point-space `zoom` caused real sub-pixel overlaps that only the chart-
  matrix test caught.
- `Figure.draw` is patched exactly once, permanently, at import time. `enable()`/`disable()`
  only flip `Config.enabled`, which the wrapper checks first and is a pure pass-through when
  `False` — this is what makes disabled output byte-identical to unpatched matplotlib.
- `pyproject.toml`'s `[tool.mypy] python_version` is `"3.12"`, not the package's `requires-python`
  floor of `"3.10"` — numpy's bundled stubs need PEP 695 syntax mypy can only parse at 3.12+.
  Not a statement that the package needs 3.12 at runtime.

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
