"""Generate the README's before/after hero image.

Renders the same chart twice (plain matplotlib, then with catplotlib active) and stitches
them side by side into docs/before_after.png. Regenerate after any change to placement,
render, or asset code that would visibly affect the default output:

    python scripts/make_readme_image.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

OUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "before_after.png"


def _make_chart(ax: plt.Axes) -> None:
    x = np.linspace(0, 10, 200)
    ax.plot(x, np.sin(x), label="signups")
    ax.plot(x, 0.5 * np.cos(x) + 1, label="churn")
    ax.set_xlabel("Week")
    ax.set_ylabel("Rate")
    ax.set_title("Weekly metrics")
    ax.legend()


def _render_panel(path: Path, with_cats: bool) -> None:
    if with_cats:
        import catplotlib

        catplotlib.set_style("mix")
        catplotlib.set_density("chaotic")
        catplotlib.set_seed(7)
    fig, ax = plt.subplots(figsize=(5, 4))
    _make_chart(ax)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    OUT_PATH.parent.mkdir(exist_ok=True)
    before_path = OUT_PATH.parent / "_before_tmp.png"
    after_path = OUT_PATH.parent / "_after_tmp.png"

    _render_panel(before_path, with_cats=False)
    _render_panel(after_path, with_cats=True)

    before_img = Image.open(before_path)
    after_img = Image.open(after_path)
    gap = 24
    height = max(before_img.height, after_img.height)
    combined = Image.new(
        "RGBA", (before_img.width + after_img.width + gap, height), (255, 255, 255, 255)
    )
    combined.paste(before_img, (0, 0))
    combined.paste(after_img, (before_img.width + gap, 0))
    combined.save(OUT_PATH)

    before_path.unlink()
    after_path.unlink()
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
