# Research: Style System & Assets

## Decision: TOML parsing without a new dependency

`styles.toml` needs parsing, but constitution #6 forbids adding a required dependency beyond
matplotlib (numpy acceptable as transitive). Python's `tomllib` is stdlib only from 3.11+; this
project's floor is 3.10 (STANDUP_PLAN.md §2 resolved decision #6).

**Decision**: Use `tomllib` when available (`sys.version_info >= (3, 11)`); otherwise fall back
to a small hand-written parser covering only the exact subset `styles.toml` actually uses — flat
`[styles.<name>]` sections each containing a `display_name` string and an optional `scale`
float. This is not a general TOML parser; it's scoped narrowly to our own manifest format, which
we fully control.

**Rationale**: Avoids a new required dependency (even a conditional one via environment markers
still adds an install requirement for 3.10/3.10 users, which reads as "add no required
dependencies" being violated in spirit even if pip's marker syntax makes it technically
optional-per-version). The manifest format is simple enough (a handful of flat key-value pairs
per section) that a ~20-line parser is lower risk than pulling in a general-purpose library for a
first-party file we control end to end.

**Alternatives considered**: `tomli` as a conditional dependency for `python_version < "3.11"`
(rejected: still a new install requirement for a meaningful slice of supported users, however
small the library); switching the manifest format to JSON (rejected: STANDUP_PLAN.md's
architecture explicitly names `styles.toml`, and TOML's `[section]` syntax reads more naturally
for a small hand-authored config than JSON does — not worth deviating from the named file format
for a self-imposed dependency constraint that's solvable another way).

## Decision: Registry re-scans on every query (no caching)

Per the spec's Assumptions (already resolved, not re-litigated here): `assets/registry.py`
exposes a function that scans `assets/images/` and parses `styles.toml` fresh on each call,
rather than caching at import time.

**Rationale**: Style counts are tiny (single-digit directories for the foreseeable v1/v2
lifetime); a full re-scan costs microseconds. This keeps "drop a file, it just works" literally
true even mid-process (e.g., in a long-running notebook kernel where Chuck might add a style
directory without restarting), with zero cache-invalidation code to get wrong.

**Alternatives considered**: Cache-on-first-call with manual invalidation (rejected: added
complexity for a cost that isn't a measured problem — YAGNI).

## Decision: Even weighting via style-first, then image-within-style sampling

To satisfy FR-003 (even weighting across styles, not across raw image count), style resolution
in the render layer works in two steps: first pick a style uniformly at random from the
resolved style list (already how M1's `place_cats()` selects `Placement.style` — `rng.choice
(config.styles)`, confirmed unaffected by M3), then, in `render/artist.py`'s image resolution,
pick uniformly at random from *that style's* image pool.

**Rationale**: `PlacementConfig.styles` already carries a flat list of style names (M1's existing
contract, unchanged). M1's `rng.choice()` over that list is already even-per-style by
construction — as long as `styles.toml`'s style list has no duplicate names (each style
contributes exactly one entry to `config.styles`), M3 doesn't need to change M1 at all. The only
new logic is entirely within M3's own registry + artist code: resolving a style name to one of
its pool images.

**Alternatives considered**: none needed — this is a direct, low-risk consequence of the
existing M1 contract; no design tension to resolve.

## Decision: Deterministic (not RNG-based) image selection within a style's pool

A style with multiple images needs to pick *which* image a given placement uses. Naively using a
fresh `random.Random()` call inside `render/artist.py` would break constitution #3/M2's SC-002:
the same seed already guarantees identical `Placement` lists from M1, but M1's `Placement` has
no field for "which image within the style's pool" — so an independently-randomized image pick
at render time would make two seeded renders differ in which image is drawn per cat, even though
every position/size/rotation/style matched exactly.

**Decision**: Derive the image index deterministically from the placement's own already-seeded
fields: `index = hash((placement.x, placement.y, placement.size, placement.rotation)) %
len(pool)`, with the pool's image list sorted by filename first (glob/directory iteration order
isn't guaranteed stable across OSes, so sorting is required for the hash-to-index mapping to be
reproducible across machines, not just across runs on one machine).

**Rationale**: `hash()` on a tuple of floats is deterministic within and across Python processes
(unlike `str`/`bytes` hashing, float/int hashing is not affected by `PYTHONHASHSEED` salting), so
this requires no new RNG, no change to M1's `Placement` type, and no coupling between M1's
internal seeded RNG and M3's rendering code — it's a pure function of data M1 already guarantees
is reproducible.

**Alternatives considered**: Add an `image_index` field to M1's `Placement` (rejected: would
require M1's core engine to know pool sizes per style, breaking the "styles are opaque strings"
boundary between `core/` and `assets/`/`render/` that M1's spec explicitly established); a
second RNG seeded from the same seed value, threaded separately into the render layer (rejected:
works, but adds a second seeded-RNG code path to reason about and keep in sync with M1's, for no
benefit over the hash approach).
