"""Tests for catplotlib.render.bboxes — see specs/002-matplotlib-integration/."""

from __future__ import annotations

import matplotlib.pyplot as plt

from catplotlib.render.bboxes import extract_exclusions


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
