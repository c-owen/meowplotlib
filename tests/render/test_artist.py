"""Tests for style resolution wired through render/artist.py — see specs/003-style-system/."""

from __future__ import annotations

import io

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

import catplotlib
from catplotlib.assets.registry import available_styles


def _reference_figure() -> plt.Figure:
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    return fig


def _style_image_arrays() -> dict[str, list[np.ndarray]]:
    return {
        name: [mpimg.imread(p) for p in info.image_paths]
        for name, info in available_styles().items()
    }


def _cat_style_names(fig: plt.Figure) -> list[str]:
    """Infer each placed cat's style by matching its rendered image array against pools."""
    pools = _style_image_arrays()
    resolved = []
    for ax in fig.axes:
        if not getattr(ax, "_catplotlib_cat", False):
            continue
        rendered = np.asarray(ax.images[0].get_array())
        for name, images in pools.items():
            if any(np.array_equal(rendered, img) for img in images):
                resolved.append(name)
                break
    return resolved


# --- User Story 1: single style ------------------------------------------------------


def test_single_style_all_cats_from_that_pool() -> None:
    catplotlib.set_style("chonk")
    catplotlib.set_density("chaotic")
    catplotlib.set_seed(1)
    fig = _reference_figure()
    fig.canvas.draw()

    resolved = _cat_style_names(fig)
    assert resolved
    assert all(name == "chonk" for name in resolved)


# --- User Story 2: mixing --------------------------------------------------------------


def test_mix_produces_more_than_one_style_across_seeds() -> None:
    catplotlib.set_style("mix")
    catplotlib.set_density("chaotic")

    saw_multiple = False
    for seed in range(20):
        catplotlib.set_seed(seed)
        fig = _reference_figure()
        fig.canvas.draw()
        if len(set(_cat_style_names(fig))) > 1:
            saw_multiple = True
        plt.close(fig)

    assert saw_multiple


# --- Polish: deterministic pooling + reproducibility ------------------------------------


def test_reproducibility_survives_style_resolution() -> None:
    catplotlib.set_style("chonk")
    catplotlib.set_seed(1)
    catplotlib.set_density("chaotic")

    fig1 = _reference_figure()
    buf1 = io.BytesIO()
    fig1.savefig(buf1, format="png")

    fig2 = _reference_figure()
    buf2 = io.BytesIO()
    fig2.savefig(buf2, format="png")

    assert buf1.getvalue() == buf2.getvalue()
