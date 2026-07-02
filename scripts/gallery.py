"""Render a quick visual gallery of catplotlib output for human review.

Not a shipped feature (STANDUP_PLAN.md explicitly scopes a public "gallery mode" as P2/out of
v1) — this is a dev-loop tool so Chuck can judge charm/placement aesthetics from PNGs instead of
running his own test plots. Regenerate after any change to placement, render, or asset code:

    python scripts/gallery.py

Output goes to gallery_output/ (gitignored).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

import catplotlib

OUT_DIR = Path(__file__).resolve().parent.parent / "gallery_output"


def _line_chart(ax: plt.Axes) -> None:
    x = np.linspace(0, 10, 50)
    ax.plot(x, np.sin(x), label="sin(x)")
    ax.plot(x, np.cos(x), label="cos(x)")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()


def _bar_chart(ax: plt.Axes) -> None:
    ax.bar(["Mon", "Tue", "Wed", "Thu", "Fri"], [12, 19, 7, 15, 22])
    ax.set_xlabel("Day")
    ax.set_ylabel("Count")


def _scatter_chart(ax: plt.Axes) -> None:
    rng = np.random.default_rng(0)
    ax.scatter(rng.normal(size=60), rng.normal(size=60))
    ax.set_xlabel("x")
    ax.set_ylabel("y")


def _histogram_chart(ax: plt.Axes) -> None:
    rng = np.random.default_rng(0)
    ax.hist(rng.normal(size=500), bins=30)
    ax.set_xlabel("value")
    ax.set_ylabel("frequency")


CHARTS = {
    "line": _line_chart,
    "bar": _bar_chart,
    "scatter": _scatter_chart,
    "histogram": _histogram_chart,
}

FIGSIZES = {
    "small": (2.5, 2.5),
    "default": (6.4, 4.8),
    "large": (10.0, 7.5),
}

DENSITIES = ("sparse", "normal", "chaotic")


def render_chart_type_grid() -> None:
    """One PNG per chart type, default figsize, normal density, seeded."""
    catplotlib.set_density("normal")
    catplotlib.set_seed(1)
    for name, plot_fn in CHARTS.items():
        fig, ax = plt.subplots(figsize=FIGSIZES["default"])
        plot_fn(ax)
        fig.savefig(OUT_DIR / f"chart-{name}.png", dpi=150)
        plt.close(fig)


def render_density_grid() -> None:
    """Same chart at each density tier, to compare sparse/normal/chaotic side by side."""
    catplotlib.set_seed(1)
    for density in DENSITIES:
        catplotlib.set_density(density)
        fig, ax = plt.subplots(figsize=FIGSIZES["default"])
        _line_chart(ax)
        fig.savefig(OUT_DIR / f"density-{density}.png", dpi=150)
        plt.close(fig)
    catplotlib.set_density("normal")


def render_figsize_grid() -> None:
    """Same chart at each figsize tier, to check graceful degradation on small figures."""
    catplotlib.set_density("chaotic")  # stress the degradation behavior
    catplotlib.set_seed(1)
    for size_name in FIGSIZES:
        fig, ax = plt.subplots(figsize=FIGSIZES[size_name])
        _bar_chart(ax)
        fig.savefig(OUT_DIR / f"figsize-{size_name}.png", dpi=150)
        plt.close(fig)
    catplotlib.set_density("normal")


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    render_chart_type_grid()
    render_density_grid()
    render_figsize_grid()
    written = sorted(p.name for p in OUT_DIR.glob("*.png"))
    print(f"Wrote {len(written)} PNGs to {OUT_DIR}:")
    for name in written:
        print(f"  {name}")


if __name__ == "__main__":
    main()
