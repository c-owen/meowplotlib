# Feature Specification: Style System & Assets

**Feature Branch**: `003-style-system`

**Created**: 2026-07-02

**Status**: Draft

**Input**: User description: "assets/registry.py: styles discovered from assets/images/<style>/ + a small manifest (styles.toml). Multiple images per style — each cat drawn samples one image from its style's pool. API: set_style('chonk'), set_style(['classic','derp']) for a mix, set_style('mix') = all styles. Lightweight spec per STANDUP_PLAN.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A single style decorates the whole figure (Priority: P1)

A user calls `catplotlib.set_style("chonk")`. Every cat subsequently placed on any figure is
drawn from the "chonk" style's image pool only.

**Why this priority**: PRD requirement 6's core promise — single-style selection is the simplest
and most-used form of style control.

**Independent Test**: `set_style("chonk")`, render a figure at a density that places multiple
cats, inspect each placed cat's resolved image path/identifier; assert all come from the
"chonk" directory.

**Acceptance Scenarios**:

1. **Given** `set_style("chonk")` has been called, **When** a figure with multiple cats is
   rendered, **Then** every cat's image comes from `assets/images/chonk/`.
2. **Given** a style's directory contains multiple images, **When** several cats of that style
   are placed on one figure, **Then** different cats may sample different images from the pool
   (not always the same one).

---

### User Story 2 - Mixing styles on one figure (Priority: P1)

A user calls `catplotlib.set_style(["classic", "derp"])` or `catplotlib.set_style("mix")`
(all styles). At typical densities, more than one style appears among the cats on a single
figure, evenly weighted across the selected styles.

**Why this priority**: PRD requirement 6's second half — mixing is what gives the product
"replay value" per the PRD's stated goal.

**Independent Test**: `set_style("mix")` with a fixed seed, render at chaotic density (several
cats), assert more than one distinct style appears among the placed cats' resolved styles, and
that no single style accounts for statistically all of them across repeated seeds.

**Acceptance Scenarios**:

1. **Given** `set_style(["classic", "derp"])`, **When** a figure with several cats is rendered,
   **Then** each placed cat's style is one of "classic" or "derp", and at typical densities both
   appear on the same figure across a handful of seeds.
2. **Given** `set_style("mix")`, **When** a figure is rendered, **Then** cats are drawn from
   every currently-registered style's pool (not a hardcoded subset), evenly weighted.

---

### User Story 3 - Adding a style requires zero code changes (Priority: P2)

The package owner drops a new directory of PNGs under `assets/images/<new-style>/` and adds one
entry to `styles.toml`. Without touching any `.py` file, the new style becomes selectable via
`set_style("<new-style>")` and participates in `"mix"`.

**Why this priority**: Constitution #7 and the PRD's explicit goal of extensibility for future
style packs (P1/P2 roadmap items) depend on this contract holding from day one.

**Independent Test**: In a test, register a temporary style directory + manifest entry (not
touching the shipped `assets/` tree), confirm the registry discovers it and it's selectable and
included in `"mix"`, without any code path change.

**Acceptance Scenarios**:

1. **Given** a new style directory + manifest entry exists at startup, **When** the registry is
   queried, **Then** the new style's name and image pool are discoverable.
2. **Given** the three launch styles (classic, derp, chonk) ship with the package, **When**
   rendered at typical sizes, **Then** each is visually distinguishable from the others (manual
   gate at v1 sign-off with real assets; automated test uses the placeholder images in the
   interim, asserting they are pixel-distinct, not asserting subjective "distinguishability").

---

### Edge Cases

- What happens when `set_style()` is given a style name that isn't registered? Out of scope for
  this spec's automated tests to define precise error behavior; a reasonable default (raise a
  clear error at `set_style()` call time, not deferred to render time) is assumed — see
  Assumptions.
