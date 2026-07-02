# Data Model: Style System & Assets

## `StyleInfo` (new, in `assets/registry.py`)

| Field | Type | Notes |
|---|---|---|
| `name` | `str` | Directory name / manifest key, e.g. `"chonk"`. |
| `display_name` | `str` | From `styles.toml`. |
| `scale` | `float` | From `styles.toml`, defaults to `1.0` if omitted. |
| `image_paths` | `list[Path]` | Every image file found in `assets/images/<name>/`. |

## Registry functions (`assets/registry.py`)

- `discover_styles(images_dir: Path, manifest_path: Path) -> dict[str, StyleInfo]` — the core,
  parametrized scan (test-friendly: pass a temp dir + temp manifest for FR-006/SC-003 tests).
  Returns only styles with both a non-empty directory AND a manifest entry (spec Edge Cases).
- `available_styles() -> dict[str, StyleInfo]` — convenience wrapper calling `discover_styles`
  against the package's real `assets/images/` and `assets/styles.toml`, via
  `importlib.resources`.
- `resolve_style_names(selection: str | list[str]) -> list[str]` — given `api.set_style()`'s
  raw value (`"chonk"`, `["classic", "derp"]`, or `"mix"`), returns the flat list of style names
  to hand to `core.placement.PlacementConfig.styles`. Raises `ValueError` for an unregistered
  name (spec Assumption: fail-fast at `set_style()` call time — `api.set_style()` calls this
  eagerly, not deferred to render time).

## Render-layer change (`render/artist.py`)

- `_resolve_image(placement: Placement) -> tuple[np.ndarray, float]` (signature change from M2's
  `(style: str) -> np.ndarray` — needs the full placement, not just the style name, to derive a
  deterministic pool index, and now also returns the resolved style's clamped scale so
  `draw_placements` doesn't need a second registry lookup): looks up `placement.style` in
  `available_styles()`, sorts that style's `image_paths` by filename, picks the image at
  `hash((placement.x, placement.y, placement.size, placement.rotation)) % len(pool)`
  (research.md), loads and caches it (cache keyed by resolved file path, same caching pattern as
  the M2 stub — avoids re-reading PNGs from disk on every draw). Returns `(image, min(scale,
  1.0))` — scale is clamped, never grown (see spec Assumptions and the 2026-07-02 rotation
  addendum below).
- **2026-07-02 addendum (post-M3)**: the user requested rotation actually render as a v1
  feature. `draw_placements` now sizes each cat's inset axes to the FULL rotation-inclusive
  `Placement.bbox()` (see `specs/001-core-placement-engine/research.md`'s matching addendum),
  sets that axes' data limits to span the bbox exactly, draws the image at its true unrotated
  extent (`placement.size * scale`, centered at the origin), and applies an `Affine2D` rotation
  transform in data-space. `scale`'s effect is therefore now "how much of the reserved,
  rotation-inclusive bbox the image actually fills," not an inset of the axes rect itself (the
  pre-rotation-addendum mechanism) — the clamp-to-`1.0` behavior and its rationale (never exceed
  the collision-safe reserved area) are unchanged.

## State transitions

None — registry discovery is a pure read-and-return per call (no persistent state introduced).
