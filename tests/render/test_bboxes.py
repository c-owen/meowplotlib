"""Tests for catplotlib.render.bboxes — see specs/002-matplotlib-integration/."""

from __future__ import annotations

import matplotlib.pyplot as plt

import catplotlib
from catplotlib.render.bboxes import ensure_minimum_margin, extract_exclusions


def test_extract_exclusions_covers_axes_and_labels() -> None:
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    ax.set_xlabel("x label")
    ax.set_ylabel("y label")
    fig.canvas.draw()

    exclusions = extract_exclusions(fig)

    assert len(exclusions) == 1
    rect = exclusions[0]
    # The tight bbox should be a substantial fraction of the figure, not a sliver.
    assert rect.width > 0.3
    assert rect.height > 0.3


def test_extract_exclusions_includes_legend_when_present() -> None:
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9], label="series")
    ax.legend()
    fig.canvas.draw()

    exclusions = extract_exclusions(fig)

    assert len(exclusions) == 2  # axes tight bbox + legend bbox


def test_extract_exclusions_empty_for_bare_figure() -> None:
    fig = plt.figure()
    fig.canvas.draw()

    assert extract_exclusions(fig) == []


def test_ensure_minimum_margin_guarantees_all_four_sides() -> None:
    catplotlib.disable()  # avoid the hook's own automatic ensure_minimum_margin call
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    ax.plot([1, 2, 3], [1, 4, 9])
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.canvas.draw()

    before = extract_exclusions(fig)[0]
    assert before.y < 0.05  # natural layout leaves almost no bottom margin

    ensure_minimum_margin(fig, 0.10)
    fig.canvas.draw()
    after = extract_exclusions(fig)[0]

    assert after.x >= 0.10 - 1e-9
    assert after.y >= 0.10 - 1e-9
    assert after.x + after.width <= 0.90 + 1e-9
    assert after.y + after.height <= 0.90 + 1e-9


def test_ensure_minimum_margin_does_not_grow_already_generous_margin() -> None:
    catplotlib.disable()  # avoid the hook's own automatic ensure_minimum_margin call
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    ax.plot([1, 2, 3], [1, 4, 9])
    fig.canvas.draw()

    ensure_minimum_margin(fig, 0.01)  # smaller than the natural margin
    fig.canvas.draw()
    after = extract_exclusions(fig)[0]

    # A tiny requested margin should leave the axes essentially where matplotlib put it.
    assert after.x < 0.1
    assert after.y < 0.1
