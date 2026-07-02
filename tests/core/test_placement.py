"""Tests for meowplotlib.core.placement — see specs/001-core-placement-engine/."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from meowplotlib.core.placement import PlacementConfig, Rect, place_cats

DENSITIES: tuple[str, ...] = ("sparse", "normal", "chaotic")

# --- Shared hypothesis strategies -------------------------------------------------

canvas_dims = st.floats(min_value=0.05, max_value=2.0, allow_nan=False, allow_infinity=False)
degenerate_dims = st.floats(min_value=-10.0, max_value=0.0, allow_nan=False, allow_infinity=False)


def _rect_strategy(max_dim: float = 5.0) -> st.SearchStrategy[Rect]:
    return st.builds(
        Rect,
        x=st.floats(min_value=-1.0, max_value=max_dim, allow_nan=False, allow_infinity=False),
        y=st.floats(min_value=-1.0, max_value=max_dim, allow_nan=False, allow_infinity=False),
        width=st.floats(min_value=0.0, max_value=max_dim, allow_nan=False, allow_infinity=False),
        height=st.floats(min_value=0.0, max_value=max_dim, allow_nan=False, allow_infinity=False),
    )


exclusions_strategy = st.lists(_rect_strategy(), min_size=0, max_size=4)
density_strategy = st.sampled_from(DENSITIES)
seed_strategy = st.one_of(st.none(), st.integers(min_value=0, max_value=2**31 - 1))


def _config(density: str = "normal", seed: int | None = 1) -> PlacementConfig:
    return PlacementConfig(density=density, size_range=(0.03, 0.08), seed=seed, styles=["classic"])


REFERENCE_W, REFERENCE_H = 1.0, 1.0
REFERENCE_EXCLUSIONS = [Rect(x=0.15, y=0.15, width=0.7, height=0.7)]

# --- User Story 1: cats never cover the chart --------------------------------------


def test_us1_placements_avoid_centered_exclusion() -> None:
    result = place_cats(REFERENCE_W, REFERENCE_H, REFERENCE_EXCLUSIONS, _config())
    for placement in result:
        assert not placement.bbox().intersects(REFERENCE_EXCLUSIONS[0])


def test_us1_near_full_coverage_leaves_only_slivers_or_nothing() -> None:
    near_full = [Rect(x=0.02, y=0.02, width=0.96, height=0.96)]
    result = place_cats(REFERENCE_W, REFERENCE_H, near_full, _config("chaotic"))
    for placement in result:
        assert not placement.bbox().intersects(near_full[0])


@given(
    canvas_width=canvas_dims,
    canvas_height=canvas_dims,
    exclusions=exclusions_strategy,
    density=density_strategy,
    seed=seed_strategy,
)
@settings(max_examples=100, deadline=None)
def test_us1_property_never_intersects_exclusions_or_margin(
    canvas_width: float,
    canvas_height: float,
    exclusions: list[Rect],
    density: str,
    seed: int | None,
) -> None:
    config = _config(density, seed)
    result = place_cats(canvas_width, canvas_height, exclusions, config)
    margin = 0.03 * min(canvas_width, canvas_height)
    for placement in result:
        bbox = placement.bbox()
        for exclusion in exclusions:
            assert not bbox.intersects(exclusion)
        assert bbox.x >= margin - 1e-9
        assert bbox.y >= margin - 1e-9
        assert bbox.x + bbox.width <= canvas_width - margin + 1e-9
        assert bbox.y + bbox.height <= canvas_height - margin + 1e-9


@given(
    canvas_width=canvas_dims,
    canvas_height=canvas_dims,
    exclusions=exclusions_strategy,
    density=density_strategy,
    seed=seed_strategy,
)
@settings(max_examples=100, deadline=None)
def test_us1_property_placements_never_overlap_each_other(
    canvas_width: float,
    canvas_height: float,
    exclusions: list[Rect],
    density: str,
    seed: int | None,
) -> None:
    result = place_cats(canvas_width, canvas_height, exclusions, _config(density, seed))
    for i, a in enumerate(result):
        for b in result[i + 1 :]:
            assert not a.bbox().intersects(b.bbox())


# --- User Story 2: reproducibility with a seed --------------------------------------


def test_us2_same_seed_produces_identical_placements() -> None:
    config = _config(seed=42)
    first = place_cats(REFERENCE_W, REFERENCE_H, REFERENCE_EXCLUSIONS, config)
    second = place_cats(REFERENCE_W, REFERENCE_H, REFERENCE_EXCLUSIONS, config)
    assert first == second


def test_us2_no_seed_produces_different_consecutive_results() -> None:
    config = _config(seed=None)
    first = place_cats(REFERENCE_W, REFERENCE_H, REFERENCE_EXCLUSIONS, config)
    second = place_cats(REFERENCE_W, REFERENCE_H, REFERENCE_EXCLUSIONS, config)
    assert first != second


@given(
    canvas_width=canvas_dims,
    canvas_height=canvas_dims,
    exclusions=exclusions_strategy,
    density=density_strategy,
    seed=st.integers(min_value=0, max_value=2**31 - 1),
)
@settings(max_examples=100, deadline=None)
def test_us2_property_seeded_calls_are_byte_identical(
    canvas_width: float, canvas_height: float, exclusions: list[Rect], density: str, seed: int
) -> None:
    config = _config(density, seed)
    first = place_cats(canvas_width, canvas_height, exclusions, config)
    second = place_cats(canvas_width, canvas_height, exclusions, config)
    assert first == second


# --- User Story 3: density tiers ----------------------------------------------------


def test_us3_density_tiers_strictly_increase_on_reference_canvas() -> None:
    counts = [
        len(place_cats(REFERENCE_W, REFERENCE_H, REFERENCE_EXCLUSIONS, _config(d, seed=7)))
        for d in DENSITIES
    ]
    assert counts[0] < counts[1] < counts[2]


@given(seed=st.integers(min_value=0, max_value=2**31 - 1))
@settings(max_examples=20)
def test_us3_property_density_ordering_holds_across_seeds(seed: int) -> None:
    counts = [
        len(place_cats(REFERENCE_W, REFERENCE_H, REFERENCE_EXCLUSIONS, _config(d, seed)))
        for d in DENSITIES
    ]
    assert counts[0] < counts[1] < counts[2]


# --- User Story 4: graceful degradation ---------------------------------------------


def test_us4_full_coverage_returns_empty() -> None:
    full = [Rect(x=0.0, y=0.0, width=REFERENCE_W, height=REFERENCE_H)]
    assert place_cats(REFERENCE_W, REFERENCE_H, full, _config()) == []


def test_us4_nonpositive_canvas_dims_return_empty() -> None:
    assert place_cats(0.0, 1.0, [], _config()) == []
    assert place_cats(1.0, 0.0, [], _config()) == []
    assert place_cats(-1.0, 1.0, [], _config()) == []


def test_us4_empty_styles_return_empty() -> None:
    config = PlacementConfig(density="chaotic", size_range=(0.03, 0.08), seed=1, styles=[])
    assert place_cats(REFERENCE_W, REFERENCE_H, [], config) == []


@given(seed=st.integers(min_value=0, max_value=2**31 - 1))
@settings(max_examples=30)
def test_us4_property_count_trends_to_zero_as_coverage_grows(seed: int) -> None:
    checkpoints = [0.0, 0.5, 0.8, 0.95, 0.99, 1.0]
    counts = []
    for coverage_fraction in checkpoints:
        inset = (1 - coverage_fraction) / 2
        exclusion = Rect(x=inset, y=inset, width=coverage_fraction, height=coverage_fraction)
        result = place_cats(REFERENCE_W, REFERENCE_H, [exclusion], _config("chaotic", seed))
        counts.append(len(result))
    assert counts[-1] == 0
    assert counts == sorted(counts, reverse=True)
