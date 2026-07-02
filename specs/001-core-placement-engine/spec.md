# Feature Specification: Core Placement Engine

**Feature Branch**: `001-core-placement-engine`

**Created**: 2026-07-02

**Status**: Draft

**Input**: User description: "Core placement engine for catplotlib (src/catplotlib/core/placement.py and core/rng.py). Pure logic layer, no matplotlib imports, no I/O (constitution rule #1). Given canvas dimensions, a list of exclusion rectangles, and config (density tier, size range, seed, allowed styles), return a list of cat placements (x, y, size, rotation, style id) confined to the border/margin region of the canvas, never overlapping any exclusion rectangle."

## User Scenarios & Testing *(mandatory)*

<!--
  The "user" of this internal engine is the render layer (src/catplotlib/render/hook.py, M2)
  and, transitively, the person viewing a catplotlib-decorated figure. Each story below is
  independently testable via the engine's pure function API without any matplotlib rendering.
-->

### User Story 1 - Cats never cover the chart (Priority: P1)

A caller supplies canvas dimensions and a set of exclusion rectangles representing the plot's
data area, axis labels, tick labels, and legend. The engine returns cat placements confined to
the border region, none of which intersect any exclusion rectangle.

**Why this priority**: This is the product's core non-negotiable promise (constitution #2,
PRD requirement 2). Every other capability is worthless if it's violated.

**Independent Test**: Call the engine with a fixed canvas size, a fixed set of exclusion
rectangles, and any config; assert no returned placement's bounding box intersects any
exclusion rectangle. Fully testable without rendering a single pixel.

**Acceptance Scenarios**:

1. **Given** a canvas with a large centered exclusion rectangle (typical plot with axes),
   **When** placements are generated at any density, **Then** no placement bounding box
   intersects the exclusion rectangle.
2. **Given** an exclusion rectangle that covers nearly the entire canvas, **When** placements
   are generated, **Then** the engine returns only placements that fit in the remaining slivers,
   or zero placements if no space remains — it never raises an error and never overlaps.

---

### User Story 2 - Reproducible layouts with a seed (Priority: P1)

A caller supplies the same canvas, exclusions, and config twice, along with the same seed value.
The engine returns identical placements both times, so a chart regenerated for a report doesn't
visually change.

**Why this priority**: PRD requirement 4 (reproducibility) is P0 and is one of the five
constitution rules with a dedicated enforcement test.

**Independent Test**: Call the engine twice with identical inputs including seed; assert the
returned placement lists are element-for-element identical (position, size, rotation, style).

**Acceptance Scenarios**:

1. **Given** a fixed seed, **When** the engine is called twice with identical inputs,
   **Then** both calls return identical placement lists.
2. **Given** no seed (`None`), **When** the engine is called twice with identical inputs,
   **Then** the two calls return visibly different placement lists (different positions and/or
   counts and/or styles, not just different object identity).

---

### User Story 3 - Density controls how populated the figure feels (Priority: P2)

A caller selects a density tier (sparse, normal, or chaotic). The number of cats placed on a
reference canvas increases strictly from sparse to normal to chaotic, so the three tiers are
visually distinguishable.

**Why this priority**: PRD requirement 5 (density control) is P0, but depends on User Story 1
being correct first — a badly-placed dense figure is worse than a correct sparse one.

**Independent Test**: Call the engine three times on the same reference canvas (same exclusions,
same seed) varying only density; assert `len(sparse) < len(normal) < len(chaotic)`.

**Acceptance Scenarios**:

1. **Given** a reference canvas and a fixed seed, **When** density is set to sparse, normal,
   then chaotic in turn, **Then** the resulting placement counts strictly increase.

---

### User Story 4 - Small figures degrade gracefully instead of breaking (Priority: P2)

A caller supplies a very small canvas (e.g., a thumbnail-sized figure) where the border region
available after excluding the plot area is tiny or nonexistent. The engine automatically reduces
cat count and size to fit, and returns zero placements rather than an error when there is truly
no room.

**Why this priority**: PRD requirement 2 (non-destructive rendering / graceful degradation) is
P0. This is the "never break, never corrupt" guarantee for edge-case figure sizes.

**Independent Test**: Call the engine with shrinking canvas sizes (or a growing exclusion
rectangle) down to zero available border area; assert placement count trends toward zero, sizes
never force overlap with exclusions, and no exception is ever raised.

**Acceptance Scenarios**:

1. **Given** a canvas whose available border area is small but non-zero, **When** placements are
   generated, **Then** the engine returns fewer and/or smaller placements than it would on a
   generously-sized canvas, still respecting all exclusions.
2. **Given** a canvas with zero available border area (exclusion rectangle fills the canvas),
   **When** placements are generated, **Then** the engine returns an empty list, not an error.

---

### Edge Cases