- What happens when a style directory exists but contains zero images? The registry excludes it
  from the discoverable set (a style with no images can't be sampled from) rather than crashing.
- What happens when `styles.toml` has a manifest entry with no matching directory, or a
  directory with no matching manifest entry? Only styles with both a directory AND a manifest
  entry are considered valid/discoverable (constitution #7's "directory + manifest entry"
  contract, applied literally as an AND, not an OR).
- What happens when `"mix"` is selected but zero styles are currently registered (e.g. a
  corrupted install)? The registry returns an empty style list; M1's `place_cats()` already
  contractually returns zero placements when given an empty style list (M1 FR-008/postcondition
  3) — no new error-handling code needed here, this composes for free.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The registry MUST discover styles by scanning `assets/images/` for
  subdirectories, and cross-referencing each against `styles.toml` — a style is valid only if
  both a non-empty image directory and a manifest entry exist.
- **FR-002**: `set_style(name: str)` MUST cause all subsequently placed cats to be drawn only
  from that style's image pool.
- **FR-003**: `set_style([name, ...])` MUST cause all subsequently placed cats to be drawn only
  from the union of the listed styles' pools, with even weighting across styles (not across raw
  image count — a style with 1 image and a style with 5 images each get equal selection
  probability, matching STANDUP_PLAN.md §2's resolved "even weighting across styles" decision).
- **FR-004**: `set_style("mix")` MUST behave identically to passing the full list of every
  currently-registered style's name.
- **FR-005**: WHEN a style's pool contains multiple images, cats of that style MUST be capable
  of sampling different images across multiple placements (not always the pool's first image).
- **FR-006**: Adding a new style MUST require only a new `assets/images/<name>/` directory with
  at least one image plus one `styles.toml` entry — no changes to any `.py` file.
- **FR-007**: The render layer (M2's `render/artist.py`) MUST resolve each placement's style via
  the registry instead of the M2-era hardcoded single-image stub.
- **FR-008**: The three launch styles' placeholder images MUST be pixel-distinct from one
  another (automatable today); true subjective visual distinguishability with real assets is a
  manual v1 sign-off gate, not an automated test (per STANDUP_PLAN.md §5 M3).

### Key Entities

- **Style**: a name (directory name, also the manifest key), a display name, an optional base
  scale factor, and a pool of one or more images.
- **Manifest (`styles.toml`)**: maps style name → `{display_name, scale}`.
- **Registry**: the queryable set of currently-valid (directory + manifest both present) styles,
  built by scanning `assets/images/` and parsing `styles.toml` at query time (or cached — see
  Assumptions).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With a single style selected, 100% of placed cats across a seeded multi-cat render
  resolve to an image from that style's directory.
- **SC-002**: With `"mix"` selected and at least 2 styles registered, across 20 different seeds
  at chaotic density, more than one distinct style appears among the placed cats' resolved
  styles in at least 90% of seeds (allows for rare unlucky single-style draws at very low counts,
  while proving mixing genuinely occurs).
- **SC-003**: A style registered only via a temporary test fixture (directory + manifest entry
  outside the shipped tree) is discoverable and selectable with zero production code changes,
  verified by a test that adds such a fixture and asserts it appears in the registry's output.
- **SC-004**: The three shipped launch styles' placeholder images are pairwise pixel-distinct
  (not byte-identical, not near-duplicate at a coarse hash level).

## Assumptions

- `set_style()` given an unregistered style name raises a clear error immediately at call time
  (fail-fast), rather than silently falling back to another style or deferring the failure to
  the next render. This matches the general principle that misconfiguration should surface
  immediately, not as a mysterious "why don't I see cats" bug report.
- The registry re-scans the filesystem on each query rather than caching at import time, since
  style counts are small (single-digit directories) and this keeps "drop a file, it just works"
  literally true even within a running process — no cache-invalidation logic needed. If this
  becomes a measured performance concern later, caching is a pure optimization, not a behavior
  change.
- `styles.toml`'s per-style `scale` field (already present in the M0-authored manifest) is
  applied as a multiplier on `Placement.size` when the render layer draws that style's image, so
  differently-sized source images render at a visually consistent apparent size. This spec
  defines the field's existence and intended use; exact scale-application arithmetic is an
  implementation (plan-time) detail, not a user-facing contract.
- Rendering cat rotation (`Placement.rotation`) remains explicitly out of scope for this spec —
  tracked separately in PROGRESS.md, not resolved here.
