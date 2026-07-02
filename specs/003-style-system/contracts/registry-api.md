# Contract: `catplotlib.assets.registry`

## `discover_styles(images_dir, manifest_path) -> dict[str, StyleInfo]`

**Preconditions**: `images_dir` and `manifest_path` are `Path`s; neither is required to exist
(missing → empty result, not an error).

**Postconditions**:
- A style name appears in the result only if `images_dir/<name>/` exists, contains at least one
  image file, AND `manifest_path` has a `[styles.<name>]` section (FR-001, edge cases).
- Never raises for a missing directory, missing manifest file, or malformed manifest section
  (malformed → that style is simply excluded, not a process-wide failure — a bad manifest entry
  for one style shouldn't break every other style).

## `resolve_style_names(selection) -> list[str]`

**Preconditions**: `selection` is `"mix"`, a single style name `str`, or a `list[str]` of style
names.

**Postconditions**:
- `"mix"` → every currently-registered style name (FR-004).
- A single name or list → that name/list, unchanged, IF every name is registered.
- Any unregistered name anywhere in the input → raises `ValueError` immediately, naming the bad
  style (spec Assumption: fail-fast, not deferred).

## `render.artist._resolve_image(style: str) -> np.ndarray` (contract addition over M2)

**Preconditions**: `style` is a name already validated by `resolve_style_names` (the render
layer never calls this with a raw unvalidated user string).

**Postconditions**:
- Returns an image array sampled from `style`'s pool. Given the *same full `Placement`* (all
  fields — x, y, size, rotation, style), the same image is always chosen (deterministic hash of
  the placement's own fields against a filename-sorted pool — see research.md), so a seeded
  `place_cats()` call's reproducibility guarantee (M1 FR-004) extends losslessly through image
  selection: same seed → same placements → same images, every time.
- Never raises for a style with exactly one image (degenerate but valid pool).
