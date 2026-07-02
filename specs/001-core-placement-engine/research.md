# Research: Core Placement Engine

## Decision: Rectangle-based collision model

Every exclusion zone and every placed cat is represented as an axis-aligned bounding rectangle
`(x, y, width, height)` in figure-fraction coordinates (`0..1` on both axes, matching
matplotlib's `transFigure` space that the render layer will supply in M2).

**Rationale**: Axis-aligned bounding box (AABB) intersection is O(1) per pair and trivial to
property-test exhaustively with `hypothesis`. Using the true rotated-rectangle intersection would
require SAT (separating axis theorem) — meaningfully more complex than the AABB-of-the-rotated-
square approach adopted below (2026-07-02 addendum), for no correctness benefit: both approaches
guarantee zero visual overlap, SAT would just pack slightly denser.

**Alternatives considered**: Full SAT-based rotated-rectangle collision (rejected: meaningfully
more complex for a marginal packing-density gain — the AABB-of-rotated-square approach below
already achieves the actual product requirement, visible rotation with zero overlap); pixel-mask
collision (rejected: requires rendering, violates constitution #1 core purity).

### Addendum — 2026-07-02: `Placement.bbox()` now reserves the rotated footprint

Originally, `bbox()` returned the *unrotated* square (rotation stored as metadata only, never
rendered). The user reviewed the M2/M3 gallery output, found it looked static, and asked for
rotation to actually render as a v1 feature rather than staying deferred metadata. Rendering a
rotated square makes its true on-screen footprint bigger than the unrotated square (up to
~1.41x the side length, i.e. ~2x the area, at a 45-degree rotation) — so `bbox()` was changed to
return the axis-aligned bounding box of the *rotated* square: `side = size * (|cos theta| +
|sin theta|)`. This keeps the non-overlap guarantee (constitution #2) exactly intact when
rotation is actually rendered, at the cost of reserving more space per cat on average (~1.27x
side length / ~1.62x area, averaged over a uniform rotation distribution) — verified this did
not require retuning the density divisors below; the reference-canvas 3/6/12 sparse/normal/
chaotic counts held exactly after the change. `place_cats()`'s candidate-sampling loop was
updated to draw the candidate's rotation before its position, so the position-sampling bounds
already account for the rotation-dependent half-extent rather than the old code's fixed `size/2`
(which relied on the edge margin happening to absorb the difference — correct by accident, not
by construction, for the size range in use; the fix removes that fragility).

## Decision: Placement search — rejection sampling with shrink-on-failure

For each of the tier's target-count candidate slots: sample a random center point and size within
the min/max size range inside the border region's overall bounding box, using rejection sampling
against (a) the fixed edge margin, (b) all exclusion rectangles, and (c) all placements already
accepted in this call. After a bounded number of failed attempts for one candidate (e.g. 30), the
engine retries with the size scaled down by a fixed factor (e.g. ×0.85), down to the size range's
minimum; if still no fit is found, that candidate is skipped (not an error — see FR-003a's edge
case in the spec).

**Rationale**: Rejection sampling is simple, has no external dependencies, is trivially seedable
via a single `random.Random(seed)` instance threaded through the whole call, and naturally
produces the "scattered, not tiled" look the PRD wants (requirement 3). It degrades gracefully:
as available space shrinks, more attempts fail, sizes shrink, and eventually candidates are
dropped — which is exactly the graceful-degradation behavior FR-007/FR-008 require, with no
separate code path needed for the "small figure" case.

**Alternatives considered**: Deterministic grid/Poisson-disk sampling (rejected: produces a more
regular, less "randomized" look that cuts against PRD requirement 3, and is harder to make
visually distinct across density tiers); full backtracking search (rejected: unbounded worst-case
cost for a decorative feature with no correctness requirement to *maximize* placed count, only to
never violate exclusions).

## Decision: RNG — `random.Random`, not `numpy.random`

Use the standard library's `random.Random(seed)` instance, not `numpy.random.Generator`.

**Rationale**: `numpy` is already a transitive dependency of matplotlib and is fine to depend on
per constitution #6, but the placement engine's randomness needs (floats, choice from a list) are
fully covered by `random.Random` with zero additional API surface, and stdlib `random.Random`
instances are simple to snapshot/thread explicitly (no global state), which keeps `core/rng.py`
a thin, obviously-pure wrapper.

**Alternatives considered**: `numpy.random.default_rng` (rejected: no benefit for this workload,
adds a numpy-specific seeding API to learn/document for no gain).

## Decision: Property-based testing with `hypothesis`

FR-002/FR-003a (never overlap exclusions or other cats) are safety properties best verified by
generating many randomized canvases, exclusion layouts, densities, and seeds rather than a fixed
set of example-based tests.

**Rationale**: Already specified in STANDUP_PLAN.md §8 and listed as a dev dependency in
`pyproject.toml`. `hypothesis` strategies will generate: canvas width/height pairs (including
degenerate 0/negative cases per the spec's edge cases), lists of 0-N exclusion rectangles
(including overlapping ones), all three density tiers, and both seeded and unseeded calls.

**Alternatives considered**: Hand-written example tests only (rejected: cannot practically cover
the input space broadly enough to back SC-001's "100% of generated placements" claim).
