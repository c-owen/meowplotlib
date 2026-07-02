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

- `_resolve_image(placement: Placement) -> np.ndarray` (signature change from M2's `(style:
  str)` — needs the full placement, not just the style name, to derive a deterministic pool
  index): looks up `placement.style` in `available_styles()`, sorts that style's `image_paths`
  by filename, picks the image at `hash((placement.x, placement.y, placement.size,
  placement.rotation)) % len(pool)` (research.md), loads and caches it (cache keyed by resolved
  file path, same caching pattern as the M2 stub — avoids re-reading PNGs from disk on every
  draw).
- The image's `scale` is applied as a multiplier on the placement's rendered size (Assumption
  from spec.md, exact arithmetic: `effective_size = placement.size * style_info.scale`).

## State transitions

None — registry discovery is a pure read-and-return per call (no persistent state introduced).
