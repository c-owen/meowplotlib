"""Generate simple, visually distinct placeholder cat PNGs for each launch style.

Run: python scripts/make_placeholders.py
Overwrites existing placeholder-generated files under assets/images/<style>/.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Ellipse, Polygon

ASSETS_DIR = Path(__file__).resolve().parent.parent / "src" / "meowplotlib" / "assets" / "images"


def _new_canvas() -> tuple[Figure, Axes]:
    fig = Figure(figsize=(1.28, 1.28), dpi=100)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor("none")
    return fig, ax


def _save(fig: Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, transparent=True)


def make_classic(path: Path) -> None:
    fig, ax = _new_canvas()
    color = "#4a4a4a"
    ax.add_patch(Circle((0.5, 0.42), 0.28, facecolor=color, edgecolor="none", zorder=1))
    ax.add_patch(Polygon([[0.28, 0.62], [0.34, 0.85], [0.42, 0.64]], facecolor=color, zorder=0))
    ax.add_patch(Polygon([[0.72, 0.62], [0.66, 0.85], [0.58, 0.64]], facecolor=color, zorder=0))
    ax.add_patch(Circle((0.42, 0.44), 0.03, facecolor="#f5c542", zorder=2))
    ax.add_patch(Circle((0.58, 0.44), 0.03, facecolor="#f5c542", zorder=2))
    _save(fig, path)


def make_derp(path: Path) -> None:
    fig, ax = _new_canvas()
    color = "#d97b4f"
    ax.add_patch(Ellipse((0.5, 0.4), 0.62, 0.5, facecolor=color, edgecolor="none", zorder=1))
    ax.add_patch(Polygon([[0.24, 0.58], [0.18, 0.9], [0.36, 0.62]], facecolor=color, zorder=0))
    ax.add_patch(Polygon([[0.76, 0.58], [0.9, 0.78], [0.62, 0.62]], facecolor=color, zorder=0))
    ax.add_patch(Circle((0.4, 0.42), 0.05, facecolor="white", zorder=2))
    ax.add_patch(Circle((0.4, 0.42), 0.02, facecolor="black", zorder=3))
    ax.add_patch(Circle((0.63, 0.38), 0.045, facecolor="white", zorder=2))
    ax.add_patch(Circle((0.63, 0.38), 0.018, facecolor="black", zorder=3))
    ax.plot([0.46, 0.58], [0.28, 0.3], color="black", linewidth=2, zorder=2)
    _save(fig, path)


def make_chonk(path: Path) -> None:
    fig, ax = _new_canvas()
    color = "#e8a33d"
    ax.add_patch(Ellipse((0.5, 0.4), 0.85, 0.62, facecolor=color, edgecolor="none", zorder=1))
    ax.add_patch(Polygon([[0.2, 0.62], [0.16, 0.88], [0.32, 0.66]], facecolor=color, zorder=0))
    ax.add_patch(Polygon([[0.8, 0.62], [0.84, 0.88], [0.68, 0.66]], facecolor=color, zorder=0))
    for stripe_x in (0.35, 0.5, 0.65):
        ax.plot(
            [stripe_x, stripe_x],
            [0.55, 0.72],
            color="#c07f22",
            linewidth=3,
            zorder=1,
            solid_capstyle="round",
        )
    ax.add_patch(Circle((0.38, 0.42), 0.035, facecolor="black", zorder=2))
    ax.add_patch(Circle((0.62, 0.42), 0.035, facecolor="black", zorder=2))
    _save(fig, path)


STYLE_GENERATORS = {
    "classic": make_classic,
    "derp": make_derp,
    "chonk": make_chonk,
}


def main() -> None:
    for style, generator in STYLE_GENERATORS.items():
        out_path = ASSETS_DIR / style / f"{style}_01.png"
        generator(out_path)
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
