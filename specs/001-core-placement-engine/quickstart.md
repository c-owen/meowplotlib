# Quickstart: Core Placement Engine

Validates the feature end-to-end without any matplotlib rendering (this module has none).

## Prerequisites

```bash
source .venv/Scripts/activate   # or: .venv/Scripts/activate.ps1 on PowerShell
```

## Run the automated acceptance tests

```bash
pytest tests/core/test_placement.py -q
```

Expect all tests green, including the `hypothesis` property-based suite covering SC-001–SC-004.

## Manual smoke check

```python
from meowplotlib.core.placement import PlacementConfig, Rect, place_cats

canvas_w, canvas_h = 1.0, 1.0
exclusions = [Rect(x=0.15, y=0.15, width=0.7, height=0.7)]  # a typical centered axes area

cfg = PlacementConfig(density="normal", size_range=(0.03, 0.08), seed=42, styles=["classic"])
placements = place_cats(canvas_w, canvas_h, exclusions, cfg)

assert placements  # normal density on a generous border should place at least one cat
assert all(not p.bbox().intersects(exclusions[0]) for p in placements)

# Reproducibility
placements_again = place_cats(canvas_w, canvas_h, exclusions, cfg)
assert placements == placements_again

# Tier ordering
sparse = place_cats(canvas_w, canvas_h, exclusions, PlacementConfig("sparse", (0.03, 0.08), 42, ["classic"]))
chaotic = place_cats(canvas_w, canvas_h, exclusions, PlacementConfig("chaotic", (0.03, 0.08), 42, ["classic"]))
assert len(sparse) < len(placements) < len(chaotic)

# Graceful degradation to zero
full_cover = [Rect(x=0.0, y=0.0, width=1.0, height=1.0)]
assert place_cats(canvas_w, canvas_h, full_cover, cfg) == []
```

## Expected outcome

All assertions pass; no exception is raised for any input in this script, including the
full-coverage zero-placements case.