- What happens when the exclusion list is empty (e.g., a bare figure with no axes)? The entire
  canvas minus a minimal safety margin is available for placement.
- What happens when exclusion rectangles overlap each other? The engine treats their union as
  the excluded area; overlapping input is not an error.
- What happens when canvas width or height is zero or negative? The engine returns an empty
  placement list rather than raising.
- What happens when the requested style list is empty? The engine returns an empty placement
  list rather than raising (the render layer is responsible for supplying at least one valid
  style; the core engine does not validate style existence — see Assumptions).
- How does the engine handle a very large canvas with sparse density? Placement count still
  follows the density→count function; it does not scale unboundedly with canvas area alone.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The engine MUST accept canvas dimensions (width, height), a list of exclusion
  rectangles, and a config (density tier, size range, seed, list of allowed style identifiers),
  and return a list of placements, each with position, size, rotation, and a style identifier
  drawn from the allowed styles.
- **FR-002**: The engine MUST NOT return any placement whose bounding box intersects any
  exclusion rectangle, at any density tier, for any seed, for any valid canvas size.
- **FR-003**: The engine MUST confine all placements to the border/margin region of the canvas
  (the area outside the exclusion rectangles' union, within canvas bounds).
- **FR-004**: WHEN the same seed and identical other inputs are supplied, the engine MUST
  produce identical output on repeated calls (same order, same values).
- **FR-005**: WHEN no seed is supplied, the engine MUST produce non-deterministic output such
  that two consecutive calls with identical other inputs visibly differ.
- **FR-006**: The engine MUST support at least three density tiers (sparse, normal, chaotic)
  whose placement counts on a fixed reference canvas are strictly increasing in that order.
- **FR-007**: WHEN available border area shrinks, the engine MUST reduce placement count and/or
  size rather than violate the non-overlap guarantee (FR-002).
- **FR-008**: WHEN available border area is zero, the engine MUST return an empty placement
  list rather than raising an exception.
- **FR-009**: The engine MUST behave as a pure function of its inputs — no global mutable
  state, no I/O, no import of matplotlib or any rendering library (constitution #1). RNG state
  MUST be derived solely from the supplied seed (or a fresh source of randomness when unseeded),
  never from ambient/global state.
- **FR-010**: Each placement's style identifier MUST be one of the styles supplied in the
  config's allowed-styles list; when more than one style is allowed, the engine MUST be capable
  of selecting different styles across placements within a single call (mixing).

### Key Entities

- **Canvas dimensions**: width and height in a single, caller-defined coordinate unit (the
  render layer is responsible for unit consistency with the exclusion rectangles it supplies).
- **Exclusion rectangle**: a rectangle (x, y, width, height) in the same coordinate space as the
  canvas, representing an area cats must not overlap.
- **Config**: density tier, min/max size range, optional seed, list of allowed style
  identifiers.
- **Placement**: the engine's output unit — position (x, y), size, rotation angle, and a style
  identifier.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Across a property-based test suite generating randomized canvas sizes, exclusion
  layouts, densities, and seeds, 100% of generated placements have zero bounding-box
  intersection with any exclusion rectangle.
- **SC-002**: Given identical inputs including a fixed seed, repeated calls to the engine
  produce byte-for-byte identical placement lists in 100% of trials.
- **SC-003**: On a fixed reference canvas, placement counts for sparse/normal/chaotic satisfy
  sparse < normal < chaotic in 100% of trials across at least 20 different seeds.
- **SC-004**: As available border area is reduced from generous to zero across a swept range of
  test canvases, placement count is non-increasing and reaches exactly zero at zero available
  area, with zero exceptions raised across the sweep.
- **SC-005**: The engine module and its sibling RNG module contain zero references to
  matplotlib or any file/network I/O primitive, verified by static analysis of their imports.

## Assumptions

- The render layer (M2) is responsible for computing exclusion rectangles from a live
  matplotlib figure and for validating that supplied style identifiers actually exist in the
  asset registry (M3); the core engine treats style identifiers as opaque strings.
- Canvas dimensions and exclusion rectangles share one coordinate system defined by the caller
  (e.g., figure-fraction coordinates); the engine does not perform unit conversion.
- "Border/margin region" means the canvas area outside the union of all exclusion rectangles,
  inset by a small minimum safety margin from the canvas edge itself — exact margin and
  border-region shape (uniform border vs. best-fit remaining slivers) are open design questions
  to resolve in `/speckit-clarify` before planning.
- Cat-to-cat overlap policy (whether two placed cats may visually overlap each other) is an open
  design question to resolve in `/speckit-clarify`; this spec only constrains overlap with
  exclusion rectangles, not between placements.
- The density→count function's exact shape (e.g., linear vs. stepped, and how it scales with
  available border area) is an open design question to resolve in `/speckit-clarify`; this spec
  only constrains the ordering (sparse < normal < chaotic) and the degradation direction.
