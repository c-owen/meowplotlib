"""Tests for catplotlib.render.hook — see specs/002-matplotlib-integration/."""

from __future__ import annotations

import io
import subprocess
import sys

import matplotlib.pyplot as plt
import pytest

import catplotlib
from tests.render._helpers import count_cat_axes

# --- User Story 1: one import, cats everywhere --------------------------------------


def test_import_does_not_raise_under_agg() -> None:
    script = (
        "import matplotlib; matplotlib.use('Agg'); "
        "import matplotlib.pyplot as plt; import catplotlib; plt.figure()"
    )
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def _plot_reference_figure() -> plt.Figure:
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    return fig


def test_savefig_path_decorates() -> None:
    fig = _plot_reference_figure()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")

    assert getattr(fig, "_catplotlib_decorated", False) is True
    assert count_cat_axes(fig) > 0


def test_canvas_draw_path_decorates() -> None:
    fig = _plot_reference_figure()
    fig.canvas.draw()

    assert getattr(fig, "_catplotlib_decorated", False) is True
    assert count_cat_axes(fig) > 0


# --- User Story 2: no duplication on redraw ------------------------------------------


def test_repeated_redraws_do_not_change_artist_count() -> None:
    fig = _plot_reference_figure()
    fig.canvas.draw()
    before = count_cat_axes(fig)

    for _ in range(5):
        fig.canvas.draw()

    assert count_cat_axes(fig) == before


def test_repeated_savefig_produces_identical_bytes() -> None:
    fig = _plot_reference_figure()
    buf1 = io.BytesIO()
    fig.savefig(buf1, format="png")
    buf2 = io.BytesIO()
    fig.savefig(buf2, format="png")

    assert buf1.getvalue() == buf2.getvalue()


# --- User Story 3: session on/off switch ---------------------------------------------


def _no_catplotlib_baseline_bytes() -> bytes:
    script = (
        "import io, matplotlib\n"
        "matplotlib.use('Agg')\n"
        "import matplotlib.pyplot as plt\n"
        "fig, ax = plt.subplots()\n"
        "ax.plot([1, 2, 3], [1, 4, 9])\n"
        "ax.set_xlabel('x')\n"
        "ax.set_ylabel('y')\n"
        "buf = io.BytesIO()\n"
        "fig.savefig(buf, format='png')\n"
        "import sys\n"
        "sys.stdout.buffer.write(buf.getvalue())\n"
    )
    result = subprocess.run([sys.executable, "-c", script], capture_output=True)
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_disable_produces_byte_identical_output_to_no_import_baseline() -> None:
    baseline = _no_catplotlib_baseline_bytes()

    catplotlib.disable()
    fig = _plot_reference_figure()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")

    assert buf.getvalue() == baseline
    assert getattr(fig, "_catplotlib_decorated", False) is False


def test_enable_after_disable_restores_decoration() -> None:
    catplotlib.disable()
    catplotlib.enable()

    fig = _plot_reference_figure()
    fig.canvas.draw()

    assert getattr(fig, "_catplotlib_decorated", False) is True


def test_disable_does_not_strip_already_decorated_figure() -> None:
    fig = _plot_reference_figure()
    fig.canvas.draw()
    decorated_count = count_cat_axes(fig)
    assert decorated_count > 0

    catplotlib.disable()
    fig.canvas.draw()

    assert count_cat_axes(fig) == decorated_count


# --- Seaborn compatibility (edge case) -------------------------------------------------


def test_seaborn_figures_decorate_if_seaborn_available() -> None:
    seaborn = pytest.importorskip("seaborn")
    fig, ax = plt.subplots()
    seaborn.lineplot(x=[1, 2, 3], y=[1, 4, 9], ax=ax)
    fig.canvas.draw()

    assert getattr(fig, "_catplotlib_decorated", False) is True
